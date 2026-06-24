"""
Pistas de música de fondo gratis y de dominio público (sin derechos de autor),
para que la monetización en Facebook/YouTube no tenga problemas de copyright.
Se descargan una sola vez y se guardan en caché local.
"""
import os
import requests

MUSIC_DIR = "assets/music"
os.makedirs(MUSIC_DIR, exist_ok=True)

# Pistas de FreePD.com (licencia PD0 - dominio público, uso libre sin atribución)
MUSIC_TRACKS = {
    "mystery": "https://freepd.com/music/Mysterioso%20March.mp3",
    "suspense": "https://freepd.com/music/Eerie.mp3",
    "epic": "https://freepd.com/music/Epic%20Adventure.mp3",
    "none": None,
}


def get_music_path(key: str) -> str:
    """
    Devuelve la ruta local de la pista de música, descargándola si es la primera vez.
    Si key es "none", no existe, o la descarga falla, devuelve None
    (el video se genera igual, solo que sin música de fondo).
    """
    url = MUSIC_TRACKS.get(key)
    if not url:
        return None

    local_path = os.path.join(MUSIC_DIR, f"{key}.mp3")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path

    try:
        resp = requests.get(url, stream=True, timeout=20)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        if os.path.getsize(local_path) == 0:
            raise RuntimeError("Archivo de música vacío")
        return local_path
    except Exception as e:
        print(f"[music_client] No se pudo descargar la música '{key}': {e}. Se continúa sin música.", flush=True)
        if os.path.exists(local_path):
            os.remove(local_path)
        return None
