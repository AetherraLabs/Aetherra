#!/usr/bin/env python3
"""
🎯 AI OS KERNEL INTEGRATION TEST
===============================

Comprehensive test suite for the Aether Runtime and Lyrixa integration.
Tests all components of the AI OS Kernel implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Aetherra.runtime.aether_runtime import AetherRuntime, ExecutionContext
    from lyrixa.core.agents import LyrixaAgentManager
    from lyrixa.core.memory import LyrixaMemorySystem
    from lyrixa.core.plugins import LyrixaPluginManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some components may not be available for testing")


def safe_print(message: str) -> None:
    """Safe print function that handles Unicode encoding issues on Windows"""
    try:
        print(message)
    except UnicodeEncodeError:
        safe_message = message.encode("ascii", "ignore").decode("ascii")
        print(
            safe_message.replace("🎯", "[*]")
            .replace("🚀", "[*]")
            .replace("✅", "[OK]")
            .replace("❌", "[X]")
        )


class AIKernelTester:
    """Comprehensive tester for AI OS Kernel implementation"""

    def __init__(self):
        self.runtime = None
        self.tests_passed = 0
        self.tests_failed = 0

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        if success:
            self.tests_passed += 1
            safe_print(f"✅ {test_name}")
            if details:
                safe_print(f"   {details}")
        else:
            self.tests_failed += 1
            safe_print(f"❌ {test_name}")
            if details:
                safe_print(f"   {details}")

    def test_runtime_initialization(self):
        """Test 1: Aether Runtime Initialization"""
        safe_print("\n🎯 TEST 1: Aether Runtime Initialization")
        try:
            self.runtime = AetherRuntime()
            self.log_test(
                "Runtime creation", True, "AetherRuntime instance created successfully"
            )

            # Test context initialization
            if hasattr(self.runtime, "context") and isinstance(
                self.runtime.context, ExecutionContext
            ):
                self.log_test(
                    "ExecutionContext initialization",
                    True,
                    "ExecutionContext properly initialized",
                )
            else:
                self.log_test(
                    "ExecutionContext initialization",
                    False,
                    "ExecutionContext not properly initialized",
                )

        except Exception as e:
            self.log_test("Runtime creation", False, f"Exception: {e}")

    def test_lyrixa_integration(self):
        """Test 2: Lyrixa Component Integration"""
        safe_print("\n🎯 TEST 2: Lyrixa Component Integration")

        try:
            # Create mock Lyrixa components (or real ones if available)
            memory_system = self.create_mock_memory()
            plugin_manager = self.create_mock_plugins()
            agent_system = self.create_mock_agents()

            # Register with runtime
            self.runtime.register_context(
                memory=memory_system, plugins=plugin_manager, agents=agent_system
            )

            # Verify registration
            if self.runtime.context.memory is not None:
                self.log_test(
                    "Memory system registration", True, "Memory system connected"
                )
            else:
                self.log_test(
                    "Memory system registration", False, "Memory system not connected"
                )

            if self.runtime.context.plugins is not None:
                self.log_test(
                    "Plugin manager registration", True, "Plugin manager connected"
                )
            else:
                self.log_test(
                    "Plugin manager registration", False, "Plugin manager not connected"
                )

            if self.runtime.context.agents is not None:
                self.log_test(
                    "Agent system registration", True, "Agent system connected"
                )
            else:
                self.log_test(
                    "Agent system registration", False, "Agent system not connected"
                )

        except Exception as e:
            self.log_test("Lyrixa integration", False, f"Exception: {e}")

    def test_aether_commands(self):
        """Test 3: .aether Command Processing"""
        safe_print("\n🎯 TEST 3: .aether Command Processing")

        test_commands = [
            ('goal "test goal creation"', "Goal definition"),
            ('$test_var = "hello world"', "Variable assignment"),
            ("show variables", "Variable display"),
            ("status", "Status command"),
            ("show goals", "Goal display"),
        ]

        for command, description in test_commands:
            try:
                safe_print(f"   Testing: {command}")
                self.runtime.interpret_command(command)
                self.log_test(f"{description} command", True)
            except Exception as e:
                self.log_test(f"{description} command", False, f"Exception: {e}")

    def test_script_execution(self):
        """Test 4: Script Execution"""
        safe_print("\n🎯 TEST 4: Script Execution")

        test_script = """
