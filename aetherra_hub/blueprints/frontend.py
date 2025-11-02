"""Frontend static file serving blueprint.

Serves the built Lyrixa UI from frontend/dist/ at the root path.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from flask import Blueprint, send_from_directory
from flask.wrappers import Response

logger = logging.getLogger(__name__)

bp = Blueprint("frontend", __name__)

# Determine frontend dist path (dev vs frozen)
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    FRONTEND_DIST = base_path / "Aetherra" / "lyrixa" / "gui" / "dist"
else:
    # Running from source
    base_path = Path(__file__).parent.parent.parent
    FRONTEND_DIST = base_path / "Aetherra" / "lyrixa" / "gui" / "dist"


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def serve_frontend(path: str) -> Response | tuple[str, int]:
    """Serve frontend static files or fallback to index.html for SPA routing."""
    try:
        # Check if frontend dist exists
        if not FRONTEND_DIST.exists():
            logger.warning(
                "[FRONTEND] dist folder not found at %s. "
                "Build frontend with: npm run build",
                FRONTEND_DIST,
            )
            return (
                "<h1>Lyrixa UI Not Available</h1>"
                "<p>Frontend not built. Run <code>npm run build</code> in the frontend/ directory.</p>",
                404,
            )

        # Serve requested file if it exists
        if path and (FRONTEND_DIST / path).exists():
            return send_from_directory(FRONTEND_DIST, path)

        # Fallback to index.html for SPA routing
        index_path = FRONTEND_DIST / "index.html"
        if index_path.exists():
            return send_from_directory(FRONTEND_DIST, "index.html")

        logger.error("[FRONTEND] index.html not found in %s", FRONTEND_DIST)
        return "<h1>Frontend Error</h1><p>index.html not found</p>", 500

    except Exception as e:
        logger.exception("[FRONTEND] Error serving file: %s", e)
        return f"<h1>Error</h1><p>{e}</p>", 500


logger.info("[FRONTEND] Blueprint registered (serving from %s)", FRONTEND_DIST)
