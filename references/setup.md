# Setup Guide

## Installation

inkwell is pre-installed in the Hermes venv. To reinstall:

```bash
~/.hermes/hermes-agent/venv/bin/pip3 install -e ~/.hermes/skills/creative/inkwell
```

## Dependencies

Python: `httpx`, `python-dotenv`, `Pillow`

System fonts (for CJK support):
```bash
sudo apt install fonts-noto-cjk fonts-wqy-zenhei -y
```

## Environment

Copy `.env.example` to `.env` and fill in your Zectrix API key:
```bash
ZECTRIX_API_KEY=zt_480...
ZECTRIX_DEVICE_ID=20:6E:F1:B5:9E:0C
```

The CLI auto-loads `.env` via `python-dotenv`. For scripts, call `load_dotenv()` first.

## Verify

```bash
inkwell devices list
```

Should show your device MAC and model.
