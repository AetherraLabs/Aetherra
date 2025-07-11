#!/usr/bin/env python3
"""
Run the Lyrixa Self-Improvement Dashboard API server.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "lyrixa.self_improvement_dashboard_api:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        factory=False,
    )
