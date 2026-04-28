from datetime import datetime
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "token_dashboard.py"
spec = importlib.util.spec_from_file_location("token_dashboard", MODULE_PATH)
token_dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(token_dashboard)


def test_format_push_time_uses_24_hour_clock():
    assert token_dashboard.format_push_time(datetime(2026, 4, 28, 7, 5)) == "07:05"
    assert token_dashboard.format_push_time(datetime(2026, 4, 28, 19, 47)) == "19:47"
