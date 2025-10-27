"""Aetherra Hub package initializer.

Avoid importing the Flask app or blueprints at package import time to prevent
import‑time side effects and circular imports. Expose a lightweight wrapper for
create_app that imports the real factory lazily when invoked.
"""

from __future__ import annotations

# No additional imports here to avoid import-time side effects


def create_app(*args, **kwargs):  # type: ignore[override]
    """Lazy app factory import to avoid import‑time side effects.

    This indirection breaks cycles such as:
    homeostasis_core -> stability_metrics -> aetherra_hub.services.registry_client
    -> aetherra_hub (this module) -> app -> blueprints.homeostasis ->
    homeostasis_integration -> homeostasis_core (partially initialized).
    """
    from .app import create_app as _create_app  # local import

    return _create_app(*args, **kwargs)


__all__ = ["create_app"]
