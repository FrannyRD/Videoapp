"""
Generación de voz en off usando edge-tts (gratis, voces de Microsoft Edge).
"""
import asyncio
import os
import edge_tts

# Voces en español disponibles (puedes cambiar según prefieras)
VOICE_ES_MEXICO = "es-MX-JorgeNeural"
VOICE_ES_ESPANA_MUJER = "es-ES-ElviraNeural"
VOICE_ES_ESPANA_HOMBRE = "es-ES-AlvaroNeural"

DEFAULT_VOICE = VOICE_ES_MEXICO
TTS_TIMEOUT_SECONDS = int(os.environ.get("TTS_TIMEOUT_SECONDS", "180"))


async def _generate(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await asyncio.wait_for(communicate.save(output_path), timeout=TTS_TIMEOUT_SECONDS)


async def _generate_with_words(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    """
    Genera la voz Y captura el momento exacto (en segundos) en que se dice cada palabra,
    usando los eventos "WordBoundary" que transmite Edge-TTS. Esto es lo que permite
    sincronizar los subtítulos con precisión, en vez de solo repartir el tiempo a ojo.

    Si por alguna razón Edge-TTS no entrega esos eventos (cambios en la librería, voz
    no soportada, etc.), no truena: cae a un reparto uniforme del tiempo total, y deja
    un registro (log) de qué tipos de evento sí llegaron, para poder diagnosticarlo.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    seen_types = set()
    audio_bytes_written = 0

    async def _stream():
        nonlocal audio_bytes_written
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                ctype = chunk.get("type")
                seen_types.add(str(ctype))
                if ctype == "audio":
                    data = chunk.get("data", b"")
                    f.write(data)
                    audio_bytes_written += len(data)
                elif ctype == "WordBoundary":
                    offset = chunk.get("offset")
                    duration = chunk.get("duration")
                    word_text = chunk.get("text", "")
                    if offset is not None and duration is not None:
                        start = offset / 10_000_000
                        dur = duration / 10_000_000
                        words.append({"text": word_text, "start": start, "end": start + dur})

    await asyncio.wait_for(_stream(), timeout=TTS_TIMEOUT_SECONDS)
    print(f"[tts_client] Tipos de evento recibidos de Edge-TTS: {seen_types}. "
          f"Palabras capturadas: {len(words)}. Bytes de audio: {audio_bytes_written}.", flush=True)
    return words


def generate_voice(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    """
    Genera un archivo de audio .mp3 con la voz en off a partir del texto.
    Esta función es sincrónica por fuera, pero corre la tarea async internamente.
    Si la conexión con el servicio de voz se cuelga, falla a los 30s en vez de quedarse colgada.
    """
    try:
        asyncio.run(_generate(text, output_path, voice, rate))
    except asyncio.TimeoutError:
        raise RuntimeError(
            f"El servicio de voz (Edge-TTS) no respondió a tiempo ({TTS_TIMEOUT_SECONDS}s). "
            "Puede ser un problema temporal del servicio — intenta generar el video de nuevo."
        )
    return output_path


def generate_voice_with_words(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> list:
    """
    Igual que generate_voice, pero además devuelve una lista de palabras con su tiempo
    exacto de inicio/fin (en segundos), para poder sincronizar subtítulos con la voz real.
    Devuelve: [{"text": "Hola", "start": 0.0, "end": 0.3}, ...]

    Si Edge-TTS no entrega los tiempos exactos por palabra, se cae a un reparto uniforme
    del tiempo total entre las palabras (sincronización aproximada, no exacta, pero el
    video se sigue generando en vez de fallar por completo).
    """
    try:
        words = asyncio.run(_generate_with_words(text, output_path, voice, rate))
    except asyncio.TimeoutError:
        raise RuntimeError(
            f"El servicio de voz (Edge-TTS) no respondió a tiempo ({TTS_TIMEOUT_SECONDS}s). "
            "Puede ser un problema temporal del servicio — intenta generar el video de nuevo."
        )

    if words:
        return words

    # --- Fallback: reparto uniforme usando la duración real del audio ya generado ---
    print("[tts_client] AVISO: no llegaron word boundaries de Edge-TTS. "
          "Usando reparto uniforme de tiempo (sincronización aproximada).", flush=True)

    import os as _os
    if not _os.path.exists(output_path) or _os.path.getsize(output_path) == 0:
        raise RuntimeError(
            "Edge-TTS no generó audio válido para esta voz/texto. Intenta de nuevo "
            "o prueba con otra voz."
        )

    import subprocess
    import json as _json
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", output_path],
        capture_output=True, text=True, check=True,
    )
    total_duration = float(_json.loads(probe.stdout)["format"]["duration"])

    raw_words = text.split()
    n = len(raw_words)
    if n == 0:
        return []
    step = total_duration / n
    return [
        {"text": w, "start": i * step, "end": (i + 1) * step - 0.02}
        for i, w in enumerate(raw_words)
    ]
