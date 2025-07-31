# Minimal system_logger for Aetherra
# Logs to console and to a file in the system directory
import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "system_log.txt"


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
