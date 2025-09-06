#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Legacy shim retained for backward compatibility; delegates to aetherra_os."""

from aetherra_os import main as os_main

if __name__ == "__main__":  # pragma: no cover
    os_main()
#!/usr/bin/env python3
"""
🌌 Aetherra OS Unicode-Compatible Launcher
=========================================
A launcher that properly handles Unicode characters and emojis on Windows.
"""

import asyncio
import locale
import os
import sys

# Force UTF-8 encoding for all console output
if sys.platform == "win32":
    # Set console code page to UTF-8 on Windows
    os.system("chcp 65001 > nul")

    # Set environment variables for UTF-8 encoding
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

    # Try to set console encoding
    try:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except:
        pass

# Set locale to UTF-8 if possible
try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_ALL, "C.UTF-8")
    except:
        pass


def main():
    """Launch Aetherra OS with proper Unicode support."""
    print("🌌 Launching Aetherra OS with Unicode support...")

    # Import and run the main launcher
    try:
        from aetherra_os_launcher import main as aetherra_main

        return asyncio.run(aetherra_main())
    except Exception as e:
        print(f"❌ Error launching Aetherra OS: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
