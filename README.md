# inkwell

Python SDK & CLI for the [Zectrix](https://cloud.zectrix.com) e-ink cloud platform.

## Install

```bash
pip install -e .
```

## Quick Start

```python
from inkwell import ZectrixClient

client = ZectrixClient(api_key="zt_your_key_here")

# List devices
devices = client.devices.list()

# List todos
todos = client.todos.list()

# Push text to a device
client.display.push_text("20:6E:F1:B5:9E:0C", "Hello, e-ink!")
```

## CLI

```bash
inkwell devices list
inkwell todos list --status pending
inkwell display text 20:6E:F1:B5:9E:0C "Hello"
```

## API Docs

See [docs/api-reference.md](docs/api-reference.md) for the full HTTP reference.
