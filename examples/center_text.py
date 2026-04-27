#!/usr/bin/env python3
"""Push centered text to e-ink display."""

import os

from dotenv import load_dotenv

from inkwell import ZectrixClient, render_centered_text

load_dotenv()

API_KEY = os.environ["ZECTRIX_API_KEY"]
DEVICE_ID = os.environ["ZECTRIX_DEVICE_ID"]
WIDTH = int(os.environ.get("ZECTRIX_DISPLAY_WIDTH", "400"))
HEIGHT = int(os.environ.get("ZECTRIX_DISPLAY_HEIGHT", "300"))


def main() -> None:
    with ZectrixClient(API_KEY) as client:
        image_bytes = render_centered_text(
            "Hello inkwell",
            width=WIDTH,
            height=HEIGHT,
            font_size=28,
        )
        result = client.display.push_image(
            DEVICE_ID,
            images=[("hello.png", image_bytes)],
            dither=True,
            page_id=1,
        )
        print(f"Pushed: {result}")


if __name__ == "__main__":
    main()
