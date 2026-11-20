"""Child-process harness for the normal full launcher and Hub chat endpoint.

Only text generation is replaced. Synthetic prompts/provider inputs are written
to the explicitly requested test artifact, never to ordinary application logs.
"""
from __future__ import annotations

import ast
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace


class ContextResponder:
    """Offline generator: quote supplied evidence, without an answer/record oracle."""

    primary_provider = SimpleNamespace(value="deterministic")

    def __init__(self):
        self.prompts = []

    def list_available_models(self):
        return {"context-responder": {"provider": "deterministic"}}

    def set_model(self, name):
        return name == "context-responder"

    def get_current_model_info(self):
        return {"provider": "deterministic", "model": "context-responder"}

    async def generate_response(self, prompt):
        self.prompts.append(prompt)
        # Accept both the original prompt and the evidence envelope introduced
        # by the fix. No saved answers or previous turns are available here.
        records = []
        for line in prompt.splitlines():
            if line.startswith("- "):
                try:
                    item = ast.literal_eval(line[2:])
                    content = item.get("content", item)
                    if isinstance(content, str) and content.startswith("{"):
                        content = json.loads(content)
                    if isinstance(content, dict):
                        content = content.get("content", "")
                    if content:
                        records.append(str(content))
                except (ValueError, SyntaxError, AttributeError):
                    pass
        query = prompt.split("User: ", 1)[-1].split("\n", 1)[0]
        if "?" not in query:
            return "I'll keep that in mind."
        # A generator must not fill a missing attribute from another fact.
        attribute = re.search(r"what (color|colour|date|age)\b", query, re.I)
        if attribute and not any(attribute[1].lower() in r.lower() for r in records):
            return "I don't know that detail yet. You haven't told me."
        if records:
            return "You told me: " + records[0]
        return "I don't have that in my memories yet."

    async def close(self, **kwargs):
        return {"ok": True}


async def run(request_path, result_path, *, live=False):
    # No outbound networking, even if an optional startup component tries it.
    def offline(event, args):
        if event in {"socket.connect", "socket.bind"}:
            address = args[1]
            if not isinstance(address, tuple) or address[0] not in {
                "127.0.0.1",
                "::1",
                "localhost",
            }:
                raise PermissionError("continuity_test_external_network_denied")
        if event == "socket.getaddrinfo" and args[0] not in {
            "127.0.0.1",
            "::1",
            "localhost",
            b"localhost",
        }:
            raise PermissionError("continuity_test_external_dns_denied")
        if event == "subprocess.Popen":
            raise PermissionError("continuity_test_subprocess_denied")

    if not live:
        sys.addaudithook(offline)
    from unittest.mock import patch

    responder = ContextResponder()
    if live:
        from Aetherra.core.multi_llm_manager import MultiLLMManager

        generate = MultiLLMManager.generate_response

        async def observed_generate(manager, prompt, **kwargs):
            responder.prompts.append(prompt)
            return await generate(manager, prompt, **kwargs)

        generation = patch.object(
            MultiLLMManager, "generate_response", observed_generate
        )
    else:
        generation = patch(
            "Aetherra.core.multi_llm_manager.get_llm_manager", return_value=responder
        )
    with generation:
        from aetherra_os_launcher import AetherraOSLauncher

        launcher = AetherraOSLauncher()
        task = asyncio.create_task(
            launcher.launch_full_os(
                {
                    "mode": "full",
                    "presence_enabled": False,
                    "gui_enabled": False,
                    "hub_enabled": True,
                    "hmr_enabled": False,
                    "engine_text_statistics_enabled": False,
                }
            )
        )
        result = {
            "pid": os.getpid(),
            "responder": "configured-live-model"
            if live
            else "deterministic-context-responder",
            "turns": [],
        }
        try:
            async with asyncio.timeout(120):
                while not launcher.running:
                    if task.done():
                        await task
                        raise RuntimeError("launcher_stopped_before_ready")
                    await asyncio.sleep(0.1)
            engine = launcher.systems["aetherra"].impl
            # The launcher sends its own diagnostic greeting. Begin a new user
            # session through the existing API; do not replay any prior turns.
            await engine.start_conversation()
            result["initial_session_id"] = engine.session_id
            result["initial_message_count"] = engine.conversation_context.get(
                "message_count", 0
            )
            result["readiness"] = launcher.readiness_report
            import aiohttp

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=90)
            ) as client:
                for message in json.loads(request_path.read_text(encoding="utf-8")):
                    before = len(responder.prompts)
                    async with client.post(
                        os.environ["AETHERRA_HUB_URL"] + "/api/ai/ask",
                        json={"message": message, "scratchpad_policy": "ephemeral"},
                        headers={"X-Aetherra-Token": "synthetic-continuity-token"},
                    ) as reply:
                        result["turns"].append(
                            {
                                "status": reply.status,
                                "body": await reply.json(),
                                "provider_prompts": [
                                    p
                                    for p in responder.prompts[before:]
                                    if f"User: {message}\n" in p
                                ],
                            }
                        )
        finally:
            launcher.running = False
            await asyncio.wait_for(launcher._graceful_shutdown(), 30)
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            result["stopped"] = not launcher.running
            result_path.write_text(
                json.dumps(result, indent=2, default=str), encoding="utf-8"
            )


if __name__ == "__main__":
    asyncio.run(
        run(Path(sys.argv[1]), Path(sys.argv[2]), live="--live" in sys.argv[3:])
    )
