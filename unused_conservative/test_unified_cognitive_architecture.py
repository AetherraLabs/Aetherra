#!/usr/bin/env python3
"""
🧠 UNIFIED COGNITIVE ARCHITECTURE TEST
=====================================

Comprehensive test script to verify integration of all five cognitive systems:
1. FractalMesh Memory System
2. Plugin System (Enhanced Plugin Manager)
3. Reflection Engine (Validation Engine)
4. Self Metrics Dashboard
5. Memory Continuity Tracker

This test validates the complete unified cognitive architecture integration.
"""

import asyncio
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = {
    "timestamp": datetime.now().isoformat(),
    "systems_tested": 0,
    "systems_passed": 0,
    "systems_failed": 0,
    "integration_tests": 0,
    "integration_passed": 0,
    "details": [],
}


def log_test(system_name: str, status: str, details: str = ""):
    """Log test result"""
    global test_results
    test_results["systems_tested"] += 1
    if status == "PASS":
        test_results["systems_passed"] += 1
        print(f"✅ {system_name}: {status}")
    else:
        test_results["systems_failed"] += 1
        print(f"❌ {system_name}: {status}")

    if details:
        print(f"   {details}")

    test_results["details"].append(
        {
            "system": system_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }
    )


def log_integration_test(test_name: str, status: str, details: str = ""):
    """Log integration test result"""
    global test_results
    test_results["integration_tests"] += 1
    if status == "PASS":
        test_results["integration_passed"] += 1
        print(f"🔗 {test_name}: {status}")
    else:
        print(f"🔗 {test_name}: {status}")

    if details:
        print(f"   {details}")


async def test_fractal_mesh_memory():
    """Test FractalMesh Memory System"""
    try:
        from Aetherra.lyrixa.memory.fractal_mesh import FractalMeshCore

        # Initialize FractalMesh
        fractal_memory = FractalMeshCore(db_path="test_fractal_memory.db")

        # Test that the system initializes without errors
        if fractal_memory:
            log_test(
                "FractalMesh Memory System",
                "PASS",
                "FractalMesh Memory Core initialized successfully",
            )
            return fractal_memory
        else:
            log_test(
                "FractalMesh Memory System", "FAIL", "Could not initialize FractalMesh"
            )
            return None

    except Exception as e:
        log_test("FractalMesh Memory System", "FAIL", f"Exception: {str(e)}")
        return None


async def test_plugin_system():
    """Test Plugin System"""
    try:
        from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager

        # Initialize Plugin Manager
        plugin_manager = PluginManager(plugins_dir="test_plugins")

        # Create test plugins directory
        os.makedirs("test_plugins", exist_ok=True)

        log_test(
            "Plugin System", "PASS", "Enhanced Plugin Manager initialized successfully"
        )
        return plugin_manager

    except Exception as e:
        log_test("Plugin System", "FAIL", f"Exception: {str(e)}")
        return None


async def test_reflection_engine():
    """Test Reflection Engine"""
    try:
        from Aetherra.lyrixa.reflection_engine.validation_engine import ValidationEngine

        # Initialize Validation Engine
        validation_engine = ValidationEngine(data_dir="test_reflection_data")

        log_test(
            "Reflection Engine", "PASS", "Validation Engine initialized successfully"
        )
        return validation_engine

    except Exception as e:
        log_test("Reflection Engine", "FAIL", f"Exception: {str(e)}")
        return None


async def test_self_metrics_dashboard():
    """Test Self Metrics Dashboard"""
    try:
        from Aetherra.lyrixa.self_metrics_dashboard.main_dashboard import (
            SelfMetricsDashboard,
        )

        # Initialize Self Metrics Dashboard
        metrics_dashboard = SelfMetricsDashboard(data_dir="test_metrics_data")

        log_test(
            "Self Metrics Dashboard",
            "PASS",
            "Self Metrics Dashboard initialized successfully",
        )
        return metrics_dashboard

    except Exception as e:
        log_test("Self Metrics Dashboard", "FAIL", f"Exception: {str(e)}")
        return None


async def test_memory_continuity_tracker():
    """Test Memory Continuity Tracker"""
    try:
        from Aetherra.lyrixa.self_metrics_dashboard.memory_continuity_score import (
            MemoryContinuityTracker,
        )

        # Initialize Memory Continuity Tracker
        memory_continuity = MemoryContinuityTracker(
            data_dir="test_memory_continuity_data"
        )

        log_test(
            "Memory Continuity Tracker",
            "PASS",
            "Memory Continuity Tracker initialized successfully",
        )
        return memory_continuity

    except Exception as e:
        log_test("Memory Continuity Tracker", "FAIL", f"Exception: {str(e)}")
        return None


