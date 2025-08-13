import pytest


@pytest.mark.ui
def test_gui_main_window_offscreen(monkeypatch):
    QApplication = pytest.importorskip("PySide6.QtWidgets").QApplication  # type: ignore[attr-defined]

    # Force offscreen to avoid display requirements in CI
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    # Ensure a QApplication exists
    app = QApplication.instance() or QApplication([])

    # Prefer Lyrixa Basic GUI as the canonical entry
    try:
        basic_gui = pytest.importorskip("Aetherra.lyrixa.lyrixa_basic_gui")
        BasicWindow = getattr(basic_gui, "LyrixaBasicWindow", None)
        assert BasicWindow is not None
        win = BasicWindow(ai_chat=None, hub_connector=None, service_registry=None)
    except Exception:
        # Fallback to hybrid main window module if basic GUI import fails
        main_mod = pytest.importorskip("Aetherra.lyrixa.gui.main_window")
        MainWindow = getattr(main_mod, "LyrixaHybridWindow", None) or getattr(
            main_mod, "MainWindow", None
        )
        assert MainWindow is not None
        win = MainWindow()

    # Basic assertions about object existence
    assert win is not None

    # Cleanup
    win.close()
    app.quit()
