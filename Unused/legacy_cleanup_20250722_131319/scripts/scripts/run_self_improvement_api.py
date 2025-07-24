#!/usr/bin/env python3
"""
Run the Lyrixa Self-Improvement Dashboard API server.
Updated to use the direct endpoint registration version for reliability.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "Aetherra.lyrixa.fixed_api_server:app",
        host="127.0.0.1",
        port=8005,
        log_level="info",
        reload=False,  # Disable reload for background process
    )
