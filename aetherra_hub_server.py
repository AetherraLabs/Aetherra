#!/usr/bin/env python3
"""Deprecated monolithic hub server shim.

Legacy implementation removed. This module now only re-exports the
compatibility layer for backward compatibility. Migrate imports to:

    from aetherra_hub import create_app
    # or
    from aetherra_hub.compat import AetherraHubServer, start_hub_server

Safe to delete after migration.
"""

from __future__ import annotations

# Standard library imports
import warnings

try:  # optional legacy flag
    # Third party imports
    from flask import Flask  # type: ignore  # noqa: F401

    FLASK_AVAILABLE = True
except Exception:  # pragma: no cover
    FLASK_AVAILABLE = False  # type: ignore

# Aetherra imports
from aetherra_hub.compat import AetherraHubServer, start_hub_server  # noqa: F401

warnings.filterwarnings("once", category=DeprecationWarning, module=__name__)
warnings.warn(
    "aetherra_hub_server is deprecated; use aetherra_hub.compat or aetherra_hub.create_app instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["AetherraHubServer", "start_hub_server", "FLASK_AVAILABLE"]
