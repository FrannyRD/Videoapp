"""
Ensamblador de video final usando FFmpeg.
Toma una lista de escenas (clip de video + texto + audio de voz) y genera
un .mp4 vertical (1080x1920) listo para subir a Facebook/YouTube (Reels/Shorts).
"""
import os
import subprocess
import json


def get_duration(filepath: str) -> float:
    """Obtiene la duración en segundos de un archivo de audio/video con ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", filepath,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
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
                    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    """
    Recorta/ajusta un clip a 1080x1920, a la duración exacta requerida,
    y opcionalmente le agrega texto incrustado (subtítulo) en la parte inferior.
    """
    vf_filters = [
        "scale=1080:1920:force_original_aspect_ratio=increase",
        "crop=1080:1920",
    ]

    if text:
        lines = _wrap_text(text, max_chars_per_line=18)
        safe_lines = [_escape_text_for_ffmpeg(line) for line in lines]
        safe_text = "\n".join(safe_lines)
        drawtext = (
            f"drawtext=fontfile={font_path}:expansion=none:text='{safe_text}':"
            f"fontcolor=white:fontsize=52:box=1:boxcolor=black@0.55:boxborderw=20:"
            f"x=(w-text_w)/2:y=h-450:line_spacing=14"
        )
        vf_filters.append(drawtext)

    vf = ",".join(vf_filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-an",  # sin audio del clip original (usaremos la voz aparte)
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path


def concat_clips(clip_paths: list, output_path: str):
    """Concatena una lista de clips normalizados (mismo formato) en un solo video."""
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
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    os.remove(list_file)
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
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    os.remove(list_file)
    return output_path


def merge_video_audio_music(video_path: str, voice_path: str, music_path: str,
                             output_path: str, music_volume: float = 0.15):
    """
    Combina: video silencioso + voz en off + música de fondo (a bajo volumen).
    Si no hay música disponible, music_path puede ser None.
    """
    if music_path and os.path.exists(music_path):
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", voice_path,
            "-i", music_path,
            "-filter_complex",
            f"[2:a]volume={music_volume}[music];"
            f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path,
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
            "-shortest",
            output_path,
        ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_path
