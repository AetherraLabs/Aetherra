"""
Launch utilities for Lyrixa
"""

import os
import subprocess
import sys
import time
import socket
from pathlib import Path


def check_port_available(port):
    """Check if a port is available for connection"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0  # 0 means connection successful (port in use)
    except:
        return False


def wait_for_api_server(port=8007, timeout=60):
    """Wait for the API server to be ready before proceeding (increased timeout)"""
    print(f">> Waiting for API server on port {port}...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if check_port_available(port):
            print(">> API server is ready!")
            return True
        time.sleep(1)

    print(f">> API server not ready after {timeout} seconds")
    return False


def run_self_improvement_api():
    """Start the enhanced API server in the background"""
    try:
        # Get the project root directory
        project_root = Path(
            __file__
        ).parent.parent.parent  # Go up from utils to Aetherra Project
        api_script = project_root / "run_self_improvement_api.py"

        if api_script.exists():
            print(">> Starting Enhanced Lyrixa API server...")
            print(f"   Script: {api_script}")

            # Check if port is already in use
            if check_port_available(8007):
                print(">> Port 8007 already in use - server may already be running")
                return True

            # Create log file for debugging
            log_file = project_root / "api_server_startup.log"

            # Start the API server in background with logging
            with open(log_file, "w") as log:
                process = subprocess.Popen(
                    [sys.executable, str(api_script)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    if os.name == "nt"
                    else 0,
                    cwd=str(project_root)  # Set working directory
                )

                print(f"   Server process started (PID: {process.pid})")
                print(f"   Logs: {log_file}")

            # Wait for server to be ready
            if wait_for_api_server():
                print(">> Enhanced API server started and ready")
                return True
            else:
                print(">> API server failed to start properly")
                # Show recent log entries for debugging
                if log_file.exists():
                    print("Recent log entries:")
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                        for line in lines[-10:]:  # Show last 10 lines
                            print(f"   {line.strip()}")
                return False
        else:
            print(f">> API script not found at {api_script}")
            return False

    except Exception as e:
        print(f">> Failed to start API server: {e}")
        import traceback
        traceback.print_exc()
        return False


def setup_environment():
    """Setup the environment for Lyrixa"""
    # Add project paths to Python path if needed
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Set up any environment variables if needed
    os.environ.setdefault("LYRIXA_ENV", "development")


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")

    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")

    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")

    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install them using: pip install " + " ".join(missing_deps))
        return False

    return True
