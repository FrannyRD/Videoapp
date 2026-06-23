"""
Pipeline principal: toma una lista de escenas (texto + palabra clave) y genera
el video final listo para subir, combinando Pexels + TTS + FFmpeg.
"""
import os
import uuid
import shutil

from pexels_client import fetch_clip_for_keyword
from tts_client import generate_voice
import video_builder as vb

TEMP_DIR = "temp"
OUTPUT_DIR = "output"


def generate_video(scenes: list, music_path: str = None, voice: str = None, job_id: str = None) -> str:
    """
    scenes: lista de dicts [{"text": "...", "keyword": "..."}, ...]
    Devuelve la ruta del .mp4 final.
    """
    job_id = job_id or str(uuid.uuid4())[:8]
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    try:
        scene_clip_paths = []
        scene_voice_paths = []

        for i, scene in enumerate(scenes):
            text = scene["text"]
            keyword = scene["keyword"]
            print(f"[job {job_id}] Escena {i}: generando voz...", flush=True)

            # 1. Generar voz primero (así sabemos cuánto debe durar el clip)
            voice_path = os.path.join(job_dir, f"voice_{i}.mp3")
            kwargs = {"voice": voice} if voice else {}
            generate_voice(text, voice_path, **kwargs)
            duration = vb.get_duration(voice_path)
            # Pequeño margen extra para que no se corte abruptamente
            duration = duration + 0.4
            print(f"[job {job_id}] Escena {i}: voz lista ({duration:.1f}s). Buscando video para '{keyword}'...", flush=True)

            # 2. Buscar y descargar el clip de video para esa escena
            raw_clip_path = os.path.join(job_dir, f"raw_{i}.mp4")
            found = fetch_clip_for_keyword(keyword, raw_clip_path, min_duration=int(duration) + 1)
            if not found:
                raise RuntimeError(
                    f"No se encontró ningún video en Pexels para la palabra clave: '{keyword}'. "
                    f"Prueba con otra palabra clave más genérica."
                )
            print(f"[job {job_id}] Escena {i}: video descargado. Normalizando...", flush=True)

            # 3. Normalizar el clip (recortar a 1080x1920, duración exacta, texto incrustado)
            scene_path = os.path.join(job_dir, f"scene_{i}.mp4")
            vb.normalize_clip(raw_clip_path, scene_path, duration=duration, text=text)
            print(f"[job {job_id}] Escena {i}: lista.", flush=True)

            scene_clip_paths.append(scene_path)
            scene_voice_paths.append(voice_path)

        print(f"[job {job_id}] Concatenando clips...", flush=True)
        # 4. Concatenar todos los clips de video (silenciosos)
        video_silent = os.path.join(job_dir, "video_silent.mp4")
        vb.concat_clips(scene_clip_paths, video_silent)

        print(f"[job {job_id}] Concatenando audio...", flush=True)
        # 5. Concatenar todas las voces en un solo audio
        voice_full = os.path.join(job_dir, "voice_full.m4a")
        vb.concat_audio(scene_voice_paths, voice_full)

        print(f"[job {job_id}] Mezclando video final...", flush=True)
        # 6. Mezclar video + voz + música de fondo
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final_path = os.path.join(OUTPUT_DIR, f"video_{job_id}.mp4")
        vb.merge_video_audio_music(video_silent, voice_full, music_path, final_path, music_volume=0.15)

        print(f"[job {job_id}] ¡Listo! {final_path}", flush=True)
        return final_path

    finally:
        # Limpieza de archivos temporales del job (no del output final)
        shutil.rmtree(job_dir, ignore_errors=True)