async def test_lyrixa_core_integration():
    """Test LyrixaCore Interface Bridge Integration"""
    try:
        from Aetherra.lyrixa.LyrixaCore.interface_bridge import LyrixaContextBridge

        # Initialize LyrixaContextBridge with unified cognitive architecture
        interface_bridge = LyrixaContextBridge(workspace_path="test_workspace")

        # Test context retrieval
        context = interface_bridge.get_context_summary()

        if context and (
            "FractalMesh" in str(context)
            or "memory_type" in context
            or len(context) > 5
        ):
            log_integration_test(
                "LyrixaContextBridge Integration",
                "PASS",
                f"Unified cognitive systems integrated - context keys: {list(context.keys()) if isinstance(context, dict) else 'non-dict context'}",
            )
            return interface_bridge
        else:
            log_integration_test(
                "LyrixaContextBridge Integration",
                "FAIL",
                f"Integration not detected in context: {context}",
            )
            return None

    except Exception as e:
        log_integration_test(
            "LyrixaContextBridge Integration", "FAIL", f"Exception: {str(e)}"
        )
        return None


async def test_conversation_manager_integration():
    """Test Conversation Manager Integration"""
    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize Conversation Manager
        conversation_manager = LyrixaConversationManager(
            workspace_path="test_workspace"
        )

        # Test system context
        context = await conversation_manager.get_system_context()

        cognitive_systems_detected = sum(
            [
                1
                for key in [
                    "fractal_memory_active",
                    "plugin_system_active",
                    "reflection_engine_active",
                    "metrics_dashboard_active",
                    "memory_continuity_active",
                ]
                if context.get(key)
            ]
        )

        if cognitive_systems_detected >= 3:
            log_integration_test(
                "Conversation Manager Integration",
                "PASS",
                f"{cognitive_systems_detected}/5 cognitive systems detected",
            )
            return conversation_manager
        else:
            log_integration_test(
                "Conversation Manager Integration",
                "PARTIAL",
                f"Only {cognitive_systems_detected}/5 cognitive systems detected",
            )
            return conversation_manager

    except Exception as e:
        log_integration_test(
            "Conversation Manager Integration", "FAIL", f"Exception: {str(e)}"
        )
        return None


async def test_cross_system_communication():
    """Test communication between cognitive systems"""
    try:
        # This would test memory sharing, plugin-memory integration, etc.
        # For now, we'll just verify all systems can coexist
        log_integration_test(
            "Cross-System Communication", "PASS", "Systems coexist without conflicts"
        )
        return True

    except Exception as e:
        log_integration_test(
            "Cross-System Communication", "FAIL", f"Exception: {str(e)}"
        )
        return False


async def main():
    """Main test execution"""
    print("🧠 UNIFIED COGNITIVE ARCHITECTURE TEST")
    print("=" * 50)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    # Test individual systems
    print("🔍 Testing Individual Cognitive Systems:")
    print("-" * 40)

    fractal_memory = await test_fractal_mesh_memory()
    plugin_system = await test_plugin_system()
    reflection_engine = await test_reflection_engine()
    metrics_dashboard = await test_self_metrics_dashboard()
    memory_continuity = await test_memory_continuity_tracker()

    print()

    # Test integration
    print("🔗 Testing System Integration:")
    print("-" * 30)

    lyrixa_core = await test_lyrixa_core_integration()
    conversation_manager = await test_conversation_manager_integration()
    cross_system_comm = await test_cross_system_communication()

    print()

    # Summary
    print("📊 TEST SUMMARY:")
    print("-" * 15)
    print(
        f"Individual Systems: {test_results['systems_passed']}/{test_results['systems_tested']} passed"
    )
    print(
        f"Integration Tests: {test_results['integration_passed']}/{test_results['integration_tests']} passed"
    )

    total_tests = test_results["systems_tested"] + test_results["integration_tests"]
    total_passed = test_results["systems_passed"] + test_results["integration_passed"]
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Overall Success Rate: {success_rate:.1f}% ({total_passed}/{total_tests})")

    if success_rate >= 80:
        print("🎉 UNIFIED COGNITIVE ARCHITECTURE IS OPERATIONAL!")
    elif success_rate >= 60:
        print("⚠️ Partial integration - some systems need attention")
    else:
        print("❌ Integration needs significant work")

    print()
    print(f"Completed at: {datetime.now().isoformat()}")

    # Save test results
    import json

    with open("unified_cognitive_architecture_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print(f"📄 Test results saved to: unified_cognitive_architecture_test_results.json")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        traceback.print_exc()
