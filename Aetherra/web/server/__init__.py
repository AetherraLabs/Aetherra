"""
🖥️ Aetherra Web Server
======================
Web server components for the Aetherra web interface.

This package provides:
- Web interface server implementations
- Web adapters for integration with Aetherra core
- Bridge components for web-to-core communication
- Static file and template serving

Key Components:
- WebInterfaceAdapter: Core integration adapter
- Web bridge implementations
- Server configuration and management
"""

import logging

logger = logging.getLogger(__name__)

# Server system status
SERVER_SYSTEMS = {"adapter": False, "bridge": False, "interface_server": False}


def get_server_status():
    """Get current server system status."""
    return {
        "systems": SERVER_SYSTEMS.copy(),
        "total_systems": len(SERVER_SYSTEMS),
        "active_systems": sum(SERVER_SYSTEMS.values()),
        "health": "healthy" if any(SERVER_SYSTEMS.values()) else "inactive",
    }


# Lazy imports for server components
def get_web_adapter():
    """Get the web interface adapter."""
    try:
        from .web_adapter import web_adapter

        SERVER_SYSTEMS["adapter"] = True
        return web_adapter
    except ImportError as e:
        logger.warning(f"Failed to import WebInterfaceAdapter: {e}")
        return None


def get_web_bridge():
    """Get the web bridge components."""
    try:
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.web.server.web_bridge")
        if spec is not None:
            SERVER_SYSTEMS["bridge"] = True
            return True
        return False
    except ImportError as e:
        logger.warning(f"Failed to import web bridge: {e}")
        return None


def get_interface_server():
    """Get the web interface server."""
    try:
        import importlib.util

        spec = importlib.util.find_spec("Aetherra.web.server.web_interface_server")
        if spec is not None:
            SERVER_SYSTEMS["interface_server"] = True
            return True
        return False
    except ImportError as e:
        logger.warning(f"Failed to import interface server: {e}")
        return None


# Initialize server systems
def initialize_server_systems():
    """Initialize web server components."""
    logger.info("🖥️ Initializing Aetherra Web Server...")

    # Check adapter availability
    adapter = get_web_adapter()
    if adapter:
        logger.info("[OK] Web adapter available")

    # Check bridge availability
    bridge = get_web_bridge()
    if bridge:
        logger.info("[OK] Web bridge available")

    # Check interface server availability
    server = get_interface_server()
    if server:
        logger.info("[OK] Interface server available")

    active_count = sum(SERVER_SYSTEMS.values())
    total_count = len(SERVER_SYSTEMS)
    logger.info(f"🖥️ Web Server: {active_count}/{total_count} components active")

    return SERVER_SYSTEMS


# Auto-initialize on import
try:
    initialize_server_systems()
except Exception as e:
    logger.error(f"❌ Failed to initialize server systems: {e}")

__all__ = [
    "get_server_status",
    "get_web_adapter",
    "get_web_bridge",
    "get_interface_server",
    "initialize_server_systems",
    "SERVER_SYSTEMS",
]
