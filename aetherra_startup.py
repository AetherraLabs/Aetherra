# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
DEPRECATED: aetherra_startup.py
--------------------------------
This legacy bootstrap is no longer used by the Aetherra OS.

Use one of these instead:
- aetherra_os_launcher.py (GUI-capable)
- aetherra_os.py (headless)

This file remains only as a compatibility forwarder and will be removed.
"""

from __future__ import annotations

import sys
import traceback


def aetherra_startup() -> bool:
    try:
        # Prefer headless OS entrypoint to avoid accidental GUI
        import aetherra_os as _os  # type: ignore

        if hasattr(_os, "main"):
            _os.main()
        else:
            raise RuntimeError("aetherra_os has no main() entrypoint")
        return True
    except Exception:
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = aetherra_startup()
    sys.exit(0 if ok else 1)
