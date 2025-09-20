# Standard library imports
import sys
import time
import types

# Third party imports
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server


class _FakeService:
    async def handle_message(self, message_type, payload):
        return {
            "text": "Applied analysis",
            "suggestions": [
                {
                    "title": "Resolve merge conflict markers",
                    "file": "tests/tmp_conflict.py",
                    "action": "remove_conflict_markers",
                }
            ],
            "applied_changes": [],
        }


class _FakeRegistry:
    def get_service(self, name):
        return _FakeService() if name == "lyrixa_chat" else None


fake_mod = types.ModuleType("aetherra_service_registry")


async def get_service_registry():
    return _FakeRegistry()


fake_mod.get_service_registry = get_service_registry  # type: ignore
sys.modules["aetherra_service_registry"] = fake_mod

port = 5014
s = start_hub_server(port=port)
print("running", s.is_running())
# small wait for server
for _ in range(20):
    try:
        r = requests.get(f"http://localhost:{port}/metrics", timeout=1)
        if r.status_code == 200:
            break
    except Exception:
        time.sleep(0.05)

resp = requests.post(
    f"http://localhost:{port}/api/lyrixa/chat",
    json={"message": "please fix conflicts", "allow_edits": False},
    timeout=5,
)
print("status", resp.status_code)
print("json", resp.json())
