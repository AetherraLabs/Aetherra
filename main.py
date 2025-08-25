"""
🧬 Aetherra OS Bootstrapper

- Initializes the Aetherra Kernel
- Connects Lyrixa as the interface
- Mounts memory systems, plugin manager, and agents
- Starts event loop or runtime controller

🖥️ Developer Entry Point
- Local dev launch script
- Useful for testing modular integrations without launching the full GUI

🧪 Fallback Integration Test
- Runs a lightweight version of the OS to ensure modular connections are stable

🗺️ Debug Sandbox
- Historically used for rapid testing before modules were mature
"""

import asyncio
import sys
import traceback


def main():
    print("🧬 Bootstrapping Aetherra OS Kernel...")
    try:
        # Prefer the canonical OS launcher when available
        from aetherra_os_launcher import AetherraOSLauncher

        asyncio.run(AetherraOSLauncher().launch_full_os({"quiet": True}))
        print("✅ Aetherra OS launched via canonical launcher.")
    except Exception as e:
        print(f"⚠️ OS launcher not available or failed: {e}")
        print("🧪 Running fallback integration test...")
        try:
            # Lightweight integration test using canonical modules
            from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
                AetherraMemoryEngine as MemorySystem,
            )
            from Aetherra.aetherra_core.plugins.plugin_manager import PluginManager

            memory = MemorySystem()
            plugins = PluginManager()

            # Basic sanity checks
            assert hasattr(memory, "store"), "Memory system not functional"
            discovered = plugins.discover_plugins()
            assert isinstance(discovered, list)

            print(
                "✅ Fallback integration test passed: Core memory and plugins are usable."
            )
        except Exception:
            print("❌ Fallback integration test failed.")
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
