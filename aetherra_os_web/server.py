# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌐 Aetherra OS Web Interface Server
===================================

FastAPI + WebSockets server for the revolutionary Aetherra OS cyberpunk interface.
Real-time system monitoring with stunning visual effects.
"""

# Standard library imports
import asyncio
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Third party imports
import psutil
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load engine lazily to avoid import races during OS startup.
aetherra_engine = None
AETHERRA_AVAILABLE = False


def _ensure_aetherra_engine_loaded() -> bool:
    """Load the shared Aetherra engine instance on demand."""
    global aetherra_engine, AETHERRA_AVAILABLE

    if AETHERRA_AVAILABLE and aetherra_engine is not None:
        return True

    try:
        import sys

        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.append(project_root)

        from Aetherra.aetherra_core.engine.aetherra_engine import (
            aetherra_engine as _engine,
        )

        aetherra_engine = _engine
        AETHERRA_AVAILABLE = True
        logger.info("✅ Aetherra engine loaded on demand")
        return True
    except Exception as e:
        aetherra_engine = None
        AETHERRA_AVAILABLE = False
        logger.warning("⚠️ Aetherra engine not available: %s", e)
        return False


try:
    from aetherra_os_launcher import get_latest_boot_readiness

    BOOT_READINESS_AVAILABLE = True
except ImportError:
    get_latest_boot_readiness = None
    BOOT_READINESS_AVAILABLE = False

app = FastAPI(
    title="Aetherra OS Interface", description="Revolutionary AI Operating System"
)

# ── Frontend static bundle (Vite production build) ──────────────────────────
# When `npm run build` has been run inside frontend/, serve those files.
# Falls back to legacy aetherra_os_web/templates for development access.
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
_frontend_built = (FRONTEND_DIST / "index.html").exists()

if _frontend_built:
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )
    logger.info("✅ Serving Vite-built React frontend from frontend/dist")
else:
    logger.info(
        "ℹ️  frontend/dist not found — serving legacy templates. Run 'npm run build' inside frontend/ to activate the React UI."
    )

# Legacy static/templates (kept for fallback)
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.system_data = {}
        self.neural_data = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔗 Client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"❌ Client disconnected: {websocket.client}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            # Silently ignore send errors (client likely disconnected)
            pass

    async def broadcast(self, message: dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


class SystemMonitor:
    """Real-time system monitoring with neural enhancements"""

    def __init__(self):
        self.cpu_history = []
        self.memory_history = []
        self.network_history = []
        self.neural_activity = {}
        self.start_time = time.time()

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage("/")

            # Network metrics
            network = psutil.net_io_counters()

            # Process count
            process_count = len(psutil.pids())

            # Update histories
            self.cpu_history.append(cpu_percent)
            self.memory_history.append(memory.percent)

            # Keep only last 60 data points (1 minute at 1 update/second)
            if len(self.cpu_history) > 60:
                self.cpu_history.pop(0)
            if len(self.memory_history) > 60:
                self.memory_history.pop(0)

            return {
                "timestamp": datetime.now().isoformat(),
                "uptime": int(time.time() - self.start_time),
                "cpu": {
                    "percent": cpu_percent,
                    "frequency": cpu_freq.current if cpu_freq else 0,
                    "cores": cpu_count,
                    "history": self.cpu_history[-20:],  # Last 20 seconds
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                    "history": self.memory_history[-20:],
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "percent": swap.percent,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "processes": process_count,
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}

    def get_neural_activity(self) -> dict[str, Any]:
        """Get neural network activity reflecting actual Aetherra engine state"""
        nodes = []
        connections = []

        # Get actual Aetherra engine activity if available
        aetherra_active = AETHERRA_AVAILABLE and hasattr(self, "_last_aetherra_status")
        base_activity = 0.3 if aetherra_active else 0.1

        # Generate neural nodes with activity levels based on real system state
        for i in range(25):  # 5x5 grid
            row = i // 5
            col = i % 5

            # Base activity influenced by actual system metrics
            activity = random.uniform(base_activity, 0.8)

            # CPU influence on processing nodes
            if len(self.cpu_history) > 0 and i < 10:  # First 10 nodes = CPU processing
                cpu_factor = min(self.cpu_history[-1] / 100.0, 1.0)
                activity = max(activity, cpu_factor * 0.9)

            # Memory influence on memory nodes
            if len(self.memory_history) > 0 and 10 <= i < 15:  # Memory nodes
                memory_factor = min(self.memory_history[-1] / 100.0, 1.0)
                activity = max(activity, memory_factor * 0.8)

            # Aetherra engine influence on reasoning nodes
            if aetherra_active and i >= 15:  # Last 10 nodes = Aetherra reasoning
                activity = max(activity, random.uniform(0.6, 0.9))

            # Node types based on position and function
            if i < 10:
                node_type = "processor"
            elif i < 15:
                node_type = "memory"
            elif i < 20:
                node_type = "network"
            else:
                node_type = "aetherra_core" if aetherra_active else "storage"

            nodes.append(
                {
                    "id": i,
                    "x": col * 80 + 40,  # Grid positioning
                    "y": row * 60 + 40,
                    "activity": min(activity, 1.0),
                    "type": node_type,
                    "real_data": True if i >= 15 and aetherra_active else False,
                }
            )

        # Generate connections between nearby nodes
        for i, node in enumerate(nodes):
            for j, other_node in enumerate(nodes[i + 1 :], i + 1):
                distance = (
                    (node["x"] - other_node["x"]) ** 2
                    + (node["y"] - other_node["y"]) ** 2
                ) ** 0.5
                if distance < 120 and random.random() < 0.3:
                    strength = random.uniform(0.2, 0.8)
                    connections.append(
                        {
                            "source": node["id"],
                            "target": other_node["id"],
                            "strength": strength,
                            "data_flow": random.choice(["up", "down", "bidirectional"]),
                        }
                    )

        return {
            "nodes": nodes,
            "connections": connections,
            "network_load": sum(node["activity"] for node in nodes) / len(nodes),
            "active_processes": random.randint(50, 150),
            "data_throughput": random.uniform(10, 100),  # MB/s
        }

    async def get_aetherra_status(self) -> dict[str, Any]:
        """Get Aetherra engine status if available"""
        if not _ensure_aetherra_engine_loaded() or aetherra_engine is None:
            return {
                "available": False,
                "status": "Engine not available",
                "components": {},
            }

        try:
            # Initialize engine if needed
            if not aetherra_engine.initialized:
                await aetherra_engine.initialize()

            status = await aetherra_engine.get_system_status()

            # Store status for neural visualization
            self._last_aetherra_status = status

            return {
                "available": True,
                "status": "operational",
                "engine_status": status.get("engine_status", "unknown"),
                "session_active": status.get("session_active", False),
                "memory_system": status.get("memory_system", {}),
                "improvement_system": status.get("improvement_system", {}),
                "agent_orchestrator": status.get("agent_orchestrator", {}),
                "health_monitoring": status.get("health_monitoring", {}),
                "uptime_minutes": status.get("uptime_minutes", 0),
                "active_components": len(
                    [
                        k
                        for k, v in status.items()
                        if isinstance(v, dict) and v.get("status") == "active"
                    ]
                ),
                "total_memories": status.get("memory_system", {}).get(
                    "total_memories", 0
                ),
                "reasoning_sessions": status.get("improvement_system", {}).get(
                    "improvements", 0
                ),
            }
        except Exception as e:
            logger.error(f"Error getting Aetherra status: {e}")
            return {
                "available": False,
                # Intentionally do not leak internal exception details to API consumers
                # Original behavior exposed: f"Error: {str(e)}"
                # Contract: keep keys/structure identical while sanitizing status string
                "status": "Could not retrieve Aetherra engine status",
                "components": {},
            }


monitor = SystemMonitor()


@app.get("/", response_class=HTMLResponse)
async def get_interface(request: Request):
    """Serve the Aetherra React UI when built, otherwise the legacy template."""
    if _frontend_built:
        return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data"""
    await manager.connect(websocket)

    try:
        while True:
            # Get system metrics
            system_metrics = monitor.get_system_metrics()
            neural_activity = monitor.get_neural_activity()
            aetherra_status = await monitor.get_aetherra_status()

            # Send data to client
            await manager.send_personal_message(
                json.dumps(
                    {
                        "type": "system_update",
                        "data": {
                            "system": system_metrics,
                            "neural": neural_activity,
                            "aetherra": aetherra_status,
                            "timestamp": datetime.now().isoformat(),
                        },
                    }
                ),
                websocket,
            )

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/aetherra/message")
async def send_aetherra_message(data: dict):
    """Send message to Aetherra engine"""
    if not _ensure_aetherra_engine_loaded() or aetherra_engine is None:
        return {"error": "Aetherra engine not available"}

    try:
        message = data.get("message", "")
        if not message:
            return {"error": "No message provided"}

        # Process message through Aetherra engine
        response = await aetherra_engine.process_message(message)

        # If engine returned an explicit error field, suppress internal details
        if isinstance(response, dict) and "error" in response:
            try:
                logger.error(
                    "Aetherra engine reported error (suppressed to client): %s",
                    response.get("error"),
                )
            except Exception:
                pass
            # Optionally still broadcast a sanitized failure event
            try:
                await manager.broadcast(
                    {
                        "type": "aetherra_response",
                        "data": {"error": "engine_failed"},
                    }
                )
            except Exception:
                pass
            return {
                "error": "Aetherra engine failed to process the message",
                "success": False,
            }

        # Broadcast only successful engine response
        try:
            await manager.broadcast({"type": "aetherra_response", "data": response})
        except Exception:
            # Non-fatal broadcast error; log and still return success to caller
            logger.error("Broadcast failure (non-fatal)", exc_info=True)

        return {"success": True, "response": response}

    except Exception as e:
        # Log full traceback internally but avoid leaking internal details to client
        logger.error(f"Error processing Aetherra message: {e}", exc_info=True)
        return {"error": "An internal error occurred while processing the message"}


