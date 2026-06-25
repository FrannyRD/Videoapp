"""
Construye subtítulos estilo "meme" (texto grande, blanco, con borde negro grueso)
sincronizados con los tiempos exactos de la voz (word boundaries de Edge-TTS).
"""


def _seconds_to_ass_time(seconds: float) -> str:
    """Convierte segundos a formato de tiempo ASS: H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def group_words_into_chunks(words: list, max_words: int = 4, max_chars: int = 26) -> list:
    """
    Agrupa una lista de palabras con tiempos [{"text":..,"start":..,"end":..}, ...]
    en frases cortas (chunks) para mostrar como subtítulo, cortando también
    si hay signos de puntuación fuertes (. ? !) para que las frases respiren.
    """
    chunks = []
    current = []

    def flush():
        if current:
            text = " ".join(w["text"] for w in current)
            chunks.append({
                "text": text,
                "start": current[0]["start"],
                "end": current[-1]["end"],
            })

    for w in words:
        current.append(w)
        joined = " ".join(x["text"] for x in current)
        ends_strong = w["text"].rstrip().endswith((".", "?", "!"))
        if len(current) >= max_words or len(joined) >= max_chars or ends_strong:
            flush()
            current = []
    flush()
    return chunks


def build_ass(chunks: list, output_path: str, width: int, height: int,
              fontsize: int = 64, font: str = "DejaVu Sans", margin_v: int = 260):
    """
    Genera un archivo .ass con estilo "meme": texto blanco, mayúsculas,
    borde negro grueso, centrado horizontalmente, cerca de la parte inferior.
    """
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{fontsize},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in chunks:
        start = _seconds_to_ass_time(c["start"])
        end = _seconds_to_ass_time(c["end"])
        text = c["text"].upper().replace("\n", "\\N")
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))

    return output_path
