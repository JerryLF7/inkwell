#!/usr/bin/env python3
"""Token usage dashboard for Zectrix e-ink display.

Queries Hermes state.db for daily token usage and renders a dashboard.
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
PAGE_ID = 3  # Use page 3 for token dashboard

# --- Font setup ---
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]


def get_font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def get_mono_font(size: int) -> ImageFont.FreeTypeFont:
    """Try to get a monospace font, fall back to CJK."""
    mono_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for path in mono_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return get_font(size)


def query_daily_stats(target_date: datetime) -> list[dict]:
    """Query token usage for a specific date."""
    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    day_end = (target_date + timedelta(days=1)).replace(hour=0, minute=0, second=0).timestamp()

    if not STATE_DB.exists():
        return []

    conn = sqlite3.connect(str(STATE_DB))
    cur = conn.execute(
        """
        SELECT
            model,
            COUNT(*) as sessions,
            COALESCE(SUM(input_tokens), 0) as input_tok,
            COALESCE(SUM(output_tokens), 0) as output_tok,
            COALESCE(SUM(cache_read_tokens), 0) as cache_read,
            COALESCE(SUM(reasoning_tokens), 0) as reasoning
        FROM sessions
        WHERE started_at >= ? AND started_at < ?
        GROUP BY model
        ORDER BY input_tok DESC
        """,
        (day_start, day_end),
    )
    rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
    conn.close()
    return rows


def shorten_model(name: str) -> str:
    """Shorten model names for display."""
    mapping = {
        "kimi-for-coding": "kimi-code",
        "deepseek-v4-pro": "ds-v4-pro",
        "deepseek-v4-flash": "ds-v4-flash",
        "gpt-5.4": "gpt-5.4",
        "MiniMax-M2.7": "MiniMax",
    }
    return mapping.get(name, name[:12])


def fmt_tokens(n: int) -> str:
    """Format token count for display."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def render_dashboard(rows: list[dict], date_str: str) -> bytes:
    """Render token dashboard as PNG bytes."""
    img = Image.new("1", (W, H), 1)  # white
    draw = ImageDraw.Draw(img)

    title_font = get_font(18)
    header_font = get_font(13)
    body_font = get_font(14)
    small_font = get_font(11)
    total_font = get_font(16)

    y = 8

    # Title
    draw.text((10, y), f"📊 Token 用量", font=title_font, fill=0)
    draw.text((W - 100, y + 2), date_str, font=small_font, fill=0)
    y += 28

    # Divider
    draw.line((10, y, W - 10, y), fill=0, width=1)
    y += 6

    if not rows:
        draw.text((10, y + 40), "今日暂无数据", font=body_font, fill=0)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # Column headers
    col_x = [10, 110, 200, 270, 340]
    headers = ["Model", "Input", "Output", "Cache", "Total"]
    for i, h in enumerate(headers):
        draw.text((col_x[i], y), h, font=header_font, fill=0)
    y += 18

    # Data rows
    for row in rows:
        model_short = shorten_model(row["model"])
        total = row["input_tok"] + row["output_tok"]

        vals = [
            model_short,
            fmt_tokens(row["input_tok"]),
            fmt_tokens(row["output_tok"]),
            fmt_tokens(row["cache_read"]),
            fmt_tokens(total),
        ]
        for i, v in enumerate(vals):
            draw.text((col_x[i], y), v, font=body_font, fill=0)
        y += 22

    # Divider
    y += 2
    draw.line((10, y, W - 10, y), fill=0, width=1)
    y += 8

    # Total row
    total_all = sum(r["input_tok"] + r["output_tok"] for r in rows)
    input_all = sum(r["input_tok"] for r in rows)
    output_all = sum(r["output_tok"] for r in rows)
    cache_all = sum(r["cache_read"] for r in rows)

    draw.text((10, y), "TOTAL", font=total_font, fill=0)
    draw.text((col_x[1], y), fmt_tokens(input_all), font=total_font, fill=0)
    draw.text((col_x[2], y), fmt_tokens(output_all), font=total_font, fill=0)
    draw.text((col_x[3], y), fmt_tokens(cache_all), font=total_font, fill=0)
    draw.text((col_x[4], y), fmt_tokens(total_all), font=total_font, fill=0)
    y += 28

    # Footer
    draw.text((10, H - 18), f"sessions: {len(rows)}  |  models: {len(set(r['model'] for r in rows))}", font=small_font, fill=0)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def push_to_device(png_bytes: bytes) -> dict:
    """Push dashboard to e-ink device."""
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

    date_str = target_date.strftime("%m/%d")
    rows = query_daily_stats(target_date)

    print(f"Date: {date_str}, models: {len(rows)}, sessions: {sum(r['sessions'] for r in rows)}")
    for r in rows:
        total = r["input_tok"] + r["output_tok"]
        print(f"  {r['model']:25} in={r['input_tok']:>10,} out={r['output_tok']:>8,} total={total:>10,}")

    png = render_dashboard(rows, date_str)

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
