# API Reference

## ZectrixClient

```python
from inkwell import ZectrixClient

client = ZectrixClient(api_key: str, base_url="https://cloud.zectrix.com/open/v1")
```

## Devices

```python
client.devices.list() -> list[Device]
# Device fields: device_id, alias, board
```

## Todos

```python
client.todos.list(status=None, device_id=None) -> list[Todo]
client.todos.create(payload: dict) -> Todo
client.todos.update(todo_id: int, payload: dict) -> Todo
client.todos.toggle_complete(todo_id: int) -> dict
client.todos.delete(todo_id: int) -> dict
```

## Display

```python
client.display.push_image(
    device_id: str,
    images: list[tuple[str, bytes]],  # [(filename, png_bytes), ...]
    dither: bool = True,
    page_id: int | None = None,
) -> dict

client.display.push_text(
    device_id: str,
    text: str,
    page_id: int | None = None,
) -> dict

client.display.push_structured_text(
    device_id: str,
    title: str,
    body: str,
    page_id: int | None = None,
) -> dict

client.display.delete_page(device_id: str, page_id: int | None = None) -> dict
```

## Response Format

All API calls return `dict` with structure:
```python
{"code": 0, "msg": "success", "data": {...}}
```

## Traps

| Problem | Cause | Fix |
|---------|-------|-----|
| Image pushed but screen blank | dither=false | Always pass `dither=True` |
| 401 Unauthorized | API key invalid or expired | Check `ZECTRIX_API_KEY` |
| Page not updating | Wrong page_id | Device supports pages 1-5 |
