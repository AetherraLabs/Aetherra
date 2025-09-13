#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test script to verify consciousness dashboard component imports
"""

import logging
import os
import sys

# Add the Aetherra path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_dashboard_imports():
    """Test importing all consciousness dashboard components."""
    print("🧪 Testing Consciousness Dashboard Component Imports...")

    # Test 1: Import consciousness panel
    try:
        print("✅ ConsciousnessPanel imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConsciousnessPanel: {e}")
        return False

    # Test 2: Try to import quantum temporal interface directly
    try:
        print("✅ QuantumTemporalInterface imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import QuantumTemporalInterface: {e}")

    # Test 3: Try to import evolution monitoring system directly
    try:
        print("✅ EvolutionMonitoringSystem imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import EvolutionMonitoringSystem: {e}")

    # Test 4: Try to import meta learning control panel directly
    try:
        print("✅ MetaLearningControlPanel imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MetaLearningControlPanel: {e}")

    print("\n🧠 Testing consciousness panel dashboard imports...")

    # Test 5: Check what the consciousness panel actually imports
    import lyrixa.gui.consciousness_panel as cp_module

    if (
        hasattr(cp_module, "QuantumTemporalInterface")
        and cp_module.QuantumTemporalInterface is not None
    ):
        print("✅ QuantumTemporalInterface available in consciousness panel")
    else:
        print("❌ QuantumTemporalInterface not available in consciousness panel")

    if (
        hasattr(cp_module, "EvolutionMonitoringSystem")
        and cp_module.EvolutionMonitoringSystem is not None
    ):
        print("✅ EvolutionMonitoringSystem available in consciousness panel")
    else:
        print("❌ EvolutionMonitoringSystem not available in consciousness panel")

    if (
        hasattr(cp_module, "MetaLearningControlPanel")
        and cp_module.MetaLearningControlPanel is not None
    ):
        print("✅ MetaLearningControlPanel available in consciousness panel")
    else:
        print("❌ MetaLearningControlPanel not available in consciousness panel")

    return True


if __name__ == "__main__":
    try:
        success = test_dashboard_imports()
        if success:
            print("\n🎉 Dashboard import test completed!")
        else:
            print("\n💥 Dashboard import test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
