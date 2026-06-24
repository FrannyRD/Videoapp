"""
Cliente para buscar y descargar videos de Pexels.
Requiere PEXELS_API_KEY (gratis en https://www.pexels.com/api/)
"""
import os
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def search_video(query: str, orientation: str = "portrait", min_duration: int = 3):
    """
    Busca un video en Pexels para una palabra clave.
    Devuelve la URL del archivo de video de mejor calidad disponible (HD, no 4K, para no pesar tanto).
    """
    if not PEXELS_API_KEY:
        raise RuntimeError("Falta PEXELS_API_KEY en las variables de entorno")

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": 5,
        "size": "medium",
    }

    resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    videos = data.get("videos", [])
    if not videos:
        return None

    # Elegimos el primer video que cumpla con duración mínima
    for video in videos:
        if video.get("duration", 0) >= min_duration:
            files = video.get("video_files", [])
            if not files:
                continue
            # Filtramos solo archivos mp4 con ancho conocido
            files = [f for f in files if f.get("file_type") == "video/mp4" and f.get("width")]
            if not files:
                continue
            # Elegimos el archivo MÁS LIVIANO posible que aún se vea bien (ancho >= 640px),
            # para no agotar la memoria en servidores con poco RAM (ej. plan gratis de Render).
            candidates = [f for f in files if f["width"] >= 640]
            pool = candidates if candidates else files
            chosen = min(pool, key=lambda f: f["width"])
            return chosen["link"]
    return None


def download_video(url: str, output_path: str):
    """Descarga un video desde una URL a una ruta local."""
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


def fetch_clip_for_keyword(keyword: str, output_path: str, min_duration: int = 3):
    """Busca y descarga un clip para una palabra clave. Devuelve True/False según éxito."""
    url = search_video(keyword, min_duration=min_duration)
    if not url:
        return False
    download_video(url, output_path)
    return True
