FROM python:3.9-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Tüm dosyaları kopyala (data dahil)
COPY . .

# Gerekli izinleri ayarla
RUN chmod +x startup/* && \
    mkdir -p /app/data && \
    touch /app/data/.gitkeep

# Bağımlılıkları yükle
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
