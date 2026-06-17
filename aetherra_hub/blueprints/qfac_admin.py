"""QFAC admin endpoints (safe/quiet defaults).

Routes:
- GET  /api/qfac/admin/show  -> tools.qfac_admin.do_show()
- POST /api/qfac/admin/reset -> tools.qfac_admin.do_reset()

Security:
- Uses the Hub control authorization policy. Production requires a configured
  control token; local non-production access is allowed when no token is set.

Notes:
- Endpoints reuse the CLI logic and inherit its safe defaults (no live QFAC instance
  unless AETHERRA_QFAC_ADMIN_ENABLE_LIVE=1). This keeps the HTTP layer thin.
"""

from __future__ import annotations

# Standard library imports
import contextlib
import importlib
import io
import os
import time

# Third party imports
from flask import Blueprint, jsonify, request

from ..services.control_auth import authorize_control_request

bp = Blueprint("qfac_admin", __name__)


def _authorize():
    decision = authorize_control_request(request.headers, request.remote_addr)
    if decision.allowed:
        return None
    return jsonify({"ok": False, "error": decision.error}), decision.status_code


def _load_cli_funcs():
    """Load do_show/do_reset from tools.qfac_admin with stdout/stderr suppression.

    Returns (do_show, do_reset) or (None, None) on failure.
    """
    noise = io.StringIO()
    with contextlib.redirect_stdout(noise), contextlib.redirect_stderr(noise):
        try:
            mod = importlib.import_module("tools.qfac_admin")
            return getattr(mod, "do_show", None), getattr(mod, "do_reset", None)
        except Exception:
            return None, None


@bp.get("/api/qfac/admin/show")
def qfac_admin_show():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    do_show, _ = _load_cli_funcs()
    if not callable(do_show):
        resp = jsonify({"available": False, "error": "qfac_admin_unavailable"})
        resp.status_code = 200
        return resp
    # Inherit CLI quiet defaults; ensure AETHERRA_QUIET=1 for any inner imports
    os.environ.setdefault("AETHERRA_QUIET", "1")
    try:
        noise = io.StringIO()
        with contextlib.redirect_stdout(noise), contextlib.redirect_stderr(noise):
            data = do_show()
            # give a moment for any async prints from imported modules
            time.sleep(0.02)
    except Exception as e:
        resp = jsonify({"available": False, "error": str(e)})
        resp.status_code = 200
        return resp
    resp = jsonify(data)
    resp.status_code = 200
    return resp


@bp.post("/api/qfac/admin/reset")
def qfac_admin_reset():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error
    _, do_reset = _load_cli_funcs()
    if not callable(do_reset):
        resp = jsonify({"ok": False, "error": "qfac_admin_unavailable"})
        resp.status_code = 200
        return resp
    os.environ.setdefault("AETHERRA_QUIET", "1")
    try:
        noise = io.StringIO()
        with contextlib.redirect_stdout(noise), contextlib.redirect_stderr(noise):
            res = do_reset()
            time.sleep(0.02)
    except Exception as e:
        resp = jsonify({"ok": False, "error": str(e)})
        resp.status_code = 200
        return resp
    resp = jsonify(res)
    resp.status_code = 200
    return resp
