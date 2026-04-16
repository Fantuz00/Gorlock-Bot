
import discord
import os
import yt_dlp
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import re
import aiohttp
from datetime import datetime, timedelta, timezone


try:
    discord.opus.load_opus('/usr/local/lib/libopus.so')
    print("✅ OPUS CARICATO CON SUCCESSO!")
except Exception as e:
    print(f"❌ ERRORE CARICAMENTO OPUS: {e}")


queues = {}
raid_mode = False  # Inizializzazione necessaria per il sistema anti-raid


# Serve per tenere traccia della velocità dei messaggi per utente
user_spam_counter = {} 


path_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=path_env)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_KEY = os.getenv('WEATHER_API_KEY')
PROXY_KEY = os.getenv('PROXYCHECK_KEY')


if DISCORD_TOKEN is None:
    print("❌ ERRORE: Il file .env esiste ma non riesco a leggere 'DISCORD_TOKEN'.")
    print(f"Percorso cercato: {path_env}")
else:
    print("✅ Token caricato correttamente!")


intents = discord.Intents.default()
intents.members = True  # Necessario per info utenti e join
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# --- CONFIGURAZIONI MUSICA (Unificate e Ottimizzate) ---
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

@bot.event
async def on_ready():
    print(f'✅ Bot online come {bot.user}')

