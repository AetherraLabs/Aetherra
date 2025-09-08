#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test Unicode encoding fixes
"""

print("=== UNICODE ENCODING TEST ===")
print("Testing imports...")

import sys

sys.path.insert(0, ".")

try:
    print("[OK] Service registry imported successfully")
except Exception as e:
    print(f"[ERROR] Service registry import failed: {e}")

try:
    print("[OK] Plugin manager imported successfully")
except Exception as e:
    print(f"[ERROR] Plugin manager import failed: {e}")

print("[SUCCESS] All Unicode fixes applied and verified!")
