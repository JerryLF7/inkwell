#!/usr/bin/env python3
"""E-ink countdown display."""

from __future__ import annotations

import os
from datetime import date, datetime
from io import BytesIO

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

from inkwell import ZectrixClient, render_centered_text

load_dotenv()

API_KEY = os.environ["ZECTRIX_API_KEY"]
DEVICE_ID = os.environ["ZECTRIX_DEVICE_ID"]
W = int(os.environ.get("ZECTRIX_DISPLAY_WIDTH", "400"))
H = int(os.environ.get("ZECTRIX_DISPLAY_HEIGHT", "300"))

# 配置你的倒数日
events: list[tuple[str, str]] = [
    ("2025-05-01", "五一假期"),
    ("2025-06-01", "露露生日"),
    ("2025-10-01", "国庆假期"),
    # 添加更多...
]


def days_until(target: str) -> int:
    d = datetime.strptime(target, "%Y-%m-%d").date()
    return (d - date.today()).days


def render_countdown(events: list[tuple[str, str]], width: int = 400, height: int = 300) -> bytes:
    img = Image.new("1", (width, height), 1)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 22, index=0)
        font_days = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 52, index=0)
        font_label = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18, index=0)
        font_small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 12, index=0)
    except Exception:
        font_title = font_days = font_label = font_small = ImageFont.load_default()

    # 排序，最近的放最上面
    upcoming = [(days_until(d), label) for d, label in events if days_until(d) >= 0]
    upcoming.sort(key=lambda x: x[0])

    if not upcoming:
        return render_centered_text("No upcoming events", width=width, height=height, font_size=24)

    # 画主标题
    y = 15
    draw.text((width // 2, y), "倒计时", font=font_title, fill=0, anchor="mm")
    y += 35

    # 第一个事件：大字号
    days, label = upcoming[0]
    draw.text((width // 2, y), str(days), font=font_days, fill=0, anchor="mm")
    y += 55
    draw.text((width // 2, y), f"天后 {label}", font=font_label, fill=0, anchor="mm")
    y += 30

    # 分割线
    draw.line((40, y, width - 40, y), fill=0, width=1)
    y += 12

    # 后续事件小字号
    for days, label in upcoming[1:3]:
        draw.text((width // 2, y), f"{days} 天后  {label}", font=font_small, fill=0, anchor="mm")
        y += 18

    # 底部日期
    draw.text((width // 2, height - 15), date.today().isoformat(), font=font_small, fill=0, anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    image = render_countdown(events, width=W, height=H)
    with ZectrixClient(API_KEY) as client:
        result = client.display.push_image(
            DEVICE_ID,
            images=[("countdown.png", image)],
            dither=True,
            page_id=1,
        )
        print(f"Pushed: {result}")


if __name__ == "__main__":
    main()
