"""
Simple test to identify where QWidget error occurs
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 DEBUGGING QWIDGET ERROR")
print("=" * 40)


def test_step(step_name, test_func):
    """Test a single step and report results."""
    try:
        print(f"Testing: {step_name}...")
        result = test_func()
        if result:
            print(f"✅ {step_name} - Success")
        else:
            print(f"⚠️ {step_name} - Failed")
        return result
    except Exception as e:
        print(f"❌ {step_name} - Error: {e}")
        return False


def test_basic_imports():
    """Test basic imports without creating objects."""
    from lyrixa.gui import enhanced_lyrixa
    from lyrixa.gui.unified import context_bridge, main

    return True


def test_context_bridge_only():
    """Test ContextBridge creation only."""
    from lyrixa.gui.unified.context_bridge import ContextBridge

    bridge = ContextBridge()
    return bridge is not None


def test_enhanced_window_creation():
    """Test Enhanced Window creation (should fail here)."""
    from lyrixa.gui import EnhancedLyrixaWindow

    window = EnhancedLyrixaWindow()
    return window is not None


def test_unified_launcher_creation():
    """Test Unified Launcher creation."""
    from lyrixa.gui.unified.main import UnifiedLyrixaLauncher

    launcher = UnifiedLyrixaLauncher()
    return launcher is not None


# Run tests step by step
tests = [
    ("Basic Imports", test_basic_imports),
    ("ContextBridge Creation", test_context_bridge_only),
    ("Enhanced Window Creation", test_enhanced_window_creation),
    ("Unified Launcher Creation", test_unified_launcher_creation),
]

for test_name, test_func in tests:
    if not test_step(test_name, test_func):
        print(f"\n❌ Failed at: {test_name}")
        break

print("\n🏁 Debug test complete")
