#!/usr/bin/env python3
"""
NeuroCode UI Verification Script
===============================

This script verifies that the UI subsystem works correctly with
all the fixes applied, ensuring proper fallbacks are available.
"""

import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ui_verification")

# Add parent directory to path to allow importing src
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def check_syntax():
    """Check syntax of all UI files"""
    logger.info("Checking syntax of UI files...")
    ui_dir = "src/neurocode/ui"
    errors = 0
    for f in os.listdir(ui_dir):
        if f.endswith(".py"):
            file_path = f"{ui_dir}/{f}"
            logger.info(f"Checking {f}...")
            try:
                with open(file_path, "r") as file:
                    compile(file.read(), file_path, "exec")
                logger.info(f"✓ {f} syntax OK")
            except SyntaxError as e:
                errors += 1
                logger.error(f"✗ Syntax error in {f}: {e}")
    return errors == 0


def verify_imports():
    """Verify that all critical UI modules can be imported"""
    logger.info("Verifying critical UI imports...")

    try:
        from src.aethercode.ui import (
            BASIC_UI_AVAILABLE,
            NEUROPLEX_AVAILABLE,
            QT_AVAILABLE,
        )

        logger.info(f"Qt Available: {QT_AVAILABLE}")
        logger.info(f"Neuroplex Available: {NEUROPLEX_AVAILABLE}")
        logger.info(f"Basic UI Available: {BASIC_UI_AVAILABLE}")

        # Check that we can get a window
        from src.aethercode.ui import get_main_window

        window = get_main_window()
        logger.info(f"Main window created: {type(window).__name__}")

        # Test fallback UI
        from src.aethercode.ui.fallback_ui import FallbackUI

        fallback = FallbackUI()
        logger.info("Fallback UI available")

        # Check safe UI calls
        from src.aethercode.ui.safe_ui_calls import UIErrorHandler, safe_call

        logger.info("Safe UI calls available")

        return True
    except Exception as e:
        logger.error(f"Import verification failed: {e}")
        return False


def verify_launch_function():
    """Verify the launch_gui function works but don't actually launch UI"""
    logger.info("Verifying launch_gui function...")

    try:
        # Just import the function, don't call it
        from src.aethercode.ui import launch_gui

        logger.info("launch_gui function is available")
        return True
    except Exception as e:
        logger.error(f"launch_gui verification failed: {e}")
        return False


def main():
    logger.info("=== NeuroCode UI Verification ===")

    # Run verification tests
    syntax_ok = check_syntax()
    imports_ok = verify_imports()
    launch_ok = verify_launch_function()

    # Summary
    logger.info("\n=== Verification Results ===")
    logger.info(f"Syntax Check: {'✓ PASS' if syntax_ok else '✗ FAIL'}")
    logger.info(f"Imports Check: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    logger.info(f"Launch Function: {'✓ PASS' if launch_ok else '✗ FAIL'}")

    if syntax_ok and imports_ok and launch_ok:
        logger.info("\n✅ ALL CHECKS PASSED - UI system is ready!")
        return 0
    else:
        logger.error("\n❌ VERIFICATION FAILED - See logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
