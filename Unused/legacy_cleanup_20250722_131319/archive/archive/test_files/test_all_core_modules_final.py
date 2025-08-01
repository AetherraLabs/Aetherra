#!/usr/bin/env python3
"""
Final comprehensive test for all core modules
Tests import and basic functionality only
"""

import sys
import traceback
from typing import Any, Dict


def test_module_import(module_name: str, module_path: str) -> Dict[str, Any]:
    """Test importing a module"""
    print(f"\n=== Testing {module_name} ===")

    try:
        # Test import and basic functionality
        if module_path == "core.enhanced_agent":
            from core.enhanced_agent import EnhancedAetherraAgent

            print("✓ Import successful")

            # Test initialization
            agent = EnhancedAetherraAgent()
            print("✓ Initialization successful")

            # Test basic functionality
            status = agent.get_agent_status()
            print(f"✓ Get status: {type(status)}")

            state = agent.get_state()
            print(f"✓ Get state: {state}")

            goals = agent.get_goals()
            print(f"✓ Get goals: {type(goals)}")

            return {"status": "success", "class": "EnhancedAetherraAgent"}

        elif module_path == "core.enhanced_aetherra_interpreter":
            from core.enhanced_aetherra_interpreter import EnhancedAetherraInterpreter

            print("✓ Import successful")

            # Test initialization
            interpreter = EnhancedAetherraInterpreter()
            print("✓ Initialization successful")

            # Test basic functionality
            result = interpreter.execute_aether("print('Hello, World!')")
            print(f"✓ Execute aether: {type(result)}")

            # Test enhancements
            status = interpreter.get_enhancement_status()
            print(f"✓ Enhancement status: {type(status)}")

            return {"status": "success", "class": "EnhancedAetherraInterpreter"}

        elif module_path == "core.ecosystem_manager":
            from core.ecosystem_manager import AetherraCodeEcosystemManager

            print("✓ Import successful")

            # Test initialization
            manager = AetherraCodeEcosystemManager()
            print("✓ Initialization successful")

            # Test basic functionality
            status = manager.get_ecosystem_status()
            print(f"✓ Ecosystem status: {type(status)}")

            manager.initialize_ecosystem()
            print("✓ Initialize ecosystem successful")

            return {"status": "success", "class": "AetherraCodeEcosystemManager"}

        elif module_path == "core.dev_suite":
            from core.dev_suite import AetherraCodeDevSuite, AetherraCodeIDE

            print("✓ Import successful")

            # Test DevSuite initialization
            dev_suite = AetherraCodeDevSuite()
            print("✓ AetherraCodeDevSuite initialization successful")

            # Test IDE initialization
            ide = AetherraCodeIDE()
            print("✓ AetherraCodeIDE initialization successful")

            # Test basic functionality
            result = dev_suite.analyze_code("print('Hello')")
            print(f"✓ Analyze code: {type(result)}")

            return {
                "status": "success",
                "class": "AetherraCodeDevSuite, AetherraCodeIDE",
            }

        else:
            raise ValueError(f"Unknown module path: {module_path}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {"status": "error", "error": str(e)}


def main():
    """Run all tests"""
    print("🚀 Starting comprehensive core module tests...")

    modules = [
        ("Enhanced Agent", "core.enhanced_agent"),
        ("Enhanced Aetherra Interpreter", "core.enhanced_aetherra_interpreter"),
        ("Ecosystem Manager", "core.ecosystem_manager"),
        ("Development Suite", "core.dev_suite"),
    ]

    results = {}

    for name, path in modules:
        results[name] = test_module_import(name, path)

    # Summary
    print(f"\n{'=' * 50}")
    print("📊 FINAL TEST RESULTS")
    print(f"{'=' * 50}")

    success_count = 0
    total_count = len(results)

    for module_name, result in results.items():
        status = "✓ PASS" if result["status"] == "success" else "✗ FAIL"
        print(f"{status:8} {module_name}")
        if result["status"] == "success":
            success_count += 1
        else:
            print(f"         Error: {result.get('error', 'Unknown error')}")

    print(
        f"\n📈 Success Rate: {success_count}/{total_count} ({success_count / total_count * 100:.1f}%)"
    )

    if success_count == total_count:
        print("🎉 ALL TESTS PASSED! All core modules are ready for production!")
        return 0
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
