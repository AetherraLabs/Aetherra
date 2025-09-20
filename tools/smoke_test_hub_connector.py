#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quick smoke test for Aetherra Hub Connector and Hub Server integration.

Steps:
- Start the Hub server in-process (Flask thread)
- Register a sample plugin on the Hub
- Use AetherraHubConnector to connect and fetch available plugins
- Print results and exit
"""

# Standard library imports
import asyncio
import json
import os
import sys
from pathlib import Path

# Aetherra imports
from Aetherra.lyrixa.integrations.aetherra_hub_connector import (
    hub_connector,
    os_detector,
)
from aetherra_hub.compat import start_hub_server

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def main():
    # Ensure ports are as expected
    os.environ.setdefault("AETHERRA_HUB_HOST", "localhost")
    os.environ.setdefault("AETHERRA_HUB_PORT", "3001")
    os.environ.setdefault("AETHERRA_HUB_WS_PORT", "3002")

    # Start hub server
    server = start_hub_server(port=int(os.environ.get("AETHERRA_HUB_PORT", "3001")))

    # Register a sample plugin directly
    server.register_plugin(
        {
            "name": "workflow_builder_plugin",
            "version": "1.0.0",
            "description": "Drag-and-drop workflow authoring",
            "type": "workflow",
        }
    )

    # Detect hub/OS
    detect = await os_detector.detect_aetherra_os()
    print("[SMOKE] OS detect:", json.dumps(detect))

    # Connect and list plugins
    ok = await hub_connector.connect()
    print("[SMOKE] hub connect:", ok)

    plugins = await hub_connector.get_available_plugins()
    print("[SMOKE] plugins:", json.dumps(plugins))

    await hub_connector.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
