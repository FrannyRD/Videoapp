"""
Música de fondo para la app.

Antes la app intentaba descargar canciones externas. Si una URL fallaba con 404,
el video se generaba sin música. Ahora la música se crea localmente con FFmpeg,
sin depender de URLs externas y sin riesgo de copyright por pistas descargadas.

Cada categoría genera una pista ambiental distinta y la guarda en assets/music/.
Si FFmpeg falla por alguna razón, el video continúa sin música para no romper el flujo.
"""
from __future__ import annotations

import os
import subprocess
from typing import Dict, List

MUSIC_DIR = "assets/music"
os.makedirs(MUSIC_DIR, exist_ok=True)

# Opciones visibles en la app.
MUSIC_LABELS: Dict[str, str] = {
    "mystery": "Misterio general",
    "suspense": "Suspenso suave",
    "epic": "Épica documental",
    "true_crime": "True crime / investigación",
    "psychology": "Psicología / tensión sutil",
    "wildlife": "Animal / naturaleza intensa",
    "historical": "Historia / archivo secreto",
    "biblical": "Bíblico / épico emocional",
    "enigma": "Enigma / misterio diario",
    "none": "Sin música",
}

# Presets de música generativa local.
# Son fondos ambientales simples, pensados para quedar bajos detrás de la voz.
MUSIC_PRESETS: Dict[str, Dict] = {
    "mystery": {
        "freqs": [82, 164, 246],
        "volumes": [0.10, 0.035, 0.020],
        "noise_amp": 0.018,
        "lowpass": 2600,
        "highpass": 35,
    },
    "suspense": {
        "freqs": [73, 146, 219],
        "volumes": [0.09, 0.035, 0.018],
        "noise_amp": 0.022,
        "lowpass": 2300,
        "highpass": 30,
    },
    "epic": {
        "freqs": [65, 130, 196, 262],
        "volumes": [0.11, 0.045, 0.025, 0.018],
        "noise_amp": 0.012,
        "lowpass": 3200,
        "highpass": 35,
    },
    "true_crime": {
        "freqs": [55, 110, 165],
        "volumes": [0.11, 0.038, 0.020],
        "noise_amp": 0.025,
        "lowpass": 2100,
        "highpass": 28,
    },
    "psychology": {
        "freqs": [96, 192, 288],
        "volumes": [0.08, 0.030, 0.016],
        "noise_amp": 0.014,
        "lowpass": 3000,
        "highpass": 45,
    },
    "wildlife": {
        "freqs": [61, 122, 244, 366],
        "volumes": [0.10, 0.045, 0.022, 0.014],
        "noise_amp": 0.030,
        "lowpass": 3600,
        "highpass": 40,
    },
    "historical": {
        "freqs": [87, 174, 261],
        "volumes": [0.09, 0.035, 0.018],
        "noise_amp": 0.016,
        "lowpass": 2700,
        "highpass": 35,
    },
    "biblical": {
        "freqs": [98, 196, 294, 392],
        "volumes": [0.09, 0.040, 0.022, 0.015],
        "noise_amp": 0.010,
        "lowpass": 3400,
        "highpass": 45,
    },
    "enigma": {
        "freqs": [70, 140, 210, 280],
        "volumes": [0.095, 0.035, 0.018, 0.012],
        "noise_amp": 0.020,
        "lowpass": 2500,
        "highpass": 35,
    },
}


def _safe_key(key: str) -> str:
    return "".join(ch for ch in key if ch.isalnum() or ch in ("_", "-")) or "music"


def _build_ffmpeg_inputs(preset: Dict, duration: int) -> tuple[List[str], List[str]]:
    """Crea inputs lavfi y filtros para mezclar tonos + ruido suave."""
    cmd_inputs: List[str] = []
    mix_labels: List[str] = []

    for idx, freq in enumerate(preset["freqs"]):
        cmd_inputs += ["-f", "lavfi", "-i", f"sine=frequency={freq}:sample_rate=44100:duration={duration}"]
        volume = preset["volumes"][idx]
        mix_labels.append(f"[{idx}:a]volume={volume},aecho=0.6:0.5:900|1300:0.12|0.08[t{idx}]")

    noise_index = len(preset["freqs"])
    noise_amp = preset.get("noise_amp", 0.015)
    cmd_inputs += ["-f", "lavfi", "-i", f"anoisesrc=color=pink:sample_rate=44100:duration={duration}:amplitude={noise_amp}"]
    mix_labels.append(f"[{noise_index}:a]volume=0.16[n0]")

    return cmd_inputs, mix_labels


def _generate_music_with_ffmpeg(key: str, output_path: str, duration: int = 180) -> str | None:
    """Genera una pista ambiental local con FFmpeg."""
    preset = MUSIC_PRESETS.get(key) or MUSIC_PRESETS["mystery"]
    cmd_inputs, label_filters = _build_ffmpeg_inputs(preset, duration)

    tone_count = len(preset["freqs"])
    input_labels = "".join(f"[t{i}]" for i in range(tone_count)) + "[n0]"
    input_count = tone_count + 1
    filter_complex = (
        ";".join(label_filters)
        + f";{input_labels}amix=inputs={input_count}:duration=longest:dropout_transition=0,"
        + f"highpass=f={preset.get('highpass', 35)},lowpass=f={preset.get('lowpass', 2800)},"
        + "acompressor=threshold=-24dB:ratio=2:attack=50:release=600,"
        + f"afade=t=in:st=0:d=4,afade=t=out:st={max(duration - 5, 1)}:d=5,"
        + "volume=0.85[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        *cmd_inputs,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", str(duration),
        "-ac", "2",
        "-ar", "44100",
        "-q:a", "5",
        output_path,
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=240)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"[music_client] Música local generada: {key} -> {output_path}", flush=True)
            return output_path
        raise RuntimeError("FFmpeg no generó archivo de música válido")
    except Exception as e:
        print(f"[music_client] No se pudo generar música local '{key}': {e}. Se continúa sin música.", flush=True)
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return None


def get_music_path(key: str) -> str | None:
    """
    Devuelve la ruta local de la música.

    - Si key es "none", devuelve None.
    - Si ya existe una pista local, la reutiliza.
    - Si no existe, la genera con FFmpeg.
    - Si falla, devuelve None para que el video no se rompa.
    """
    key = (key or "none").strip()
    if key == "none":
        return None

    if key not in MUSIC_LABELS:
        key = "mystery"

    local_path = os.path.join(MUSIC_DIR, f"{_safe_key(key)}.mp3")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path

    return _generate_music_with_ffmpeg(key, local_path)
