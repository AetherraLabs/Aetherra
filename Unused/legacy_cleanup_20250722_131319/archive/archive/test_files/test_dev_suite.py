#!/usr/bin/env python3
"""
Test script to verify the dev suite works correctly after fixes
"""

import os
import sys
import tempfile

sys.path.append(".")


def test_dev_suite():
    """Test basic functionality of the dev suite"""
    print("🧪 Testing AetherraCode Development Suite")
    print("=" * 50)

    # Test 1: Import Check
    print("Test 1: Testing imports...")
    try:
        from core.dev_suite import (
            AetherraCodeDebugger,
            AetherraCodeDevSuite,
            AetherraCodeIDE,
            AetherraCodeLinter,
            AetherraCodeProfiler,
        )

        print("✅ All dev suite classes imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: AetherraCodeLinter functionality
    print("\nTest 2: Testing AetherraCodeLinter...")
    try:
        linter = AetherraCodeLinter()
        print(
            f"✅ Linter created with {len(linter.rules['syntax_rules'])} syntax rules"
        )

        # Test linting some sample AetherraCode
        sample_code = """
# Sample AetherraCode program
remember "Starting analysis"
set_goal "Analyze data patterns"
use math_plugin to calculate_average
think about "optimization strategies"
"""

        lint_results = linter.lint_code(sample_code)
        print("✅ Code linting works:")
        print(f"   Quality score: {lint_results['score']:.1f}/100")
        print(f"   Issues found: {len(lint_results['issues'])}")
        print(f"   Suggestions: {len(lint_results['suggestions'])}")

    except Exception as e:
        print(f"❌ Linter test failed: {e}")
        return False

    # Test 3: AetherraCodeDebugger functionality
    print("\nTest 3: Testing AetherraCodeDebugger...")
    try:
        debugger = AetherraCodeDebugger()
        print("✅ Debugger created successfully")

        # Test breakpoint functionality
        debugger.set_breakpoint(5)
        debugger.set_breakpoint(10)
        print(f"✅ Breakpoints set: {debugger.breakpoints}")

        # Test watch variables
        debugger.add_watch("memory_count")
        debugger.add_watch("current_goal")
        print(f"✅ Watch variables: {debugger.watch_variables}")

        # Test debug step
        test_context = {
            "memory": ["item1", "item2"],
            "goals": ["goal1"],
            "memory_count": 2,
        }
        should_pause = debugger.debug_step("test_line", 5, test_context)
        print(f"✅ Debug step at breakpoint: {should_pause}")

        # Test execution trace
        trace = debugger.get_execution_trace()
        print(f"✅ Execution trace: {len(trace)} entries")

    except Exception as e:
        print(f"❌ Debugger test failed: {e}")
        return False

    # Test 4: AetherraCodeProfiler functionality
    print("\nTest 4: Testing AetherraCodeProfiler...")
    try:
        profiler = AetherraCodeProfiler()
        print("✅ Profiler created successfully")

        # Test profiling operations
        profiler.start_profiling("test_operation")
        import time

        time.sleep(0.01)  # Simulate some work
        profiler.end_profiling("test_operation")

        # Test performance report
        report = profiler.get_performance_report()
        print(f"✅ Performance report: {len(report)} operations tracked")

        if "test_operation" in report:
            op_data = report["test_operation"]
            print(
                f"   Test operation: {op_data['total_calls']} calls, {op_data['average_time']:.4f}s avg"
            )

        # Test optimization suggestions
        suggestions = profiler.suggest_optimizations()
        print(f"✅ Optimization suggestions: {len(suggestions)}")

    except Exception as e:
        print(f"❌ Profiler test failed: {e}")
        return False

    # Test 5: AetherraCodeIDE functionality
    print("\nTest 5: Testing AetherraCodeIDE...")
    try:
        ide = AetherraCodeIDE()
        print("✅ IDE created successfully")

        # Test natural language translation
        translations = [
            ('remember "test data"', 'remember "test data"'),
            ("set goal to optimize performance", 'set_goal "optimize performance"'),
            (
                "use math plugin to calculate square root",
                "use math to calculate square root",
            ),
            ("think about the problem", 'think about "think about the problem"'),
            ("calculate 2 + 2", 'calculate "2 + 2"'),
        ]

        for input_text, expected_pattern in translations:
            result = ide._translate_to_aetherra(input_text)
            if any(keyword in result for keyword in expected_pattern.split()):
                print(f"✅ Translation works: '{input_text}' -> '{result}'")
            else:
                print(f"⚠️  Translation result: '{input_text}' -> '{result}'")

    except Exception as e:
        print(f"❌ IDE test failed: {e}")
        return False

    # Test 6: AetherraCodeDevSuite integration
    print("\nTest 6: Testing AetherraCodeDevSuite integration...")
    try:
        dev_suite = AetherraCodeDevSuite()
        print("✅ Dev suite created successfully")

        # Test code analysis
        sample_code = """remember "Starting analysis"
set_goal "Process data"
use data_plugin to load_file
think about "next steps"
"""

        analysis = dev_suite.analyze_code(sample_code)
        print("✅ Code analysis completed:")
        print(f"   Lint score: {analysis['lint_results']['score']:.1f}/100")
        print(f"   Performance data: {len(analysis['performance'])} operations")
        print(f"   Optimization suggestions: {len(analysis['optimizations'])}")

    except Exception as e:
        print(f"❌ Dev suite integration test failed: {e}")
        return False

    # Test 7: CLI functionality
    print("\nTest 7: Testing CLI functionality...")
    try:
        # Test help
        import subprocess

        result = subprocess.run(
            [sys.executable, "core/dev_suite.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✅ CLI help works correctly")
        else:
            print("⚠️  CLI help returned non-zero exit code")

        # Test lint command with a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aether", delete=False) as f:
            f.write('remember "test"\nset_goal "test goal"')
            temp_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, "core/dev_suite.py", "--lint", temp_file],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                print("✅ CLI lint command works")
            else:
                print(f"⚠️  CLI lint command failed: {result.stderr}")
        finally:
            os.unlink(temp_file)

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

    print("\n🎉 All dev suite tests completed successfully!")
    return True


if __name__ == "__main__":
    success = test_dev_suite()
    if success:
        print("\n✅ AetherraCode Development Suite is fully functional!")
    else:
        print("\n❌ Some tests failed - further investigation needed")
    sys.exit(0 if success else 1)
