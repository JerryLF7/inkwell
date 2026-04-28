#!/usr/bin/env python3
"""Token usage dashboard for Zectrix e-ink display.

Queries Hermes state.db for daily token usage and renders a clean dashboard.
"""

from __future__ import annotations

import sqlite3
import os
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# --- Config ---
STATE_DB = Path.home() / ".hermes" / "state.db"
DEVICE_ID = os.environ.get("ZECTRIX_DEVICE_ID", "20:6E:F1:B5:9E:0C")
API_KEY = os.environ.get("ZECTRIX_API_KEY", "")
W, H = 400, 300
PAGE_ID = 1
MARGIN = 12

# --- Fonts ---
FONT_CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_MONO = "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"
FONT_SYMBOLA = "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"


def _load(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size, index=index)
    except OSError:
        return ImageFont.load_default()


def get_font(size: int) -> ImageFont.FreeTypeFont:
    return _load(FONT_CJK, size)


def get_mono(size: int) -> ImageFont.FreeTypeFont:
    try:
        return _load(FONT_MONO, size)
    except Exception:
        return get_font(size)


def get_symbol(size: int) -> ImageFont.FreeTypeFont:
    try:
        return _load(FONT_SYMBOLA, size)
    except Exception:
        return _load(FONT_CJK, size)


# --- Data ---
def query_daily_stats(target_date: datetime) -> list[dict]:
    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    day_end = (target_date + timedelta(days=1)).replace(hour=0, minute=0, second=0).timestamp()
    if not STATE_DB.exists():
        return []
    conn = sqlite3.connect(str(STATE_DB))
    cur = conn.execute(
        """SELECT model, COUNT(*) as sessions,
                  COALESCE(SUM(input_tokens),0) AS input_tok,
                  COALESCE(SUM(output_tokens),0) AS output_tok,
                  COALESCE(SUM(cache_read_tokens),0) AS cache_read
           FROM sessions
           WHERE started_at >= ? AND started_at < ?
           GROUP BY model ORDER BY input_tok DESC""",
        (day_start, day_end))
    rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    conn.close()
    return rows


def shorten_model(name: str) -> str:
    m = {
        "kimi-for-coding": "kimi-code",
        "deepseek-v4-pro": "ds-v4-pro",
        "deepseek-v4-flash": "ds-v4-flash",
        "gpt-5.4": "gpt-5.4",
        "MiniMax-M2.7": "MiniMax",
    }
    return m.get(name, name[:12])


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1000:.0f}K"
    return str(n)


def format_push_time(dt: datetime) -> str:
    """Return push time in 24-hour HH:MM format."""
    return dt.strftime("%H:%M")


def bar_width(tokens: int, max_tokens: int, available: int) -> int:
    if max_tokens == 0:
        return 0
    return max(1, int(tokens / max_tokens * available))


