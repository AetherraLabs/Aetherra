#!/usr/bin/env python3
"""
Test script for the integration fix
"""
import sys
sys.path.insert(0, '.')

try:
    from Aetherra.simplified_lyrixa_aetherra_integration import SimplifiedLyrixaAetherraIntegration

    # Create instance
    integration = SimplifiedLyrixaAetherraIntegration()

    print("✅ Integration created successfully")
    print(f"Engines available: {integration.engines_available}")
    print(f"Reasoning engine type: {type(integration.reasoning_engine)}")

    # Test the autonomous status
    import asyncio
    async def test():
        status = await integration.get_autonomous_status()
        print(f"✅ Autonomous status engines available: {status['engines_available']}")

        # Test initial self-analysis
        print("🔍 Testing autonomous mode activation...")
        result = await integration.start_autonomous_mode()
        print(f"✅ Autonomous mode result: {result['success']}")

    asyncio.run(test())

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
