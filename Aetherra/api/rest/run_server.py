# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors


# Standard library imports
# Clean Architecture Imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


#!/usr/bin/env python3
"""
Aetherra API Server Launcher
============================

Startup script for the Aetherra .aether Script Execution API.
"""


# Standard library imports
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for the API server"""
    try:
        # Third party imports
        import uvicorn

        # Aetherra imports
        from Aetherra.api.aether_server import app

        print("🚀 Starting Aetherra Script Execution API...")
        print("📍 API Documentation: http://localhost:8000/docs")
        print("🔍 API Explorer: http://localhost:8000/redoc")
        print("💚 Health Check: http://localhost:8000/health")
        print()

        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
        )

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("[DISC] Install dependencies with: pip install -r Aetherra/api/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