# --- Render ---
def render_dashboard(rows: list[dict], date_str: str) -> bytes:
    img = Image.new("1", (W, H), 1)
    draw = ImageDraw.Draw(img)

    f_title = get_font(20)
    f_date = get_mono(13)
    f_model = get_font(15)
    f_num = get_mono(15)
    f_small = get_font(12)
    f_total_lbl = get_font(16)
    f_total_val = get_mono(16)
    f_symbol = get_symbol(18)

    y = MARGIN

    # --- Header ---
    # Use a simple bullet from Symbola: ⬩ (U+2B29) or just use text
    draw.text((MARGIN, y), "Token 用量", font=f_title, fill=0)
    date_w = draw.textlength(date_str, font=f_date)
    draw.text((W - MARGIN - date_w, y + 4), date_str, font=f_date, fill=0)
    y += 32

    # Divider
    draw.line((MARGIN, y, W - MARGIN, y), fill=0, width=1)
    y += 10

    if not rows:
        draw.text((MARGIN, y + 30), "(no data yet)", font=f_model, fill=0)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # --- Model rows with bars ---
    max_total = max((r["input_tok"] or 0) + (r["output_tok"] or 0) for r in rows)
    bar_area_w = 140  # width for the bar chart area
    model_col_w = 110

    for row in rows:
        model_short = shorten_model(row["model"] or "(unknown)")
        total = (row["input_tok"] or 0) + (row["output_tok"] or 0)
        total_str = fmt_tokens(total)

        # Model name
        draw.text((MARGIN, y), model_short, font=f_model, fill=0)

        # Bar
        bar_x = MARGIN + model_col_w
        bw = bar_width(total, max_total, bar_area_w)
        bar_y = y + 4
        bar_h = 14
        # Bar background (outline)
        draw.rectangle((bar_x, bar_y, bar_x + bar_area_w, bar_y + bar_h), outline=0)
        # Bar fill
        if bw > 0:
            draw.rectangle((bar_x + 1, bar_y + 1, bar_x + bw, bar_y + bar_h - 1), fill=0)

        # Token count (right-aligned)
        num_w = draw.textlength(total_str, font=f_num)
        draw.text((W - MARGIN - num_w, y), total_str, font=f_num, fill=0)

        y += 24

    y += 6

    # --- Divider ---
    draw.line((MARGIN, y, W - MARGIN, y), fill=0, width=1)
    y += 10

    # --- Total ---
    total_all = sum((r["input_tok"] or 0) + (r["output_tok"] or 0) for r in rows)
    sessions_all = sum(r["sessions"] for r in rows)

    draw.text((MARGIN, y), "TOTAL", font=f_total_lbl, fill=0)
    total_w = draw.textlength(fmt_tokens(total_all), font=f_total_val)
    draw.text((W - MARGIN - total_w, y), fmt_tokens(total_all), font=f_total_val, fill=0)
    y += 24

    # --- Footer ---
    footer = f"{sessions_all} sessions  |  {len(rows)} models"
    y += 3
    draw.text((MARGIN, y), footer, font=f_small, fill=0)

    # Input / Output breakdown on right
    input_all = sum(r["input_tok"] or 0 for r in rows)
    output_all = sum(r["output_tok"] or 0 for r in rows)
    detail = f"in {fmt_tokens(input_all)}  out {fmt_tokens(output_all)}"
    det_w = draw.textlength(detail, font=f_small)
    draw.text((W - MARGIN - det_w, y), detail, font=f_small, fill=0)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def push_to_device(png_bytes: bytes) -> dict:
    from inkwell import ZectrixClient
    client = ZectrixClient(API_KEY)
    return client.display.push_image(
        DEVICE_ID,
        images=[("token_dashboard.png", png_bytes)],
        dither=True,
        page_id=PAGE_ID,
    )


def main():
    target_date = datetime.now()
    if len(sys.argv) > 1 and sys.argv[1] == "--yesterday":
        target_date = datetime.now() - timedelta(days=1)

    now = datetime.now()
    date_str = target_date.strftime("%m/%d")
    header_time = format_push_time(now)
    rows = query_daily_stats(target_date)

    print(f"Date: {date_str}, pushed: {header_time}, models: {len(rows)}, sessions: {sum(r['sessions'] for r in rows)}")
    for r in rows:
        in_tok = r["input_tok"] or 0
        out_tok = r["output_tok"] or 0
        total = in_tok + out_tok
        print(f"  {(r['model'] or '(unknown)'):25} in={in_tok:>10,} out={out_tok:>8,} total={total:>10,}")

    png = render_dashboard(rows, f"{date_str} {header_time}")

    if "--dry-run" in sys.argv:
        out_path = Path.home() / ".hermes" / "token_dashboard_preview.png"
        with open(out_path, "wb") as f:
            f.write(png)
        print(f"Preview saved to {out_path}")
        return

    result = push_to_device(png)
    print(f"Push result: {result}")
    if result.get("code") != 0:
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
