#!/usr/bin/env python3
"""
Minimal server startup script for testing
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def start_server():
    """Start the server"""
    try:
        import uvicorn

        from Aetherra.api.aether_server import app

        print("🚀 Starting Aetherra API Server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📖 API docs: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop")

        # Configure and run server
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(start_server())
