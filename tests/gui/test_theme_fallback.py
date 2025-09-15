#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Test that LyrixaBasicWindow applies either theme or fallback stylesheet.

We simulate a missing/empty theme by pointing LYRIXA_THEME to a non-existent name.
Expectation: window.styleSheet() is non-empty due to fallback path.
"""

import os
import sys

from PySide6.QtWidgets import QApplication

# Ensure package import path contains project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_theme_or_fallback_applied():
    os.environ["LYRIXA_THEME"] = "__does_not_exist__"  # force failure path
    os.environ.pop("LYRIXA_USE_PLUGIN_CARDS", None)  # keep legacy UI for test speed

    app = QApplication.instance() or QApplication([])

    from Aetherra.lyrixa.lyrixa_basic_gui import LyrixaBasicWindow  # import after env

    window = LyrixaBasicWindow(ai_chat=None, hub_connector=None, service_registry=None)
    # Even if theme load fails, fallback stylesheet should be set
    ss = window.styleSheet()
    assert isinstance(ss, str)
    assert ss.strip() != "", "Expected non-empty stylesheet (theme or fallback)"

    # Clean up
    window.close()
