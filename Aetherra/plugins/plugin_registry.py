# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for legacy ``plugins.plugin_registry`` imports."""

from __future__ import annotations

from Aetherra.plugins.core.plugin_registry import discover_plugins

__all__ = ["discover_plugins"]