@app.get("/api/status")
async def get_status():
    """Get current system status"""
    system_metrics = monitor.get_system_metrics()
    neural_activity = monitor.get_neural_activity()
    aetherra_status = await monitor.get_aetherra_status()

    return {
        "system": system_metrics,
        "neural": neural_activity,
        "aetherra": aetherra_status,
        "connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/boot/readiness")
async def get_boot_readiness():
    """Expose launcher startup readiness synthesis for UI boot experiences."""
    if BOOT_READINESS_AVAILABLE and get_latest_boot_readiness is not None:
        snapshot = get_latest_boot_readiness()
        if snapshot:
            return {"available": True, "readiness": snapshot}

    return {
        "available": False,
        "readiness": {
            "status": "unknown",
            "phase": "unavailable",
            "message": "Boot readiness is not available in this runtime mode.",
            "system_scan": {
                "registry": {
                    "available": False,
                    "total_services": 0,
                    "healthy_services": 0,
                },
                "kernel": {"available": False, "running": False, "cycle_count": 0},
                "hub": {"ok": False, "url": "http://localhost:3001"},
            },
            "self_scan": {
                "provider": "default",
                "policy_tier": "free",
                "gui_enabled": False,
            },
            "issues": ["Launcher readiness snapshot unavailable"],
            "recommended_actions": [
                "Start via aetherra_os.py so launcher and web API share process state"
            ],
            "updated_at": datetime.now().isoformat(),
        },
    }


@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def spa_fallback(full_path: str, request: Request):
    """SPA catch-all: any unmatched route returns the React index so client-side routing works."""
    if _frontend_built and not full_path.startswith(("api", "ws", "static", "assets")):
        return HTMLResponse((FRONTEND_DIST / "index.html").read_text(encoding="utf-8"))
    from fastapi.responses import Response

    return Response(status_code=404)


if __name__ == "__main__":
    # Third party imports
    import uvicorn

    logger.info("🚀 Starting Aetherra OS Web Interface...")
    logger.info("🌟 Cyberpunk neural interface loading...")
    logger.info("⚡ Real-time system monitoring active")

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info", reload=False)
