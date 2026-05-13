---
name: inkwell
slug: inkwell
version: 1.2.0
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
| Canvas API (render functions, custom layouts) | `skill/references/canvas.md` |
| Client API (devices, todos, display) | `skill/references/api.md` |
| Setup guide (install, fonts, verify) | `skill/references/setup.md` |
| Token Dashboard (daily + weekly) | `scripts/token_dashboard.py` |

## Built-in Dashboards

### Token Dashboard (`token_dashboard.py`)

Queries Hermes `state.db` (`sessions` table) for daily LLM token usage and renders a bar-chart dashboard on page 1. Also supports weekly aggregation on page 2.

```bash
# Push today's stats (page 1)
./scripts/token_dashboard.py

# Push yesterday's stats (page 1)
./scripts/token_dashboard.py --yesterday

# Push weekly summary (page 2)
./scripts/token_dashboard.py --weekly

# Preview without pushing
./scripts/token_dashboard.py --dry-run
./scripts/token_dashboard.py --weekly --dry-run
```

- **Data source**: `~/.hermes/state.db` → `sessions` table (`input_tokens`, `output_tokens`, `cache_read_tokens`, `started_at`, `model`)
- **History log**: `~/.hermes/token_history.json` — daily aggregated stats written on every run. Weekly mode reads this file (not state.db) to aggregate last 7 days.
- **Cron**: 
  - Daily: hourly via `cronjob` (job_id: `07ec9810f6b1`), pushes to e-ink **page 1**
  - Weekly: Mondays 09:00 via `cronjob` (job_id: `5e5221cc36b1`), pushes to e-ink **page 2**
- **Fonts**: NotoSansCJK (labels) + LiberationMono (numbers), no emoji (1-bit clean)
- **Push time**: header includes the render/push time in 24-hour `HH:MM` format (e.g. `04/28 20:55`). Keep this compact so it fits the 400px width.
- **Testing**: `pytest` may not be on PATH; run tests with Hermes venv: `/home/jerry/.hermes/hermes-agent/venv/bin/python -m pytest -q scripts/tests/` from the inkwell project directory.
- **Pitfall — NULL model**: sessions rows with `model IS NULL` can sneak in despite `COALESCE` on token columns (SQL `GROUP BY` includes NULL as a group). The rendering code guards with `(r["model"] or "(unknown)")` and `(r["input_tok"] or 0)` throughout.
- **Pitfall — weekly data gaps**: `aggregate_weekly()` only sums days present in `token_history.json`. If a day is missing (e.g. cron was down), the weekly total is understated. No interpolation is performed.
