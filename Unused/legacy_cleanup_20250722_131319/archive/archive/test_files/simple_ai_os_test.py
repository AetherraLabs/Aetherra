#!/usr/bin/env python3
"""
🚀 SIMPLE AI OS KERNEL TEST
===========================

Direct test of the Aether Runtime without complex dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def safe_print(message: str) -> None:
    """Safe print function that handles Unicode encoding issues on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        safe_message = message.encode("ascii", "ignore").decode("ascii")
        print(
            safe_message.replace("🚀", "[*]").replace("✅", "[OK]").replace("❌", "[X]")
        )


def main():
    """Test the Aether Runtime directly"""
    safe_print("🚀 SIMPLE AI OS KERNEL TEST")
    safe_print("=" * 40)

    try:
        # Import Aether Runtime
        from Aetherra.runtime.aether_runtime import AetherRuntime

        safe_print("✅ AetherRuntime imported successfully")

        # Initialize runtime
        runtime = AetherRuntime()
        safe_print("✅ AetherRuntime initialized")

        # Test basic commands
        safe_print("\n🎯 Testing basic commands:")

        test_commands = [
            'goal "test goal"',
            '$test_var = "hello"',
            "show variables",
            "status",
        ]

        for cmd in test_commands:
            safe_print(f"   → {cmd}")
            try:
                runtime.interpret_command(cmd)
                safe_print("     ✅ Command executed")
            except Exception as e:
                safe_print(f"     ❌ Error: {e}")

        # Test script execution
        safe_print("\n🎯 Testing script execution:")
        test_script = """goal "script test"
$script_var = "working"
show variables"""

        try:
            runtime.execute_goal(test_script)
            safe_print("✅ Script execution successful")
        except Exception as e:
            safe_print(f"❌ Script execution failed: {e}")

        # Test goal queue
        safe_print("\n🎯 Testing goal queue:")
        try:
            runtime.queue_goal('goal "queued test"')
            runtime.queue_goal('$queued_var = "test"')
            safe_print(f"✅ Queued 2 goals")

            processed = runtime.process_goal_queue()
            safe_print(f"✅ Processed {processed} goals")
        except Exception as e:
            safe_print(f"❌ Goal queue test failed: {e}")

        # Test bootstrap loading
        safe_print("\n🎯 Testing bootstrap script:")
        bootstrap_path = project_root / "bootstrap.aether"
        if bootstrap_path.exists():
            try:
                runtime.load_script(str(bootstrap_path), from_file=True)
                safe_print(f"✅ Bootstrap loaded: {len(runtime.script_lines)} commands")
            except Exception as e:
                safe_print(f"❌ Bootstrap loading failed: {e}")
        else:
            safe_print("❌ bootstrap.aether not found")

        # Final status
        safe_print("\n📊 Final Status:")
        stats = runtime.get_execution_stats()
        safe_print(f"   Goals completed: {stats['goals_completed']}")
        safe_print(f"   Variables set: {stats['variables_set']}")
        safe_print(f"   Goals defined: {stats['goals_defined']}")

        safe_print("\n🎉 AI OS KERNEL BASIC TEST COMPLETED!")

    except ImportError as e:
        safe_print(f"❌ Import failed: {e}")
        safe_print("   Check that Aetherra.runtime.aether_runtime exists")
    except Exception as e:
        safe_print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main()
