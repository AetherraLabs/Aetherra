"""Shared operator restrictions for Homeostasis execution paths."""

# Standard library imports
import os


def observe_only_requested() -> bool:
    """An explicit observation request takes precedence over active modes."""
    flag = os.environ.get("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "").strip().lower()
    mode = os.environ.get("AETHERRA_HOMEOSTASIS_MODE", "").strip().lower()
    return flag in {"1", "true", "yes", "on"} or mode == "observe_only"
