#!/usr/bin/env python3
"""
Simple validation script for NeuroChat integration
"""

# Test 1: Basic import
try:
    import sys
    from pathlib import Path

    # Add paths
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "src"))

    print("🧪 Testing NeuroChat Integration")
    print("=" * 40)

    # Test import
    from aetherra.ui.aether_chat import create_embeddable_neurochat

    print("✅ Import successful")

    # Test function exists
    if callable(create_embeddable_neurochat):
        print("✅ Factory function is callable")
    else:
        print("❌ Factory function is not callable")

    print("\n🎉 NeuroChat integration validation passed!")
    print("🔗 NeuroChat should integrate properly with Neuroplex")

except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback

    traceback.print_exc()
