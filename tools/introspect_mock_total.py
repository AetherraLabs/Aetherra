# Third party imports
import requests

# Aetherra imports
import aetherra_hub.compat as hs

port = 3052
s = hs.start_hub_server(port=port)
print("running", s.is_running())
print("mock_total initial", s.chat_metrics.get("fallback_mock_total"))
print(
    "GET metrics:",
    requests.get(f"http://localhost:{port}/metrics", timeout=5).status_code,
)
print("mock_total after first metrics", s.chat_metrics.get("fallback_mock_total"))
resp = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
)
print("POST status", resp.status_code)
print("mock_total after post", s.chat_metrics.get("fallback_mock_total"))
line = [
    line_text
    for line_text in requests.get(
        f"http://localhost:{port}/metrics", timeout=5
    ).text.splitlines()
    if 'aetherra_chat_fallback_total{path="mock"}' in line_text
][0]
print("metrics mock line:", line)
