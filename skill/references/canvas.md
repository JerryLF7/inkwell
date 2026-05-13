# Canvas API Reference

## Functions

### `render_centered_text(text, font_size=24, width=400, height=300, font_path=None) -> bytes`

Single-line text centered on white background. Returns PNG bytes.

### `render_text_block(text, font_size=16, width=400, height=300, line_spacing=4, padding=8, font_path=None) -> bytes`

Multi-line text with word wrapping and vertical centering. Splits on `\n` and spaces.

## Font Loading

```python
from PIL import ImageFont

FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # index=0 for SC
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

def get_font(size, index=0):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()
```

## Custom Layouts

For dashboards or multi-section layouts, use Pillow directly:

```python
from PIL import Image, ImageDraw

img = Image.new("1", (400, 300), 1)  # white
draw = ImageDraw.Draw(img)
font = get_font(18)

# Header
draw.text((10, 10), "Weather", font=font, fill=0)
# Divider
draw.line((10, 40, 390, 40), fill=0, width=1)
# Body
draw.text((10, 50), "22°C 晴", font=font, fill=0)

buf = BytesIO()
img.save(buf, format="PNG")
return buf.getvalue()
```

## Traps

| Problem | Cause | Fix |
|---------|-------|-----|
| Chinese shows as boxes | Font missing CJK glyphs | Install `fonts-noto-cjk` |
| Text cut off at bottom | Line count exceeds canvas | Reduce `font_size` or split to multiple pages |
| Extra top padding | PIL textbbox includes ascent | Test render, adjust y offset manually |
| English text misaligned with Chinese | Mixed font metrics | Use CJK font for everything |
| Emoji font `NotoColorEmoji.ttf` throws `OSError: invalid pixel size` in PIL for all sizes | Colored emoji fonts not supported by PIL's `ImageFont.truetype` | Use `/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf` — renders emoji as clean 1-bit line art, perfect for e-ink |
