#!/usr/bin/env python3
"""
Lyrixa Self-Improvement Dashboard API - Redirect to Enhanced Server

This script redirects to the working enhanced_api_server.py which has all
the latest features including:
- Plugin Intelligence API
- Meta-Reasoning Engine API
- Goals Forecasting API
- Plugin Editor Integration API

This redirect fixes import issues and provides a unified entry point.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("🔄 Lyrixa Self-Improvement Dashboard API")
    print("   Redirecting to Enhanced API Server...")
    print()

    # Check if enhanced server is available
    enhanced_server_path = project_root / "enhanced_api_server.py"

    if enhanced_server_path.exists():
        print("✅ Enhanced API Server found")
        print("🚀 Starting Enhanced Lyrixa API Server...")
        print("   • Plugin Intelligence API")
        print("   • Meta-Reasoning Engine API")
        print("   • Goals Forecasting API")
        print("   • Plugin Editor Integration API")
        print("   • Server running on http://127.0.0.1:8007")
        print()

        # Import and run the enhanced server
        try:
            # Change to project root directory for imports
            os.chdir(str(project_root))

            # Import the enhanced server app
            from enhanced_api_server import app

            # Start the server
            import uvicorn
            uvicorn.run(app, host="127.0.0.1", port=8007, log_level="info")

        except Exception as e:
            print(f"❌ Failed to start enhanced server: {e}")
            print("\n💡 Alternative: Run directly with:")
            print("   python enhanced_api_server.py")
            sys.exit(1)
    else:
        print("❌ Enhanced API Server not found")
        print(f"   Expected at: {enhanced_server_path}")
        print("\n💡 Please ensure enhanced_api_server.py exists in the project root")
        sys.exit(1)

if __name__ == "__main__":
    main()
