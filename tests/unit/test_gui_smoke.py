# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import os

import pytest


@pytest.mark.ui
def test_gui_main_window_offscreen(monkeypatch):
    # Gate execution unless explicitly enabled. Use os.getenv because monkeypatch fixture
    # does not provide a getenv accessor (only setenv/delenv helpers).
    if not os.getenv("AETHERRA_RUN_GUI_TESTS"):
        pytest.skip("GUI tests disabled (set AETHERRA_RUN_GUI_TESTS=1 to enable)")
    qapplication_cls = pytest.importorskip("PySide6.QtWidgets").QApplication  # type: ignore[attr-defined]

    # Force offscreen to avoid display requirements in CI
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    # Ensure a QApplication exists
    app = qapplication_cls.instance() or qapplication_cls([])

    # Prefer Lyrixa Basic GUI as the canonical entry
    try:
        basic_gui = pytest.importorskip("Aetherra.lyrixa.lyrixa_basic_gui")
        basic_window_cls = getattr(basic_gui, "LyrixaBasicWindow", None)
        assert basic_window_cls is not None
        win = basic_window_cls(ai_chat=None, hub_connector=None, service_registry=None)
    except Exception:
        # Fallback to hybrid main window module if basic GUI import fails
        main_mod = pytest.importorskip("Aetherra.lyrixa.gui.main_window")
        main_window_cls = getattr(main_mod, "LyrixaHybridWindow", None) or getattr(
            main_mod, "MainWindow", None
        )
        assert main_window_cls is not None
        win = main_window_cls()

    # Basic assertions about object existence
    assert win is not None

    # Cleanup
    win.close()
    app.quit()
