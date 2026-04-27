"""inkwell CLI."""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from .client import ZectrixClient

load_dotenv()


def _get_client() -> ZectrixClient:
    key = os.environ.get("ZECTRIX_API_KEY")
    if not key:
        print("Error: ZECTRIX_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return ZectrixClient(key)


def cmd_devices_list(_args: argparse.Namespace) -> None:
    with _get_client() as client:
        for device in client.devices.list():
            print(f"{device.device_id}\t{device.alias}\t{device.board}")


def cmd_todos_list(args: argparse.Namespace) -> None:
    with _get_client() as client:
        todos = client.todos.list(
            status=args.status,
            device_id=args.device,
        )
        for todo in todos:
            status = "✓" if todo.completed else " "
            print(f"[{status}] {todo.id}: {todo.title} (due {todo.due_date})")


def cmd_display_text(args: argparse.Namespace) -> None:
    with _get_client() as client:
        result = client.display.push_text(args.device, args.text, page_id=args.page)
        print(f"Pushed to page {result['data']['pageId']}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="inkwell", description="Zectrix CLI")
    sub = parser.add_subparsers(dest="cmd")

    # devices
    dev = sub.add_parser("devices", help="Device management")
    dev_sub = dev.add_subparsers(dest="dev_cmd")
    dev_sub.add_parser("list", help="List devices")

    # todos
    todo = sub.add_parser("todos", help="Todo management")
    todo_sub = todo.add_subparsers(dest="todo_cmd")
    todo_list = todo_sub.add_parser("list", help="List todos")
    todo_list.add_argument("--status", type=int, default=None)
    todo_list.add_argument("--device", default=None)

    # display
    disp = sub.add_parser("display", help="Display push")
    disp_sub = disp.add_subparsers(dest="disp_cmd")
    disp_text = disp_sub.add_parser("text", help="Push text")
    disp_text.add_argument("device")
    disp_text.add_argument("text")
    disp_text.add_argument("--page", type=int, default=None)

    args = parser.parse_args()

    if args.cmd == "devices" and args.dev_cmd == "list":
        cmd_devices_list(args)
    elif args.cmd == "todos" and args.todo_cmd == "list":
        cmd_todos_list(args)
    elif args.cmd == "display" and args.disp_cmd == "text":
        cmd_display_text(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
