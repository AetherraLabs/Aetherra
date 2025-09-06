#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test script to install multiple plugins and test the workflow
"""

import asyncio
import sys
from pathlib import Path

# Add the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from test_plugin_installation import PluginInstaller


async def test_multiple_plugin_installation():
    """Test installing multiple plugins"""
    installer = PluginInstaller()

    print("🧪 Testing Multiple Plugin Installation")
    print("=" * 50)

    # Show current state
    print("\n1. Current installed plugins:")
    await installer.list_installed_plugins()

    # Install another plugin
    print("\n2. Installing 'context_aware_surfacing' plugin:")
    success1 = await installer.install_plugin_from_hub("context_aware_surfacing")

    print("\n3. Installing 'introspector_plugin' plugin:")
    success2 = await installer.install_plugin_from_hub("introspector_plugin")

    if success1 or success2:
        print("\n4. Final installed plugins list:")
        await installer.list_installed_plugins()

    return success1 and success2


if __name__ == "__main__":
    asyncio.run(test_multiple_plugin_installation())
