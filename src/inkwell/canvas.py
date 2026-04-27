"""E-ink canvas helpers for generating centered/layout images."""

from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def render_centered_text(
    text: str,
    *,
    width: int = 400,
    height: int = 300,
    font_size: int = 24,
    font_path: str | None = None,
) -> bytes:
    """Render white-background black text centered on a 1-bit image."""
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", font_size, index=0)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = (height - text_h) // 2

    draw.text((x, y), text, font=font, fill=0)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_text_block(
    text: str,
    *,
    width: int = 400,
    height: int = 300,
    font_size: int = 16,
    line_spacing: int = 4,
    padding: int = 8,
    font_path: str | None = None,
) -> bytes:
    """Render multi-line text with word wrapping."""
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", font_size, index=0)
        except Exception:
            font = ImageFont.load_default()

    max_width = width - padding * 2
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

    bbox = draw.textbbox((0, 0), "Ay", font=font)
    line_h = bbox[3] - bbox[1] + line_spacing
    total_h = len(lines) * line_h
    y = (height - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        draw.text((x, y), line, font=font, fill=0)
        y += line_h

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
