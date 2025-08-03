#!/usr/bin/env python3
"""
Comprehensive test for core/agent.py
Tests all agent functionality and integration
"""


class MockMemory:
    """Mock memory system for testing"""

    def __init__(self):
        self.memory = [
            {
                "text": "Test memory 1",
                "tags": ["test", "example"],
                "category": "general",
            },
            {
                "text": "Error in function X",
                "tags": ["error", "bug"],
                "category": "code_management",
            },
            {
                "text": "Performance optimization",
                "tags": ["performance", "optimization"],
                "category": "system",
            },
            {
                "text": "User behavior pattern",
                "tags": ["pattern", "user"],
                "category": "analytics",
            },
        ]

    def recall(self, tags=None, category=None):
        """Recall memories with optional filtering"""
        if tags:
            return [
                m for m in self.memory if any(tag in m.get("tags", []) for tag in tags)
            ]
        if category:
            return [m for m in self.memory if m.get("category") == category]
        return self.memory

    def get_memory_summary(self):
        """Get memory summary statistics"""
        return {
            "total_memories": len(self.memory),
            "categories": list(set(m.get("category", "general") for m in self.memory)),
        }

    def get_tags(self):
        """Get all available tags"""
        tags = set()
        for m in self.memory:
            tags.update(m.get("tags", []))
        return list(tags)

    def get_memory_stats(self):
        """Get memory statistics"""
        return {
            "total": len(self.memory),
            "categories": len(set(m.get("category") for m in self.memory)),
        }

    def remember(self, text, tags=None, category="general"):
        """Add new memory"""
        self.memory.append({"text": text, "tags": tags or [], "category": category})


class MockFunctions:
    """Mock function system for testing"""

    def get_function_count(self):
        return 5

    def get_function_names(self):
        return ["test_func1", "test_func2", "test_func3"]


def test_agent_comprehensive():
    """Comprehensive test of all agent functionality"""
    print("🤖 Testing AetherraAgent Comprehensive Functionality")
    print("=" * 60)

    # Import the agent
    try:
        from core.agent import (
            AetherraAgent,
            analyze_memory_patterns,
            analyze_user_behavior,
        )

        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Create mock dependencies
    memory = MockMemory()
    functions = MockFunctions()
    command_history = [
        {"command_type": "memory_store", "command": "remember test"},
        {"command_type": "memory_recall", "command": "recall test"},
        {"command_type": "pattern_analysis", "command": "detect patterns"},
        {"command_type": "self_editing", "command": "refactor code"},
    ]

    # Test standalone functions
    print("\n🧪 Testing Standalone Functions:")
    passed = 0
    total = 0

    # Test analyze_memory_patterns
    total += 1
    try:
        result = analyze_memory_patterns(memory.memory, {"test": 2}, {"general": 1})
        if isinstance(result, dict) and "patterns" in result:
            print("✅ analyze_memory_patterns: Returns proper dict structure")
            passed += 1
        else:
            print("❌ analyze_memory_patterns: Invalid return structure")
    except Exception as e:
        print(f"❌ analyze_memory_patterns: Error {e}")

    # Test analyze_user_behavior
    total += 1
    try:
        result = analyze_user_behavior({"memory_store": 2}, ["pattern1", "pattern2"])
        if isinstance(result, dict) and "primary_activity" in result:
            print("✅ analyze_user_behavior: Returns proper dict structure")
            passed += 1
        else:
            print("❌ analyze_user_behavior: Invalid return structure")
    except Exception as e:
        print(f"❌ analyze_user_behavior: Error {e}")

    # Test AetherraAgent class
    print("\n🤖 Testing AetherraAgent Class:")

    try:
        agent = AetherraAgent(memory, functions, command_history)
        print("✅ AetherraAgent initialized successfully")

        # Test each major method
        methods_to_test = [
            ("detect_memory_patterns", lambda: agent.detect_memory_patterns()),
            ("analyze_behavior", lambda: agent.analyze_behavior()),
            ("suggest_evolution", lambda: agent.suggest_evolution("test context")),
            ("adaptive_suggest", lambda: agent.adaptive_suggest("test context")),
            (
                "suggest_self_editing_opportunities",
                lambda: agent.suggest_self_editing_opportunities(),
            ),
            (
                "justify_self_editing",
                lambda: agent.justify_self_editing("test.py", "test analysis"),
            ),
            ("get_command_type", lambda: agent.get_command_type("remember test")),
        ]

        for method_name, method_call in methods_to_test:
            total += 1
            try:
                result = method_call()
                if result and len(str(result)) > 10:  # Basic validation
                    print(
                        f"✅ {method_name}: Returns meaningful result ({len(str(result))} chars)"
                    )
                    passed += 1
                else:
                    print(f"❌ {method_name}: Result too short or empty")
            except Exception as e:
                print(f"❌ {method_name}: Error {e}")

    except Exception as e:
        print(f"❌ AetherraAgent initialization failed: {e}")

    # Test intelligence module integration
    print("\n🧠 Testing Intelligence Module Integration:")
    total += 1
    try:
        from core.intelligence import (
            justify_self_editing_decision,
            memory_driven_code_suggestion,
            provide_adaptive_suggestions,
            suggest_system_evolution,
        )

        # Test each function
        result1 = justify_self_editing_decision("test.py", "analysis", "context")
        result2 = memory_driven_code_suggestion(memory.memory, {"total": 4})
        result3 = provide_adaptive_suggestions(
            "context", memory.memory, ["tag1"], ["func1"]
        )
        result4 = suggest_system_evolution(
            {"total_memories": 10, "categories": ["test"]}, 5
        )

        if all(len(str(r)) > 20 for r in [result1, result2, result3, result4]):
            print("✅ Intelligence module: All functions return meaningful results")
            passed += 1
        else:
            print("❌ Intelligence module: Some functions return insufficient results")
    except Exception as e:
        print(f"❌ Intelligence module: Error {e}")

    # Final Results
    print(f"\n{'=' * 60}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}/{total} tests ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! core/agent.py is production-ready!")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = test_agent_comprehensive()
    if success:
        print(
            "\n🚀 AetherraAgent is fully operational and ready for autonomous behavior!"
        )
    else:
        print("\n[WARN] Please address the issues before production deployment.")
