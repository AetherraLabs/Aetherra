import time

import requests

import aetherra_hub.compat as hs

port = 3050
s = hs.start_hub_server(port=port)
print("running", s.is_running())
print("initial mock count", s.chat_metrics.get("fallback_path_counts", {}).get("mock"))
print(
    "GET metrics:",
    requests.get(f"http://localhost:{port}/metrics", timeout=5).status_code,
)
print(
    "baseline mock count (internal)",
    s.chat_metrics.get("fallback_path_counts", {}).get("mock"),
)
resp = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
)
print("POST status", resp.status_code)
print("mock after internal", s.chat_metrics.get("fallback_path_counts", {}).get("mock"))
line = [
    l
    for l in requests.get(
        f"http://localhost:{port}/metrics", timeout=5
    ).text.splitlines()
    if 'aetherra_chat_fallback_total{path="mock"}' in l
][0]
print("metrics mock line:", line)
