---
name: inkwell
slug: inkwell
version: 1.1.0
description: Generate and push content to Zectrix e-ink displays via Pillow canvas and REST API.
metadata:
  hermes:
    tags: [zectrix, eink, epaper, display, canvas]
    category: creative
---

# Inkwell — Zectrix 墨水屏推送

## When to Use

- Push text, images, or structured content to a Zectrix e-ink device
- Generate 1-bit PNG layouts with Chinese text support
- Query device list, manage todos, or check display pages

## Device

| Property | Value |
|----------|-------|
| Resolution | 400 × 300 |
| MAC | `20:6E:F1:B5:9E:0C` |
| Model | zectrix-s3-epaper-4.2 |

## Quick Start

```python
from dotenv import load_dotenv; load_dotenv()
from inkwell import ZectrixClient
from inkwell.canvas import render_centered_text
import os

client = ZectrixClient(os.environ["ZECTRIX_API_KEY"])
img = render_centered_text("Hello 世界", font_size=28)
client.display.push_image(
    "20:6E:F1:B5:9E:0C",
    images=[("image.png", img)],
    dither=True,
    page_id=1,
)
```

CLI:
```bash
inkwell devices list
inkwell display text 20:6E:F1:B5:9E:0C "Hello" --page 1
```

## Core Rules

1. **Always `dither=True`** — without it screen may stay blank
2. **`.env` auto-load**: CLI calls `load_dotenv()`. In Python scripts, add `from dotenv import load_dotenv; load_dotenv()` first.
3. **Canvas returns `bytes`** (PNG), not PIL Image — pass directly to `push_image`
4. **CJK fonts**: `fonts-noto-cjk` → `fonts-wqy-zenhei` → PIL default
5. **Emoji**: Use `Symbola_hint.ttf`, not `NotoColorEmoji` (PIL rejects it)
6. **Hermes venv**: inkwell is installed in `~/.hermes/hermes-agent/venv/`. If module not found:
   ```bash
   ~/.hermes/hermes-agent/venv/bin/pip3 install -e ~/.hermes/skills/creative/inkwell
   ```

## References

| Topic | File |
|-------|------|
| Canvas API (render functions, custom layouts) | `references/canvas.md` |
| Client API (devices, todos, display) | `references/api.md` |
| Setup guide (install, fonts, verify) | `references/setup.md` |

## Built-in Dashboards

### Token Dashboard (`token_dashboard.py`)

Queries Hermes `state.db` (`sessions` table) for daily LLM token usage and renders a bar-chart dashboard on page 1.

```bash
# Push today's stats
./token_dashboard.py

# Push yesterday's stats
./token_dashboard.py --yesterday

# Preview without pushing
./token_dashboard.py --dry-run
```

- **Data source**: `~/.hermes/state.db` → `sessions` table (`input_tokens`, `output_tokens`, `cache_read_tokens`, `started_at`, `model`)
- **Cron**: hourly via `cronjob` (job_id: `07ec9810f6b1`), pushes to e-ink page 1
- **Fonts**: NotoSansCJK (labels) + LiberationMono (numbers), no emoji (1-bit clean)
- **Pitfall — NULL model**: sessions rows with `model IS NULL` can sneak in despite `COALESCE` on token columns (SQL `GROUP BY` includes NULL as a group). The rendering code guards with `(r["model"] or "(unknown)")` and `(r["input_tok"] or 0)` throughout.
