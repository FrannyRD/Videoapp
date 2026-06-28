"""Estado persistente de checklist de videos listos."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from copy import deepcopy

from content_library import CONTENT_LIBRARY

DATA_DIR = "data"
STATE_PATH = os.path.join(DATA_DIR, "video_status.json")
os.makedirs(DATA_DIR, exist_ok=True)
_lock = threading.Lock()


def _load_state() -> dict:
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


def _save_state(data: dict) -> None:
    tmp_path = STATE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, STATE_PATH)


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
    with _lock:
        state = _load_state()
        current = state.setdefault("videos", {}).setdefault(video_id, {})
        current["ready"] = bool(ready)
        current["ready_at"] = datetime.now(timezone.utc).isoformat() if ready else None
        _save_state(state)
    return {"ok": True, "video_id": video_id, "ready": bool(ready)}


def reset_page(page_id: str) -> dict:
    prefix = f"{page_id}_"
    with _lock:
        state = _load_state()
        videos = state.setdefault("videos", {})
        for vid in list(videos.keys()):
            if vid.startswith(prefix):
                videos[vid]["ready"] = False
                videos[vid]["ready_at"] = None
        _save_state(state)
    return {"ok": True, "page_id": page_id}
