#!/usr/bin/env python3
"""
🌌 AETHERRA WITH LYRIXA AI ASSISTANT
===================================

The complete Aetherra development environment with Lyrixa AI Assistant integration.
Launch intelligent coding, natural language workflows, and .aether development.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def launch_lyrixa():
    """Launch Lyrixa AI Assistant"""
    try:
        # Import from the modularized lyrixa package
        from lyrixa.launcher import main as lyrixa_main

        print("🎙️ Starting Lyrixa AI Assistant...")
        asyncio.run(lyrixa_main())

    except ImportError as e:
        print(f"❌ Failed to import modularized Lyrixa: {e}")
        print("The Lyrixa system may need to be rebuilt.")
        print("Please check the lyrixa/ directory structure.")
    except Exception as e:
        print(f"❌ Error launching Lyrixa: {e}")


def test_lyrixa():
    """Test Lyrixa AI Assistant"""
    try:
        print("🧪 Running Lyrixa GUI tests...")

        # Run the test_gui.py script
        import subprocess
        import sys

        test_file = Path(__file__).parent / "testing" / "test_gui.py"
        result = subprocess.run(
            [sys.executable, str(test_file)], capture_output=True, text=True
        )

        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Warnings: {result.stderr}")

        if result.returncode == 0:
            print("✅ Tests completed successfully")
        else:
            print(f"❌ Tests failed with return code {result.returncode}")

    except Exception as e:
        print(f"❌ Error running tests: {e}")


def launch_aetherra():
    """Launch Aetherra UI"""
    try:
        # Try to launch the enhanced Lyrixa GUI
        from src.aetherra.ui.enhanced_lyrixa import main as enhanced_main

        enhanced_main()
    except ImportError:
        try:
            # Fallback to desktop app
            from lyrixa_desktop import main as desktop_main

            desktop_main()
        except ImportError as e:
            print(f"❌ Failed to launch Aetherra UI: {e}")
    except Exception as e:
        print(f"❌ Error launching Aetherra UI: {e}")


def show_status():
    """Show system status"""
    print("\n📊 SYSTEM STATUS")
    print("=" * 30)

    # Check Python version
    print(f"🐍 Python: {sys.version.split()[0]}")

    # Check key components
    components = [
        ("Lyrixa Core", "lyrixa.launcher"),
        ("Aetherra UI", "src.aetherra.ui.enhanced_lyrixa"),
        ("Testing", "testing.test_gui"),
        ("Desktop App", "lyrixa_desktop"),
    ]

    for name, module in components:
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Not available")

    print()


def main():
    """Launch Aetherra with Lyrixa integration"""
    print("🌌 AETHERRA WITH LYRIXA AI ASSISTANT")
    print("=" * 50)
    print("Welcome to the intelligent development environment!")
    print()

    print("Available options:")
    print("1. Launch Lyrixa AI Assistant (Interactive)")
    print("2. Test Lyrixa AI Assistant")
    print("3. Launch Aetherra UI")
    print("4. Show System Status")
    print("5. Exit")
    print()

    while True:
        try:
            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                print("\n🎙️ Launching Lyrixa AI Assistant...")
                launch_lyrixa()
                break
            elif choice == "2":
                print("\n🧪 Testing Lyrixa AI Assistant...")
                test_lyrixa()
                break
            elif choice == "3":
                print("\n🌌 Launching Aetherra UI...")
                launch_aetherra()
                break
            elif choice == "4":
                show_status()
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            break


if __name__ == "__main__":
    main()
