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

import sys
import traceback


def main():
    print("🧬 Bootstrapping Aetherra OS Kernel...")
    try:
        from aetherra_core.system import AetherraRuntime

        runtime = AetherraRuntime()
        runtime.launch()
        print("✅ Aetherra Kernel launched successfully.")
    except ImportError as e:
        print(f"❌ Could not import AetherraRuntime: {e}")
        print("🧪 Running fallback integration test...")
        try:
            # Lightweight integration test
            from aetherra_core.memory import MemorySystem
            from aetherra_core.plugins import PluginManager
            from lyrixa.interface import LyrixaInterface

            memory = MemorySystem()
            plugins = PluginManager()
            interface = LyrixaInterface()

            assert memory.is_ready()
            assert plugins.discover_plugins()
            assert interface.mount()

            print(
                "✅ Fallback integration test passed: All core modules are mountable."
            )
        except Exception as test_exc:
            print("❌ Fallback integration test failed.")
            traceback.print_exc()
            sys.exit(1)
    except Exception as exc:
        print("❌ Unexpected error during bootstrap.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
