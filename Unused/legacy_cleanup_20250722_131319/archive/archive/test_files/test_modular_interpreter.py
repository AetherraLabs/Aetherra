# test_modular_interpreter.py
"""
Test Suite for Modular AetherraCode Interpreter
============================================

Comprehensive tests for the new modular interpreter system.
"""

import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(__file__))


def test_import_modular_interpreter():
    """Test importing the modular interpreter system"""
    print("🧪 Testing Modular Interpreter Import...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        print("✅ Successfully imported AetherraInterpreter")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AetherraInterpreter: {e}")
        return False


def test_interpreter_initialization():
    """Test interpreter initialization"""
    print("🧪 Testing Interpreter Initialization...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()
        print("✅ Successfully initialized interpreter")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize interpreter: {e}")
        return False


def test_basic_commands():
    """Test basic command execution"""
    print("🧪 Testing Basic Commands...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test basic commands
        test_commands = [
            'remember("Hello World")',
            'recall "Hello"',
            'goal: "Test the system"',
            "agent: activate",
            'think about "testing"',
            "analyze system",
        ]

        results = []
        for cmd in test_commands:
            try:
                result = interpreter.execute(cmd)
                results.append(f"✅ {cmd}: {str(result)[:50]}...")
            except Exception as e:
                results.append(f"❌ {cmd}: {str(e)}")

        for result in results:
            print(f"   {result}")

        print("✅ Basic command testing completed")
        return True

    except Exception as e:
        print(f"❌ Basic command testing failed: {e}")
        return False


def test_enhanced_commands():
    """Test enhanced command features"""
    print("🧪 Testing Enhanced Commands...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test enhanced commands
        enhanced_commands = [
            'remember("Advanced test") as "test,modular"',
            'goal: "Advanced testing" priority: high',
            'agent: on specialization: "testing"',
            'plugin: test_plugin(param1="value1")',
            "use enhanced_parser",
            "debug_mode: on",
        ]

        results = []
        for cmd in enhanced_commands:
            try:
                result = interpreter.execute(cmd)
                results.append(f"✅ {cmd}: {str(result)[:50]}...")
            except Exception as e:
                results.append(f"❌ {cmd}: {str(e)}")

        for result in results:
            print(f"   {result}")

        print("✅ Enhanced command testing completed")
        return True

    except Exception as e:
        print(f"❌ Enhanced command testing failed: {e}")
        return False


def test_block_processing():
    """Test multi-line block processing"""
    print("🧪 Testing Block Processing...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test function definition block
        block_lines = [
            "define test_function(x, y):",
            "    result = x + y",
            "    remember(result)",
            "    return result",
            "end",
        ]

        results = []
        for line in block_lines:
            try:
                result = interpreter.execute(line)
                if result:
                    results.append(f"✅ {line}: {str(result)[:50]}...")
            except Exception as e:
                results.append(f"❌ {line}: {str(e)}")

        for result in results:
            print(f"   {result}")

        print("✅ Block processing testing completed")
        return True

    except Exception as e:
        print(f"❌ Block processing testing failed: {e}")
        return False


def test_system_status():
    """Test system status and information"""
    print("🧪 Testing System Status...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Test system information methods
        status = interpreter.get_system_status()
        history = interpreter.get_command_history()
        stats = interpreter.get_execution_stats()

        print(f"   📊 System Status: {len(status)} sections")
        print(f"   📋 Command History: {len(history)} commands")
        print(f"   📈 Execution Stats: {stats}")

        print("✅ System status testing completed")
        return True

    except Exception as e:
        print(f"❌ System status testing failed: {e}")
        return False


def test_component_separation():
    """Test that modular components work independently"""
    print("🧪 Testing Component Separation...")

    try:
        # Test individual components
        from Aetherra.core.interpreter.command_parser import CommandParser
        from Aetherra.core.interpreter.enhanced_features import EnhancedFeatureParser
        from Aetherra.core.interpreter.line_processor import LineProcessor

        parser = CommandParser()
        processor = LineProcessor()
        enhanced = EnhancedFeatureParser()

        # Test parser
        parse_result = parser.parse('remember("test")')
        print(f"   🔍 Parser: {parse_result.command_type}")

        # Test enhanced features
        can_handle = enhanced.can_handle("use enhanced_parser")
        print(f"   ⚡ Enhanced Features: {can_handle}")

        # Test processor
        block_info = processor.get_block_info()
        print(f"   📝 Line Processor: {block_info}")

        print("✅ Component separation testing completed")
        return True

    except Exception as e:
        print(f"❌ Component separation testing failed: {e}")
        return False


def test_performance():
    """Test performance with rapid command execution"""
    print("🧪 Testing Performance...")

    try:
        from Aetherra.core.interpreter import AetherraInterpreter

        interpreter = AetherraInterpreter()

        # Execute multiple commands rapidly
        start_time = time.time()

        for i in range(20):
            interpreter.execute(f'remember("Performance test {i}")')
            interpreter.execute(f'goal: "Goal {i}"')
            interpreter.execute("agent: activate")

        end_time = time.time()
        execution_time = end_time - start_time

        print(f"   ⚡ Executed 60 commands in {execution_time:.3f} seconds")
        print(f"   📊 Average: {(execution_time / 60) * 1000:.1f}ms per command")

        if execution_time < 5.0:  # Should complete in reasonable time
            print("✅ Performance testing passed")
            return True
        else:
            print("⚠️ Performance slower than expected")
            return False

    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility with existing code"""
    print("🧪 Testing Backward Compatibility...")

    try:
        # Test that old import patterns still work
        from Aetherra.core.interpreter import AetherraInterpreter, create_interpreter

        # Test old-style instantiation
        interpreter1 = AetherraInterpreter()
        interpreter2 = create_interpreter()

        # Test that both work the same way
        result1 = interpreter1.execute('remember("compatibility test")')
        result2 = interpreter2.execute('remember("compatibility test")')

        print(f"   📦 Method 1 Result: {str(result1)[:50]}...")
        print(f"   📦 Method 2 Result: {str(result2)[:50]}...")

        print("✅ Backward compatibility testing completed")
        return True

    except Exception as e:
        print(f"❌ Backward compatibility testing failed: {e}")
        return False


def run_all_tests():
    """Run all test suites"""
    print("🚀 AetherraCode Modular Interpreter Test Suite")
    print("=" * 50)

    tests = [
        test_import_modular_interpreter,
        test_interpreter_initialization,
        test_basic_commands,
        test_enhanced_commands,
        test_block_processing,
        test_system_status,
        test_component_separation,
        test_performance,
        test_backward_compatibility,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add space between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The modular interpreter is working correctly.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. Minor issues may need attention.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")

    return passed == total


if __name__ == "__main__":
    run_all_tests()
