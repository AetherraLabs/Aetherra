import asyncio
import json
import os
import time

import requests

from aetherra_hub.compat import start_hub_server
from aetherra_service_registry import get_service_registry

PORT = 3012
BASE = f"http://localhost:{PORT}"
STREAM = f"{BASE}/api/ai/stream"


def main():
    os.environ["AETHERRA_AI_API_ENABLED"] = "1"
    os.environ["AETHERRA_AI_API_STREAM"] = "1"
    os.environ["AETHERRA_AI_API_REQUIRE_TOKEN"] = "0"
    os.environ["AETHERRA_RETRY_AFTER_SEC"] = "1"
    start_hub_server(PORT)

    class RateLimitedEngine:
        async def process_message(self, msg: str, ctx: dict | None = None):
            raise Exception("Rate limit: tokens exhausted")

    async def reg(e):
        reg = await get_service_registry()
        await reg.register_service("aetherra_engine", e)

    asyncio.run(reg(RateLimitedEngine()))
    with requests.post(
        STREAM, json={"message": "limit then resume"}, stream=True, timeout=10
    ) as r:
        print("status", r.status_code)
        for chunk in r.iter_lines(decode_unicode=True):
            if not chunk:
                print("--")
                continue
            print(chunk)


if __name__ == "__main__":
    main()
