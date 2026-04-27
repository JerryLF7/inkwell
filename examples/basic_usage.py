#!/usr/bin/env python3
"""Basic inkwell usage examples."""

import os

from dotenv import load_dotenv

from inkwell import ZectrixClient

load_dotenv()

API_KEY = os.environ.get("ZECTRIX_API_KEY", "zt_your_key_here")
DEVICE_ID = os.environ.get("ZECTRIX_DEVICE_ID", "20:6E:F1:B5:9E:0C")


def main() -> None:
    with ZectrixClient(API_KEY) as client:
        # List devices
        print("=== Devices ===")
        for device in client.devices.list():
            print(f"  {device.device_id} - {device.alias} ({device.board})")

        # List pending todos
        print("\n=== Pending Todos ===")
        for todo in client.todos.list(status=0):
            print(f"  [{todo.id}] {todo.title} (due {todo.due_date})")

        # Push text to device
        print("\n=== Push Text ===")
        result = client.display.push_text(
            DEVICE_ID,
            "Hello from inkwell!",
            page_id=1,
        )
        print(f"  Pushed to page {result['data']['pageId']}")


if __name__ == "__main__":
    main()
