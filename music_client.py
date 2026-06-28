"""
Pistas de música de fondo gratis/de dominio público. La app permite elegir música por página.
Si alguna descarga falla, el video se genera igual sin música para no romper el flujo.
"""
import os
import requests

MUSIC_DIR = "assets/music"
os.makedirs(MUSIC_DIR, exist_ok=True)

# FreePD.com (PD0 / dominio público). Varias categorías apuntan a pistas distintas o equivalentes.
MUSIC_TRACKS = {
    "mystery": "https://freepd.com/music/Mysterioso%20March.mp3",
    "suspense": "https://freepd.com/music/Eerie.mp3",
    "epic": "https://freepd.com/music/Epic%20Adventure.mp3",
    "true_crime": "https://freepd.com/music/Mysterioso%20March.mp3",
    "psychology": "https://freepd.com/music/Eerie.mp3",
    "wildlife": "https://freepd.com/music/Epic%20Adventure.mp3",
    "historical": "https://freepd.com/music/Mysterioso%20March.mp3",
    "biblical": "https://freepd.com/music/Epic%20Adventure.mp3",
    "enigma": "https://freepd.com/music/Mysterioso%20March.mp3",
    "none": None,
}

MUSIC_LABELS = {
    "mystery": "Misterio general",
    "suspense": "Suspenso suave",
    "epic": "Épica documental",
    "true_crime": "True crime / investigación",
    "psychology": "Psicología / tensión sutil",
    "wildlife": "Animal / naturaleza intensa",
    "historical": "Historia / archivo secreto",
    "biblical": "Bíblico / épico emocional",
    "enigma": "Enigma / misterio diario",
    "none": "Sin música",
}


def get_music_path(key: str) -> str | None:
    """
    Devuelve la ruta local de la pista de música, descargándola si es la primera vez.
    Si key es "none", no existe, o la descarga falla, devuelve None.
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
                if chunk:
                    f.write(chunk)
        if os.path.getsize(local_path) == 0:
            raise RuntimeError("Archivo de música vacío")
        return local_path
    except Exception as e:
        print(f"[music_client] No se pudo descargar la música '{key}': {e}. Se continúa sin música.", flush=True)
        if os.path.exists(local_path):
            os.remove(local_path)
        return None
