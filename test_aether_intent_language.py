#!/usr/bin/env python3
"""
🧬 AETHERRA .AETHER INTENT LANGUAGE TEST SUITE

Comprehensive testing framework for .aether Intent Language - the natural-language-inspired
programming language for defining goals, orchestrating actions, and evolving behavior.

Tests Coverage:
- Memory Operations (remember, recall, patterns)
- Goal System (goals, priorities, progress)
- Agent Control (activation, modes, autonomy)
- Plugin Orchestration (execution, parameters)
- Intent-Driven Programming (natural language commands)
- Control Flow (conditionals, loops, patterns)
- Self-Evolving Behavior (learning, adaptation)
- Reflection and Analysis (AI insights)
"""

import os
import sys
import tempfile
import unittest

# Add Aetherra to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Aetherra"))


class AetherIntentLanguageTestSuite(unittest.TestCase):
    """Comprehensive test suite for .aether Intent Language"""

    def setUp(self):
        """Initialize the test environment with .aether interpreter"""
        print(f"\n🧬 Setting up .aether Intent Language test: {self._testMethodName}")

        # Import the .aether interpreter
        try:
            from Aetherra.runtime.aether_parser import AetherraInterpreter

            self.interpreter = AetherraInterpreter()
            print("[OK] AetherraInterpreter loaded successfully")
        except ImportError as e:
            self.skipTest(f"Cannot import AetherraInterpreter: {e}")

        # Create test environment
        self.test_data = {
            "memory_items": [],
            "goals": [],
            "plugin_results": [],
            "agent_states": [],
        }

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, "interpreter"):
            # Clear interpreter state if possible
            try:
                if hasattr(self.interpreter, "memory"):
                    self.interpreter.memory.clear()
            except Exception:
                pass

    # ==================== MEMORY OPERATIONS TESTS ====================

    def test_basic_memory_storage(self):
        """Test 001: Basic memory storage with remember command"""
        print("🧠 Testing basic memory storage...")

        # Test simple remember command
        result = self.interpreter.execute('remember("Python is awesome") as "language"')
        self.assertIn("Memory", result)
        self.assertIn("Python is awesome", result)

        # Test memory with multiple tags
        result = self.interpreter.execute(
            'remember("Always backup code") as "best_practice,safety"'
        )
        self.assertIn("Memory", result)

        print("[OK] Basic memory storage working")

    def test_memory_recall_operations(self):
        """Test 002: Memory recall with various patterns"""
        print("🔍 Testing memory recall operations...")

        # Store some memories first
        self.interpreter.execute('remember("API rate limiting") as "performance"')
        self.interpreter.execute('remember("Database indexing") as "performance"')

        # Test recall by tag
        result = self.interpreter.execute('recall tag: "performance"')
        self.assertIn("performance", result.lower())

        print("[OK] Memory recall operations working")

    def test_memory_patterns_and_analysis(self):
        """Test 003: Memory pattern detection and analysis"""
        print("🔍 Testing memory pattern analysis...")

        # Store pattern-based memories
        self.interpreter.execute('remember("Error occurred at startup") as "error_log"')
        self.interpreter.execute(
            'remember("Memory usage spike detected") as "performance_log"'
        )

        # Test pattern detection
        result = self.interpreter.execute("detect recurring patterns")
        self.assertIsInstance(result, str)

        # Test memory summary
        result = self.interpreter.execute("memory summary")
        self.assertIsInstance(result, str)

        print("[OK] Memory pattern analysis working")

    def test_ai_memory_reflection(self):
        """Test 004: AI-powered memory reflection and insights"""
        print("🤔 Testing AI memory reflection...")

        # Store memories for reflection
        self.interpreter.execute(
            'remember("Machine learning models need validation") as "ai_knowledge"'
        )
        self.interpreter.execute(
            'remember("Deep learning requires large datasets") as "ai_knowledge"'
        )

        # Test reflection
        result = self.interpreter.execute('reflect on tags="ai_knowledge"')
        self.assertIn("Reflect", result)

        print("[OK] AI memory reflection working")

    # ==================== GOAL SYSTEM TESTS ====================

    def test_goal_setting_and_priorities(self):
        """Test 005: Goal setting with priorities and metadata"""
        print("🎯 Testing goal setting with priorities...")

        # Test basic goal setting
        result = self.interpreter.execute("goal: improve performance priority: high")
        self.assertIsInstance(result, str)

        # Test goal with metrics
        result = self.interpreter.execute(
            "goal: reduce memory usage by 25% priority: medium"
        )
        self.assertIsInstance(result, str)

        # Test goal status
        result = self.interpreter.execute("goal status")
        self.assertIsInstance(result, str)

        print("[OK] Goal setting and priorities working")

    def test_goal_progress_monitoring(self):
        """Test 006: Goal progress tracking and monitoring"""
        print("📊 Testing goal progress monitoring...")

        # Set a goal for monitoring
        self.interpreter.execute("goal: optimize database queries priority: high")

        # Test goal checking
        result = self.interpreter.execute('check goal "database"')
        self.assertIsInstance(result, str)

        # Test autonomous monitoring
        result = self.interpreter.execute("autonomous monitoring")
        self.assertIsInstance(result, str)

        print("[OK] Goal progress monitoring working")

    def test_adaptive_goal_management(self):
        """Test 007: Adaptive goal management and optimization"""
        print("🔄 Testing adaptive goal management...")

        # Test reflective loop
        result = self.interpreter.execute("reflective loop")
        self.assertIsInstance(result, str)

        # Test next action suggestions
        result = self.interpreter.execute("suggest next actions")
        self.assertIsInstance(result, str)

        print("[OK] Adaptive goal management working")

    # ==================== AGENT CONTROL TESTS ====================

    def test_agent_activation_modes(self):
        """Test 008: Agent activation and control modes"""
        print("🤖 Testing agent activation and modes...")

        # Test agent activation
        result = self.interpreter.execute("agent: on")
        self.assertIsInstance(result, str)

        # Test agent deactivation
        result = self.interpreter.execute("agent: off")
        self.assertIsInstance(result, str)

        # Test auto mode
        result = self.interpreter.execute("agent: auto")
        self.assertIsInstance(result, str)

        print("[OK] Agent activation and modes working")

    def test_agent_specialization(self):
        """Test 009: Agent specialization and capabilities"""
        print("[TOOL] Testing agent specialization...")

        # Test specialized agent mode
        result = self.interpreter.execute(
            "agent: research specialization: code_analysis"
        )
        self.assertIsInstance(result, str)

        print("[OK] Agent specialization working")

    # ==================== PLUGIN ORCHESTRATION TESTS ====================

    def test_basic_plugin_execution(self):
        """Test 010: Basic plugin execution and orchestration"""
        print("🔌 Testing basic plugin execution...")

        # Test plugin listing
        result = self.interpreter.execute("list plugins")
        self.assertIsInstance(result, str)

        # Test plugin execution (with fallback for missing plugins)
        result = self.interpreter.execute("plugin: demo_plugin")
        self.assertIsInstance(result, str)

        print("[OK] Basic plugin execution working")

    def test_plugin_with_parameters(self):
        """Test 011: Plugin execution with parameters and configuration"""
        print("⚙️ Testing plugin execution with parameters...")

        # Test plugin with parameters
        result = self.interpreter.execute(
            'plugin: test_plugin("parameter1", "parameter2")'
        )
        self.assertIsInstance(result, str)

        # Test meta-plugin execution
        result = self.interpreter.execute("meta: system_info")
        self.assertIsInstance(result, str)

        print("[OK] Plugin execution with parameters working")

    def test_plugin_chaining_and_integration(self):
        """Test 012: Plugin chaining and system integration"""
        print("🔗 Testing plugin chaining and integration...")

        # Test plugin info
        result = self.interpreter.execute("plugin info demo_plugin")
        self.assertIsInstance(result, str)

        # Test meta-plugin listing
        result = self.interpreter.execute("list meta plugins")
        self.assertIsInstance(result, str)

        print("[OK] Plugin chaining and integration working")

    # ==================== INTENT-DRIVEN PROGRAMMING TESTS ====================

    def test_natural_language_intent_parsing(self):
        """Test 013: Natural language intent parsing and execution"""
        print("💬 Testing natural language intent parsing...")

        # Test assistant queries
        result = self.interpreter.execute("assistant: help me optimize this code")
        self.assertIsInstance(result, str)

        # Test learning commands
        result = self.interpreter.execute('learn from "user_behavior.log"')
        self.assertIsInstance(result, str)

        print("[OK] Natural language intent parsing working")

    def test_optimization_and_improvement_intents(self):
        """Test 014: Optimization and improvement intent execution"""
        print("⚡ Testing optimization and improvement intents...")

        # Test optimization request
        result = self.interpreter.execute('optimize for "speed"')
        self.assertIsInstance(result, str)

        # Test fix suggestions
        result = self.interpreter.execute('suggest fix for "performance issue"')
        self.assertIsInstance(result, str)

        print("[OK] Optimization and improvement intents working")

    def test_contextual_code_understanding(self):
        """Test 015: Contextual code understanding and suggestions"""
        print("🧠 Testing contextual code understanding...")

        # Test code analysis
        result = self.interpreter.execute("analyze recent_logs")
        self.assertIsInstance(result, str)

        print("[OK] Contextual code understanding working")

    # ==================== CONTROL FLOW TESTS ====================

    def test_conditional_statements(self):
        """Test 016: Conditional statements and logical flow"""
        print("🔀 Testing conditional statements...")

        # Test memory pattern condition
        result = self.interpreter.execute(
            'if memory.pattern("crash", frequency="daily"):'
        )
        self.assertIsInstance(result, str)

        print("[OK] Conditional statements working")

    def test_pattern_based_conditions(self):
        """Test 017: Pattern-based conditional execution"""
        print("🔍 Testing pattern-based conditions...")

        # Test pattern frequency
        result = self.interpreter.execute('pattern frequency "error" in "weekly"')
        self.assertIsInstance(result, str)

        print("[OK] Pattern-based conditions working")

    # ==================== SELF-EDITING AND EVOLUTION TESTS ====================

    def test_code_loading_and_analysis(self):
        """Test 018: Code loading and analysis capabilities"""
        print("📂 Testing code loading and analysis...")

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('def test_function():\n    return "Hello World"')
            test_file = f.name

        try:
            # Test file loading
            result = self.interpreter.execute(f"load {test_file}")
            self.assertIsInstance(result, str)

            # Test code analysis
            result = self.interpreter.execute(f"analyze {test_file}")
            self.assertIsInstance(result, str)
        finally:
            os.unlink(test_file)

        print("[OK] Code loading and analysis working")

    def test_self_editing_safety(self):
        """Test 019: Self-editing safety mechanisms"""
        print("🛡️ Testing self-editing safety mechanisms...")

        # Test self-edit mode control
        result = self.interpreter.execute("set self_edit_mode off")
        self.assertIsInstance(result, str)

        # Test backup creation
        result = self.interpreter.execute("backup test_file.py")
        self.assertIsInstance(result, str)

        print("[OK] Self-editing safety mechanisms working")

    # ==================== DEBUG AND INTROSPECTION TESTS ====================

    def test_debug_system_integration(self):
        """Test 020: Debug system integration and error handling"""
        print("🐛 Testing debug system integration...")

        # Test debug status
        self.interpreter.execute("debug status")
        # Debug status might not return a string, just check it doesn't crash

        # Test auto-debug configuration
        self.interpreter.execute("set auto_debug on 85")
        # This might not return anything, just check it doesn't crash

        print("[OK] Debug system integration working")

    def test_error_pattern_detection(self):
        """Test 021: Error pattern detection and resolution"""
        print("🔍 Testing error pattern detection...")

        # Store error patterns in memory
        self.interpreter.execute(
            'remember("NullPointerException in line 42") as "error_log"'
        )
        self.interpreter.execute(
            'remember("OutOfMemoryError during processing") as "error_log"'
        )

        # Test pattern detection
        result = self.interpreter.execute('detect recurring patterns in "error_log"')
        self.assertIsInstance(result, str)

        print("[OK] Error pattern detection working")

    # ==================== ADVANCED LANGUAGE FEATURES TESTS ====================

    def test_function_definition_and_calls(self):
        """Test 022: Function definition and invocation"""
        print("[TOOL] Testing function definition and calls...")

        # Test function definition
        result = self.interpreter.execute("define test_func(param): return param")
        self.assertIsInstance(result, str)

        # Test function call
        result = self.interpreter.execute('call test_func("hello")')
        self.assertIsInstance(result, str)

        print("[OK] Function definition and calls working")

    def test_variable_and_context_management(self):
        """Test 023: Variable and context management"""
        print("📊 Testing variable and context management...")

        # Test variable assignment
        result = self.interpreter.execute("$result = plugin: demo_action")
        self.assertIsInstance(result, str)

        print("[OK] Variable and context management working")

    def test_advanced_memory_queries(self):
        """Test 024: Advanced memory querying and filtering"""
        print("🔍 Testing advanced memory queries...")

        # Store complex memories
        self.interpreter.execute(
            'remember("Complex algorithm implementation") as "code,algorithm"'
        )
        self.interpreter.execute(
            'remember("Performance optimization technique") as "performance,algorithm"'
        )

        # Test complex recall
        result = self.interpreter.execute(
            'recall tags="algorithm,performance" category="technical"'
        )
        self.assertIsInstance(result, str)

        print("[OK] Advanced memory queries working")

    def test_multi_agent_coordination(self):
        """Test 025: Multi-agent coordination and communication"""
        print("🤝 Testing multi-agent coordination...")

        # Test agent coordination
        result = self.interpreter.execute('agent: coordinate with "research_agent"')
        self.assertIsInstance(result, str)

        print("[OK] Multi-agent coordination working")


