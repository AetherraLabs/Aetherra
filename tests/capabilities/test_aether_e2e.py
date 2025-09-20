# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
from pathlib import Path

# Aetherra imports
from aetherra_script_service import get_aether_script_service


def test_aether_script_end_to_end(tmp_path: Path):
    async def _run():
        # Prepare a simple .aether script
        script = "\n".join(
            [
                'goal "analyze sample data"',
                'remember "weekly insights alpha" as "weekly_insights"',
                "x = 42",
            ]
        )
        script_file = tmp_path / "insights.aether"
        script_file.write_text(script, encoding="utf-8")

        # Start service
        svc = await get_aether_script_service(None)
        await svc.start()

        # Execute
        result = await svc.execute_script_file(str(script_file))
        assert result["success"] is True
        outputs = result["result"]["results"]

        # Verify parsed steps
        assert any(r.get("type") == "goal" for r in outputs)
        assert any(r.get("type") == "remember" for r in outputs)
        assert any(r.get("type") == "assignment" for r in outputs)

        # Verify memory persistence if engine available
        mem = svc.get_memory_engine()
        if mem is not None:
            recalled = mem.retrieve("weekly insights")
            assert isinstance(recalled, list)
            assert any("weekly insights" in r.get("content", "") for r in recalled)

        await svc.stop()

    asyncio.run(_run())
