# SPDX-License-Identifier: GPL-3.0-or-later
"""Legacy compatibility shim for tests importing `from gui.main_window import LyrixaHybridWindow`.
Re-exports the stub window from `Aetherra.lyrixa.gui.main_window`.
"""

from Aetherra.lyrixa.gui.main_window import LyrixaHybridWindow, MainWindow  # noqa: F401
