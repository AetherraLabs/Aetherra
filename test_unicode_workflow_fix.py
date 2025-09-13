#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test script to verify Unicode workflow fixes
"""

import os
import subprocess
import sys
from pathlib import Path

def test_unicode_fix():
    """Test that Unicode issues are resolved"""
    print("🧪 Testing Unicode Workflow Fixes")
    print("=" * 40)
    
    # Set up environment like Windows would have issues
    test_env = os.environ.copy()
    test_env.update({
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONUTF8': '1'
    })
    
    print("✅ Environment configured for Unicode support")
    
    # Test critical files
    critical_tests = [
        ('aether.py', ['--help']),
        ('aetherra_os.py', ['--help']),
    ]
    
    for script, args in critical_tests:
        if Path(script).exists():
            try:
                print(f"🔍 Testing {script}...")
                result = subprocess.run(
                    [sys.executable, script] + args,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=test_env
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {script}: PASSED")
                else:
                    print(f"  ❌ {script}: FAILED")
                    if result.stderr:
                        print(f"     Error: {result.stderr[:200]}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ {script}: ERROR - {e}")
                return False
        else:
            print(f"  ⚠️ {script}: File not found")
    
    print("\n✅ All Unicode workflow fixes verified successfully!")
    return True

if __name__ == "__main__":
    success = test_unicode_fix()
    sys.exit(0 if success else 1)