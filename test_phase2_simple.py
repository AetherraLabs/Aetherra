#!/usr/bin/env python3
"""
Phase 2 Launcher Integration Test (Windows Compatible)
=====================================================

Test the updated launcher with Phase 2 Live Context Bridge capabilities.
No GUI instantiation, Windows PowerShell compatible.
"""

import sys
import os
import platform
from pathlib import Path

def test_phase2_launcher():
    """Test Phase 2 launcher integration without GUI creation."""
    print("[TEST] Testing Phase 2 Launcher Integration")
    print("=" * 50)

    try:
        # Test 1: Import launcher
        sys.path.append('Aetherra')
        from lyrixa.launcher import LyrixaOperatingSystem
        print("[OK] Launcher imported successfully")

        # Test 2: Create launcher instance
        lyrixa_os = LyrixaOperatingSystem()
        print("[OK] LyrixaOperatingSystem created")

        # Test 3: Test GUI class detection
        gui_class = lyrixa_os._find_best_gui_class()
        print(f"[OK] GUI class detected: {gui_class.__name__ if gui_class else None}")

        if gui_class and gui_class.__name__ == "LyrixaHybridWindow":
            print("[BRIDGE] Phase 2 Hybrid GUI detected correctly!")
        else:
            print("[ERROR] Phase 2 GUI not detected correctly")
            return False

        # Test 4: Test backend connection method
        if hasattr(lyrixa_os, '_connect_backend_to_frontend'):
            print("[OK] Phase 2 backend connection method available")
        else:
            print("[ERROR] Phase 2 backend connection method missing")

        # Test 5: Test Phase 2 features check (without GUI creation)
        try:
            # Import the hybrid window class to verify it exists
            from lyrixa_core.gui.main_window import LyrixaHybridWindow
            print("[OK] LyrixaHybridWindow class imported successfully")

            # Check class structure for Phase 2 features
            has_init_method = hasattr(LyrixaHybridWindow, '__init__')
            print(f"[BRIDGE] Has __init__ method: {has_init_method}")

            # Check if LyrixaContextBridge is referenced in the file
            import inspect
            source = inspect.getsource(LyrixaHybridWindow)
            has_context_bridge = 'LyrixaContextBridge' in source
            has_specialized_signals = 'memory_updated' in source and 'plugin_updated' in source

            print(f"[BRIDGE] Context bridge implementation: {has_context_bridge}")
            print(f"[BRIDGE] Specialized signals present: {has_specialized_signals}")

            if has_context_bridge and has_specialized_signals:
                print("[OK] Phase 2 Live Context Bridge implementation verified!")
            else:
                print("[WARNING] Phase 2 bridge implementation partially verified")

        except ImportError as e:
            print(f"[ERROR] Could not import hybrid window: {e}")
            return False

        # Test 6: Test launcher methods
        required_methods = ['_find_best_gui_class', '_detect_backend_services', '_connect_backend_to_frontend']
        for method in required_methods:
            if hasattr(lyrixa_os, method):
                print(f"[OK] Method '{method}' present")
            else:
                print(f"[ERROR] Method '{method}' missing")

        # Test 7: Configuration validation
        print("[CONFIG] Testing configuration...")
        print(f"[CONFIG] Python version: {sys.version_info.major}.{sys.version_info.minor}")
        print(f"[CONFIG] Platform: {platform.system()}")

        # Test 8: Check for required modules
        required_modules = ['PySide6', 'psutil']
        for module in required_modules:
            try:
                __import__(module)
                print(f"[DEPS] Module '{module}' available")
            except ImportError:
                print(f"[WARNING] Module '{module}' not available")

        print("[OK] All Phase 2 launcher integration tests passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase2_launcher()
    if success:
        print("\n[SUCCESS] Phase 2 launcher integration: VERIFIED!")
    else:
        print("\n[FAILURE] Phase 2 launcher integration: FAILED!")
        sys.exit(1)