goal "test script execution"
$message = "Script running successfully"
$counter = 5
show variables
status
"""

        try:
            result = self.runtime.execute_goal(test_script)
            self.log_test("Script execution", True, "Test script executed successfully")
        except Exception as e:
            self.log_test("Script execution", False, f"Exception: {e}")

    def test_goal_queue(self):
        """Test 5: Goal Queue System"""
        safe_print("\n🎯 TEST 5: Goal Queue System")

        try:
            # Queue some test goals
            test_goals = [
                'goal "queued goal 1"',
                'goal "queued goal 2"',
                '$queued_var = "test"',
            ]

            for goal in test_goals:
                self.runtime.queue_goal(goal)

            # Check queue size
            if self.runtime.context.goal_queue.qsize() == len(test_goals):
                self.log_test(
                    "Goal queuing", True, f"Successfully queued {len(test_goals)} goals"
                )
            else:
                self.log_test(
                    "Goal queuing",
                    False,
                    f"Expected {len(test_goals)} goals, got {self.runtime.context.goal_queue.qsize()}",
                )

            # Process queue
            processed = self.runtime.process_goal_queue()
            self.log_test("Goal queue processing", True, f"Processed {processed} goals")

        except Exception as e:
            self.log_test("Goal queue system", False, f"Exception: {e}")

    def test_bootstrap_script(self):
        """Test 6: Bootstrap Script"""
        safe_print("\n🎯 TEST 6: Bootstrap Script")

        bootstrap_path = project_root / "bootstrap.aether"

        if not bootstrap_path.exists():
            self.log_test(
                "Bootstrap file existence", False, "bootstrap.aether not found"
            )
            return

        self.log_test("Bootstrap file existence", True, "bootstrap.aether found")

        try:
            # Read and validate bootstrap content
            with open(bootstrap_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "goal" in content and "bootstrap" in content.lower():
                self.log_test(
                    "Bootstrap content validation",
                    True,
                    "Valid bootstrap script structure",
                )
            else:
                self.log_test(
                    "Bootstrap content validation",
                    False,
                    "Invalid bootstrap script structure",
                )

            # Test loading (but not executing to avoid side effects)
            self.runtime.load_script(str(bootstrap_path), from_file=True)
            if len(self.runtime.script_lines) > 0:
                self.log_test(
                    "Bootstrap script loading",
                    True,
                    f"Loaded {len(self.runtime.script_lines)} commands",
                )
            else:
                self.log_test("Bootstrap script loading", False, "No commands loaded")

        except Exception as e:
            self.log_test("Bootstrap script testing", False, f"Exception: {e}")

    def test_chat_integration(self):
        """Test 7: Chat Integration Methods"""
        safe_print("\n🎯 TEST 7: Chat Integration Methods")

        try:
            # Test interpret_aether_line method
            test_lines = [
                'goal "chat integration test"',
                "invalid command here",
                '$chat_var = "test value"',
            ]

            for line in test_lines:
                try:
                    result = self.runtime.interpret_aether_line(line)
                    if "goal" in line or "$" in line:
                        expected_result = True
                    else:
                        expected_result = False

                    if result == expected_result:
                        self.log_test(f"Chat integration: '{line[:20]}...'", True)
                    else:
                        self.log_test(
                            f"Chat integration: '{line[:20]}...'",
                            False,
                            f"Expected {expected_result}, got {result}",
                        )
                except Exception as e:
                    self.log_test(
                        f"Chat integration: '{line[:20]}...'", False, f"Exception: {e}"
                    )

        except Exception as e:
            self.log_test("Chat integration methods", False, f"Exception: {e}")

    def create_mock_memory(self):
        """Create a mock memory system for testing"""

        class MockMemory:
            def __init__(self):
                self.data = {}

            def search(self, query):
                return f"Mock search result for: {query}"

            def store(self, data, tag=None):
                self.data[tag or "default"] = data
                return True

        return MockMemory()

    def create_mock_plugins(self):
        """Create a mock plugin manager for testing"""

        class MockPlugins:
            def execute_plugin(self, name):
                return f"Mock plugin {name} executed successfully"

        return MockPlugins()

    def create_mock_agents(self):
        """Create a mock agent system for testing"""

        class MockAgents:
            def run(self, name, data):
                return f"Mock agent {name} processed: {data}"

        return MockAgents()

    def run_all_tests(self):
        """Run all tests"""
        safe_print("🚀 AI OS KERNEL INTEGRATION TEST SUITE")
        safe_print("=" * 50)

        self.test_runtime_initialization()
        self.test_lyrixa_integration()
        self.test_aether_commands()
        self.test_script_execution()
        self.test_goal_queue()
        self.test_bootstrap_script()
        self.test_chat_integration()

        # Final results
        safe_print("\n" + "=" * 50)
        safe_print("🎯 TEST RESULTS SUMMARY")
        safe_print("=" * 50)
        safe_print(f"✅ Tests Passed: {self.tests_passed}")
        safe_print(f"❌ Tests Failed: {self.tests_failed}")
        safe_print(
            f"📊 Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%"
        )

        if self.tests_failed == 0:
            safe_print("\n🎉 ALL TESTS PASSED! AI OS Kernel is ready!")
        else:
            safe_print(f"\n⚠️  {self.tests_failed} tests failed. Review implementation.")

        safe_print("=" * 50)


def main():
    """Main test function"""
    tester = AIKernelTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
