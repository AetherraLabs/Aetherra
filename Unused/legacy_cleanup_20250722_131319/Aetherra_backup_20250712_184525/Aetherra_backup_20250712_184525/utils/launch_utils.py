"""
Launch utilities for Lyrixa
"""

import os
import subprocess
import sys
from pathlib import Path


def run_self_improvement_api():
    """Start the self-improvement API server in the background"""
    try:
        # Get the project root directory
        project_root = Path(
            __file__
        ).parent.parent.parent  # Go up from utils to Aetherra Project
        api_script = project_root / "run_self_improvement_api.py"

        if api_script.exists():
            print("🚀 Starting self-improvement API server...")
            # Start the API server in background
            subprocess.Popen(
                [sys.executable, str(api_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                if os.name == "nt"
                else 0,
            )
            print("✅ API server started in background")
        else:
            print(f"⚠️ API script not found at {api_script}")

    except Exception as e:
        print(f"❌ Failed to start API server: {e}")


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
