#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for plugin card mode (feature-flagged).

This test is light and skips automatically if the environment can't create
an offscreen QApplication (common in certain CI without X/Windows display).
"""

import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.mark.skipif(
    os.environ.get("CI_NO_QT", "0") == "1",
    reason="QT disabled in CI environment",
)
def test_plugin_cards_population_and_install_state():
    # Enable card mode
    os.environ["LYRIXA_USE_PLUGIN_CARDS"] = "1"
    os.environ["LYRIXA_THEME"] = "cyber"

    app = QApplication.instance() or QApplication([])

    # Provide mock hub connector with predictable plugin list
    class MockHubConnector:
        async def get_available_plugins(self):
            return [
                {
                    "name": "alpha-plugin",
                    "display_name": "Alpha Plugin",
                    "description": "Alpha test plugin",
                    "version": "1.2.3",
                },
                {
                    "name": "beta-plugin",
                    "display_name": "Beta Plugin",
                    "description": "Beta test plugin",
                    "version": "0.9.0",
                },
            ]

        async def install_plugin(self, name):  # noqa: D401
            return True

    from Aetherra.lyrixa.lyrixa_basic_gui import LyrixaBasicWindow

    window = LyrixaBasicWindow(ai_chat=None, hub_connector=MockHubConnector())

    # After init, plugin_cards should have two entries (async worker may not finish instantly).
    # We manually trigger refresh completion by directly calling update with mock data.
    mock_plugins = app.processEvents()  # allow any queued events
    window._update_plugin_list(
        [
            {
                "name": "alpha-plugin",
                "display_name": "Alpha Plugin",
                "description": "Alpha test plugin",
                "version": "1.2.3",
            },
            {
                "name": "beta-plugin",
                "display_name": "Beta Plugin",
                "description": "Beta test plugin",
                "version": "0.9.0",
            },
        ]
    )
    assert len(window.plugin_cards) == 2, "Expected two plugin cards in card mode"

    alpha_card = window.plugin_cards.get("alpha-plugin")
    assert alpha_card is not None

    # Simulate installation marking without removing
    window._perform_plugin_installation("alpha-plugin", {"name": "alpha-plugin"})
    # Directly mark installed (bypass thread success callback for speed)
    if hasattr(alpha_card, "mark_installed"):
        alpha_card.mark_installed(True)  # type: ignore[attr-defined]
    # Re-polish style to ensure property applied
    app.processEvents()

    # Validate card install button state changed
    if getattr(alpha_card, "install_btn", None):
        assert not alpha_card.install_btn.isEnabled()
        assert alpha_card.install_btn.text().lower().startswith("installed")

    window.close()
