#!/usr/bin/env python3
"""Test modified files to ensure they can be imported."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_module(module_path):
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Module {module_path} imports successfully")
        return True
    except Exception as e:
        print(f"❌ Module {module_path} import error: {e}")
        return False


# Test neuro_chat.py
neuro_chat_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src",
    "Aetherra",
    "ui",
    "neuro_chat.py",
)
check_module(neuro_chat_path)

# Test aetherplex.py
aetherplex_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "src", "Aetherra", "ui", "aetherplex.py"
)
check_module(aetherplex_path)
