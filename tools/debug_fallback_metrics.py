import os
import re
import time

import requests

from aetherra_hub.compat import start_hub_server

port = 3040
# Ensure AI disabled
os.environ["AETHERRA_AI_API_ENABLED"] = "0"
os.environ["AETHERRA_AI_API_STREAM"] = "0"

s = start_hub_server(port=port)
assert s.is_running()


def get_val():
    txt = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
    m = re.search(
        r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)', txt
    )
    return float(m.group(1)) if m else -1


base = get_val()
print("BASE", base)
resp = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
)
print("POST status", resp.status_code)
# brief delay
for i in range(5):
    time.sleep(0.05)
    after = get_val()
    print("AFTER try", i, after)
print("DONE")
