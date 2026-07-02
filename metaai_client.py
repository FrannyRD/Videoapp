"""Cliente opcional para generar videos con Meta AI.

Esta integración queda aislada del flujo principal de la app. Solo se usa desde
la subpágina /meta-ai y requiere cookies de una sesión de Meta AI configuradas
como variables de entorno en Render.
"""
from __future__ import annotations

import os
from typing import Any


def _clean(value: str | None) -> str:
    return (value or "").strip()


def metaai_env_status() -> dict[str, Any]:
    """Devuelve qué variables están configuradas sin exponer sus valores."""
    datr = _clean(os.environ.get("META_AI_DATR"))
    ecto = _clean(os.environ.get("META_AI_ECTO_1_SESS"))
    abra = _clean(os.environ.get("META_AI_ABRA_SESS"))
    token = _clean(os.environ.get("META_AI_ACCESS_TOKEN"))
    missing = []
    if not datr:
        missing.append("META_AI_DATR")
    if not ecto:
        missing.append("META_AI_ECTO_1_SESS")
    return {
        "configured": bool(datr and ecto),
        "missing": missing,
        "has_datr": bool(datr),
        "has_ecto_1_sess": bool(ecto),
        "has_abra_sess": bool(abra),
        "has_access_token": bool(token),
    }


def _cookies_from_env() -> dict[str, str]:
    status = metaai_env_status()
    if not status["configured"]:
        missing = ", ".join(status["missing"])
        raise RuntimeError(f"Faltan variables de Meta AI en Render: {missing}")

    cookies = {
        "datr": _clean(os.environ.get("META_AI_DATR")),
        "ecto_1_sess": _clean(os.environ.get("META_AI_ECTO_1_SESS")),
    }
    abra = _clean(os.environ.get("META_AI_ABRA_SESS"))
    if abra:
        cookies["abra_sess"] = abra
    return cookies


def generate_metaai_video(prompt: str, *, auto_poll: bool = True, max_poll_attempts: int = 12, poll_wait_seconds: int = 4) -> dict[str, Any]:
    """Genera videos con el SDK no oficial de Meta AI.

    Importa el SDK solo cuando se usa esta función, para que la app principal
    no falle si esta sección opcional no está configurada.
    """
    prompt = _clean(prompt)
    if len(prompt) < 8:
        raise ValueError("El prompt debe tener al menos 8 caracteres.")

    try:
        from metaai_api import MetaAI
    except Exception as exc:  # pragma: no cover - depende del entorno de Render
        raise RuntimeError(
            "No se pudo cargar el SDK de Meta AI. Revisa que requirements.txt se haya instalado completo. "
            f"Detalle: {exc}"
        ) from exc

    ai = MetaAI(cookies=_cookies_from_env())
    result = ai.generate_video_new(
        prompt,
        auto_poll=auto_poll,
        max_poll_attempts=max_poll_attempts,
        poll_wait_seconds=poll_wait_seconds,
    )

    # Limpiar la respuesta para no enviar payloads enormes al navegador.
    video_urls = result.get("video_urls") or []
    media_ids = result.get("media_ids") or []
    conversation_id = result.get("conversation_id")
    return {
        "success": bool(result.get("success")),
        "status": result.get("status") or ("READY" if video_urls else "PROCESSING" if conversation_id else "FAILED"),
        "prompt": prompt,
        "conversation_id": conversation_id,
        "media_ids": media_ids,
        "video_urls": video_urls,
        "meta_prompt_url": f"https://www.meta.ai/prompt/{conversation_id}" if conversation_id else None,
        "meta_create_urls": [f"https://www.meta.ai/create/{mid}" for mid in media_ids],
        "error": result.get("error"),
        "processing": bool(result.get("processing")),
    }
