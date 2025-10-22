#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 LYRIXA LAUNCHER - The Living System
=====================================

Aetherra's interface isn't a window. It's a living mind made visible.

This launcher bridges the Python backend (Aetherra OS) with the React frontend,
creating a seamless experience where the user sees the OS breathe and think.

Visual Signature:
- Fractal nucleus pulsing with teal light (#00ff88)
- Living quantum grid background
- Layers of consciousness (Surface → Cognitive → Control)
- Everything breathes, phases, and flows with intelligence

Architecture:
- FastAPI backend server for real-time communication
- React frontend with Framer Motion animations
- WebSocket connections for live system state
- RESTful API for system operations

Usage:
    python Aetherra/lyrixa/gui/Lyrixa_Launcher.py
    python Aetherra/lyrixa/gui/Lyrixa_Launcher.py --dev    # Development mode
    python Aetherra/lyrixa/gui/Lyrixa_Launcher.py --port 3000
"""

import argparse
import asyncio
import contextlib
import urllib.request
import urllib.error
import json
import logging
import os
import subprocess
import sys
import webbrowser
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party imports
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI not installed. Install with: pip install fastapi uvicorn websockets")

# Aetherra imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)

# Colors for console output
AETHER_GREEN = "\033[38;2;0;255;136m"
RESET = "\033[0m"
CYAN = "\033[96m"
YELLOW = "\033[93m"


class LyrixaLauncher:
    """
    🌌 The Lyrixa Launcher - Bridging Mind and Interface

    This class manages the lifecycle of the Lyrixa GUI:
    1. Starts the Aetherra backend services
    2. Launches the FastAPI bridge server
    3. Serves the React frontend
    4. Manages real-time communication via WebSockets
    """

    def __init__(self, port: int = 3012, dev_mode: bool = False):
        self.port = port
        self.dev_mode = dev_mode
        self.app = None
        self.active_connections: List[WebSocket] = []
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.gui_root = Path(__file__).parent
        self.frontend_root = self.gui_root / "frontend"

        # Aetherra OS integration
        self.service_registry = None
        self.kernel_loop = None
        self.memory_system = None
        self.agent_orchestrator = None
        self.aetherra_engine = None
        self.hub_url = os.environ.get("AETHERRA_HUB_URL", "http://localhost:3001")

        # Chat service integration
        self.chat_service = None

        # System state
        self.system_state = {
            "kernel": {"status": "connecting", "heartbeat_ms": 0},
            "memory": {"coherence": 0.0, "active_memories": 0},
            "agents": {"active": 0, "total": 0, "list": []},
            "security": {"status": "clean", "alerts": []},
            "homeostasis": {"balance": 0.0, "target": 0.75},
        }

    def print_banner(self):
        """Display the iconic Aetherra startup banner."""
        banner = f"""
{CYAN}════════════════════════════════════════════════════════════════════════════════{RESET}

                    {AETHER_GREEN}█████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ ██████╗  █████╗ {RESET}
                   {AETHER_GREEN}██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗{RESET}
                   {AETHER_GREEN}███████║█████╗     ██║   ███████║█████╗  ██████╔╝██████╔╝███████║{RESET}
                   {AETHER_GREEN}██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗██╔══██╗██╔══██║{RESET}
                   {AETHER_GREEN}██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║██║  ██║██║  ██║{RESET}
                   {AETHER_GREEN}╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝{RESET}

                              {YELLOW}🌌  L Y R I X A  -  The Living System  🌌{RESET}

                                      {AETHER_GREEN}"Code Awakened."{RESET}

{CYAN}════════════════════════════════════════════════════════════════════════════════{RESET}

        🧬 Visual Signature: Fractal nucleus • Quantum grid • Layers of consciousness
        💫 Interface: The mind made visible • Every element breathes with intelligence
        ⚡ Architecture: Python backend ↔ FastAPI bridge ↔ React frontend

{CYAN}════════════════════════════════════════════════════════════════════════════════{RESET}
"""
        print(banner)

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed."""
        logger.info("🔍 Checking dependencies...")

        # Check Python dependencies
        missing_python = []
        if not FASTAPI_AVAILABLE:
            missing_python.append("fastapi uvicorn websockets")

        if missing_python:
            print(f"\n{YELLOW}⚠️  Missing Python dependencies:{RESET}")
            for dep in missing_python:
                print(f"   - {dep}")
            print(f"\n{AETHER_GREEN}Install with:{RESET} pip install {' '.join(missing_python)}")
            return False

        # Check if Node.js is installed
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"\n{YELLOW}⚠️  Node.js not found. Please install Node.js 18+ from https://nodejs.org{RESET}")
                return False
        except FileNotFoundError:
            print(f"\n{YELLOW}⚠️  Node.js not found. Please install Node.js 18+ from https://nodejs.org{RESET}")
            return False

        # Check if frontend exists and is built
        if not self.frontend_root.exists():
            print(f"\n{YELLOW}⚠️  Frontend directory not found at: {self.frontend_root}{RESET}")
            print(f"{AETHER_GREEN}Run:{RESET} npm run setup:frontend")
            return False

        logger.info("✅ All dependencies satisfied")
        return True

    def create_fastapi_app(self) -> FastAPI:
        """Create the FastAPI application for the bridge server."""
        app = FastAPI(
            title="Lyrixa - The Living System",
            description="Aetherra OS Interface Bridge",
            version="8.0.0"
        )

        # CORS middleware for React dev server
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://localhost:3012"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # API Routes
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "alive", "message": "The system breathes."}

        @app.get("/api/os/kernel/status")
        async def os_kernel_status():
            """Proxy kernel status from Hub/registry for diagnostics."""
            try:
                # Prefer Hub cross-process
                try:
                    url = f"{self.hub_url}/api/kernel/status"
                    with urllib.request.urlopen(url, timeout=1.0) as resp:
                        ks = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        return ks if isinstance(ks, dict) else {"running": False}
                except Exception:
                    pass

                # Fallback to in-process kernel_loop
                if self.kernel_loop and hasattr(self.kernel_loop, "get_status"):
                    try:
                        ks = self.kernel_loop.get_status()
                        return ks if isinstance(ks, dict) else {"running": False}
                    except Exception:
                        pass
            except Exception as e:
                logger.debug(f"kernel status proxy error: {e}")
            return {"running": False}

        @app.get("/api/os/kernel/metrics")
        async def os_kernel_metrics():
            """Proxy kernel metrics from Hub if available."""
            try:
                url = f"{self.hub_url}/api/kernel/metrics"
                with urllib.request.urlopen(url, timeout=1.0) as resp:
                    mt = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    return mt if isinstance(mt, dict) else {"ok": False}
            except Exception as e:
                logger.debug(f"kernel metrics proxy error: {e}")
                return {"ok": False}

        @app.get("/api/os/memory/status")
        async def os_memory_status():
            """Proxy memory system status from registry."""
            try:
                if self.memory_system and hasattr(self.memory_system, "get_status"):
                    mem_st = await self.memory_system.get_status()
                    return mem_st if isinstance(mem_st, dict) else {"available": False}
            except Exception as e:
                logger.debug(f"memory status error: {e}")
            return {"available": False}

        @app.get("/api/os/agents/status")
        async def os_agents_status():
            """Proxy agent orchestrator status from registry."""
            try:
                if self.agent_orchestrator and hasattr(self.agent_orchestrator, "get_status"):
                    ag_st = self.agent_orchestrator.get_status()
                    return ag_st if isinstance(ag_st, dict) else {"available": False}
            except Exception as e:
                logger.debug(f"agents status error: {e}")
            return {"available": False}

        @app.get("/api/os/homeostasis/status")
        async def os_homeostasis_status():
            """Proxy homeostasis status from Hub with live metrics."""
            try:
                # Try Hub first (cross-process with live metrics)
                try:
                    url = f"{self.hub_url}/homeostasis"
                    logger.debug(f"Fetching homeostasis from Hub: {url}")
                    with urllib.request.urlopen(url, timeout=1.0) as resp:
                        hub_data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        logger.debug(f"Hub homeostasis response: {hub_data}")
                        if isinstance(hub_data, dict) and hub_data.get("status") == "available":
                            # Use live metrics from Hub
                            return {
                                "available": True,
                                "balance": hub_data.get("balance", 0.0),
                                "target": hub_data.get("target", 0.75),
                                "mode": hub_data.get("mode", "unknown"),
                                "metrics_available": hub_data.get("metrics_available", False),
                                "description": hub_data.get("description", "Homeostasis System"),
                                "features": hub_data.get("features", []),
                            }
                except Exception as hub_err:
                    logger.debug(f"Hub homeostasis fetch failed: {hub_err}")

                # Fallback to in-process engine
                if self.aetherra_engine and hasattr(self.aetherra_engine, "get_status"):
                    eng_st = self.aetherra_engine.get_status()
                    if isinstance(eng_st, dict):
                        return {"available": True, **eng_st}
            except Exception as e:
                logger.debug(f"homeostasis status error: {e}")
            return {"available": False}

        @app.get("/api/system/state")
        async def get_system_state():
            """Get current system state for the UI."""
            return self.system_state

        @app.post("/api/system/action")
        async def system_action(action: Dict[str, Any] = Body(...)):
            """Execute a system action."""
            logger.info(f"Action received: {action}")
            # TODO: Integrate with Aetherra backend
            return {"status": "acknowledged", "action": action}

        @app.post("/api/chat/message")
        async def chat_message(request: Dict[str, Any] = Body(...)):
            """Handle chat messages from the UI."""
            try:
                message = request.get("message", "")
                if not message:
                    return {"error": "No message provided"}

                # Initialize chat service if needed
                if not self.chat_service:
                    await self._initialize_chat_service()

                # Process message through chat service
                if self.chat_service:
                    from Aetherra.lyrixa.chat.lyrixa_chat_service import ChatOptions

                    opts = ChatOptions(
                        user_id=request.get("user_id", "user"),
                        session_id=request.get("session_id", "default"),
                        max_tokens=request.get("max_tokens", 600),
                    )

                    response = await self.chat_service.chat(message, opts)
                    # Attach provider/path hints into awareness if available for debugging
                    try:
                        if hasattr(self.chat_service, "_orchestrator") and self.chat_service._orchestrator:
                            # Orchestrator embeds provider selection in evidence; ChatService already merges some into awareness
                            pass
                    except Exception:
                        pass

                    return {
                        "success": True,
                        "text": response.text,
                        "suggestions": response.suggestions,
                        "awareness": response.awareness,
                        "identity": response.identity,
                    }
                else:
                    # Fallback response
                    return {
                        "success": True,
                        "text": f"I received your message: {message}. Chat service is initializing...",
                        "suggestions": [],
                        "awareness": {},
                    }

            except Exception as e:
                logger.error(f"Chat error: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "text": "I'm having trouble processing that. Please try again.",
                }

        @app.get("/api/ai/providers")
        async def ai_providers():
            """Report available AI providers and active provider for debugging."""
            try:
                # Ensure chat service exists so intelligence is initialized
                if not self.chat_service:
                    await self._initialize_chat_service()

                providers_info: Dict[str, Any] = {}
                active = None
                if self.chat_service and getattr(self.chat_service, "_intelligence", None):
                    intel = self.chat_service._intelligence
                    active = getattr(intel, "active_provider", None)
                    prov_map = getattr(intel, "providers", {}) or {}
                    for name, p in prov_map.items():
                        try:
                            providers_info[name] = {
                                "available": bool(p.get("available")),
                                "model": p.get("model"),
                                "priority": p.get("priority"),
                            }
                        except Exception:
                            providers_info[name] = {"available": False}
                return {"providers": providers_info, "active": active}
            except Exception as e:
                logger.debug(f"ai_providers endpoint error: {e}")
                return {"providers": {}, "active": None, "error": str(e)}

        @app.get("/api/ai/status")
        async def ai_status():
            """Composite AI wiring status: intelligence, orchestrator, memory, registry, consciousness."""
            try:
                if not self.chat_service:
                    await self._initialize_chat_service()
                status: Dict[str, Any] = {
                    "orchestrator": bool(getattr(self.chat_service, "_orchestrator", None)),
                    "multidimensional_memory": bool(getattr(self.chat_service, "_mdmem", None)),
                    "consciousness_bridge": bool(getattr(self.chat_service, "_conscious", None)),
                    "registry": bool(self.service_registry),
                }
                # Intelligence detailed status
                intel = getattr(self.chat_service, "_intelligence", None)
                if intel is not None:
                    try:
                        providers_info: Dict[str, Any] = {}
                        for name, p in (getattr(intel, "providers", {}) or {}).items():
                            providers_info[name] = {
                                "available": bool(p.get("available")),
                                "model": p.get("model"),
                                "priority": p.get("priority"),
                            }
                        status["intelligence"] = {
                            "active": getattr(intel, "active_provider", None),
                            "providers": providers_info,
                        }
                    except Exception:
                        status["intelligence"] = {"error": "introspection_failed"}
                else:
                    status["intelligence"] = {"active": None, "providers": {}}
                return status
            except Exception as e:
                return {"error": str(e)}

        # ============================================================================
        # FILE SYSTEM API - Full Access for Lyrixa
        # ============================================================================

        @app.get("/api/fs/list")
        async def fs_list(path: str = "."):
            """List directory contents with full metadata."""
            try:
                target = self.project_root / path
                if not target.exists():
                    return {"error": "path_not_found", "path": str(target)}

                if not target.is_dir():
                    return {"error": "not_a_directory", "path": str(target)}

                items = []
                for item in sorted(target.iterdir()):
                    try:
                        stat = item.stat()
                        items.append({
                            "name": item.name,
                            "path": str(item.relative_to(self.project_root)),
                            "type": "directory" if item.is_dir() else "file",
                            "size": stat.st_size if item.is_file() else 0,
                            "modified": stat.st_mtime,
                            "extension": item.suffix if item.is_file() else None,
                        })
                    except Exception:
                        continue

                return {
                    "path": str(target.relative_to(self.project_root)),
                    "items": items,
                    "count": len(items)
                }
            except Exception as e:
                return {"error": str(e)}

        @app.get("/api/fs/read")
        async def fs_read(path: str):
            """Read file contents."""
            try:
                target = self.project_root / path
                if not target.exists():
                    return {"error": "file_not_found", "path": str(target)}

                if not target.is_file():
                    return {"error": "not_a_file", "path": str(target)}

                # Read with UTF-8, fallback to latin-1 for binary-ish files
                try:
                    content = target.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = target.read_text(encoding="latin-1")

                return {
                    "path": str(target.relative_to(self.project_root)),
                    "content": content,
                    "size": len(content),
                    "lines": content.count('\n') + 1
                }
            except Exception as e:
                return {"error": str(e)}

        @app.post("/api/fs/write")
        async def fs_write(data: Dict[str, Any] = Body(...)):
            """Write content to file. Creates parent directories if needed."""
            try:
                path = data.get("path")
                content = data.get("content")
                create_backup = data.get("backup", True)

                if not path or content is None:
                    return {"error": "missing_path_or_content"}

                target = self.project_root / path

                # Create backup if file exists
                if create_backup and target.exists():
                    backup_path = target.with_suffix(target.suffix + ".backup")
                    backup_path.write_bytes(target.read_bytes())

                # Create parent directories
                target.parent.mkdir(parents=True, exist_ok=True)

                # Write content
                target.write_text(content, encoding="utf-8")

                return {
                    "success": True,
                    "path": str(target.relative_to(self.project_root)),
                    "size": len(content),
                    "backup": str(backup_path.relative_to(self.project_root)) if create_backup and backup_path.exists() else None
                }
            except Exception as e:
                return {"error": str(e)}

        @app.post("/api/fs/search")
        async def fs_search(data: Dict[str, Any] = Body(...)):
            """Search for files and content across Aetherra filesystem."""
            try:
                query = data.get("query", "")
                search_type = data.get("type", "content")  # "content", "filename", "both"
                path = data.get("path", ".")
                extensions = data.get("extensions", [])  # Filter by file extensions
                max_results = data.get("max_results", 100)

                base_path = self.project_root / path
                if not base_path.exists():
                    return {"error": "path_not_found"}

                results = []

                def search_recursive(directory: Path, depth: int = 0):
                    if depth > 10 or len(results) >= max_results:  # Limit recursion
                        return

                    try:
                        for item in directory.iterdir():
                            if item.name.startswith('.') or item.name == '__pycache__':
                                continue

                            if item.is_file():
                                # Extension filter
                                if extensions and item.suffix not in extensions:
                                    continue

                                # Filename search
                                if search_type in ("filename", "both"):
                                    if query.lower() in item.name.lower():
                                        results.append({
                                            "path": str(item.relative_to(self.project_root)),
                                            "match_type": "filename",
                                            "name": item.name,
                                            "size": item.stat().st_size
                                        })
                                        if len(results) >= max_results:
                                            return

                                # Content search
                                if search_type in ("content", "both"):
                                    try:
                                        content = item.read_text(encoding="utf-8", errors="ignore")
                                        if query.lower() in content.lower():
                                            # Find line numbers
                                            lines = content.split('\n')
                                            matches = [(i+1, line.strip()) for i, line in enumerate(lines)
                                                     if query.lower() in line.lower()][:5]  # Max 5 matches per file

                                            results.append({
                                                "path": str(item.relative_to(self.project_root)),
                                                "match_type": "content",
                                                "name": item.name,
                                                "size": item.stat().st_size,
                                                "matches": matches
                                            })
                                            if len(results) >= max_results:
                                                return
                                    except Exception:
                                        continue

                            elif item.is_dir():
                                search_recursive(item, depth + 1)
                    except PermissionError:
                        pass

                search_recursive(base_path)

                return {
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "truncated": len(results) >= max_results
                }
            except Exception as e:
                return {"error": str(e)}

        @app.post("/api/fs/delete")
        async def fs_delete(data: Dict[str, Any] = Body(...)):
            """Delete file or directory (with safety backup)."""
            try:
                path = data.get("path")
                create_backup = data.get("backup", True)

                if not path:
                    return {"error": "missing_path"}

                target = self.project_root / path
                if not target.exists():
                    return {"error": "path_not_found"}

                # Safety: Create backup in trash folder
                if create_backup:
                    trash_dir = self.project_root / ".lyrixa_trash"
                    trash_dir.mkdir(exist_ok=True)

                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{target.name}.{timestamp}"
                    backup_path = trash_dir / backup_name

                    if target.is_file():
                        shutil.copy2(target, backup_path)
                    else:
                        shutil.copytree(target, backup_path)

                # Delete
                if target.is_file():
                    target.unlink()
                else:
                    import shutil
                    shutil.rmtree(target)

                return {
                    "success": True,
                    "path": str(target.relative_to(self.project_root)),
                    "backup": str(backup_path.relative_to(self.project_root)) if create_backup else None
                }
            except Exception as e:
                return {"error": str(e)}

        @app.get("/api/fs/tree")
        async def fs_tree(path: str = "Aetherra", max_depth: int = 3):
            """Get directory tree structure."""
            try:
                base_path = self.project_root / path
                if not base_path.exists():
                    return {"error": "path_not_found"}

                def build_tree(directory: Path, depth: int = 0):
                    if depth > max_depth:
                        return None

                    try:
                        tree = {
                            "name": directory.name,
                            "path": str(directory.relative_to(self.project_root)),
                            "type": "directory",
                            "children": []
                        }

                        for item in sorted(directory.iterdir()):
                            if item.name.startswith('.') or item.name == '__pycache__':
                                continue

                            if item.is_dir():
                                subtree = build_tree(item, depth + 1)
                                if subtree:
                                    tree["children"].append(subtree)
                            else:
                                tree["children"].append({
                                    "name": item.name,
                                    "path": str(item.relative_to(self.project_root)),
                                    "type": "file",
                                    "size": item.stat().st_size,
                                    "extension": item.suffix
                                })

                        return tree
                    except PermissionError:
                        return None

                tree = build_tree(base_path)
                return tree if tree else {"error": "access_denied"}
            except Exception as e:
                return {"error": str(e)}

        @app.get("/api/fs/stats")
        async def fs_stats():
            """Get filesystem statistics for Aetherra project."""
            try:
                aetherra_path = self.project_root / "Aetherra"

                stats = {
                    "total_files": 0,
                    "total_size": 0,
                    "by_extension": {},
                    "by_directory": {}
                }

                def count_recursive(directory: Path, depth: int = 0):
                    if depth > 10:
                        return

                    try:
                        for item in directory.iterdir():
                            if item.name.startswith('.') or item.name == '__pycache__':
                                continue

                            if item.is_file():
                                stats["total_files"] += 1
                                size = item.stat().st_size
                                stats["total_size"] += size

                                # By extension
                                ext = item.suffix or "no_extension"
                                if ext not in stats["by_extension"]:
                                    stats["by_extension"][ext] = {"count": 0, "size": 0}
                                stats["by_extension"][ext]["count"] += 1
                                stats["by_extension"][ext]["size"] += size

                                # By directory
                                dir_name = directory.name
                                if dir_name not in stats["by_directory"]:
                                    stats["by_directory"][dir_name] = {"count": 0, "size": 0}
                                stats["by_directory"][dir_name]["count"] += 1
                                stats["by_directory"][dir_name]["size"] += size

                            elif item.is_dir():
                                count_recursive(item, depth + 1)
                    except PermissionError:
                        pass

                count_recursive(aetherra_path)

                return stats
            except Exception as e:
                return {"error": str(e)}

        @app.websocket("/ws/live")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"🔌 WebSocket connected (total: {len(self.active_connections)})")

            try:
                # Send initial state
                await websocket.send_json({
                    "type": "init",
                    "data": self.system_state
                })

                # Keep connection alive and listen for messages
                while True:
                    data = await websocket.receive_json()
                    logger.info(f"📨 WebSocket message: {data}")

                    # Echo back for now (TODO: integrate with backend)
                    await websocket.send_json({
                        "type": "ack",
                        "data": data
                    })
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                logger.info(f"🔌 WebSocket disconnected (remaining: {len(self.active_connections)})")

        # Serve static files in production mode
        if not self.dev_mode:
            dist_path = self.frontend_root / "dist"
            if not dist_path.exists():
                # Try to build once so we serve the current UI when launching in prod mode
                try:
                    logger.info("🛠️  Building frontend (npm run build) since dist/ is missing...")
                    result = subprocess.run(
                        ["npm", "run", "build"],
                        cwd=str(self.frontend_root),
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode != 0:
                        logger.warning("Frontend build failed; serving will likely be unavailable.\n%s", result.stderr[:500])
                except Exception as e:
                    logger.warning(f"Frontend build attempt failed: {e}")
            # Mount if available now
            if dist_path.exists():
                app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")
            else:
                logger.warning(f"⚠️  Frontend not built. Run: npm run build in {self.frontend_root}")

        return app

    def _is_port_alive(self, url: str, timeout: float = 0.75) -> bool:
        """Quickly probe a URL to see if it's responding (used for dev server detection)."""
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # Any HTTP response means something is serving; don't require 200 strictly
                return True
        except Exception:
            return False

    async def broadcast_state_update(self, update: Dict[str, Any]):
        """Broadcast system state updates to all connected clients."""
        if not self.active_connections:
            return

        message = {
            "type": "state_update",
            "data": update,
            "timestamp": asyncio.get_event_loop().time()
        }

        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

    async def _initialize_chat_service(self):
        """Initialize the Lyrixa chat service."""
        try:
            # Import chat service
            from Aetherra.lyrixa.chat.lyrixa_chat_service import LyrixaChatService

            logger.info("🗨️  Initializing Lyrixa Chat Service...")
            self.chat_service = LyrixaChatService(workspace_root=self.project_root)

            # Initialize with OS services if available
            await self.chat_service.initialize()

            # Wire registry if we have it
            if self.service_registry:
                self.chat_service.registry = self.service_registry

            logger.info("✅ Chat Service initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize chat service: {e}")
            self.chat_service = None

    async def connect_to_aetherra_os(self):
        """Connect to the running Aetherra OS services."""
        logger.info("🔌 Connecting to Aetherra OS...")

        try:
            # Import service registry
            sys.path.insert(0, str(self.project_root))
            from aetherra_service_registry import get_service_registry

            # Get the global service registry
            self.service_registry = await get_service_registry()

            if self.service_registry:
                logger.info("✅ Connected to Service Registry")

                # Get core services
                self.kernel_loop = self.service_registry.get_service("kernel_loop")
                self.memory_system = self.service_registry.get_service("memory_system")
                self.agent_orchestrator = self.service_registry.get_service("agent_orchestrator")
                self.aetherra_engine = self.service_registry.get_service("aetherra_engine")

                # Log what we found
                services = self.service_registry.list_services()
                logger.info(f"📊 Found {len(services)} OS services:")
                for name in services:
                    logger.info(f"   - {name}")

                # If kernel_loop is present (same-process), mark running
                if self.kernel_loop:
                    self.system_state["kernel"]["status"] = "running"
                    return True

                # Cross-process fallback: query Aetherra Hub for kernel status
                try:
                    url = f"{self.hub_url}/api/kernel/status"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=1.5) as resp:
                        payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        running = bool(payload.get("running"))
                        self.system_state["kernel"]["status"] = "running" if running else "degraded"
                        logger.info("🌐 Hub kernel status: %s", "running" if running else "degraded")
                        return True
                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
                    logger.info("Hub kernel status unavailable: %s", e)

                # Default degraded if we couldn't detect
                self.system_state["kernel"]["status"] = "degraded"
                return False
            else:
                logger.warning("⚠️  Service Registry not available")
                # Try Hub-only detection even if registry unavailable
                try:
                    url = f"{self.hub_url}/api/kernel/status"
                    with urllib.request.urlopen(url, timeout=1.5) as resp:
                        payload = json.loads(resp.read().decode("utf-8", errors="ignore"))
                        running = bool(payload.get("running"))
                        self.system_state["kernel"]["status"] = "running" if running else "degraded"
                        logger.info("🌐 Hub-only kernel status: %s", "running" if running else "degraded")
                        return running
                except Exception:
                    pass
                return False

        except ImportError as e:
            logger.warning(f"⚠️  Aetherra OS not found: {e}")
            logger.info("   Running in standalone mode with simulated data")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to Aetherra OS: {e}")
            return False

    async def update_state_from_os(self):
        """Update system state from real Aetherra OS services."""
        try:
            # Get kernel status (prefer Hub cross-process; fallback to in-process)
            kernel_status: Dict[str, Any] | None = None
            try:
                url = f"{self.hub_url}/api/kernel/status"
                with urllib.request.urlopen(url, timeout=1.0) as resp:
                    kernel_status = json.loads(resp.read().decode("utf-8", errors="ignore"))
            except Exception:
                if self.kernel_loop and hasattr(self.kernel_loop, "get_status"):
                    try:
                        kernel_status = self.kernel_loop.get_status()
                    except Exception:
                        kernel_status = None

            if isinstance(kernel_status, dict):
                # Normalize to UI schema
                running = bool(kernel_status.get("running", False))
                self.system_state["kernel"]["status"] = "running" if running else "degraded"
                # Heuristic heartbeat: prefer provided, else derive from metrics or uptime
                hb = kernel_status.get("heartbeat_ms")
                if not isinstance(hb, (int, float)):
                    metrics = kernel_status.get("metrics") or {}
                    hb = metrics.get("heartbeat_ms") or 60
                try:
                    self.system_state["kernel"]["heartbeat_ms"] = int(hb) if isinstance(hb, (int, float)) else 60
                except Exception:
                    self.system_state["kernel"]["heartbeat_ms"] = 60

            # Get memory status
            if self.memory_system:
                try:
                    memory_status = await self.memory_system.get_status()
                    self.system_state["memory"]["coherence"] = memory_status.get("coherence", 0.85)
                    self.system_state["memory"]["active_memories"] = memory_status.get("total_memories", 0)
                except Exception as e:
                    logger.debug(f"Memory status unavailable: {e}")

            # Get agent status
            if self.agent_orchestrator:
                try:
                    agent_status = self.agent_orchestrator.get_status()
                    self.system_state["agents"]["active"] = agent_status.get("active_agents", 0)
                    self.system_state["agents"]["total"] = agent_status.get("total_agents", 0)
                    self.system_state["agents"]["list"] = agent_status.get("agents", [])
                except Exception as e:
                    logger.debug(f"Agent status unavailable: {e}")

            # Get homeostasis from Hub (cross-process with live metrics)
            try:
                url = f"{self.hub_url}/homeostasis"
                with urllib.request.urlopen(url, timeout=1.0) as resp:
                    hub_data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    if isinstance(hub_data, dict):
                        self.system_state["homeostasis"]["balance"] = hub_data.get("balance", 0.0)
                        self.system_state["homeostasis"]["target"] = hub_data.get("target", 0.75)
            except Exception:
                # Fallback to in-process engine if available
                if self.aetherra_engine:
                    try:
                        engine_status = self.aetherra_engine.get_status()
                        self.system_state["homeostasis"]["balance"] = engine_status.get("homeostasis", 0.75)
                    except Exception as e:
                        logger.debug(f"Engine status unavailable: {e}")

        except Exception as e:
            logger.error(f"Error updating state from OS: {e}")

    async def simulate_heartbeat(self):
        """Update system state and broadcast to clients."""
        import random

        while True:
            await asyncio.sleep(2)  # Update every 2 seconds

            # Try to get real OS data first
            if self.service_registry:
                await self.update_state_from_os()
            else:
                # Fallback to simulated data
                self.system_state["kernel"]["heartbeat_ms"] = random.randint(40, 80)
                self.system_state["memory"]["coherence"] = min(1.0, random.uniform(0.85, 0.95))
                self.system_state["agents"]["active"] = random.randint(5, 12)
                self.system_state["homeostasis"]["balance"] = random.uniform(0.65, 0.85)

            # Broadcast to connected clients
            await self.broadcast_state_update(self.system_state)

    async def _run_async(self):
        """Internal async runner: connect to OS, start heartbeat, and serve API."""
        # Connect to Aetherra OS if running
        await self.connect_to_aetherra_os()

        # Initialize chat service with registry access
        await self._initialize_chat_service()

        # Create FastAPI app inside running loop
        self.app = self.create_fastapi_app()

        # Start background heartbeat task
        heartbeat_task = asyncio.create_task(self.simulate_heartbeat())

        # Configure and run uvicorn server
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info" if self.dev_mode else "warning",
        )
        server = uvicorn.Server(config)

        try:
            await server.serve()
        finally:
            # Ensure heartbeat task is cancelled on shutdown
            if not heartbeat_task.done():
                heartbeat_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await heartbeat_task

    def run(self):
        """Launch the Lyrixa GUI."""
        self.print_banner()

        if not FASTAPI_AVAILABLE:
            print(f"\n{YELLOW}❌ Cannot start: FastAPI not installed{RESET}")
            print(f"{AETHER_GREEN}Install with:{RESET} pip install fastapi uvicorn websockets")
            sys.exit(1)

        if not self.check_dependencies():
            sys.exit(1)

        logger.info(f"🚀 Starting Lyrixa on port {self.port}...")

        # Prefer the live dev UI automatically when it's already running
        dev_ui_alive = self._is_port_alive("http://localhost:5173")

        if self.dev_mode:
            logger.info("🔧 Dev mode: React dev server should be running on http://localhost:5173")
            logger.info(f"🔧 API server will run on http://localhost:{self.port}")
            # Attempt to auto-start the frontend dev server if not already running
            try:
                if not dev_ui_alive:
                    logger.info("🧩 Frontend dev server not detected — starting 'npm run dev' in frontend/")
                    env = os.environ.copy()
                    env.setdefault("BROWSER", "none")  # avoid extra tabs from Vite
                    subprocess.Popen(
                        ["npm", "run", "dev"],
                        cwd=str(self.frontend_root),
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    # Give the dev server a brief moment to come up
                    for _ in range(20):  # up to ~10s
                        if self._is_port_alive("http://localhost:5173"):
                            dev_ui_alive = True
                            break
                        time.sleep(0.5)
                else:
                    logger.info("🧩 Frontend dev server detected on http://localhost:5173")
            except Exception as e:
                logger.warning(f"Could not ensure frontend dev server: {e}")

            # Open the dev UI in the browser (current version served by Vite)
            if dev_ui_alive:
                try:
                    webbrowser.open("http://localhost:5173")
                except Exception:
                    pass
            else:
                logger.info("Dev UI is not reachable yet; static prod UI will be available on the API port once built.")
        else:
            # If user launches without --dev but the dev server is already running, prefer opening the current dev UI
            if dev_ui_alive:
                logger.info("🔧 Dev server detected; opening live UI at http://localhost:5173 (API still on %s)", self.port)
                try:
                    webbrowser.open("http://localhost:5173")
                except Exception:
                    pass
            else:
                url = f"http://localhost:{self.port}"
                logger.info(f"🌐 Opening browser: {url}")
                webbrowser.open(url)

        print(f"\n{AETHER_GREEN}✨ Lyrixa is alive. The system breathes.{RESET}\n")

        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            print(f"\n\n{CYAN}🌙 Lyrixa enters rest. Until next awakening.{RESET}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🌌 Lyrixa Launcher - The Living System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python Lyrixa_Launcher.py                    # Launch in production mode
  python Lyrixa_Launcher.py --dev              # Launch in development mode
  python Lyrixa_Launcher.py --port 3000        # Use custom port

The dark field breathes once. The Aetherra symbol ignites.
"Code Awakened."
        """
    )

    parser.add_argument(
        "--port",
        type=int,
        default=3012,
        help="Port for the bridge server (default: 3012)"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (expects React dev server on port 5173)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    # Create and run launcher
    launcher = LyrixaLauncher(port=args.port, dev_mode=args.dev)
    launcher.run()


if __name__ == "__main__":
    main()
