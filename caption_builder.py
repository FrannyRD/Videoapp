"""
Construye subtítulos .ASS sincronizados con los tiempos exactos de la voz.
Incluye varios estilos para adaptar cada página sin tocar el render principal.
"""

CAPTION_STYLES = {
    "meme": {
        "label": "Meme grande blanco",
        "fontsize": 80,
        "font": "DejaVu Sans",
        "primary": "&H00FFFFFF",
        "outline": "&H00000000",
        "back": "&H00000000",
        "bold": -1,
        "italic": 0,
        "border_style": 1,
        "outline_size": 6,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 260,
        "uppercase": True,
    },
    "cinematic": {
        "label": "Cinemático elegante",
        "fontsize": 66,
        "font": "DejaVu Serif",
        "primary": "&H00F5F5F5",
        "outline": "&H00101010",
        "back": "&H00000000",
        "bold": -1,
        "italic": 0,
        "border_style": 1,
        "outline_size": 4,
        "shadow": 1,
        "alignment": 2,
        "margin_v": 300,
        "uppercase": False,
    },
    "clean": {
        "label": "Limpio moderno",
        "fontsize": 62,
        "font": "DejaVu Sans",
        "primary": "&H00FFFFFF",
        "outline": "&H003A2A18",
        "back": "&H00000000",
        "bold": -1,
        "italic": 0,
        "border_style": 1,
        "outline_size": 3,
        "shadow": 1,
        "alignment": 2,
        "margin_v": 260,
        "uppercase": False,
    },
    "yellow": {
        "label": "Amarillo impacto",
        "fontsize": 72,
        "font": "DejaVu Sans",
        "primary": "&H0000FFFF",
        "outline": "&H00000000",
        "back": "&H00000000",
        "bold": -1,
        "italic": 0,
        "border_style": 1,
        "outline_size": 5,
        "shadow": 1,
        "alignment": 2,
        "margin_v": 260,
        "uppercase": True,
    },
    "minimal": {
        "label": "Minimal discreto",
        "fontsize": 52,
        "font": "DejaVu Sans",
        "primary": "&H00FFFFFF",
        "outline": "&H00000000",
        "back": "&H00000000",
        "bold": 0,
        "italic": 0,
        "border_style": 1,
        "outline_size": 2,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 230,
        "uppercase": False,
    },
}


def _seconds_to_ass_time(seconds: float) -> str:
    """Convierte segundos a formato de tiempo ASS: H:MM:SS.cc"""
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _escape_ass_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("{", "")
        .replace("}", "")
        .replace("\n", "\\N")
    )


def group_words_into_chunks(words: list, max_words: int = 4, max_chars: int = 26) -> list:
    """
    Agrupa una lista de palabras con tiempos [{"text":..,"start":..,"end":..}, ...]
    en frases cortas para mostrar como subtítulo.
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
              fontsize: int | None = None, font: str | None = None, margin_v: int | None = None,
              style_key: str = "meme"):
    """Genera archivo .ass con un estilo visual seleccionable."""
    style = dict(CAPTION_STYLES.get(style_key) or CAPTION_STYLES["meme"])
    if fontsize is not None:
        style["fontsize"] = fontsize
    if font is not None:
        style["font"] = font
    if margin_v is not None:
        style["margin_v"] = margin_v

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style['font']},{style['fontsize']},{style['primary']},&H000000FF,{style['outline']},{style['back']},{style['bold']},{style['italic']},0,0,100,100,0,0,{style['border_style']},{style['outline_size']},{style['shadow']},{style['alignment']},40,40,{style['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in chunks:
        start = _seconds_to_ass_time(c["start"])
        end = _seconds_to_ass_time(c["end"])
        raw = c["text"].upper() if style.get("uppercase") else c["text"]
        text = _escape_ass_text(raw)
        lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(lines))

    return output_path
