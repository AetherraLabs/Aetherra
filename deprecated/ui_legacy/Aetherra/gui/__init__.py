#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Aetherra GUI compatibility surface.

The public GUI package has been reduced to the supported OS monitor and a small
set of compatibility helpers while the unified Aetherra interface consolidates
under the canonical frontend runtime.
"""

from __future__ import annotations

from .aetherra_os_gui import main as launch_os_monitor

__version__ = "1.1.0"


def create_lyrixa_gui():
    """Temporary compatibility factory for older test and launcher code."""
    from Aetherra.lyrixa.gui.main_window import LyrixaHybridWindow

    return LyrixaHybridWindow()


__all__ = ["launch_os_monitor", "create_lyrixa_gui"]
