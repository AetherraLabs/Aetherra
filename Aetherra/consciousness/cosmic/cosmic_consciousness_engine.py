# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Shim module for backward compatibility.
# Canonical engine remains implemented at project root for now to avoid breaking imports.
# After quarantine/grace period, consider moving implementation fully here and turning the root into a thin shim.

from __future__ import annotations

# Standard library imports
# Re-export the class from the legacy root module (project root)
import importlib as _importlib

_legacy = _importlib.import_module("cosmic_consciousness_engine")
CosmicConsciousnessEngine = _legacy.CosmicConsciousnessEngine
__all__ = ["CosmicConsciousnessEngine"]
