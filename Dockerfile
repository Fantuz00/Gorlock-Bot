FROM python:3.10-bullseye

# Installazione librerie di sistema
RUN apt-get update && apt-get install -y ffmpeg libopus0 libopus-dev && rm -rf /var/lib/apt/lists/*

# Creazione del ponte per Opus
RUN ln -s /usr/lib/x86_64-linux-gnu/libopus.so.0 /usr/local/lib/libopus.so

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]