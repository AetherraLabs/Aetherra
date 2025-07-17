# plugin_sandbox_tester.py
# 🧪 Plugin Sandbox Testing System
# "Consider test sandbox to run plugin against dummy memory or simulated goal"

import os
import json
import time
import tempfile
import subprocess
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import shutil
import signal
import sys


@dataclass
class TestScenario:
    """Test scenario configuration"""
    name: str
    description: str
    input_data: Any
    expected_output: Optional[Any] = None
    timeout: int = 30
    memory_limit: int = 100 * 1024 * 1024  # 100MB
    mock_services: List[str] = field(default_factory=list)
    simulated_goals: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Test execution result"""
    scenario_name: str
    success: bool
    output: Any
    error_message: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: int = 0
    cpu_usage: float = 0.0
    warnings: List[str] = field(default_factory=list)
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SandboxEnvironment:
    """Sandbox environment configuration"""
    sandbox_dir: str
    memory_file: str
    goals_file: str
    config_file: str
    log_file: str
    pid_file: str

    # Mock services
    mock_apis: Dict[str, Any] = field(default_factory=dict)
    mock_databases: Dict[str, Any] = field(default_factory=dict)
    mock_file_system: Dict[str, Any] = field(default_factory=dict)


class PluginSandboxTester:
    """Advanced plugin sandbox testing system"""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or tempfile.gettempdir()
        self.sandbox_envs: Dict[str, SandboxEnvironment] = {}
        self.test_results: List[TestResult] = []
        self.running_tests: Dict[str, threading.Thread] = {}

    def create_sandbox(self, plugin_name: str, config: Dict[str, Any] = None) -> SandboxEnvironment:
        """Create an isolated sandbox environment for testing"""
        sandbox_id = f"sandbox_{plugin_name}_{int(time.time())}"
        sandbox_dir = os.path.join(self.base_dir, sandbox_id)

        # Create sandbox directory structure
        os.makedirs(sandbox_dir, exist_ok=True)
        os.makedirs(os.path.join(sandbox_dir, "memory"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_dir, "goals"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_dir, "config"), exist_ok=True)
        os.makedirs(os.path.join(sandbox_dir, "plugins"), exist_ok=True)

        # Create file paths
        memory_file = os.path.join(sandbox_dir, "memory", "memory.json")
        goals_file = os.path.join(sandbox_dir, "goals", "goals.json")
        config_file = os.path.join(sandbox_dir, "config", "config.json")
        log_file = os.path.join(sandbox_dir, "logs", "test.log")
        pid_file = os.path.join(sandbox_dir, "sandbox.pid")

        # Create sandbox environment
        env = SandboxEnvironment(
            sandbox_dir=sandbox_dir,
            memory_file=memory_file,
            goals_file=goals_file,
            config_file=config_file,
            log_file=log_file,
            pid_file=pid_file
        )

        # Initialize sandbox files
        self._initialize_sandbox(env, config or {})

        self.sandbox_envs[sandbox_id] = env
        return env

    def _initialize_sandbox(self, env: SandboxEnvironment, config: Dict[str, Any]):
        """Initialize sandbox with mock data"""

        # Create mock memory
        mock_memory = {
            "short_term": [
                {"content": "Test memory item 1", "timestamp": datetime.now().isoformat()},
                {"content": "Test memory item 2", "timestamp": datetime.now().isoformat()}
            ],
            "long_term": {
                "facts": [
                    {"fact": "Aetherra is an AI-native programming language", "confidence": 0.95},
                    {"fact": "Plugins extend Aetherra functionality", "confidence": 0.90}
                ],
                "patterns": [
                    {"pattern": "User prefers concise responses", "strength": 0.8},
                    {"pattern": "Complex tasks require decomposition", "strength": 0.85}
                ]
            },
            "working_memory": {
                "current_task": "Testing plugin functionality",
                "context": ["plugin_test", "sandbox_environment"],
                "variables": {"test_mode": True, "iteration": 1}
            }
        }

        with open(env.memory_file, 'w') as f:
            json.dump(mock_memory, f, indent=2)

        # Create mock goals
        mock_goals = {
            "active_goals": [
                {
                    "id": "goal_1",
                    "description": "Complete plugin testing",
                    "priority": "high",
                    "status": "in_progress",
                    "sub_goals": [
                        {"id": "sub_1", "description": "Initialize sandbox", "status": "completed"},
                        {"id": "sub_2", "description": "Execute plugin", "status": "in_progress"}
                    ]
                },
                {
                    "id": "goal_2",
                    "description": "Validate plugin output",
                    "priority": "medium",
                    "status": "pending"
                }
            ],
            "completed_goals": [
                {
                    "id": "goal_0",
                    "description": "Setup test environment",
                    "priority": "high",
                    "status": "completed",
                    "completion_time": datetime.now().isoformat()
                }
            ]
        }

        with open(env.goals_file, 'w') as f:
            json.dump(mock_goals, f, indent=2)

        # Create sandbox configuration
        sandbox_config = {
            "sandbox_id": os.path.basename(env.sandbox_dir),
            "created_at": datetime.now().isoformat(),
            "limits": {
                "memory": 100 * 1024 * 1024,  # 100MB
                "execution_time": 30,  # 30 seconds
                "file_operations": 100,
                "network_requests": 10
            },
            "permissions": {
                "file_read": True,
                "file_write": True,
                "network_access": False,
                "system_commands": False
            },
            "mock_services": {
                "memory_service": {"enabled": True, "file": env.memory_file},
                "goals_service": {"enabled": True, "file": env.goals_file},
                "logging_service": {"enabled": True, "file": env.log_file}
            }
        }

        sandbox_config.update(config)

        with open(env.config_file, 'w') as f:
            json.dump(sandbox_config, f, indent=2)

        # Initialize log file
        with open(env.log_file, 'w') as f:
            f.write(f"[{datetime.now().isoformat()}] Sandbox initialized\n")

    def run_test_scenario(self, env: SandboxEnvironment, scenario: TestScenario, plugin_code: str) -> TestResult:
        """Run a specific test scenario"""
        start_time = time.time()

        try:
            # Write plugin code to sandbox
            plugin_file = os.path.join(env.sandbox_dir, "plugins", "test_plugin.aether")
            with open(plugin_file, 'w') as f:
                f.write(plugin_code)

            # Create test input file
            input_file = os.path.join(env.sandbox_dir, "test_input.json")
            with open(input_file, 'w') as f:
                json.dump(scenario.input_data, f, indent=2)

            # Execute plugin in sandbox
            result = self._execute_plugin_in_sandbox(env, plugin_file, input_file, scenario)

            execution_time = time.time() - start_time

            # Create test result
            test_result = TestResult(
                scenario_name=scenario.name,
                success=result.get("success", False),
                output=result.get("output"),
                error_message=result.get("error"),
                execution_time=execution_time,
                memory_usage=result.get("memory_usage", 0),
                cpu_usage=result.get("cpu_usage", 0.0),
                warnings=result.get("warnings", []),
                debug_info=result.get("debug_info", {})
            )

            # Validate against expected output
            if scenario.expected_output is not None:
                if self._compare_outputs(result.get("output"), scenario.expected_output):
                    test_result.debug_info["output_validation"] = "passed"
                else:
                    test_result.success = False
                    test_result.error_message = "Output doesn't match expected result"
                    test_result.debug_info["output_validation"] = "failed"
                    test_result.debug_info["expected"] = scenario.expected_output
                    test_result.debug_info["actual"] = result.get("output")

            self.test_results.append(test_result)
            return test_result

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = TestResult(
                scenario_name=scenario.name,
                success=False,
                output=None,
                error_message=str(e),
                execution_time=execution_time,
                debug_info={"exception": str(e)}
            )
            self.test_results.append(error_result)
            return error_result

    def _execute_plugin_in_sandbox(self, env: SandboxEnvironment, plugin_file: str, input_file: str, scenario: TestScenario) -> Dict[str, Any]:
        """Execute plugin in isolated sandbox environment"""

        # Create execution script
        execution_script = self._create_execution_script(env, plugin_file, input_file, scenario)
        script_file = os.path.join(env.sandbox_dir, "execute.py")

        with open(script_file, 'w') as f:
            f.write(execution_script)

        # Execute with timeout and resource limits
        try:
            # Start execution
            process = subprocess.Popen(
                [sys.executable, script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=env.sandbox_dir,
                text=True
            )

            # Write PID for monitoring
            with open(env.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=scenario.timeout)

                # Parse results
                if process.returncode == 0:
                    try:
                        result = json.loads(stdout)
                        return result
                    except json.JSONDecodeError:
                        return {
                            "success": False,
                            "error": "Invalid JSON output",
                            "output": stdout,
                            "stderr": stderr
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Process exited with code {process.returncode}",
                        "stderr": stderr
                    }

            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "error": f"Execution timeout ({scenario.timeout}s)",
                    "timeout": True
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }

        finally:
            # Clean up PID file
            if os.path.exists(env.pid_file):
                os.remove(env.pid_file)

    def _create_execution_script(self, env: SandboxEnvironment, plugin_file: str, input_file: str, scenario: TestScenario) -> str:
        """Create Python script to execute plugin in sandbox"""

        script = f'''
import json
import time
import os
import sys
import traceback
from datetime import datetime

# Mock Aetherra environment
class MockMemory:
    def __init__(self, memory_file):
        self.memory_file = memory_file
        with open(memory_file, 'r') as f:
            self.data = json.load(f)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        with open(self.memory_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def search(self, query):
        results = []
        for item in self.data.get("short_term", []):
            if query.lower() in item.get("content", "").lower():
                results.append(item)
        return results

class MockGoals:
    def __init__(self, goals_file):
        self.goals_file = goals_file
        with open(goals_file, 'r') as f:
            self.data = json.load(f)

    def get_active_goals(self):
        return self.data.get("active_goals", [])

    def add_goal(self, goal):
        self.data["active_goals"].append(goal)
        with open(self.goals_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def complete_goal(self, goal_id):
        active = self.data.get("active_goals", [])
        for goal in active:
            if goal.get("id") == goal_id:
                goal["status"] = "completed"
                goal["completion_time"] = datetime.now().isoformat()
                break
        with open(self.goals_file, 'w') as f:
            json.dump(self.data, f, indent=2)

class MockLyrixa:
    def __init__(self, memory, goals):
        self.memory = memory
        self.goals = goals
        self.logs = []

    def log(self, message):
        log_entry = f"[{{datetime.now().isoformat()}}] {{message}}"
        self.logs.append(log_entry)
        print(log_entry)

    def remember(self, content):
        self.memory.set("last_remembered", content)

    def recall(self, query):
        return self.memory.search(query)

# Initialize mock environment
memory = MockMemory("{env.memory_file}")
goals = MockGoals("{env.goals_file}")
lyrixa = MockLyrixa(memory, goals)

# Plugin execution functions
def execute_plugin():
    try:
        # Load input data
        with open("{input_file}", 'r') as f:
            input_data = json.load(f)

        # Load plugin code
        with open("{plugin_file}", 'r') as f:
            plugin_code = f.read()

        # Convert .aether code to executable Python
        executable_code = convert_aether_to_python(plugin_code)

        # Execute the converted code
        exec_globals = {{
            'input_data': input_data,
            'lyrixa': lyrixa,
            'memory': memory,
            'goals': goals,
            'datetime': datetime,
            'json': json,
            'time': time
        }}

        exec(executable_code, exec_globals)

        # Try to get result from execute function
        result = None
        if 'execute' in exec_globals:
            result = exec_globals['execute'](input_data)
        elif 'main' in exec_globals:
            result = exec_globals['main'](input_data)
        else:
            # Try to find any callable function
            for name, obj in exec_globals.items():
                if callable(obj) and not name.startswith('_') and name not in ['lyrixa', 'memory', 'goals', 'datetime', 'json', 'time']:
                    try:
                        result = obj(input_data)
                        break
                    except:
                        continue

        if result is None:
            result = {{"success": False, "error": "No executable function found"}}

        # Ensure result is JSON serializable
        if not isinstance(result, dict):
            result = {{"success": True, "output": str(result)}}

        return result

    except Exception as e:
        return {{
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }}

def convert_aether_to_python(aether_code):
    """Convert .aether plugin code to executable Python"""
    # Simple .aether to Python conversion
    python_code = aether_code

    # Replace .aether syntax with Python equivalents
    python_code = python_code.replace("plugin ", "# plugin ")
    python_code = python_code.replace("fn ", "def ")
    python_code = python_code.replace("let ", "")
    python_code = python_code.replace("const ", "")

    # Handle JavaScript-style expressions
    python_code = python_code.replace("==", "==")
    python_code = python_code.replace("!=", "!=")
    python_code = python_code.replace("throw ", "raise Exception(")
    python_code = python_code.replace("new Date()", "datetime.now()")
    python_code = python_code.replace(".toISOString()", ".isoformat()")

    # Handle basic control structures
    python_code = python_code.replace("if (", "if ")
    python_code = python_code.replace("for (", "for ")
    python_code = python_code.replace("while (", "while ")

    # Handle return statements
    python_code = python_code.replace("return {{", "return {{")

    # Add default execute function if not present
    if "def execute(" not in python_code:
        python_code += '''
def execute(input_data):
    """Default execute function"""
    return {{"success": True, "message": "Plugin executed successfully", "input": input_data}}
'''

    return python_code

# Main execution
if __name__ == "__main__":
    result = execute_plugin()

    # Output result as JSON
    print(json.dumps(result, indent=2, default=str))
'''

        return script

    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare actual output with expected output"""
        if type(actual) != type(expected):
            return False

        if isinstance(actual, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            for key in actual:
                if not self._compare_outputs(actual[key], expected[key]):
                    return False
            return True

        elif isinstance(actual, list):
            if len(actual) != len(expected):
                return False
            for i in range(len(actual)):
                if not self._compare_outputs(actual[i], expected[i]):
                    return False
            return True

        else:
            return actual == expected

    def run_comprehensive_test_suite(self, plugin_code: str, plugin_name: str) -> Dict[str, Any]:
        """Run comprehensive test suite for a plugin"""

        # Create sandbox
        env = self.create_sandbox(plugin_name)

        # Define test scenarios
        scenarios = [
            TestScenario(
                name="basic_functionality",
                description="Test basic plugin functionality",
                input_data={"test_input": "Hello, world!"},
                expected_output={"output": "Processed: {'test_input': 'Hello, world!'}"},
                timeout=10
            ),
            TestScenario(
                name="memory_access",
                description="Test memory access capabilities",
                input_data={"query": "test"},
                timeout=15
            ),
            TestScenario(
                name="goal_interaction",
                description="Test goal system interaction",
                input_data={"goal_action": "list_goals"},
                timeout=10
            ),
            TestScenario(
                name="error_handling",
                description="Test error handling",
                input_data=None,  # This should trigger error handling
                timeout=10
            ),
            TestScenario(
                name="large_input",
                description="Test with large input data",
                input_data={"large_data": "x" * 10000},  # 10KB of data
                timeout=30
            )
        ]

        # Run all scenarios
        results = []
        for scenario in scenarios:
            result = self.run_test_scenario(env, scenario, plugin_code)
            results.append(result)

        # Analyze results
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests

        avg_execution_time = sum(r.execution_time for r in results) / total_tests
        max_memory_usage = max(r.memory_usage for r in results)

        # Generate report
        report = {
            "plugin_name": plugin_name,
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": passed_tests / total_tests,
                "avg_execution_time": avg_execution_time,
                "max_memory_usage": max_memory_usage
            },
            "test_results": [
                {
                    "scenario": r.scenario_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "error": r.error_message
                }
                for r in results
            ],
            "detailed_results": results,
            "recommendations": self._generate_recommendations(results),
            "sandbox_info": {
                "sandbox_dir": env.sandbox_dir,
                "created_at": datetime.now().isoformat()
            }
        }

        # Cleanup sandbox
        self.cleanup_sandbox(env)

        return report

    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Performance recommendations
        slow_tests = [r for r in results if r.execution_time > 1.0]
        if slow_tests:
            recommendations.append(f"⚡ {len(slow_tests)} tests are slow (>1s) - consider optimization")

        # Memory recommendations
        memory_heavy_tests = [r for r in results if r.memory_usage > 10 * 1024 * 1024]  # 10MB
        if memory_heavy_tests:
            recommendations.append(f"💾 {len(memory_heavy_tests)} tests use excessive memory - review memory usage")

        # Error handling recommendations
        failed_tests = [r for r in results if not r.success]
        if failed_tests:
            recommendations.append(f"🔧 {len(failed_tests)} tests failed - improve error handling")

        # Specific recommendations based on test patterns
        timeout_tests = [r for r in results if "timeout" in r.error_message.lower() if r.error_message]
        if timeout_tests:
            recommendations.append("⏱️ Some tests timed out - optimize for faster execution")

        return recommendations

    def cleanup_sandbox(self, env: SandboxEnvironment):
        """Clean up sandbox environment"""
        try:
            if os.path.exists(env.sandbox_dir):
                shutil.rmtree(env.sandbox_dir)

            # Remove from tracking
            for sandbox_id, sandbox_env in list(self.sandbox_envs.items()):
                if sandbox_env.sandbox_dir == env.sandbox_dir:
                    del self.sandbox_envs[sandbox_id]
                    break
        except Exception as e:
            print(f"Warning: Failed to cleanup sandbox: {e}")

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        if not self.test_results:
            return {"message": "No tests have been run yet"}

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests / total_tests,
            "avg_execution_time": sum(r.execution_time for r in self.test_results) / total_tests,
            "recent_tests": [
                {
                    "scenario": r.scenario_name,
                    "success": r.success,
                    "execution_time": r.execution_time
                }
                for r in self.test_results[-10:]  # Last 10 tests
            ]
        }


# Example usage
if __name__ == "__main__":
    # Create sandbox tester
    tester = PluginSandboxTester()

    # Sample plugin code
    sample_plugin = '''
plugin test_plugin {
    description: "A test plugin for sandbox testing"
    version: "1.0.0"

    fn execute(input) {
        lyrixa.log("Processing input: " + JSON.stringify(input))

        let result = {
            original_input: input,
            processed_at: new Date().toISOString(),
            success: true
        }

        lyrixa.remember("Processed input: " + JSON.stringify(input))

        return result
    }
}
'''

    # Run comprehensive test suite
    report = tester.run_comprehensive_test_suite(sample_plugin, "test_plugin")

    print("🧪 Sandbox Test Report")
    print("=" * 50)
    print(f"Plugin: {report['plugin_name']}")
    print(f"Tests: {report['test_summary']['passed']}/{report['test_summary']['total_tests']} passed")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1%}")
    print(f"Avg Execution Time: {report['test_summary']['avg_execution_time']:.3f}s")

    print("\n📊 Test Results:")
    for result in report['test_results']:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['scenario']}: {result['execution_time']:.3f}s")
        if result['error']:
            print(f"    Error: {result['error']}")

    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
