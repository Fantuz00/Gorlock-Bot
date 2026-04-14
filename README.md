# 👹 Gorlock il Distruttore

**Gorlock il Distruttore** è un bot Discord multifunzionale avanzato, progettato con un focus specifico sulla **sicurezza proattiva (IDS)** e l'**intrattenimento multimediale**. Sviluppato in Python utilizzando `discord.py`, integra sistemi di rilevamento delle minacce in tempo reale e un modulo musicale fluido.

---

## 🛡️ Funzionalità di Sicurezza (IDS - Intrusion Detection System)

Gorlock agisce come un guardiano vigile per il tuo server, monitorando costantemente le attività sospette:

*   **Analisi URL & Allegati**: Scansiona automaticamente ogni link e file inviato. Grazie all'integrazione con l'API di **ProxyCheck.io**, è in grado di bloccare domini malevoli, siti di phishing e server proxy/VPN pericolosi.
*   **Filtro Allegati**: Blocca file con estensioni potenzialmente dannose (es. `.exe`, `.bat`, `.vbs`) prima che possano essere scaricati dagli utenti.
*   **Anti-Spam Rapido**: Rileva gli utenti che inviano troppi messaggi in un intervallo di tempo ristretto (5 messaggi ogni 5 secondi), prevenendo l'intasamento della chat.
*   **Rilevamento Mass Mention**: Elimina istantaneamente i messaggi che tentano di taggare più di 5 utenti simultaneamente.
*   **Anti-Raid Mode**: Una modalità attivabile manualmente che espelle automaticamente i nuovi membri per proteggere il server durante un attacco coordinato.
*   **Monitoraggio Età Account**: Registra automaticamente nei log gli account creati da meno di 3 giorni che entrano nel server.
*   **Ghost Ping Detector**: Smaschera gli utenti che taggano qualcuno e cancellano immediatamente il messaggio per dare fastidio o attirare l'attenzione.
*   **Audit Logging**: Notifiche immediate nel canale dedicato (`logs-bot`) per eliminazione canali, modifiche ai permessi dei ruoli e ban.

---

## 🎵 Modulo Musica

Sistema musicale basato su `yt-dlp` e `FFmpeg` per un'esperienza audio stabile e di alta qualità:

*   **Ricerca Intelligente**: Riproduzione tramite ricerca testuale su YouTube.
*   **Gestione Coda**: Sistema di accodamento brani (`/queue`) con supporto per riproduzione continua.
*   **Controlli Completi**: Comandi per `/pause`, `/resume`, `/skip` e `/stop`.
*   **Streaming Ottimizzato**: Utilizza FFmpeg con opzioni di riconnessione automatica per evitare interruzioni durante lo streaming audio.

---

## 🛠️ Comandi Principali

| Comando | Descrizione |
| :--- | :--- |
| `/aiuto` | Visualizza il manuale completo dei comandi. |
| `/meteo [città]` | Fornisce dati meteo in tempo reale tramite OpenWeather API. |
| `/status` | Mostra la latenza (ping) e lo stato operativo dei sistemi. |
| `/play [titolo]` | Cerca e riproduce un brano nel canale vocale. |
| `/clear [n]` | Elimina un numero specificato di messaggi (Richiede permessi Staff). |
| `/pause` / `/resume` | Gestisce la riproduzione musicale corrente. |

---

## 🚀 Installazione e Deployment

Il bot è completamente containerizzato per facilitare il deployment su VPS o server locali.

### Requisiti
*   Docker e Docker Compose
*   Token Discord Bot (ottenibile dal Discord Developer Portal)
*   Chiave API OpenWeatherMap
*   Chiave API ProxyCheck.io

### Configurazione
Crea un file `.env` nella root del progetto con i seguenti parametri:
```env
DISCORD_TOKEN=il_tuo_token_qui
WEATHER_API_KEY=la_tua_chiave_meteo
PROXYCHECK_KEY=la_tua_chiave_proxycheck
```

### Avvio con Docker
Il `Dockerfile` incluso si occupa di installare tutte le dipendenze necessarie, inclusi `ffmpeg` e le librerie per l'audio Opus.

1. Posizionati nella cartella del progetto.
2. Costruisci l'immagine:
   ```bash
   docker build -t gorlock-bot .
   ```
3. Avvia il container:
   ```bash
   docker run -d --name gorlock-distruttore gorlock-bot
   ```

---

## 📂 Struttura del Progetto
*   `main.py`: Core del bot con logica IDS e comandi.
*   `Dockerfile`: Configurazione per l'ambiente Docker (Python 3.10 Bullseye).
*   `requirements.txt`: Elenco delle dipendenze Python (`discord.py`, `yt-dlp`, `aiohttp`, ecc.).
*   `logs_sospetti.txt`: File di registro locale per attività sospette.

---

## ⚖️ Disclaimer
*Gorlock il Distruttore è uno strumento di moderazione. L'autore non è responsabile per l'uso improprio del bot o per eventuali violazioni dei Termini di Servizio di Discord.*