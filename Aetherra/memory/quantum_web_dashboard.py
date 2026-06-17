# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for legacy ``memory.quantum_web_dashboard`` imports."""

from __future__ import annotations

from Aetherra.aetherra_core.memory.quantum_web_dashboard import app

__all__ = ["app"]
