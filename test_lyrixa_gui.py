#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🚀 GUI Test Launcher
====================

Simple test launcher for the new Lyrixa GUI architecture.
Demonstrates the zone-based layout and plugin system.
"""

# Standard library imports
import logging
import sys
from pathlib import Path

# Third party imports
from PySide6.QtWidgets import QApplication

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Aetherra imports
from Aetherra.gui import create_lyrixa_gui


def main():
    """Launch the test GUI."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Lyrixa GUI Test Launcher")

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa GUI Test")
    app.setApplicationVersion("1.0.0-test")
    app.setOrganizationName("Aetherra Labs")

    # Create and configure GUI
    gui = create_lyrixa_gui()

    # Show the window
    gui.show()
    logger.info("GUI launched successfully")

    # Start event loop
    return app.exec()  # nosec B102: Qt application execution


if __name__ == "__main__":
    sys.exit(main())
