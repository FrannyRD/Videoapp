"""Estado persistente de checklist de videos listos.

Este módulo mantiene la compatibilidad con el guardado local en JSON, pero si
existen las variables de entorno de Supabase usa Supabase como almacenamiento
principal para que los checks no se pierdan cuando Render se duerme/reinicia.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from copy import deepcopy
from typing import Any

import requests

from content_library import CONTENT_LIBRARY

DATA_DIR = "data"
STATE_PATH = os.path.join(DATA_DIR, "video_status.json")
os.makedirs(DATA_DIR, exist_ok=True)
_lock = threading.Lock()

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or ""
SUPABASE_TABLE = os.environ.get("SUPABASE_VIDEO_STATUS_TABLE", "video_status")
SUPABASE_TIMEOUT = float(os.environ.get("SUPABASE_TIMEOUT_SECONDS", "12"))

_VIDEO_PAGE_INDEX = {
    video["id"]: page["id"]
    for page in CONTENT_LIBRARY.get("pages", [])
    for video in page.get("videos", [])
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _page_id_for_video(video_id: str) -> str:
    """Devuelve el page_id de un video sin depender de cortar por guiones bajos."""
    if video_id in _VIDEO_PAGE_INDEX:
        return _VIDEO_PAGE_INDEX[video_id]
    # Fallback defensivo para videos agregados manualmente en el futuro.
    for page in CONTENT_LIBRARY.get("pages", []):
        page_id = page.get("id", "")
        if video_id.startswith(f"{page_id}_"):
            return page_id
    return "manual"


def _supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _supabase_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def _supabase_endpoint() -> str:
    return f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"


def _supabase_request(method: str, *, params: dict[str, str] | None = None, json_body: Any | None = None, prefer: str | None = None) -> requests.Response:
    headers = _supabase_headers({"Prefer": prefer} if prefer else None)
    response = requests.request(
        method,
        _supabase_endpoint(),
        headers=headers,
        params=params,
        json=json_body,
        timeout=SUPABASE_TIMEOUT,
    )
    response.raise_for_status()
    return response


def _load_state_local() -> dict:
    if not os.path.exists(STATE_PATH):
        return {"videos": {}}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"videos": {}}
        data.setdefault("videos", {})
        return data
    except Exception:
        return {"videos": {}}


def _save_state_local(data: dict) -> None:
    tmp_path = STATE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, STATE_PATH)


def _load_state_supabase() -> dict:
    response = _supabase_request(
        "GET",
        params={"select": "video_id,ready,ready_at,page_id,updated_at"},
    )
    rows = response.json() if response.content else []
    videos = {}
    for row in rows:
        video_id = row.get("video_id")
        if not video_id:
            continue
        videos[video_id] = {
            "ready": bool(row.get("ready")),
            "ready_at": row.get("ready_at"),
            "page_id": row.get("page_id"),
            "updated_at": row.get("updated_at"),
        }
    return {"videos": videos}


def _load_state() -> dict:
    """Lee Supabase si está configurado; si no, usa JSON local.

    El fallback local evita romper la app si todavía no configuraste Supabase
    o si hay un error temporal de conexión.
    """
    if _supabase_enabled():
        try:
            return _load_state_supabase()
        except Exception as exc:
            print(f"[content_state] AVISO: no se pudo leer Supabase. Usando JSON local. Detalle: {exc}")
    return _load_state_local()


def _upsert_video_supabase(video_id: str, ready: bool) -> None:
    now = _utc_now()
    payload = {
        "video_id": video_id,
        "page_id": _page_id_for_video(video_id),
        "ready": bool(ready),
        "ready_at": now if ready else None,
        "updated_at": now,
    }
    _supabase_request(
        "POST",
        params={"on_conflict": "video_id"},
        json_body=payload,
        prefer="resolution=merge-duplicates,return=minimal",
    )


def _set_video_ready_local(video_id: str, ready: bool) -> None:
    state = _load_state_local()
    current = state.setdefault("videos", {}).setdefault(video_id, {})
    current["ready"] = bool(ready)
    current["ready_at"] = _utc_now() if ready else None
    current["page_id"] = _page_id_for_video(video_id)
    current["updated_at"] = _utc_now()
    _save_state_local(state)


def get_library_with_status() -> dict:
    with _lock:
        state = _load_state()
    library = deepcopy(CONTENT_LIBRARY)
    statuses = state.get("videos", {})
    for page in library["pages"]:
        ready_count = 0
        next_video = None
        for video in page["videos"]:
            st = statuses.get(video["id"], {})
            video["ready"] = bool(st.get("ready"))
            video["ready_at"] = st.get("ready_at")
            if video["ready"]:
                ready_count += 1
            elif next_video is None:
                next_video = video["id"]
        page["ready_count"] = ready_count
        page["total_count"] = len(page["videos"])
        page["next_video_id"] = next_video
    return library


def set_video_ready(video_id: str, ready: bool) -> dict:
    storage = "local"
    warning = None
    with _lock:
        if _supabase_enabled():
            try:
                _upsert_video_supabase(video_id, ready)
                storage = "supabase"
            except Exception as exc:
                warning = f"No se pudo guardar en Supabase; se guardó localmente. Detalle: {exc}"
                print(f"[content_state] AVISO: {warning}")
                _set_video_ready_local(video_id, ready)
                storage = "local_fallback"
        else:
            _set_video_ready_local(video_id, ready)
    response = {"ok": True, "video_id": video_id, "ready": bool(ready), "storage": storage}
    if warning:
        response["warning"] = warning
    return response


def _reset_page_supabase(page_id: str) -> None:
    now = _utc_now()
    payload = {"ready": False, "ready_at": None, "updated_at": now}
    _supabase_request(
        "PATCH",
        params={"page_id": f"eq.{page_id}"},
        json_body=payload,
        prefer="return=minimal",
    )


def _reset_page_local(page_id: str) -> None:
    prefix = f"{page_id}_"
    state = _load_state_local()
    videos = state.setdefault("videos", {})
    for vid in list(videos.keys()):
        if vid.startswith(prefix) or videos[vid].get("page_id") == page_id:
            videos[vid]["ready"] = False
            videos[vid]["ready_at"] = None
            videos[vid]["updated_at"] = _utc_now()
    _save_state_local(state)


def reset_page(page_id: str) -> dict:
    storage = "local"
    warning = None
    with _lock:
        if _supabase_enabled():
            try:
                _reset_page_supabase(page_id)
                storage = "supabase"
            except Exception as exc:
                warning = f"No se pudo resetear en Supabase; se reseteó localmente. Detalle: {exc}"
                print(f"[content_state] AVISO: {warning}")
                _reset_page_local(page_id)
                storage = "local_fallback"
        else:
            _reset_page_local(page_id)
    response = {"ok": True, "page_id": page_id, "storage": storage}
    if warning:
        response["warning"] = warning
    return response
