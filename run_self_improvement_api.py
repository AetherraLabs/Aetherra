#!/usr/bin/env python3
"""
Run the Enhanced Lyrixa API server with complete plugin intelligence and meta-reasoning.
Updated to use the fast_api_server for quick startup, with fallback to enhanced server.
"""

import uvicorn
import os

if __name__ == "__main__":
    print("Starting Enhanced Lyrixa API Server...")
    print("   - Plugin Intelligence API")
    print("   - Meta-Reasoning Engine API")
    print("   - Goals Forecasting API")
    print("   - Plugin Editor Integration API")
    print("   - Server running on http://127.0.0.1:8007")

    # Try fast server first, fallback to enhanced server
    fast_server_path = "fast_api_server.py"
    enhanced_server_path = "enhanced_api_server.py"

    if os.path.exists(fast_server_path):
        print("   >> Using fast-start server for quick initialization")
        uvicorn.run(
            "fast_api_server:app",
            host="127.0.0.1",
            port=8007,
            log_level="info",
            reload=False,  # Disable reload for background process
        )
    elif os.path.exists(enhanced_server_path):
        print("   >> Using enhanced server (slower startup)")
        uvicorn.run(
            "enhanced_api_server:app",
            host="127.0.0.1",
            port=8007,
            log_level="info",
            reload=False,  # Disable reload for background process
        )
    else:
        print("   ERROR: No API server file found")
        print("   Please ensure fast_api_server.py or enhanced_api_server.py exists")
        exit(1)
