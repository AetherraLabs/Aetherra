#!/usr/bin/env python3
"""
🚀 AETHERRA OS - HYBRID INTERFACE LAUNCHER
==========================================

Launches the main Aetherra Operating System interface - a hybrid PySide6 + Web dashboard
that provides real-time monitoring and control of all OS components.

This is the PRIMARY interface to Aetherra OS:
- Native Python performance and OS integration
- Beautiful web-based panels for complex visualizations
- Real-time monitoring of system, memory, agents, and cognitive state
- Live dashboard with cyberpunk aesthetics

Usage:
    python launch_aetherra_os.py

Requirements:
    - PySide6 (for native desktop interface)
    - Web browser engine (QtWebEngine)
    - Aetherra OS components
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []

    try:
        import PySide6
        print("✅ PySide6 available")
    except ImportError:
        missing_deps.append("PySide6")
        print("❌ PySide6 not installed")

    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("✅ QtWebEngine available")
    except ImportError:
        missing_deps.append("QtWebEngine")
        print("❌ QtWebEngine not available")

    if missing_deps:
        print(f"\n[TOOL] Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install PySide6")
        return False

    return True

def setup_environment():
    """Setup environment for Aetherra OS"""
    print("[TOOL] Setting up Aetherra OS environment...")

    # Add project root to Python path (go up two levels from interface dir)
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Set environment variables
    os.environ['AETHERRA_OS_MODE'] = 'hybrid_interface'
    os.environ['AETHERRA_INTERFACE_TYPE'] = 'native_web_hybrid'

    print("✅ Environment configured")

def check_os_status():
    """Check if Aetherra OS is running"""
    print("🔍 Checking Aetherra OS status...")

    try:
        # Try to import and check OS components
        from aetherra_service_registry import get_service_registry
        from aetherra_kernel_loop import get_kernel

        # Check if kernel is running
        kernel = get_kernel()
        if kernel.running:
            print("✅ Aetherra OS kernel is running")
            return True
        else:
            print("[WARN] Aetherra OS kernel is not running")
            return False

    except ImportError:
        print("❌ Aetherra OS core components not available")
        return False
    except Exception as e:
        print(f"❌ Error checking OS status: {e}")
        return False

def start_aetherra_os():
    """Start the Aetherra Operating System"""
    print("🚀 Starting Aetherra AI Operating System...")

    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent
        os_launcher_path = project_root / "aetherra_os_launcher.py"

        if os_launcher_path.exists():
            print("📍 Found OS launcher, starting Aetherra OS...")

            # Import and run the OS launcher
            import asyncio
            import sys

            # Add to path if needed
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            from aetherra_os_launcher import AetherraOSLauncher

            # Create and start OS launcher in background
            async def start_os_background():
                launcher = AetherraOSLauncher()
                await launcher.launch_full_os({'gui_enabled': False})  # Start without GUI

            # Run OS startup in background thread
            import threading

            def run_os():
                asyncio.run(start_os_background())

            os_thread = threading.Thread(target=run_os, daemon=True)
            os_thread.start()

            # Give OS time to start
            print("⏳ Waiting for OS to initialize...")
            import time
            time.sleep(3)

            print("✅ Aetherra OS startup initiated")
            return True

        else:
            print("❌ OS launcher not found at expected location")
            return False

    except Exception as e:
        print(f"❌ Failed to start Aetherra OS: {e}")
        return False

def launch_interface():
    """Launch the Aetherra OS hybrid interface"""
    print("🚀 Launching Aetherra OS Hybrid Interface...")

    try:
        # Import and run the main interface
        from Aetherra.interface.main_window import main

        print("🖥️ Starting hybrid PySide6 + Web interface...")
        print("📡 Embedded web server will start automatically")
        print("🌐 Dashboard panels loading...")
        print("🤖 Connected to running Aetherra OS")
        print("\n" + "="*50)
        print("🤖 AETHERRA AI OPERATING SYSTEM")
        print("   Live Dashboard Interface")
        print("   Connected to OS Kernel")
        print("="*50)

        # Run the application
        exit_code = main()

        print(f"\n👋 Aetherra OS interface closed (exit code: {exit_code})")
        return exit_code

    except ImportError as e:
        print(f"❌ Failed to import Aetherra interface: {e}")
        print("[TOOL] Make sure Aetherra OS components are properly installed")
        return 1
    except Exception as e:
        print(f"❌ Failed to launch interface: {e}")
        return 1

def main():
    """Main launcher function"""
    print("🤖 AETHERRA AI OPERATING SYSTEM")
    print("🖥️ HYBRID INTERFACE LAUNCHER")
    print("=" * 40)

    # Check dependencies
    if not check_dependencies():
        print("\n💡 To install dependencies:")
        print("   pip install PySide6")
        return 1

    # Setup environment
    setup_environment()

    # Check if OS is running, start if needed
    if not check_os_status():
        print("\n[TOOL] Aetherra OS not detected - starting OS first...")
        if not start_aetherra_os():
            print("❌ Failed to start Aetherra OS")
            print("💡 Try running manually: python aetherra_os_launcher.py")
            return 1

        # Check again after starting
        import time
        time.sleep(2)
        if not check_os_status():
            print("[WARN] OS may still be starting up - continuing with interface launch")

    # Launch interface
    exit_code = launch_interface()

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
