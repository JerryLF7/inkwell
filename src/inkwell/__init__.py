"""inkwell - Python SDK for Zectrix e-ink cloud platform."""

from .canvas import render_centered_text, render_text_block
from .client import ZectrixClient

__all__ = ["ZectrixClient", "render_centered_text", "render_text_block"]
__version__ = "0.1.0"
