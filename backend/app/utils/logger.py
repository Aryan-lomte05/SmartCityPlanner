import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("backend/logs/system_events.jsonl")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_console(msg: str, level: str = "INFO"):
    """Print timestamped message to console."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}")

def log_event(event: dict):
    """Write structured event to JSONL file."""
    event["timestamp"] = datetime.now().isoformat()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def clear_logs():
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        log_console("Cleared all previous logs.", "SYSTEM")
