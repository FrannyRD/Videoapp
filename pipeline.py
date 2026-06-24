"""
Pipeline principal: toma una lista de escenas (texto + palabra clave) y genera
el video final listo para subir, combinando Pexels + TTS + FFmpeg.
"""
import os
import uuid
import shutil

from pexels_client import fetch_clip_for_keyword
from tts_client import generate_voice
from music_client import get_music_path
import video_builder as vb

TEMP_DIR = "temp"
OUTPUT_DIR = "output"
TRANSITION_SECONDS = 0.5  # duración del fundido entre escenas


def generate_video(scenes: list, music_key: str = "mystery", voice: str = None, job_id: str = None) -> str:
    """
    scenes: lista de dicts [{"text": "...", "keyword": "..."}, ...]
    music_key: "mystery" | "suspense" | "epic" | "none"
    Devuelve la ruta del .mp4 final.
    """
    job_id = job_id or str(uuid.uuid4())[:8]
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    try:
        scene_clip_paths = []
        scene_voice_paths = []
        n_scenes = len(scenes)

        for i, scene in enumerate(scenes):
            text = scene["text"]
            keyword = scene["keyword"]
            print(f"[job {job_id}] Escena {i}: generando voz...", flush=True)

            # 1. Generar voz primero (así sabemos cuánto debe durar el clip)
            voice_path = os.path.join(job_dir, f"voice_{i}.mp3")
            kwargs = {"voice": voice} if voice else {}
            generate_voice(text, voice_path, **kwargs)
            voice_duration = vb.get_duration(voice_path)
            scene_duration = voice_duration + 0.4  # pequeño margen para que no se corte abrupto

            # Le agregamos el tiempo de transición como EXTRA, para que el fundido
            # "consuma" ese extra en vez de robarle tiempo a la parte que coincide con la voz.
            clip_duration = scene_duration + TRANSITION_SECONDS
            print(f"[job {job_id}] Escena {i}: voz lista ({voice_duration:.1f}s). Buscando video para '{keyword}'...", flush=True)

            # 2. Buscar y descargar el clip de video para esa escena
            raw_clip_path = os.path.join(job_dir, f"raw_{i}.mp4")
            found = fetch_clip_for_keyword(keyword, raw_clip_path, min_duration=int(clip_duration) + 1)
            if not found:
                raise RuntimeError(
                    f"No se encontró ningún video en Pexels para la palabra clave: '{keyword}'. "
                    f"Prueba con otra palabra clave más genérica."
                )
            print(f"[job {job_id}] Escena {i}: video descargado. Normalizando...", flush=True)

            # 3. Normalizar el clip (recortar a 1080x1920, duración exacta, texto incrustado)
            scene_path = os.path.join(job_dir, f"scene_{i}.mp4")
            vb.normalize_clip(raw_clip_path, scene_path, duration=clip_duration, text=text)
            os.remove(raw_clip_path)  # liberar espacio/memoria, ya no se necesita
            print(f"[job {job_id}] Escena {i}: lista.", flush=True)

            scene_clip_paths.append(scene_path)
            scene_voice_paths.append(voice_path)

        # 4. Concatenar los clips CON transición (fundido) entre cada escena
        print(f"[job {job_id}] Aplicando transiciones...", flush=True)
        video_silent = os.path.join(job_dir, "video_silent.mp4")
        if n_scenes > 1:
            vb.concat_clips_with_transitions(scene_clip_paths, video_silent, transition=TRANSITION_SECONDS)
        else:
            vb.concat_clips(scene_clip_paths, video_silent)

        # 5. Concatenar todas las voces en un solo audio
        print(f"[job {job_id}] Concatenando audio...", flush=True)
        voice_full = os.path.join(job_dir, "voice_full.m4a")
        vb.concat_audio(scene_voice_paths, voice_full)

        # 6. Música de fondo (best-effort: si falla la descarga, se sigue sin música)
        print(f"[job {job_id}] Preparando música ({music_key})...", flush=True)
        music_path = get_music_path(music_key) if music_key else None

        # 7. Mezclar video + voz + música de fondo
        print(f"[job {job_id}] Mezclando video final...", flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final_path = os.path.join(OUTPUT_DIR, f"video_{job_id}.mp4")
        video_duration = vb.get_duration(video_silent)
        vb.merge_video_audio_music(video_silent, voice_full, music_path, final_path,
                                    music_volume=0.15, target_duration=video_duration)

        print(f"[job {job_id}] ¡Listo! {final_path}", flush=True)
        return final_path

    finally:
        # Limpieza de archivos temporales del job (no del output final)
        shutil.rmtree(job_dir, ignore_errors=True)
