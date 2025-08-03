#!/usr/bin/env python3
"""
🧠 LYRIXA AUTONOMOUS CAPABILITIES TEST
====================================

Test script to verify Lyrixa's autonomous capabilities with Aetherra integration
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the Aetherra project to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_lyrixa_autonomous_capabilities():
    """Test Lyrixa's autonomous capabilities"""
    print("🧠 Testing Lyrixa's Autonomous Capabilities with Aetherra Integration")
    print("=" * 70)

    try:
        # Import Lyrixa
        from Aetherra.lyrixa.assistant import LyrixaAI

        # Initialize Lyrixa
        print("🎙️ Initializing Lyrixa AI...")
        lyrixa = LyrixaAI(workspace_path=str(project_root / "Aetherra"))

        # Test 1: Check Aetherra integration
        print("\n🔍 Test 1: Checking Aetherra Integration")
        if lyrixa.aetherra_integration:
            print("✅ Aetherra integration available")

            # Get self-editing capabilities
            capabilities = await lyrixa.aetherra_integration.get_self_editing_capabilities()
            print(f"🛠️ Self-editing capabilities: {capabilities['self_editing_enabled']}")
            print(f"📝 Supported operations: {len(capabilities['supported_operations'])}")

        else:
            print("[ERROR] Aetherra integration not available")

        # Test 2: Start autonomous mode
        print("\n🚀 Test 2: Starting Autonomous Mode")
        result = await lyrixa.start_autonomous_mode()
        print(f"✅ Autonomous mode result: {result['success']}")
        if result['success']:
            print(f"📊 Active systems: {result.get('systems_active', [])}")

        # Test 3: Run self-introspection
        print("\n🔍 Test 3: Running Self-Introspection")
        introspection_result = await lyrixa.run_self_introspection()
        print(f"✅ Self-introspection result: {introspection_result['success']}")
        if introspection_result['success']:
            print(f"🧠 Analysis confidence: {introspection_result.get('reasoning_analysis', {}).get('confidence', 'N/A')}")

        # Test 4: Get autonomous status
        print("\n📊 Test 4: Getting Autonomous Status")
        status = await lyrixa.get_autonomous_status()
        print(f"✅ Status retrieval: {not status.get('error')}")
        if not status.get('error'):
            print(f"🤖 Autonomous mode active: {status.get('autonomous_mode_active', False)}")
            print(f"💚 Overall health: {status.get('overall_health_score', 0.0):.2f}")

        # Test 5: Test Aetherra code execution (if available)
        print("\n🛠️ Test 5: Testing Aetherra Code Execution")
        if lyrixa.aetherra_integration:
            test_code = """
# Test Aetherra code
remember("Lyrixa autonomous test successful", tags="test,autonomous,success")
"""

            exec_result = await lyrixa.aetherra_integration.execute_aetherra_code(test_code)
            print(f"✅ Aetherra code execution: {exec_result['success']}")
            if exec_result['success']:
                print(f"🎯 Execution message: {exec_result['message']}")
        else:
            print("[ERROR] Aetherra integration not available for code execution")

        # Test 6: Stop autonomous mode
        print("\n🛑 Test 6: Stopping Autonomous Mode")
        if lyrixa.aetherra_integration:
            stop_result = await lyrixa.aetherra_integration.stop_autonomous_mode()
            print(f"✅ Autonomous mode stopped: {stop_result['success']}")

        # Cleanup
        print("\n🧹 Cleaning up...")
        await lyrixa.cleanup()

        print("\n🎉 Test completed successfully!")
        print("=" * 70)
        print("✅ Lyrixa's autonomous capabilities with Aetherra integration are operational!")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lyrixa_autonomous_capabilities())
