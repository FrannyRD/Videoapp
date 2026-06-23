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


async def _generate(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_voice(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
    """
    Genera un archivo de audio .mp3 con la voz en off a partir del texto.
    Esta función es sincrónica por fuera, pero corre la tarea async internamente.
    """
    asyncio.run(_generate(text, output_path, voice, rate))
    return output_path