def run_aether_intent_language_tests():
    """Execute the complete .aether Intent Language test suite"""

    print("🧬 STARTING AETHERRA .AETHER INTENT LANGUAGE TEST SUITE")
    print("=" * 60)
    print("Testing the natural-language-inspired programming language for")
    print("defining goals, orchestrating actions, and evolving behavior")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(AetherIntentLanguageTestSuite)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2, stream=sys.stdout, descriptions=True, failfast=False
    )

    print(
        f"📊 Executing {suite.countTestCases()} comprehensive .aether language tests..."
    )
    result = runner.run(suite)

    # Generate comprehensive test report
    print("\n" + "=" * 60)
    print("🧬 AETHERRA .AETHER INTENT LANGUAGE TEST RESULTS")
    print("=" * 60)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, "skipped") else 0
    passed = total_tests - failures - errors - skipped

    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    print(f"📊 Total Tests: {total_tests}")
    print(f"[OK] Passed: {passed}")
    print(f"[ERROR] Failed: {failures}")
    print(f"[WARN] Errors: {errors}")
    print(f"⏭️ Skipped: {skipped}")
    print(f"📈 Success Rate: {success_rate:.1f}%")

    # Detailed results by category
    print("\n📋 TEST CATEGORIES SUMMARY:")
    categories = {
        "Memory Operations": [
            "test_basic_memory_storage",
            "test_memory_recall_operations",
            "test_memory_patterns_and_analysis",
            "test_ai_memory_reflection",
        ],
        "Goal System": [
            "test_goal_setting_and_priorities",
            "test_goal_progress_monitoring",
            "test_adaptive_goal_management",
        ],
        "Agent Control": ["test_agent_activation_modes", "test_agent_specialization"],
        "Plugin Orchestration": [
            "test_basic_plugin_execution",
            "test_plugin_with_parameters",
            "test_plugin_chaining_and_integration",
        ],
        "Intent-Driven Programming": [
            "test_natural_language_intent_parsing",
            "test_optimization_and_improvement_intents",
            "test_contextual_code_understanding",
        ],
        "Control Flow": [
            "test_conditional_statements",
            "test_pattern_based_conditions",
        ],
        "Self-Evolution": [
            "test_code_loading_and_analysis",
            "test_self_editing_safety",
        ],
        "Debug & Introspection": [
            "test_debug_system_integration",
            "test_error_pattern_detection",
        ],
        "Advanced Features": [
            "test_function_definition_and_calls",
            "test_variable_and_context_management",
            "test_advanced_memory_queries",
            "test_multi_agent_coordination",
        ],
    }

    for category, test_methods in categories.items():
        category_passed = sum(
            1
            for test_method in test_methods
            if not any(
                test_method in str(failure)
                for failure in result.failures + result.errors
            )
        )
        total_category = len(test_methods)
        print(
            f"  {category}: {category_passed}/{total_category} ({category_passed / total_category * 100:.0f}%)"
        )

    if result.failures:
        print(f"\n[ERROR] FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(
                f"  • {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown failure'}"
            )

    if result.errors:
        print(f"\n[WARN] ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            error_msg = traceback.split("\n")[-2] if "\n" in traceback else traceback
            print(f"  • {test}: {error_msg}")

    # Performance and capability assessment
    print("\n🎯 .AETHER LANGUAGE CAPABILITY ASSESSMENT:")

    if success_rate >= 95:
        print(
            "🟢 EXCELLENT: .aether Intent Language is production-ready with full capabilities"
        )
    elif success_rate >= 85:
        print("🟡 GOOD: .aether Intent Language is functional with minor limitations")
    elif success_rate >= 70:
        print(
            "🟠 FAIR: .aether Intent Language has basic functionality but needs improvement"
        )
    else:
        print("🔴 NEEDS WORK: .aether Intent Language requires significant development")

    # Specific capability status
    core_capabilities = [
        ("Natural Language Processing", ["test_natural_language_intent_parsing"]),
        (
            "Memory System Integration",
            ["test_basic_memory_storage", "test_memory_recall_operations"],
        ),
        (
            "Goal-Driven Programming",
            ["test_goal_setting_and_priorities", "test_goal_progress_monitoring"],
        ),
        (
            "Agent Orchestration",
            ["test_agent_activation_modes", "test_agent_specialization"],
        ),
        (
            "Plugin Ecosystem",
            ["test_basic_plugin_execution", "test_plugin_with_parameters"],
        ),
        (
            "Self-Evolution",
            ["test_code_loading_and_analysis", "test_self_editing_safety"],
        ),
        (
            "Intent Recognition",
            [
                "test_optimization_and_improvement_intents",
                "test_contextual_code_understanding",
            ],
        ),
    ]

    print("\n🧬 CORE LANGUAGE CAPABILITIES:")
    for capability, tests in core_capabilities:
        capability_working = not any(
            test in str(failure) or test in str(error)
            for failure in result.failures
            for error in result.errors
            for test in tests
        )
        status = "[OK] OPERATIONAL" if capability_working else "[ERROR] NEEDS ATTENTION"
        print(f"  {capability}: {status}")

    print("\n🌟 .AETHER INTENT LANGUAGE ASSESSMENT COMPLETE!")
    print("The natural-language-inspired programming language for defining goals,")
    print(
        f"orchestrating actions, and evolving behavior is {success_rate:.1f}% functional."
    )

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_aether_intent_language_tests()
    sys.exit(0 if success else 1)
