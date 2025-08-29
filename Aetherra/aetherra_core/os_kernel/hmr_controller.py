"""Forwarder to the current HMR controller implementation.

This allows importing HMR APIs from Aetherra.aetherra_core.os_kernel without
moving the implementation yet.
"""

from aetherra_hmr_controller import (  # type: ignore
    HMRController,
    get_hmr_controller,
)

__all__ = [
    "HMRController",
    "get_hmr_controller",
]
