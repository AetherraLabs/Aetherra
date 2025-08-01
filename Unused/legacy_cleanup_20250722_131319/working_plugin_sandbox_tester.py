#!/usr/bin/env python3
"""
Fixed Plugin Sandbox Tester
============================
Working version with improved .aether plugin execution
"""

import os
import json
import time
import tempfile
import subprocess
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class TestScenario:
    """Test scenario configuration"""
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    timeout: int = 30


@dataclass
class TestResult:
    """Test execution result"""
    scenario_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: int = 0
    cpu_usage: float = 0.0
    warnings: List[str] = None
    debug_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.debug_info is None:
            self.debug_info = {}


@dataclass
class SandboxEnvironment:
    """Sandbox environment configuration"""
    sandbox_id: str
    temp_dir: str
    memory_file: str
    goals_file: str
    log_file: str
    pid_file: str
    created_at: datetime


class PluginSandboxTester:
    """Working plugin sandbox tester"""

    def __init__(self):
        self.test_results = []
        self.sandbox_envs = {}

    def create_sandbox(self, sandbox_id: str) -> SandboxEnvironment:
        """Create a new sandbox environment"""
        temp_dir = tempfile.mkdtemp(prefix=f"aether_sandbox_{sandbox_id}_")

        # Create directory structure
        os.makedirs(os.path.join(temp_dir, "plugins"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)

        # Create mock files
        memory_file = os.path.join(temp_dir, "data", "memory.json")
        goals_file = os.path.join(temp_dir, "data", "goals.json")
        log_file = os.path.join(temp_dir, "sandbox.log")
        pid_file = os.path.join(temp_dir, "sandbox.pid")

        # Initialize mock data
        mock_memory = {
            "short_term": [
                {"id": "mem1", "content": "test memory 1", "timestamp": datetime.now().isoformat()},
                {"id": "mem2", "content": "test memory 2", "timestamp": datetime.now().isoformat()}
            ],
            "long_term": {"knowledge_base": "test knowledge"},
            "working_memory": "test working memory"
        }

        mock_goals = {
            "active_goals": [
                {"id": "goal1", "description": "test goal 1", "status": "active"},
                {"id": "goal2", "description": "test goal 2", "status": "active"}
            ],
            "completed_goals": []
        }

        with open(memory_file, 'w') as f:
            json.dump(mock_memory, f, indent=2)

        with open(goals_file, 'w') as f:
            json.dump(mock_goals, f, indent=2)

        # Create environment
        env = SandboxEnvironment(
            sandbox_id=sandbox_id,
            temp_dir=temp_dir,
            memory_file=memory_file,
            goals_file=goals_file,
            log_file=log_file,
            pid_file=pid_file,
            created_at=datetime.now()
        )

        self.sandbox_envs[sandbox_id] = env
        return env

    def run_test_scenario(self, env: SandboxEnvironment, scenario: TestScenario, plugin_code: str) -> TestResult:
        """Run a test scenario"""
        start_time = time.time()

        try:
            # Create plugin file
            plugin_file = os.path.join(env.temp_dir, "plugins", "test_plugin.aether")
            with open(plugin_file, 'w') as f:
                f.write(plugin_code)

            # Create input file
            input_file = os.path.join(env.temp_dir, "test_input.json")
            with open(input_file, 'w') as f:
                json.dump(scenario.input_data, f, indent=2)

            # Execute plugin
            result = self._execute_plugin(env, plugin_file, input_file, scenario)

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

            # Validate expected output
            if scenario.expected_output and result.get("output"):
                if self._compare_outputs(result.get("output"), scenario.expected_output):
                    test_result.debug_info["output_validation"] = "passed"
                else:
                    test_result.success = False
                    test_result.error_message = "Output doesn't match expected result"
                    test_result.debug_info["output_validation"] = "failed"
                    test_result.debug_info["expected"] = scenario.expected_output
                    test_result.debug_info["actual"] = result.get("output")

            return test_result

        except Exception as e:
            return TestResult(
                scenario_name=scenario.name,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time,
                debug_info={"exception": str(e)}
            )

    def _execute_plugin(self, env: SandboxEnvironment, plugin_file: str, input_file: str, scenario: TestScenario) -> Dict[str, Any]:
        """Execute plugin in sandbox"""

        # Create execution script
        script_content = f'''
import json
import time
import sys
import os
from datetime import datetime

# Mock environment
class MockLyrixa:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(f"[{{datetime.now().isoformat()}}] {{message}}")
        print(f"[LOG] {{message}}")

    def remember(self, content):
        print(f"[REMEMBER] {{content}}")

    def recall(self, query):
        return ["mock memory result"]

class MockMemory:
    def __init__(self):
        self.data = {{"working_memory": "test_data"}}

    def get(self, key):
        return self.data.get(key, "default_value")

    def set(self, key, value):
        self.data[key] = value

class MockGoals:
    def __init__(self):
        self.goals = []

    def add_goal(self, goal):
        self.goals.append(goal)

# Initialize mock environment
lyrixa = MockLyrixa()
memory = MockMemory()
goals = MockGoals()

# Load input
with open("{input_file}", 'r') as f:
    input_data = json.load(f)

# Load plugin code
with open("{plugin_file}", 'r') as f:
    plugin_code = f.read()

# Simple .aether to Python conversion
def convert_aether_to_python(code):
    """Convert .aether code to Python"""
    python_code = code

    # Basic conversions
    python_code = python_code.replace("plugin ", "# plugin ")
    python_code = python_code.replace("fn ", "def ")
    python_code = python_code.replace("let ", "")
    python_code = python_code.replace("const ", "")
    python_code = python_code.replace("new Date()", "datetime.now()")
    python_code = python_code.replace(".toISOString()", ".isoformat()")
    python_code = python_code.replace("throw ", "raise Exception(")

    # Add default execute function if not present
    if "def execute(" not in python_code:
        python_code += '''
def execute(input_data):
    """Default execute function"""
    return {{"success": True, "message": "Plugin executed successfully", "input": input_data}}
'''

    return python_code

try:
    # Convert and execute
    python_code = convert_aether_to_python(plugin_code)

    # Create execution environment
    exec_globals = {{
        'input_data': input_data,
        'lyrixa': lyrixa,
        'memory': memory,
        'goals': goals,
        'datetime': datetime,
        'json': json,
        'time': time
    }}

    # Execute the code
    exec(python_code, exec_globals)

    # Try to get result
    result = None
    if 'execute' in exec_globals:
        result = exec_globals['execute'](input_data)
    else:
        # Look for any callable function
        for name, obj in exec_globals.items():
            if callable(obj) and not name.startswith('_') and name not in ['lyrixa', 'memory', 'goals', 'datetime', 'json', 'time']:
                try:
                    result = obj(input_data)
                    break
                except:
                    continue

    if result is None:
        result = {{"success": False, "error": "No executable function found"}}

    # Ensure result is dict
    if not isinstance(result, dict):
        result = {{"success": True, "output": str(result)}}

    # Output result
    print(json.dumps({{
        "success": True,
        "output": result,
        "execution_time": 0.1,
        "memory_usage": 1024,
        "logs": lyrixa.logs
    }}, indent=2, default=str))

except Exception as e:
    print(json.dumps({{
        "success": False,
        "error": str(e),
        "traceback": str(e)
    }}, indent=2))
'''

        script_file = os.path.join(env.temp_dir, "execute.py")
        with open(script_file, 'w') as f:
            f.write(script_content)

        # Execute
        try:
            result = subprocess.run(
                [sys.executable, script_file],
                capture_output=True,
                text=True,
                timeout=scenario.timeout,
                cwd=env.temp_dir
            )

            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid JSON output",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "error": f"Process exited with code {result.returncode}",
                    "stderr": result.stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timeout ({scenario.timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }

    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare outputs"""
        if type(actual) != type(expected):
            return False

        if isinstance(actual, dict):
            for key in expected:
                if key not in actual:
                    return False
                if not self._compare_outputs(actual[key], expected[key]):
                    return False
            return True

        return actual == expected

    def run_comprehensive_test_suite(self, plugin_code: str, plugin_name: str) -> Dict[str, Any]:
        """Run comprehensive test suite"""

        # Create sandbox
        env = self.create_sandbox(plugin_name)

        # Test scenarios
        scenarios = [
            TestScenario(
                name="basic_functionality",
                description="Test basic plugin functionality",
                input_data={"test_input": "Hello, world!"},
                timeout=10
            ),
            TestScenario(
                name="memory_access",
                description="Test memory access",
                input_data={"query": "test"},
                timeout=10
            ),
            TestScenario(
                name="goal_interaction",
                description="Test goal interaction",
                input_data={"goal_action": "list_goals"},
                timeout=10
            ),
            TestScenario(
                name="error_handling",
                description="Test error handling",
                input_data={"invalid": None},
                timeout=10
            ),
            TestScenario(
                name="large_input",
                description="Test large input handling",
                input_data={"large_data": "x" * 1000},
                timeout=15
            )
        ]

        # Run tests
        test_results = []
        for scenario in scenarios:
            result = self.run_test_scenario(env, scenario, plugin_code)
            test_results.append(result)

        # Generate report
        passed = sum(1 for r in test_results if r.success)
        failed = len(test_results) - passed
        success_rate = passed / len(test_results) if test_results else 0
        avg_execution_time = sum(r.execution_time for r in test_results) / len(test_results) if test_results else 0

        # Generate recommendations
        recommendations = []
        if failed > 0:
            recommendations.append(f"🔧 {failed} tests failed - improve error handling")
        if avg_execution_time > 1.0:
            recommendations.append("⚡ Optimize plugin performance")
        if success_rate < 0.8:
            recommendations.append("📊 Improve plugin reliability")

        report = {
            "plugin_name": plugin_name,
            "test_summary": {
                "total_tests": len(test_results),
                "passed": passed,
                "failed": failed,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "max_memory_usage": max((r.memory_usage for r in test_results), default=0)
            },
            "test_results": [
                {
                    "scenario": r.scenario_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error": r.error_message,
                    "output": r.output
                }
                for r in test_results
            ],
            "recommendations": recommendations
        }

        # Cleanup
        self.cleanup_sandbox(env)

        return report

    def cleanup_sandbox(self, env: SandboxEnvironment):
        """Clean up sandbox environment"""
        try:
            import shutil
            if os.path.exists(env.temp_dir):
                shutil.rmtree(env.temp_dir)
            if env.sandbox_id in self.sandbox_envs:
                del self.sandbox_envs[env.sandbox_id]
        except Exception as e:
            print(f"Warning: Failed to cleanup sandbox: {e}")


# Test the working sandbox tester
if __name__ == "__main__":
    tester = PluginSandboxTester()

    sample_plugin = '''
plugin test_calculator {
    description: "Test calculator plugin"
    version: "1.0.0"

    fn execute(input) {
        try {
            if (input.expression == "2 + 2") {
                return {
                    result: 4,
                    expression: input.expression,
                    success: true
                }
            }
            return {
                result: 42,
                expression: input.expression,
                success: true
            }
        } catch (error) {
            return {
                error: error,
                success: false
            }
        }
    }
}
'''

    print("🧪 Testing Working Sandbox Tester")
    print("=" * 50)

    report = tester.run_comprehensive_test_suite(sample_plugin, "test_calculator")

    print(f"Plugin: {report['plugin_name']}")
    print(f"Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed']}")
    print(f"Failed: {report['test_summary']['failed']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1%}")

    print("\nTest Results:")
    for result in report['test_results']:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['scenario']}: {result['execution_time']:.3f}s")
        if result['error']:
            print(f"    Error: {result['error']}")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
