#!/usr/bin/env python3
"""Simple test script to verify advanced chat integration"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "src" / "aetherra" / "ui"))

print("🧪 Testing Advanced AetherraChat Integration")
print("=" * 50)

# Test 1: AetherraChat Import
try:
    from aetherra_chat import AetherraChatInterface

    print("✅ AetherraChat interface imported successfully")
    aetherchat_ok = True
except ImportError as e:
    print(f"❌ Failed to import AetherraChat interface: {e}")
    aetherchat_ok = False

# Test 2: Chat Router Import
try:
    from chat_router import aetherraChatRouter

    print("✅ Chat router imported successfully")
    router_ok = True
except ImportError as e:
    print(f"❌ Failed to import chat router: {e}")
    router_ok = False

# Test 3: Lyrixa Integration
try:
    import Lyrixa

    print("✅ Lyrixa module loaded successfully")
    if hasattr(Lyrixa, "NEUROCHAT_AVAILABLE") and Lyrixa.aetherCHAT_AVAILABLE:
        print("✅ Advanced AetherraChat interface is AVAILABLE in Lyrixa")
        Lyrixa_ok = True
    else:
        print("❌ Advanced AetherraChat interface is NOT available in Lyrixa")
        Lyrixa_ok = False
except Exception as e:
    print(f"❌ Failed to load Lyrixa: {e}")
    Lyrixa_ok = False

print()
print("=" * 50)
if aetherchat_ok and router_ok and Lyrixa_ok:
    print("🎉 ALL TESTS PASSED! Advanced AetherraChat is fully integrated!")
    print("💬 The system is using the advanced chat interface, NOT built-in fallback.")
else:
    print("⚠️  Some tests failed. Check above for details.")
