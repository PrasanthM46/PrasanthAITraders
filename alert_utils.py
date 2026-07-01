import json
from pathlib import Path

ALERT_FILE = Path("latest_webhook.json")


def load_latest_alert():
    if not ALERT_FILE.exists():
        return None
    try:
        with ALERT_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None
