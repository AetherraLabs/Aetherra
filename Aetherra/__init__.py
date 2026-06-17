# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Aetherra package public API.

Public objects are imported lazily so importing a focused subsystem does not
initialize AI providers, emit console output, or pull unrelated dependencies.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__version__ = "2.0.0"
__author__ = "Aetherra Development Team"

_LAZY_EXPORTS = {
    "AetherraAgent": ("Aetherra.core.agent", "AetherraAgent"),
    "AetherraInterpreter": (
        "Aetherra.core.aetherra_interpreter",
        "AetherraInterpreter",
    ),
    "AetherraMemory": ("Aetherra.core.memory.base", "AetherraMemory"),
    "AetherraParser": ("Aetherra.core.aetherra_parser", "AetherraParser"),
    "Config": ("Aetherra.core.config", "Config"),
    "PluginIntent": ("Aetherra.core.plugin_manager", "PluginIntent"),
    "PluginMetadata": ("Aetherra.core.plugin_manager", "PluginMetadata"),
    "ask_ai": ("Aetherra.core.ai_runtime", "ask_ai"),
}


def __getattr__(name: str) -> Any:
    """Resolve documented package exports on first access."""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = target
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_LAZY_EXPORTS))


__all__ = [
    "__version__",
    "__author__",
    "Config",
    "AetherraMemory",
    "ask_ai",
    "AetherraInterpreter",
    "AetherraParser",
    "PluginMetadata",
    "PluginIntent",
    "AetherraAgent",
]
