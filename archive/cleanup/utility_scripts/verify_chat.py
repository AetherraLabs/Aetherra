#!/usr/bin/env python3
"""Simple test script to verify advanced chat integration"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "src" / "aetherra" / "ui"))

print("🧪 Testing Advanced NeuroChat Integration")
print("=" * 50)

# Test 1: NeuroChat Import
try:
    from neuro_chat import NeuroChatInterface

    print("✅ NeuroChat interface imported successfully")
    neurochat_ok = True
except ImportError as e:
    print(f"❌ Failed to import NeuroChat interface: {e}")
    neurochat_ok = False

# Test 2: Chat Router Import
try:
    from chat_router import aetherraChatRouter

    print("✅ Chat router imported successfully")
    router_ok = True
except ImportError as e:
    print(f"❌ Failed to import chat router: {e}")
    router_ok = False

# Test 3: Aetherra Integration
try:
    import Aetherra

    print("✅ Aetherra module loaded successfully")
    if hasattr(Aetherra, "NEUROCHAT_AVAILABLE") and Aetherra.aetherCHAT_AVAILABLE:
        print("✅ Advanced NeuroChat interface is AVAILABLE in Aetherra")
        Aetherra_ok = True
    else:
        print("❌ Advanced NeuroChat interface is NOT available in Aetherra")
        Aetherra_ok = False
except Exception as e:
    print(f"❌ Failed to load Aetherra: {e}")
    Aetherra_ok = False

print()
print("=" * 50)
if neurochat_ok and router_ok and Aetherra_ok:
    print("🎉 ALL TESTS PASSED! Advanced NeuroChat is fully integrated!")
    print("💬 The system is using the advanced chat interface, NOT built-in fallback.")
else:
    print("⚠️  Some tests failed. Check above for details.")
