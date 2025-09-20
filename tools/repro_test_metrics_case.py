# Standard library imports
import os
import re
import time

# Third party imports
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server

port = 3018
# Clear env
os.environ["AETHERRA_AI_API_ENABLED"] = "0"
os.environ["AETHERRA_AI_API_STREAM"] = "0"

s = start_hub_server(port=port)
print("running", s.is_running())


def val():
    txt = requests.get(f"http://localhost:{port}/metrics", timeout=5).text
    m = re.search(
        r'aetherra_chat_fallback_total\{path="mock"\} ([-+]?[0-9]*\.?[0-9]+)', txt
    )
    print("LINE:", m.group(0) if m else "no match")
    return float(m.group(1)) if m else -1


base = val()
print("base", base)
r = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat", json={"message": "hi"}, timeout=5
)
print("post status", r.status_code)
after = val()
print("after", after)
