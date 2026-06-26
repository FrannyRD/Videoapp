"""
Ensamblador de video final usando FFmpeg.
Toma una lista de escenas (clip de video + texto + audio de voz) y genera
un .mp4 vertical listo para subir a Facebook/YouTube (Reels/Shorts).

IMPORTANTE sobre memoria: el procesamiento pesado (normalizar clips + transiciones)
se hace en una resolución reducida (WORK_W x WORK_H) para no agotar la memoria en
servidores con poco RAM (ej. plan gratis de Render = 512MB). Al final se hace un
único "upscale" liviano a la resolución final (FINAL_W x FINAL_H).
"""
import os
import subprocess
import json

WORK_W, WORK_H = 720, 1280      # resolución de trabajo (bajo consumo de memoria)
FINAL_W, FINAL_H = 1080, 1920   # resolución final de entrega


def get_duration(filepath: str) -> float:
    """Obtiene la duración en segundos de un archivo de audio/video con ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", filepath,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def _escape_text_for_ffmpeg(text: str) -> str:
    """Escapa caracteres especiales para que drawtext no falle."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\u2019")  # comilla simple tipográfica, evita romper el filtro
        .replace("%", "%")  # con expansion=none no requiere escape especial
    )


def _wrap_text(text: str, max_chars_per_line: int = 18) -> list:
    """
    Divide el texto en varias líneas (lista de strings) para que no se salga de pantalla.
    """
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) > max_chars_per_line and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def normalize_clip(input_path: str, output_path: str, duration: float, text: str = None,
                    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    zoom: bool = True, fps: int = 30):
    """
    Recorta/ajusta un clip a la resolución de TRABAJO (más liviana en memoria),
    a la duración exacta requerida, le agrega un zoom lento (efecto "Ken Burns")
    para que no se vea estático, y opcionalmente texto incrustado (fijo, sin zoom).
    La resolución final (1080x1920) se aplica al final con upscale_to_final().
    """
    vf_filters = [
        f"scale={WORK_W}:{WORK_H}:force_original_aspect_ratio=increase",
        f"crop={WORK_W}:{WORK_H}",
    ]

    if zoom:
        total_frames = max(round(duration * fps), 1)
        target_zoom = 1.12
        increment = (target_zoom - 1) / total_frames
        vf_filters.append(
            f"zoompan=z='min(zoom+{increment:.6f},{target_zoom})':d=1:s={WORK_W}x{WORK_H}:fps={fps}"
        )

    if text:
        lines = _wrap_text(text, max_chars_per_line=18)
        safe_lines = [_escape_text_for_ffmpeg(line) for line in lines]
        safe_text = "\n".join(safe_lines)
        # Tamaños proporcionales a la resolución de trabajo (escalados desde el diseño original a 1080 de ancho)
        scale_factor = WORK_W / 1080
        fontsize = round(52 * scale_factor)
        y_offset = round(450 * scale_factor)
        boxborder = round(20 * scale_factor)
        line_spacing = round(14 * scale_factor)
        drawtext = (
            f"drawtext=fontfile={font_path}:expansion=none:text='{safe_text}':"
            f"fontcolor=white:fontsize={fontsize}:box=1:boxcolor=black@0.55:boxborderw={boxborder}:"
            f"x=(w-text_w)/2:y=h-{y_offset}:line_spacing={line_spacing}"
        )
        vf_filters.append(drawtext)  # se agrega DESPUÉS del zoom, para que el texto quede fijo y nítido

    vf = ",".join(vf_filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "1",
        "-pix_fmt", "yuv420p",
        "-an",  # sin audio del clip original (usaremos la voz aparte)
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    return output_path


def concat_clips(clip_paths: list, output_path: str):
    """Concatena una lista de clips normalizados (mismo formato) en un solo video, sin transición."""
    list_file = output_path + ".txt"
    with open(list_file, "w") as f:
        for path in clip_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    os.remove(list_file)
    return output_path


def build_looped_background(clip_paths: list, target_duration: float, output_path: str, transition: float = 0.5):
    """
    Para historias largas (storytime): repite una lista corta de clips de ambiente
    (ya normalizados y con zoom aplicado) las veces que haga falta, con transición
    entre cada uno, hasta cubrir target_duration. Al final recorta al segundo exacto.
    """
    if not clip_paths:
        raise ValueError("Se necesita al menos un clip de fondo")

    # Duración real de cada clip (puede variar levemente entre ellos)
    clip_durations = [get_duration(p) for p in clip_paths]
    avg_step = sum(clip_durations) / len(clip_durations) - transition  # aporte neto por clip tras el fundido

    # Cuántas repeticiones del set de clips hacen falta para cubrir target_duration + margen
    needed_total = target_duration + transition * 2
    sequence = []
    seq_duration = 0.0
    i = 0
    while seq_duration < needed_total:
        path = clip_paths[i % len(clip_paths)]
        sequence.append(path)
        seq_duration += clip_durations[i % len(clip_paths)]
        if len(sequence) > 1:
            seq_duration -= transition
        i += 1
        if len(sequence) > 200:  # salvaguarda, no debería pasar nunca
            break

    raw_output = output_path + ".raw.mp4"
    concat_clips_with_transitions(sequence, raw_output, transition=transition)

    # Recortar al segundo exacto que necesitamos
    cmd = [
        "ffmpeg", "-y",
        "-i", raw_output,
        "-t", str(target_duration),
        "-c", "copy",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    os.remove(raw_output)
    return output_path


def concat_clips_with_transitions(clip_paths: list, output_path: str, transition: float = 0.5):
    """
    Concatena clips con un crossfade (fundido) suave entre cada uno.
    Los procesa de A PARES, secuencialmente (no todos a la vez), para no disparar
    el uso de memoria en servidores con poco RAM (ej. plan gratis de Render).
    """
    n = len(clip_paths)
    if n == 1:
        return concat_clips(clip_paths, output_path)

    work_dir = os.path.dirname(output_path) or "."
    current = clip_paths[0]
    is_temp_current = False

    for i in range(1, n):
        next_clip = clip_paths[i]
        is_last = (i == n - 1)
        step_output = output_path if is_last else os.path.join(work_dir, f"_xfade_step_{i}.mp4")

        current_duration = get_duration(current)
        offset = max(current_duration - transition, 0)

        cmd = [
            "ffmpeg", "-y",
            "-i", current,
            "-i", next_clip,
            "-filter_complex",
            f"[0:v]fps=30,settb=AVTB[v0];[1:v]fps=30,settb=AVTB[v1];"
            f"[v0][v1]xfade=transition=fade:duration={transition}:offset={offset:.3f}[vout]",
            "-map", "[vout]",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-threads", "1",
            "-pix_fmt", "yuv420p",
            step_output,
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)

        if is_temp_current:
            os.remove(current)

        current = step_output
        is_temp_current = not is_last

    return output_path


def burn_captions(input_video: str, ass_path: str, output_path: str):
    """
    Quema (incrusta) los subtítulos del archivo .ass en el video.
    Se hace como ÚLTIMO paso, sobre el video ya en resolución final,
    para que el texto salga nítido (no escalado/borroso).
    """
    # ffmpeg necesita la ruta del archivo .ass escapada de cierta forma dentro del filtro
    safe_ass_path = ass_path.replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", f"subtitles={safe_ass_path}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "1",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    return output_path


def upscale_to_final(input_path: str, output_path: str, width: int = FINAL_W, height: int = FINAL_H):
    """
    Escala el video final (ya con voz y música mezcladas) a la resolución de entrega.
    Es un paso liviano: un solo stream, sin transiciones ni texto que recalcular,
    por eso no representa un riesgo de memoria como el procesamiento por escena.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"scale={width}:{height}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-threads", "1",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    return output_path


def concat_audio(audio_paths: list, output_path: str):
    """Concatena los audios de voz de cada escena en uno solo, en orden."""
    list_file = output_path + ".txt"
    with open(list_file, "w") as f:
        for path in audio_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c:a", "aac",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    os.remove(list_file)
    return output_path


def merge_video_audio_music(video_path: str, voice_path: str, music_path: str,
                             output_path: str, music_volume: float = 0.15,
                             target_duration: float = None):
    """
    Combina: video silencioso + voz en off + música de fondo (a bajo volumen).
    Si no hay música disponible, music_path puede ser None.
    target_duration fija la duración exacta del archivo final (normalmente la duración
    del video), para que una música más larga o más corta no la altere.
    """
    if music_path and os.path.exists(music_path):
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", voice_path,
            "-stream_loop", "-1", "-i", music_path,  # repetir música si es más corta que el video
            "-filter_complex",
            f"[2:a]volume={music_volume}[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", voice_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
        ]

    if target_duration:
        cmd += ["-t", str(target_duration)]
    cmd.append(output_path)

    subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=180)
    return output_path