# --- COMANDO METEO ---
@bot.command()
async def meteo(ctx, *, citta: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={citta}&appid={WEATHER_KEY}&units=metric&lang=it"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                response = await resp.json()
                if response["cod"] == 200:
                    temp = response["main"]["temp"]
                    desc = response["weather"][0]["description"]
                    umidita = response["main"]["humidity"]
                    await ctx.send(f"🌤️ **Meteo per {citta.capitalize()}:**\n🌡️ Temperatura: {temp}°C\n📝 Condizioni: {desc}\n💧 Umidità: {umidita}%")
                else:
                    await ctx.send("❌ Città non trovata. Controlla il nome!")
        except Exception as e:
            await ctx.send(f"Si è verificato un errore: {e}")

@bot.command(name="aiuto", aliases=["help", "comandi"])
async def aiuto(ctx):
    """Mostra la lista di tutti i comandi e le loro funzionalità"""
    embed = discord.Embed(
        title="🤖 Manuale di Gorlock il Distruttore",
        description="Ecco tutti i comandi disponibili per interagire con me:",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="🌤️ `/meteo [città]`", value="Mostra il meteo attuale della città scelta.", inline=False)
    embed.add_field(name="🎵 `/play [titolo]`", value="Riproduce musica da YouTube nel canale vocale.", inline=False)
    embed.add_field(name="⏸️ `/pause`", value="Mette in pausa la musica attuale.", inline=False)
    embed.add_field(name="▶️ `/resume`", value="Riprende la musica in pausa.", inline=False)
    embed.add_field(name="📋 `/queue`", value="Visualizza la lista dei brani in coda.", inline=False)
    embed.add_field(name="⏭️ `/skip`", value="Passa istantaneamente al brano successivo.", inline=False)
    embed.add_field(name="⏹️ `/stop`", value="Interrompe la musica e disconnette il bot.", inline=False)
    embed.add_field(name="🧹 `/clear [n]`", value="Elimina 'n' messaggi (Staff).", inline=False)
    embed.add_field(name="📊 `/status`", value="Controlla la latenza e lo stato operativo.", inline=False)
    embed.set_footer(text="Gorlock osserva ogni tua mossa.")
    await ctx.send(embed=embed)

# --- COMANDI MUSICA ---

def check_queue(ctx, guild_id):
    if guild_id in queues and queues[guild_id]:
        next_item = queues[guild_id].pop(0)
        source = next_item[0]
        ctx.voice_client.play(source, after=lambda e: check_queue(ctx, guild_id))

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("⚠️ Devi essere in un canale vocale per usare questo comando!")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                url = info['url']
                title = info['title']
                
              
                source = await discord.FFmpegOpusAudio.from_probe(url, executable="ffmpeg", **FFMPEG_OPTIONS)
                
                guild_id = ctx.guild.id
                
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                  if guild_id not in queues:
                        queues[guild_id] = []
                    queues[guild_id].append((source, title))
                    await ctx.send(f"🎵 **{title}** aggiunto alla coda!")
                else:
                    ctx.voice_client.play(source, after=lambda e: check_queue(ctx, guild_id))
                    await ctx.send(f"🎶 In riproduzione: **{title}**")
                    
            except Exception as e:
                await ctx.send(f"❌ Errore durante la riproduzione: {e}")

@bot.command(name="queue", aliases=["lista", "q"])
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in queues or not queues[guild_id]:
        return await ctx.send("📭 La coda è vuota!")

    messaggio = "**📋 Coda attuale:**\n"
    for i, (audio, titolo) in enumerate(queues[guild_id], start=1):
        messaggio += f"{i}. {titolo}\n"
    await ctx.send(messaggio)

@bot.command()
async def pause(ctx):
    """Mette in pausa la riproduzione musicale"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ **Musica in pausa.** Usa `/resume` per riprendere.")
    else:
        await ctx.send("⚠️ Non c'è musica in riproduzione da mettere in pausa.")

@bot.command()
async def resume(ctx):
    """Riprende la riproduzione musicale"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ **Musica ripresa!**")
    else:
        await ctx.send("⚠️ La musica non è in pausa.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Canzone saltata!")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnesso dal canale vocale.")
    else:
        await ctx.send("Non sono connesso a nessun canale vocale.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Cancella un numero specificato di messaggi (es. !clear 10)"""
    if amount < 1:
        return await ctx.send("Devi cancellare almeno 1 messaggio!")
    
   
    deleted = await ctx.channel.purge(limit=amount + 1)
    
   
    msg = await ctx.send(f"✅ Ho eliminato {len(deleted)-1} messaggi, capo!")
    await asyncio.sleep(5)
    await msg.delete()


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Non hai il permesso 'Gestisci Messaggi' per farlo!")





# Logs di Sicurezza

@bot.event
async def on_member_ban(guild, user):
    channel = discord.utils.get(guild.text_channels, name="logs-bot")
    if channel:
        await channel.send(f"🚨 **ALLERTA SICUREZZA:** L'utente {user.name} è stato bannato! Possibile intrusione neutralizzata.")

@bot.event
async def on_guild_role_create(role):
    channel = discord.utils.get(role.guild.text_channels, name="logs-bot")
    if channel:
        await channel.send(f"⚠️ **ATTENZIONE:** È stato creato un nuovo ruolo: `{role.name}`. Verificare che non sia un hacker con permessi Admin!")


# Monitoraggio Ping

@bot.command(name="status", aliases=["ping", "check"])
async def status(ctx):
    """Controlla la velocità di risposta di Gorlock e lo stato del server"""
    
    
    lat_ms = round(bot.latency * 1000)
    
    
    if lat_ms < 100:
        colore = "🟢" 
        desc = "SISTEMI OTTIMIZZATI. Gorlock è pronto a distruggere."
    elif lat_ms < 250:
        colore = "🟡" 
        desc = "RALLENTAMENTO RILEVATO. Possibile sovraccarico dati."
    else:
        colore = "🔴" 
        desc = "EMERGENZA. Latenza elevata, connessione instabile!"

    await ctx.send(
        f"📊 **REPORT DI SISTEMA GORLOCK**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 **Latenza:** `{lat_ms}ms`\n"
        f"🛡️ **Stato:** {colore} {desc}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )


# Controllo Data Account Nuovi e Anti-Raid

@bot.event
async def on_member_join(member):
    # --- PARTE ANTI-RAID ---
    global raid_mode
    if raid_mode:
        try:
            await member.send("Spiacente, il server è attualmente in modalità sicurezza.")
            await member.kick(reason="Anti-Raid Attivo")
            return 
        except:
            await member.kick(reason="Anti-Raid Attivo")
            return

    # --- PARTE CONTROLLO ETA' ---
    now = datetime.now(timezone.utc)
    creation_date = member.created_at
    eta_account = (now - creation_date).days
    
    if eta_account < 3:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] SOSPETTO: {member.name} (ID: {member.id}) - Account creato da {eta_account} giorni.\n"
        with open("logs_sospetti.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        channel = discord.utils.get(member.guild.text_channels, name="logs-bot")
        if channel:
            embed = discord.Embed(title="🚨 Rilevamento Account Sospetto", color=discord.Color.red())
            embed.add_field(name="Utente", value=member.mention, inline=True)
            embed.add_field(name="Età Account", value=f"{eta_account} giorni", inline=True)
            await channel.send(embed=embed)


# Log di Emergenza

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        await channel.guild.system_channel.send(f"🚨 **ALLERTA:** Il canale `{channel.name}` è stato eliminato da **{entry.user}**!")

@bot.event
async def on_guild_role_update(before, after):
    if before.permissions != after.permissions:
        await after.guild.system_channel.send(f"⚖️ **SICUREZZA:** I permessi del ruolo `{after.name}` sono stati modificati!")



# --- LOGICA IDS DA INSERIRE DENTRO IL TUO on_message ---

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # --- IDS: FILTRO PAROLE BANDITE ---
    banned_words = ["scam", "cheat", "hacker", "regalo"] # Aggiungi qui le parole da bloccare
    if any(word in message.content.lower() for word in banned_words):
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, linguaggio non consentito dalla policy di Gorlock.", delete_after=3)
            return

    # --- IDS: ANTI-SPAM ---
    uid = message.author.id
    ora_attuale = datetime.now()
    if uid not in user_spam_counter:
        user_spam_counter[uid] = []
    user_spam_counter[uid] = [t for t in user_spam_counter[uid] if ora_attuale - t < timedelta(seconds=5)]
    user_spam_counter[uid].append(ora_attuale)

    if len(user_spam_counter[uid]) > 5 and not message.author.guild_permissions.administrator:
        await message.channel.send(f"🚫 {message.author.mention}, rallenta!", delete_after=3)
        return

    # --- IDS: MASS MENTION ---
    if len(message.mentions) > 5 and not message.author.guild_permissions.administrator:
        await message.delete()
        log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
        if log_channel:
            await log_channel.send(f"🚨 **IDS:** Mass Mention da {message.author.mention}")
        return

    # --- ANTI-LINK & URL SAFETY ---
    forbidden_keywords = [".exe", "gift", "nitro", "free-coins", "discord.gg/"]
    urls = re.findall(r'(https?://\S+|www\.\S+)', message.content.lower())
    is_forbidden = any(k in message.content.lower() for k in forbidden_keywords)
    
    is_dangerous = False
    for url in urls:
        is_dangerous = await check_url_safety(url)
        if is_dangerous: break

    # --- CONTROLLO ALLEGATI (FILE E IMMAGINI) ---
    if message.attachments and not message.author.guild_permissions.administrator:
        for attachment in message.attachments:
            # 1. Controllo estensioni eseguibili o pericolose
            forbidden_exts = [".exe", ".scr", ".bat", ".vbs", ".jar", ".msi", ".com", ".zip", ".rar"]
            file_pericoloso = any(attachment.filename.lower().endswith(ext) for ext in forbidden_exts)
            
            # 2. Controllo URL dell'allegato tramite API
            is_dangerous_attachment = await check_url_safety(attachment.url)

            if file_pericoloso or is_dangerous_attachment:
                await message.delete()
                log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
                if log_channel:
                    motivo = "Estensione proibita" if file_pericoloso else "Rilevato da API di sicurezza"
                    embed = discord.Embed(title="🛡️ Allegato Rimosso", color=discord.Color.red())
                    embed.add_field(name="Autore", value=message.author.mention)
                    embed.add_field(name="File", value=f"`{attachment.filename}`")
                    embed.add_field(name="Motivo", value=motivo)
                    await log_channel.send(embed=embed)
                await message.channel.send(f"🚫 {message.author.mention}, non puoi caricare file sospetti o potenzialmente pericolosi.", delete_after=5)
                return

    if (is_forbidden or is_dangerous) and not message.author.guild_permissions.administrator:
        await message.delete()
        log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
        if log_channel:
            await log_channel.send(f"🛡️ **Sicurezza:** Link rimosso da {message.author.mention}")
        return

    
    await bot.process_commands(message)

async def check_url_safety(url):
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    api_url = f"https://proxycheck.io/v2/{domain}?key={PROXY_KEY}&risk=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                data = await response.json()
                return data.get("risk", 0) > 60 or data.get("proxy") == "yes"
    except:
        return False


# --- EVENTO PER GHOST PING ---
@bot.event
async def on_message_delete(message):
    """Rileva quando qualcuno tagga un utente e cancella subito il messaggio"""
    if message.author.bot:
        return
    
   
    if message.mentions:
        log_channel = discord.utils.get(message.guild.text_channels, name="logs-bot")
        if log_channel:
            target = message.mentions[0].mention
            embed = discord.Embed(
                title="🕵️ IDS: Ghost Ping Rilevato",
                description=f"L'utente {message.author.mention} ha rimosso un tag per {target}.",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Contenuto rimosso", value=f"```{message.content}```")
            embed.set_footer(text=f"Ora: {datetime.now().strftime('%H:%M:%S')}")
            await log_channel.send(embed=embed)



# Avvio del Bot
bot.run(DISCORD_TOKEN)
