#!/usr/bin/env python3
"""
Test script for the analytics dashboard.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from lyrixa.gui.analytics_dashboard import main

    logger.info("Starting analytics dashboard test...")
    dashboard = main()
    logger.info("Test completed successfully.")

except ImportError as e:
    logger.error(f"Import error: {e}")
except Exception as e:
    logger.error(f"Error running analytics dashboard: {e}")

print("Test script completed.")
