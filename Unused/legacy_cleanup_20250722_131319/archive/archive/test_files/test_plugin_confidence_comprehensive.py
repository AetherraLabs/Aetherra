#!/usr/bin/env python3
"""
🧪 PLUGIN CONFIDENCE SYSTEM - COMPREHENSIVE TEST
==============================================

Comprehensive testing and demonstration of the Plugin Confidence & Safety System.
Tests all components: safety analysis, runtime metrics, confidence scoring, and integration.

This script demonstrates:
1. Safety analysis of various plugin code samples
2. Runtime metrics collection and analysis
3. Confidence scoring algorithm
4. Integration with existing Lyrixa systems
5. GUI integration capabilities
"""

import json
from pathlib import Path
from typing import Dict

# Import our confidence system components
try:
    from lyrixa.core.plugin_confidence_integration import ConfidenceEnhancedPluginSystem
    from lyrixa.core.plugin_confidence_system import (
        PluginScorer,
        RuntimeMetrics,
        SafetyAnalysis,
        get_plugin_confidence_warning,
        should_block_plugin_execution,
    )

    CONFIDENCE_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import confidence system: {e}")
    CONFIDENCE_SYSTEM_AVAILABLE = False


class PluginConfidenceTestSuite:
    """Comprehensive test suite for the plugin confidence system."""

    def __init__(self):
        self.test_results = []
        self.temp_files = []

        if CONFIDENCE_SYSTEM_AVAILABLE:
            self.scorer = PluginScorer()
            self.safety_analyzer = SafetyAnalysis()
            self.runtime_metrics = RuntimeMetrics("test_confidence.db")
        else:
            self.scorer = None
            self.safety_analyzer = None
            self.runtime_metrics = None

    def cleanup(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                temp_file.unlink()
            except Exception:
                pass

    def create_test_plugin(self, name: str, code: str) -> Path:
        """Create a temporary plugin file for testing."""

        temp_file = Path(f"test_plugin_{name}.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)

        self.temp_files.append(temp_file)
        return temp_file

    def test_safe_plugin(self) -> Dict:
        """Test analysis of a safe, well-written plugin."""

        if not self.scorer:
            return {
                "test_name": "Safe Plugin Analysis",
                "passed": False,
                "error": "Scorer not available",
            }

        safe_code = '''
"""A safe, well-written plugin example."""

def execute(command: str, **kwargs) -> dict:
    """
    Safe plugin execution function.

    Args:
        command: The command to execute
        **kwargs: Additional arguments

    Returns:
        dict: Execution result
    """
    try:
        # Safe string processing
        result = f"Safely processed: {command}"

        # Safe data manipulation
        data = kwargs.get('data', {})
        processed_data = {k: str(v) for k, v in data.items()}

        return {
            "status": "success",
            "result": result,
            "processed_data": processed_data,
            "execution_time": 0.1
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_info() -> dict:
    """Get plugin information."""
    return {
        "name": "Safe Test Plugin",
        "version": "1.0.0",
        "description": "A safe plugin for testing",
        "author": "Test Suite",
        "capabilities": ["text_processing", "data_manipulation"]
    }

def validate_input(data) -> bool:
    """Validate input data."""
    if not isinstance(data, (str, dict, list)):
        return False
    return True
'''

        plugin_file = self.create_test_plugin("safe", safe_code)
        analysis = self.scorer.analyze_plugin(
            "safe_plugin", safe_code, plugin_file.parent
        )

        return {
            "test_name": "Safe Plugin Analysis",
            "plugin_file": str(plugin_file),
            "confidence_score": analysis["confidence_score"],
            "safety_score": analysis["safety_analysis"]["safety_score"],
            "risk_level": analysis["safety_analysis"]["risk_level"],
            "issues_count": len(analysis["safety_analysis"]["issues"]),
            "warnings_count": len(analysis["safety_analysis"]["warnings"]),
            "passed": analysis["confidence_score"] > 0.6
            and analysis["safety_analysis"]["risk_level"] == "LOW",
        }

    def test_unsafe_plugin(self) -> Dict:
        """Test analysis of an unsafe plugin with security issues."""

        unsafe_code = '''
import os
import subprocess
import pickle

def execute(command, **kwargs):
    """Unsafe plugin with security vulnerabilities."""

    # SECURITY ISSUE: Direct command execution
    result = os.system(command)

    # SECURITY ISSUE: Subprocess with shell=True
    output = subprocess.run(command, shell=True, capture_output=True)

    # SECURITY ISSUE: Dynamic code execution
    user_code = kwargs.get('code', '')
    if user_code:
        exec(user_code)

    # SECURITY ISSUE: Unsafe deserialization
    data = kwargs.get('pickled_data')
    if data:
        unpickled = pickle.loads(data)

    # SECURITY ISSUE: File operations without validation
    filename = kwargs.get('filename', '/etc/passwd')
    with open(filename, 'r') as f:
        content = f.read()

    return {"result": result, "content": content}

def dangerous_function():
    """Function with directory traversal."""
    path = "../../../sensitive_file.txt"
    return open(path).read()
'''

        plugin_file = self.create_test_plugin("unsafe", unsafe_code)
        analysis = self.scorer.analyze_plugin(
            "unsafe_plugin", unsafe_code, plugin_file.parent
        )

        return {
            "test_name": "Unsafe Plugin Analysis",
            "plugin_file": str(plugin_file),
            "confidence_score": analysis["confidence_score"],
            "safety_score": analysis["safety_analysis"]["safety_score"],
            "risk_level": analysis["safety_analysis"]["risk_level"],
            "issues_count": len(analysis["safety_analysis"]["issues"]),
            "warnings_count": len(analysis["safety_analysis"]["warnings"]),
            "passed": analysis["confidence_score"] < 0.5
            and analysis["safety_analysis"]["risk_level"] in ["HIGH", "CRITICAL"],
        }

    def test_complex_plugin(self) -> Dict:
        """Test analysis of a complex but safe plugin."""

        complex_code = '''
"""Complex but safe plugin with high cyclomatic complexity."""

def execute(command, **kwargs):
    """Complex plugin execution with many branches."""

    data = kwargs.get('data', {})
    mode = kwargs.get('mode', 'default')
    options = kwargs.get('options', {})

    result = {"status": "processing"}

    # Complex branching logic (increases cyclomatic complexity)
    if mode == 'process':
        if isinstance(data, dict):
            if 'type' in data:
                if data['type'] == 'text':
                    if options.get('uppercase'):
                        result['processed'] = str(data.get('content', '')).upper()
                    elif options.get('lowercase'):
                        result['processed'] = str(data.get('content', '')).lower()
                    else:
                        result['processed'] = str(data.get('content', ''))
                elif data['type'] == 'number':
                    if options.get('multiply'):
                        result['processed'] = float(data.get('value', 0)) * float(options.get('factor', 1))
                    elif options.get('add'):
                        result['processed'] = float(data.get('value', 0)) + float(options.get('addend', 0))
                    else:
                        result['processed'] = float(data.get('value', 0))
                elif data['type'] == 'list':
                    if options.get('sort'):
                        result['processed'] = sorted(data.get('items', []))
                    elif options.get('reverse'):
                        result['processed'] = list(reversed(data.get('items', [])))
                    else:
                        result['processed'] = data.get('items', [])
                else:
                    result['error'] = 'Unknown data type'
            else:
                result['error'] = 'No type specified'
        else:
            result['error'] = 'Data must be a dictionary'
    elif mode == 'validate':
        if data and isinstance(data, dict):
            result['valid'] = True
        else:
            result['valid'] = False
    elif mode == 'transform':
        # More complex transformations
        try:
            if 'operations' in kwargs:
                for op in kwargs['operations']:
                    if op['type'] == 'filter':
                        data = {k: v for k, v in data.items() if v is not None}
                    elif op['type'] == 'map':
                        data = {k: str(v) for k, v in data.items()}
                    elif op['type'] == 'reduce':
                        if isinstance(data, dict):
                            data = sum(float(v) for v in data.values() if isinstance(v, (int, float)))
            result['transformed'] = data
        except Exception as e:
            result['error'] = f"Transformation failed: {str(e)}"
    else:
        result['error'] = 'Unknown mode'

    result['status'] = 'completed'
    return result

def get_info():
    return {
        "name": "Complex Plugin",
        "version": "1.0.0",
        "description": "A complex but safe plugin for testing complexity analysis"
    }
'''

        plugin_file = self.create_test_plugin("complex", complex_code)
        analysis = self.scorer.analyze_plugin(
            "complex_plugin", complex_code, plugin_file.parent
        )

        return {
            "test_name": "Complex Plugin Analysis",
            "plugin_file": str(plugin_file),
            "confidence_score": analysis["confidence_score"],
            "safety_score": analysis["safety_analysis"]["safety_score"],
            "risk_level": analysis["safety_analysis"]["risk_level"],
            "issues_count": len(analysis["safety_analysis"]["issues"]),
            "warnings_count": len(analysis["safety_analysis"]["warnings"]),
            "passed": analysis["confidence_score"] > 0.5
            and analysis["safety_analysis"]["risk_level"] in ["LOW", "MEDIUM"],
        }

    def test_syntax_error_plugin(self) -> Dict:
        """Test analysis of a plugin with syntax errors."""

        broken_code = '''
def execute(command, **kwargs):
    """Plugin with syntax errors."""

    # Missing closing parenthesis
    result = process_data(command, kwargs

    # Invalid indentation
  return result

def invalid_function(
    # Missing closing parenthesis and colon

# Invalid syntax
class TestClass
    def __init__(self):
        pass
'''

        plugin_file = self.create_test_plugin("broken", broken_code)
        analysis = self.scorer.analyze_plugin(
            "broken_plugin", broken_code, plugin_file.parent
        )

        return {
            "test_name": "Broken Plugin Analysis",
            "plugin_file": str(plugin_file),
            "confidence_score": analysis["confidence_score"],
            "safety_score": analysis["safety_analysis"]["safety_score"],
            "risk_level": analysis["safety_analysis"]["risk_level"],
            "issues_count": len(analysis["safety_analysis"]["issues"]),
            "warnings_count": len(analysis["safety_analysis"]["warnings"]),
            "passed": analysis["confidence_score"] < 0.4
            and analysis["safety_analysis"]["risk_level"] == "CRITICAL",
        }

    def test_runtime_metrics(self) -> Dict:
        """Test runtime metrics collection and analysis."""

        # Use a fresh metrics instance for testing
        from lyrixa.core.plugin_confidence_system import RuntimeMetrics

        test_metrics = RuntimeMetrics("test_runtime_fresh.db")

        # Simulate plugin executions
        plugin_name = "test_runtime_plugin_fresh"

        # Record successful executions
        for i in range(10):
            test_metrics.record_execution(
                plugin_name,
                execution_time=0.1 + (i * 0.01),  # Gradually increasing time
                success=True,
            )

        # Record some failures
        for i in range(3):
            test_metrics.record_execution(
                plugin_name,
                execution_time=0.5,
                success=False,
                error_info={"type": "ValueError", "message": "Invalid input"},
            )

        # Get metrics
        metrics = test_metrics.get_plugin_metrics(plugin_name)

        return {
            "test_name": "Runtime Metrics Collection",
            "plugin_name": plugin_name,
            "total_executions": metrics["total_executions"],
            "success_rate": metrics["success_rate"],
            "avg_execution_time": metrics["avg_execution_time"],
            "error_frequency": metrics["error_frequency"],
            "common_errors": metrics["common_errors"],
            "passed": (
                metrics["total_executions"] == 13
                and abs(metrics["success_rate"] - 10 / 13) < 0.01
                and metrics["error_frequency"] == 3 / 13
            ),
        }

    def test_integration_system(self) -> Dict:
        """Test the integration system with mock Lyrixa instance."""

        class MockLyrixa:
            def __init__(self):
                self.warnings = []
                self.errors = []
                self.recommendations = []

            def show_warning(self, title, message):
                self.warnings.append((title, message))

            def show_error(self, title, message):
                self.errors.append((title, message))

            def show_recommendations(self, plugin_name, recommendations):
                self.recommendations.append((plugin_name, recommendations))

        # Create mock Lyrixa instance
        mock_lyrixa = MockLyrixa()

        # Initialize integration system
        integration = ConfidenceEnhancedPluginSystem(lyrixa_instance=mock_lyrixa)

        # Test safe plugin loading
        safe_code = """
def execute(command, **kwargs):
    return {"result": "success"}

def get_info():
    return {"name": "Test Plugin"}
"""
        safe_file = self.create_test_plugin("integration_safe", safe_code)

        load_result = integration.load_plugin_with_confidence_check(
            "safe_plugin", safe_file
        )

        # Test unsafe plugin loading (should be blocked)
        unsafe_code = """
import os

def execute(command, **kwargs):
    os.system(command)  # Unsafe!
    return {"result": "executed"}
"""
        unsafe_file = self.create_test_plugin("integration_unsafe", unsafe_code)

        unsafe_result = integration.load_plugin_with_confidence_check(
            "unsafe_plugin", unsafe_file
        )

        return {
            "test_name": "Integration System Test",
            "safe_plugin_loaded": load_result.get("loaded", False),
            "unsafe_plugin_blocked": unsafe_result.get("blocked", False),
            "warnings_generated": len(mock_lyrixa.warnings),
            "errors_generated": len(mock_lyrixa.errors),
            "passed": (
                load_result.get("loaded", False) and unsafe_result.get("blocked", False)
            ),
        }

    def run_all_tests(self) -> Dict:
        """Run all tests and return comprehensive results."""

        if not CONFIDENCE_SYSTEM_AVAILABLE:
            return {
                "success": False,
                "error": "Confidence system not available for testing",
                "tests_run": 0,
                "tests_passed": 0,
            }

        print("🧪 Running Plugin Confidence System Tests...")
        print("=" * 60)

        tests = [
            self.test_safe_plugin,
            self.test_unsafe_plugin,
            self.test_complex_plugin,
            self.test_syntax_error_plugin,
            self.test_runtime_metrics,
            self.test_integration_system,
        ]

        results = []
        passed_count = 0

        for i, test_func in enumerate(tests, 1):
            print(f"\n🔍 Test {i}/{len(tests)}: {test_func.__name__}")

            try:
                result = test_func()
                results.append(result)

                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                print(f"   {status}: {result['test_name']}")

                if result["passed"]:
                    passed_count += 1

                # Print key metrics
                if "confidence_score" in result:
                    print(f"   📊 Confidence: {result['confidence_score']:.1%}")
                    print(f"   🛡️ Risk Level: {result['risk_level']}")

            except Exception as e:
                error_result = {
                    "test_name": test_func.__name__,
                    "passed": False,
                    "error": str(e),
                }
                results.append(error_result)
                print(f"   ❌ FAILED: {test_func.__name__} - {str(e)}")

        self.cleanup()

        print("\n" + "=" * 60)
        print(f"🏁 Test Summary: {passed_count}/{len(tests)} tests passed")
        print("=" * 60)

        return {
            "success": True,
            "tests_run": len(tests),
            "tests_passed": passed_count,
            "pass_rate": passed_count / len(tests),
            "detailed_results": results,
        }


def demonstrate_confidence_features():
    """Demonstrate key features of the confidence system."""

    if not CONFIDENCE_SYSTEM_AVAILABLE:
        print("❌ Confidence system not available for demonstration")
        return

    print("\n🎯 PLUGIN CONFIDENCE SYSTEM DEMONSTRATION")
    print("=" * 60)

    # Initialize scorer
    scorer = PluginScorer()

    # Demonstrate different plugin types
    plugins = {
        "Safe Plugin": '''
def execute(command, **kwargs):
    """Safe plugin example."""
    return {"result": f"Processed: {command}"}

def get_info():
    return {"name": "Safe Plugin", "version": "1.0.0"}
''',
        "Risky Plugin": '''
import os
import subprocess

def execute(command, **kwargs):
    """Risky plugin with security issues."""
    result = os.system(command)
    subprocess.run(command, shell=True)
    return {"result": result}
''',
        "Performance Issue Plugin": '''
def execute(command, **kwargs):
    """Plugin with performance issues."""
    import time
    time.sleep(2)  # Simulated slow operation

    # Inefficient algorithm
    result = []
    for i in range(10000):
        for j in range(1000):
            if i % j == 0:
                result.append((i, j))

    return {"result": len(result)}
''',
    }

    for plugin_name, code in plugins.items():
        print(f"\n📦 Analyzing: {plugin_name}")
        print("-" * 40)

        analysis = scorer.analyze_plugin(plugin_name.lower().replace(" ", "_"), code)

        print(f"🔍 Confidence Score: {analysis['confidence_score']:.1%}")
        print(f"🛡️ Safety Score: {analysis['safety_analysis']['safety_score']:.1f}/100")
        print(f"⚠️ Risk Level: {analysis['safety_analysis']['risk_level']}")

        # Show warnings
        warning = get_plugin_confidence_warning(
            plugin_name,
            analysis["confidence_score"],
            analysis["safety_analysis"]["risk_level"],
        )

        if warning:
            print(f"💬 Warning: {warning}")

        # Show blocking decision
        should_block = should_block_plugin_execution(
            analysis["safety_analysis"]["risk_level"], analysis["confidence_score"]
        )

        if should_block:
            print("🚫 Execution: BLOCKED")
        else:
            print("✅ Execution: ALLOWED")

        # Show issues and recommendations
        issues = analysis["safety_analysis"]["issues"]
        if issues:
            print(f"🚨 Issues Found: {len(issues)}")
            for issue in issues[:2]:  # Show first 2 issues
                print(f"   • {issue['type']}: {issue['message']}")

        recommendations = analysis["recommendations"]
        if recommendations:
            print(f"💡 Recommendations: {len(recommendations)}")
            for rec in recommendations[:2]:  # Show first 2 recommendations
                print(f"   • {rec['type']}: {rec['message']}")


if __name__ == "__main__":
    print("🧬 PLUGIN CONFIDENCE & SAFETY SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)

    # Run demonstration
    demonstrate_confidence_features()

    # Run test suite
    test_suite = PluginConfidenceTestSuite()
    results = test_suite.run_all_tests()

    if results["success"]:
        if results["pass_rate"] == 1.0:
            print(
                "\n🎉 ALL TESTS PASSED! The Plugin Confidence System is working perfectly."
            )
        else:
            print(f"\n⚠️ {results['tests_passed']}/{results['tests_run']} tests passed.")
            print("Some components may need attention.")
    else:
        print(f"\n❌ Test suite failed: {results.get('error', 'Unknown error')}")

    # Save detailed results
    with open("plugin_confidence_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n📁 Detailed results saved to: plugin_confidence_test_results.json")
    print("🏁 Testing completed!")
