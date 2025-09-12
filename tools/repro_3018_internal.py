import os
import re
import time

import requests

import aetherra_hub.compat as hs

port = 3018
os.environ["AETHERRA_AI_API_ENABLED"] = "0"
os.environ["AETHERRA_AI_API_STREAM"] = "0"

s = hs.start_hub_server(port=port)
print("running", s.is_running())
print("internal mock_total before metrics", s.chat_metrics.get("fallback_mock_total"))
txt = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
m = re.search(
    r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)', txt
)
print("metrics baseline line", m.group(0) if m else "missing")
print("internal mock_total after metrics", s.chat_metrics.get("fallback_mock_total"))
r = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
)
print("POST status", r.status_code)
print("internal mock_total after POST", s.chat_metrics.get("fallback_mock_total"))
txt2 = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
m2 = re.search(
    r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)', txt2
)
print("metrics after line", m2.group(0) if m2 else "missing")
