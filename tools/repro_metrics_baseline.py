#!/usr/bin/env python3
# Debug helper: print fallback mock metric before and after a chat call
import re
import time

import requests

from aetherra_hub_server import start_hub_server


def get_metric_line(text: str, name: str) -> str | None:
    for line in text.splitlines():
        if name in line:
            return line
    return None


def parse_value(text: str, pattern: str, default: float = 0.0) -> float:
    m = re.search(pattern, text)
    if not m:
        return default
    try:
        return float(m.group(1))
    except Exception:
        return default


def main():
    port = 3018
    srv = start_hub_server(port=port)
    print(f"server running: {srv.is_running()} on {port}")
    time.sleep(0.2)
    txt0 = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
    print("--- METRICS (first 25 lines) ---")
    for i, line in enumerate(txt0.splitlines()[:25], 1):
        print(f"{i:02d}: {line}")
    line0 = get_metric_line(txt0, 'aetherra_chat_fallback_total{path="mock"}')
    print("BASELINE line:", line0)
    base = parse_value(
        txt0, r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?\d*\.?\d+)'
    )
    print("BASELINE value:", base)
    r = requests.post(
        f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
    )
    print("chat status:", r.status_code)
    txt1 = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
    line1 = get_metric_line(txt1, 'aetherra_chat_fallback_total{path="mock"}')
    print("AFTER line:", line1)
    after = parse_value(
        txt1, r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?\d*\.?\d+)'
    )
    print("AFTER value:", after)


if __name__ == "__main__":
    main()
