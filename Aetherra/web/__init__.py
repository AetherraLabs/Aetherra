"""
🌐 Aetherra Web Interface
========================
Web-based user interface and server components for Aetherra.

This package provides:
- Web server components and interfaces
- Static file serving
- Template rendering
- Web bridge integration with Aetherra core

Components:
- Web server implementations
- Component libraries
- Static assets and templates
"""

import logging

logger = logging.getLogger(__name__)

# Web system status
WEB_SYSTEMS = {
    "server": False,
    "components": False,
    "static": False,
    "templates": False,
}


def get_web_status():
    """Get current web system status."""
    return {
        "systems": WEB_SYSTEMS.copy(),
        "total_systems": len(WEB_SYSTEMS),
        "active_systems": sum(WEB_SYSTEMS.values()),
        "health": "healthy" if any(WEB_SYSTEMS.values()) else "inactive",
    }


# Initialize web systems
def initialize_web_systems():
    """Initialize web system components."""
    logger.info("🌐 Initializing Aetherra Web Interface...")

    # Check server availability
    try:
        from . import server

        WEB_SYSTEMS["server"] = True
        logger.info("[OK] Web server available")
    except ImportError:
        logger.warning("[WARN] Web server not available")

    # Check components availability
    try:
        from . import components

        WEB_SYSTEMS["components"] = True
        logger.info("[OK] Web components available")
    except ImportError:
        logger.warning("[WARN] Web components not available")

    # Check static files
    from pathlib import Path

    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        WEB_SYSTEMS["static"] = True
        logger.info("[OK] Static files available")
    else:
        logger.warning("[WARN] Static files not available")

    # Check templates
    templates_path = Path(__file__).parent / "templates"
    if templates_path.exists():
        WEB_SYSTEMS["templates"] = True
        logger.info("[OK] Templates available")
    else:
        logger.warning("[WARN] Templates not available")

    active_count = sum(WEB_SYSTEMS.values())
    total_count = len(WEB_SYSTEMS)
    logger.info(f"🌐 Web Interface: {active_count}/{total_count} systems active")

    return WEB_SYSTEMS


# Auto-initialize on import
try:
    initialize_web_systems()
except Exception as e:
    logger.error(f"❌ Failed to initialize web systems: {e}")

__all__ = ["get_web_status", "initialize_web_systems", "WEB_SYSTEMS"]
