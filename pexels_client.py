"""
Cliente para buscar y descargar videos de Pexels.
Incluye historial local para evitar repetir clips dentro de una misma página/nicho.
"""
from __future__ import annotations

import json
import os
import random
import threading
import time
from typing import Optional

import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
DATA_DIR = "data"
USAGE_PATH = os.path.join(DATA_DIR, "used_pexels_clips.json")
os.makedirs(DATA_DIR, exist_ok=True)
_lock = threading.Lock()


def _load_usage() -> dict:
    if not os.path.exists(USAGE_PATH):
        return {"global": [], "scopes": {}}
    try:
        with open(USAGE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("global", [])
        data.setdefault("scopes", {})
        return data
    except Exception:
        return {"global": [], "scopes": {}}


def _save_usage(data: dict) -> None:
    tmp = USAGE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, USAGE_PATH)


def _mark_used(video_id: str, query: str, usage_scope: str | None) -> None:
    if not video_id:
        return
    scope = usage_scope or "default"
    with _lock:
        data = _load_usage()
        now = int(time.time())
        record = {"id": str(video_id), "query": query, "scope": scope, "used_at": now}
        if not any(x.get("id") == str(video_id) for x in data["global"]):
            data["global"].append(record)
        data["scopes"].setdefault(scope, [])
        if not any(x.get("id") == str(video_id) for x in data["scopes"][scope]):
            data["scopes"][scope].append(record)
        # Mantener el archivo liviano en hosting gratis.
        data["global"] = data["global"][-2000:]
        for key in list(data["scopes"].keys()):
            data["scopes"][key] = data["scopes"][key][-1000:]
        _save_usage(data)


def _used_ids(usage_scope: str | None) -> set[str]:
    scope = usage_scope or "default"
    with _lock:
        data = _load_usage()
    ids = {str(x.get("id")) for x in data.get("scopes", {}).get(scope, []) if x.get("id")}
    return ids


def search_video(query: str, orientation: str = "portrait", min_duration: int = 3,
                 usage_scope: str | None = None, blocked_ids: Optional[set[str]] = None):
    """
    Busca un video en Pexels para una palabra clave.
    Devuelve dict {url, id} del archivo elegido, intentando no repetir clips ya usados.
    """
    if not PEXELS_API_KEY:
        raise RuntimeError("Falta PEXELS_API_KEY en las variables de entorno")

    blocked = set(blocked_ids or set()) | _used_ids(usage_scope)
    headers = {"Authorization": PEXELS_API_KEY}

    # Buscamos en 2 páginas para tener margen de no repetir. No se usan todos los resultados a la vez.
    all_videos = []
    for page in (1, 2):
        params = {
            "query": query,
            "orientation": orientation,
            "per_page": 12,
            "size": "medium",
            "page": page,
        }
        resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        all_videos.extend(data.get("videos", []))
        if len(all_videos) >= 18:
            break

    if not all_videos:
        return None

    candidates = []
    fallback = []
    for video in all_videos:
        vid = str(video.get("id", ""))
        if video.get("duration", 0) < min_duration:
            continue
        files = video.get("video_files", [])
        files = [f for f in files if f.get("file_type") == "video/mp4" and f.get("width")]
        if not files:
            continue
        hd_candidates = [f for f in files if f["width"] >= 640]
        pool = hd_candidates if hd_candidates else files
        chosen_file = min(pool, key=lambda f: f["width"])
        record = {"id": vid, "url": chosen_file["link"]}
        fallback.append(record)
        if vid and vid not in blocked:
            candidates.append(record)

    pool = candidates if candidates else fallback
    if not pool:
        return None

    # Aleatoriedad ligera para que búsquedas iguales no siempre elijan el mismo primer clip.
    random.shuffle(pool)
    return pool[0]


def download_video(url: str, output_path: str):
    """Descarga un video desde una URL a una ruta local."""
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return output_path


def fetch_clip_for_keyword(keyword: str, output_path: str, min_duration: int = 3,
                           usage_scope: str | None = None, blocked_ids: Optional[set[str]] = None):
    """
    Busca y descarga un clip para una palabra clave. Devuelve True/False según éxito.
    Guarda el ID del clip usado para evitar repetirlo en próximos videos de esa página.
    """
    result = search_video(keyword, min_duration=min_duration, usage_scope=usage_scope, blocked_ids=blocked_ids)
    if not result:
        return False
    download_video(result["url"], output_path)
    _mark_used(result.get("id"), keyword, usage_scope)
    if blocked_ids is not None and result.get("id"):
        blocked_ids.add(str(result.get("id")))
    return True
