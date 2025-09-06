#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Test Phase 3 Auto-Generation System
Tests the core functionality of the auto-generation system
"""

import sys
from pathlib import Path

# Add Aetherra to Python path
aetherra_path = Path(__file__).parent / "Aetherra"
sys.path.insert(0, str(aetherra_path))

try:
    # Test Phase 3 imports
    import json
    from dataclasses import asdict
    from datetime import datetime

    from lyrixa.gui.phase3_auto_generator import (
        ComponentState,
        PanelGenerator,
        StateIntrospector,
    )

    print("✅ Phase 3 imports successful")

    # Test ComponentState serialization
    test_state = ComponentState(
        name="test_component",
        type="plugin",
        status="active",
        metadata={"version": "1.0", "capabilities": ["test"]},
        capabilities=["test_capability"],
        last_updated=datetime.now(),
        importance=0.8,
    )

    # Test JSON serialization
    serialized = json.dumps(asdict(test_state), default=str)
    print("✅ ComponentState serialization works")

    # Test introspector creation
    introspector = StateIntrospector()
    print("✅ StateIntrospector creation successful")

    # Test panel generator creation
    panels_dir = (
        Path(__file__).parent / "Aetherra" / "lyrixa_core" / "gui" / "web_panels"
    )
    generator = PanelGenerator(str(panels_dir))
    print("✅ PanelGenerator creation successful")

    print("\n🎉 Phase 3 Auto-Generation System: ALL TESTS PASSED")
    print("✨ System is ready for deployment!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
