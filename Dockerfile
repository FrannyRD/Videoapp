FROM python:3.12-slim

# FFmpeg y fuentes necesarias para incrustar texto en los videos
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY metaai_api_vendor ./metaai_api_vendor
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp output

ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "--workers", "1", "app:app"]
