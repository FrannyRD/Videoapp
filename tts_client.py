"""
Generación de voz en off usando edge-tts (gratis, voces de Microsoft Edge).
"""
import asyncio
import edge_tts

# Voces en español disponibles (puedes cambiar según prefieras)
VOICE_ES_MEXICO = "es-MX-JorgeNeural"
VOICE_ES_ESPANA_MUJER = "es-ES-ElviraNeural"
VOICE_ES_ESPANA_HOMBRE = "es-ES-AlvaroNeural"

DEFAULT_VOICE = VOICE_ES_MEXICO
TTS_TIMEOUT_SECONDS = 30


async def _generate(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await asyncio.wait_for(communicate.save(output_path), timeout=TTS_TIMEOUT_SECONDS)


async def _generate_with_words(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    """
    Genera la voz Y captura el momento exacto (en segundos) en que se dice cada palabra,
    usando los eventos "WordBoundary" que transmite Edge-TTS. Esto es lo que permite
    sincronizar los subtítulos con precisión, en vez de solo repartir el tiempo a ojo.
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    words = []

    async def _stream():
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # offset y duration vienen en unidades de 100 nanosegundos
                    start = chunk["offset"] / 10_000_000
                    dur = chunk["duration"] / 10_000_000
                    words.append({"text": chunk["text"], "start": start, "end": start + dur})

    await asyncio.wait_for(_stream(), timeout=TTS_TIMEOUT_SECONDS)
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
            "El servicio de voz (Edge-TTS) no respondió a tiempo (30s). "
            "Puede ser un problema temporal del servicio — intenta generar el video de nuevo."
        )
    return output_path


def generate_voice_with_words(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> list:
    """
    Igual que generate_voice, pero además devuelve una lista de palabras con su tiempo
    exacto de inicio/fin (en segundos), para poder sincronizar subtítulos con la voz real.
    Devuelve: [{"text": "Hola", "start": 0.0, "end": 0.3}, ...]
    """
    try:
        words = asyncio.run(_generate_with_words(text, output_path, voice, rate))
    except asyncio.TimeoutError:
        raise RuntimeError(
            "El servicio de voz (Edge-TTS) no respondió a tiempo (30s). "
            "Puede ser un problema temporal del servicio — intenta generar el video de nuevo."
        )
    if not words:
        raise RuntimeError(
            "El servicio de voz no devolvió los tiempos de las palabras (word boundaries). "
            "Puede ser un cambio temporal en Edge-TTS — intenta de nuevo."
        )
    return words
