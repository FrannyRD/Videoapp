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


def generate_video(scenes: list, music_key: str = "mystery", voice: str = None,
                    job_id: str = None, on_progress=None) -> str:
    """
    scenes: lista de dicts [{"text": "...", "keyword": "..."}, ...]
    music_key: "mystery" | "suspense" | "epic" | "none"
    on_progress: función opcional callback(text, percent) para reportar avance en vivo.
    Devuelve la ruta del .mp4 final.
    """
    job_id = job_id or str(uuid.uuid4())[:8]
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    def report(text, percent):
        print(f"[job {job_id}] {text} ({percent}%)", flush=True)
        if on_progress:
            on_progress(text, percent)

    try:
        scene_clip_paths = []
        scene_voice_paths = []
        n_scenes = len(scenes)
        # Repartimos el 0-80% entre las escenas, dejamos 80-100% para el ensamblaje final
        pct_per_scene = 80 / max(n_scenes, 1)

        for i, scene in enumerate(scenes):
            text = scene["text"]
            keyword = scene["keyword"]
            base_pct = int(i * pct_per_scene)
            report(f"Escena {i+1}/{n_scenes}: generando voz...", base_pct)

            # 1. Generar voz primero (así sabemos cuánto debe durar el clip)
            voice_path = os.path.join(job_dir, f"voice_{i}.mp3")
            kwargs = {"voice": voice} if voice else {}
            generate_voice(text, voice_path, **kwargs)
            voice_duration = vb.get_duration(voice_path)
            scene_duration = voice_duration + 0.4  # pequeño margen para que no se corte abrupto

            # Le agregamos el tiempo de transición como EXTRA, para que el fundido
            # "consuma" ese extra en vez de robarle tiempo a la parte que coincide con la voz.
            clip_duration = scene_duration + TRANSITION_SECONDS
            report(f"Escena {i+1}/{n_scenes}: buscando video ('{keyword}')...", int(base_pct + pct_per_scene * 0.3))

            # 2. Buscar y descargar el clip de video para esa escena
            raw_clip_path = os.path.join(job_dir, f"raw_{i}.mp4")
            found = fetch_clip_for_keyword(keyword, raw_clip_path, min_duration=int(clip_duration) + 1)
            if not found:
                raise RuntimeError(
                    f"No se encontró ningún video en Pexels para la palabra clave: '{keyword}'. "
                    f"Prueba con otra palabra clave más genérica."
                )
            report(f"Escena {i+1}/{n_scenes}: normalizando video...", int(base_pct + pct_per_scene * 0.6))

            # 3. Normalizar el clip (recortar a 1080x1920, duración exacta, texto incrustado)
            scene_path = os.path.join(job_dir, f"scene_{i}.mp4")
            vb.normalize_clip(raw_clip_path, scene_path, duration=clip_duration, text=text)
            os.remove(raw_clip_path)  # liberar espacio/memoria, ya no se necesita

            scene_clip_paths.append(scene_path)
            scene_voice_paths.append(voice_path)

        # 4. Concatenar los clips CON transición (fundido) entre cada escena
        report("Aplicando transiciones entre escenas...", 82)
        video_silent = os.path.join(job_dir, "video_silent.mp4")
        if n_scenes > 1:
            vb.concat_clips_with_transitions(scene_clip_paths, video_silent, transition=TRANSITION_SECONDS)
        else:
            vb.concat_clips(scene_clip_paths, video_silent)

        # 5. Concatenar todas las voces en un solo audio
        report("Combinando audio...", 88)
        voice_full = os.path.join(job_dir, "voice_full.m4a")
        vb.concat_audio(scene_voice_paths, voice_full)

        # 6. Música de fondo (best-effort: si falla la descarga, se sigue sin música)
        report("Preparando música de fondo...", 92)
        music_path = get_music_path(music_key) if music_key else None

        # 7. Mezclar video + voz + música de fondo (todavía en resolución de trabajo, baja memoria)
        report("Generando archivo final...", 96)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        merged_path = os.path.join(job_dir, "merged_lowres.mp4")
        video_duration = vb.get_duration(video_silent)
        vb.merge_video_audio_music(video_silent, voice_full, music_path, merged_path,
                                    music_volume=0.15, target_duration=video_duration)

        # 8. Único paso de "upscale" a la resolución final de entrega (liviano, un solo stream)
        report("Ajustando a resolución final...", 98)
        final_path = os.path.join(OUTPUT_DIR, f"video_{job_id}.mp4")
        vb.upscale_to_final(merged_path, final_path)

        report("¡Video listo!", 100)
        return final_path

    finally:
        # Limpieza de archivos temporales del job (no del output final)
        shutil.rmtree(job_dir, ignore_errors=True)
