#!/usr/bin/env python3
"""
Test launcher GUI detection only
"""

import sys
sys.path.append('Aetherra')

from lyrixa.launcher import LyrixaOperatingSystem

# Test GUI detection
lyrixa_os = LyrixaOperatingSystem()
gui_class = lyrixa_os._find_best_gui_class()

print(f"[RESULT] GUI Class Found: {gui_class.__name__ if gui_class else None}")

if gui_class:
    print(f"[RESULT] Module: {gui_class.__module__}")
    print(f"[RESULT] Phase 2 Expected: lyrixa_core.gui.main_window")

    if gui_class.__module__ == "lyrixa_core.gui.main_window":
        print("[SUCCESS] Launcher correctly detects Phase 2 GUI!")
    else:
        print("[WARNING] Launcher detected different GUI than expected")
else:
    print("[ERROR] No GUI class detected")
