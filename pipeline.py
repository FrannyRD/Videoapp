"""
Pipeline principal: toma una lista de escenas (texto + palabra clave) y genera
el video final listo para subir, combinando Pexels + TTS + FFmpeg.
"""
import os
import uuid
import shutil

from pexels_client import fetch_clip_for_keyword
from tts_client import generate_voice, generate_voice_with_words
from music_client import get_music_path
from caption_builder import group_words_into_chunks, build_ass
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


def generate_story_video(text: str, background_keywords: list, music_key: str = "mystery",
                          voice: str = None, job_id: str = None, on_progress=None) -> str:
    """
    Genera un video de "historia larga" (storytime): una sola narración de 2+ minutos,
    con subtítulos estilo meme sincronizados palabra por palabra, sobre un fondo de
    2-4 clips genéricos en loop (no tienen que combinar frase por frase con el guion).

    text: el guion completo de la historia.
    background_keywords: lista de 2-4 palabras clave en inglés para los clips de fondo.
    """
    job_id = job_id or str(uuid.uuid4())[:8]
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    def report(text_, percent):
        print(f"[job {job_id}] {text_} ({percent}%)", flush=True)
        if on_progress:
            on_progress(text_, percent)

    try:
        # 1. Generar la voz completa + el tiempo exacto de cada palabra
        report("Generando narración y sincronizando subtítulos...", 5)
        voice_path = os.path.join(job_dir, "story_voice.mp3")
        kwargs = {"voice": voice} if voice else {}
        words = generate_voice_with_words(text, voice_path, **kwargs)
        total_duration = vb.get_duration(voice_path) + 0.4

        # 2. Construir subtítulos estilo meme a partir de los tiempos reales de la voz
        report("Armando subtítulos...", 15)
        chunks = group_words_into_chunks(words, max_words=4, max_chars=26)
        ass_path = os.path.join(job_dir, "captions.ass")
        build_ass(chunks, ass_path, width=vb.FINAL_W, height=vb.FINAL_H, fontsize=80)

        # 3. Descargar 2-4 clips de fondo (ambiente, no tienen que combinar frase por frase)
        n_bg = len(background_keywords)
        bg_clip_paths = []
        for i, keyword in enumerate(background_keywords):
            pct = 15 + int((i / max(n_bg, 1)) * 40)
            report(f"Descargando fondo {i+1}/{n_bg} ('{keyword}')...", pct)
            raw_path = os.path.join(job_dir, f"bg_raw_{i}.mp4")
            found = fetch_clip_for_keyword(keyword, raw_path, min_duration=6)
            if not found:
                raise RuntimeError(
                    f"No se encontró ningún video en Pexels para la palabra clave: '{keyword}'. "
                    f"Prueba con otra palabra clave más genérica."
                )
            norm_path = os.path.join(job_dir, f"bg_norm_{i}.mp4")
            vb.normalize_clip(raw_path, norm_path, duration=8.0, text=None)
            os.remove(raw_path)
            bg_clip_paths.append(norm_path)

        # 4. Construir el fondo completo en loop hasta cubrir la duración de la narración
        report("Armando fondo en loop...", 60)
        bg_full_path = os.path.join(job_dir, "bg_full.mp4")
        vb.build_looped_background(bg_clip_paths, target_duration=total_duration,
                                    output_path=bg_full_path, transition=TRANSITION_SECONDS)

        # 5. Música de fondo (best-effort)
        report("Preparando música de fondo...", 75)
        music_path = get_music_path(music_key) if music_key else None

        # 6. Mezclar video + voz + música (resolución de trabajo, baja memoria)
        report("Mezclando audio y video...", 82)
        merged_path = os.path.join(job_dir, "merged_lowres.mp4")
        vb.merge_video_audio_music(bg_full_path, voice_path, music_path, merged_path,
                                    music_volume=0.15, target_duration=total_duration)

        # 7. Upscale a resolución final
        report("Ajustando a resolución final...", 90)
        upscaled_path = os.path.join(job_dir, "upscaled.mp4")
        vb.upscale_to_final(merged_path, upscaled_path)

        # 8. Quemar los subtítulos como último paso (sobre la resolución final, nítidos)
        report("Incrustando subtítulos...", 96)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final_path = os.path.join(OUTPUT_DIR, f"story_{job_id}.mp4")
        vb.burn_captions(upscaled_path, ass_path, final_path)

        report("¡Video listo!", 100)
        return final_path

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)
