#!/usr/bin/env python3
"""
🧠 LYRIXA INTELLIGENCE INTEGRATION TEST
======================================

Test the full intelligence stack integration in Lyrixa.
This test verifies that all components are properly integrated and functional.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.intelligence_integration import LyrixaIntelligenceStack


async def test_intelligence_stack():
    """Test the complete intelligence stack integration"""
    print("🧠 Testing Lyrixa Intelligence Stack Integration")
    print("=" * 60)

    # Initialize intelligence stack
    workspace_path = str(project_root)
    intelligence_stack = LyrixaIntelligenceStack(workspace_path)

    # Test 1: Initialize Intelligence Layer
    print("\n1️⃣ Testing Intelligence Layer Initialization...")
    try:
        intelligence_result = await intelligence_stack.initialize_intelligence_layer()
        print(f"✅ Intelligence Layer Status: {intelligence_result['status']}")

        if intelligence_result["status"] == "initialized":
            components = intelligence_result["components"]
            active_components = sum(1 for active in components.values() if active)
            print(f"   Active Components: {active_components}/{len(components)}")
            for component, active in components.items():
                status = "✅" if active else "❌"
                print(f"   {status} {component}")
        else:
            print(f"   ❌ Error: {intelligence_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ Intelligence Layer test failed: {e}")

    # Test 2: Initialize System Workflows
    print("\n2️⃣ Testing System Workflows Initialization...")
    try:
        workflow_result = await intelligence_stack.initialize_system_workflows()
        print(f"✅ System Workflows Status: {workflow_result['status']}")

        if workflow_result["status"] == "initialized":
            workflows = workflow_result["workflows"]
            active_workflows = sum(1 for w in workflows.values() if w["active"])
            print(f"   Active Workflows: {active_workflows}/{len(workflows)}")
            for workflow, info in workflows.items():
                status = "✅" if info["active"] else "❌"
                health = info.get("health", "unknown")
                print(f"   {status} {workflow} ({health})")
        else:
            print(f"   ❌ Error: {workflow_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ System Workflows test failed: {e}")

    # Test 3: Initialize System Modules
    print("\n3️⃣ Testing System Modules Initialization...")
    try:
        module_result = await intelligence_stack.initialize_system_modules()
        print(f"✅ System Modules Status: {module_result['status']}")

        if module_result["status"] == "initialized":
            modules = module_result["modules"]
            active_modules = sum(1 for active in modules.values() if active)
            print(f"   Active Modules: {active_modules}/{len(modules)}")
            for module, active in modules.items():
                status = "✅" if active else "❌"
                print(f"   {status} {module}")
        else:
            print(f"   ❌ Error: {module_result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ System Modules test failed: {e}")

    # Test 4: Get Intelligence Status
    print("\n4️⃣ Testing Intelligence Status Retrieval...")
    try:
        status = await intelligence_stack.get_intelligence_status()
        overall_health = status.get("overall_health", 0) * 100
        print(f"✅ Overall System Health: {overall_health:.1f}%")

        # Intelligence Layer Health
        intel_health = status["intelligence_layer"]["health"] * 100
        print(f"   🧠 Intelligence Layer: {intel_health:.1f}%")

        # Workflow Health
        workflow_health = status["system_workflows"]["health"] * 100
        active_workflows = status["system_workflows"]["active_count"]
        print(
            f"   📊 System Workflows: {workflow_health:.1f}% ({active_workflows} active)"
        )

        # Module Health
        module_health = status["system_modules"]["health"] * 100
        active_modules = status["system_modules"]["active_count"]
        print(f"   ⚙️ System Modules: {module_health:.1f}% ({active_modules} active)")

    except Exception as e:
        print(f"❌ Intelligence Status test failed: {e}")

    # Test 5: Run Sample Workflow
    print("\n5️⃣ Testing Workflow Execution...")
    try:
        workflow_result = await intelligence_stack.run_intelligence_workflow(
            "goal_autopilot"
        )
        if workflow_result.get("success", False):
            print(f"✅ Workflow execution successful")
            print(f"   Result: {workflow_result.get('result', 'No result')}")
        else:
            print(
                f"❌ Workflow execution failed: {workflow_result.get('error', 'Unknown')}"
            )
    except Exception as e:
        print(f"❌ Workflow execution test failed: {e}")

    # Test 6: Perform System Reflection
    print("\n6️⃣ Testing System Reflection...")
    try:
        reflection = await intelligence_stack.perform_system_reflection()
        if reflection.get("status") != "error":
            confidence = reflection.get("confidence_score", 0) * 100
            print(f"✅ System Reflection completed with {confidence:.1f}% confidence")

            # Show insights
            insights = reflection.get("insights", [])
            print(f"   💡 Insights Generated: {len(insights)}")
            for i, insight in enumerate(insights[:2], 1):
                print(f"      {i}. {insight}")

            # Show recommendations
            recommendations = reflection.get("recommendations", [])
            print(f"   📋 Recommendations: {len(recommendations)}")
            for i, rec in enumerate(recommendations[:2], 1):
                print(f"      {i}. {rec}")
        else:
            print(
                f"❌ System Reflection failed: {reflection.get('message', 'Unknown')}"
            )
    except Exception as e:
        print(f"❌ System Reflection test failed: {e}")

    # Test Summary
    print("\n" + "=" * 60)
    print("🎯 INTELLIGENCE STACK INTEGRATION TEST SUMMARY")
    print("=" * 60)

    # Calculate final status
    try:
        final_status = await intelligence_stack.get_intelligence_status()
        final_health = final_status.get("overall_health", 0) * 100

        if final_health >= 80:
            print(
                f"🟢 EXCELLENT: Intelligence Stack is fully operational ({final_health:.1f}%)"
            )
        elif final_health >= 60:
            print(
                f"🟡 GOOD: Intelligence Stack is mostly operational ({final_health:.1f}%)"
            )
        else:
            print(
                f"🔴 NEEDS ATTENTION: Intelligence Stack requires maintenance ({final_health:.1f}%)"
            )

        print(f"\n📊 Final Statistics:")
        print(
            f"   • Intelligence Components: {sum(1 for x in final_status['intelligence_layer']['status'].values() if x)}/6"
        )
        print(
            f"   • Active Workflows: {final_status['system_workflows']['active_count']}/5"
        )
        print(
            f"   • Active Modules: {final_status['system_modules']['active_count']}/6"
        )

    except Exception as e:
        print(f"❌ Final status calculation failed: {e}")

    print("\n✅ Intelligence Stack Integration Test Complete!")
    return True


def main():
    """Run the intelligence integration test"""
    print("🚀 Starting Lyrixa Intelligence Integration Test...")

    try:
        result = asyncio.run(test_intelligence_stack())
        if result:
            print("\n🎉 All tests completed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
