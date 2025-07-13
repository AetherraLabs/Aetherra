# test_runtime_system.py
"""
Test Suite for Aetherra Runtime System
=======================================

This test validates the modular runtime system including execution context,
code executor, and runtime services.
"""

from Aetherra.core.runtime import ExecutionContext, ExecutionMode, RuntimeServices
from Aetherra.core.runtime.context import RuntimeEnvironment
from Aetherra.core.runtime.executor import ExecutionStatus


def test_runtime_environment():
    """Test runtime environment creation and management"""
    env = RuntimeEnvironment()

    # Test context creation
    context1 = env.create_context(ExecutionMode.INTERACTIVE)
    context2 = env.create_context(ExecutionMode.BATCH)

    assert len(env.contexts) == 2
    assert context1.session_id != context2.session_id
    assert context1.mode == ExecutionMode.INTERACTIVE
    assert context2.mode == ExecutionMode.BATCH

    # Test active context management
    assert env.set_active_context(context1.session_id)
    assert env.get_active_context() == context1

    print("✓ Runtime environment test passed")


def test_execution_context():
    """Test execution context functionality"""
    context = ExecutionContext(mode=ExecutionMode.DEBUG, debug_mode=True)

    # Test variable management
    context.set_variable("test_var", "test_value")
    assert context.get_variable("test_var") == "test_value"
    assert context.has_variable("test_var")
    assert not context.has_variable("nonexistent")

    # Test function registration
    test_func = {"name": "test", "params": ["x"], "body": []}
    context.register_function("test", test_func)
    assert context.get_function("test") == test_func

    # Test call stack
    assert context.call_depth() == 0
    context.push_call("test_function")
    assert context.call_depth() == 1
    assert context.current_call() == "test_function"

    popped = context.pop_call()
    assert popped == "test_function"
    assert context.call_depth() == 0

    print("✓ Execution context test passed")


def test_code_execution():
    """Test code execution functionality"""
    # Create runtime services
    runtime = RuntimeServices()

    # Create execution context
    context = runtime.create_execution_context(ExecutionMode.INTERACTIVE)

    # Test simple code execution
    code = """
    # Simple Aetherra test
    goal: Test runtime execution

    x = 42
    y = "hello world"

    remember("Test execution completed")
    """

    result = runtime.execute_code(code, context)

    assert result.is_success()
    assert result.nodes_executed > 0
    assert len(result.output) > 0

    # Check variables were set
    assert context.get_variable("x") == "42"  # Note: stored as string for now
    assert context.get_variable("y") == '"hello world"'

    print("✓ Code execution test passed")


def test_function_execution():
    """Test function definition and execution"""
    runtime = RuntimeServices()
    context = runtime.create_execution_context(ExecutionMode.INTERACTIVE)

    code = """
    define greet(name)
        assistant: "Hello " + name
        remember("Greeted " + name)
    end

    run greet("World")
    """

    result = runtime.execute_code(code, context)

    assert result.is_success()

    # Check function was defined
    greet_func = context.get_function("greet")
    assert greet_func is not None
    assert greet_func["name"] == "greet"
    assert greet_func["params"] == ["name"]

    print("✓ Function execution test passed")


def test_memory_operations():
    """Test memory operation execution"""
    runtime = RuntimeServices()
    context = runtime.create_execution_context(ExecutionMode.INTERACTIVE)

    code = """
    remember("Important data") as "test_memory"
    recall "test_memory"
    memory.search("important")
    """

    result = runtime.execute_code(code, context)

    assert result.is_success()
    assert context.metrics.memory_operations == 3
    assert "Memory operation" in result.get_output_text()

    print("✓ Memory operations test passed")


def test_agent_operations():
    """Test agent operation execution"""
    runtime = RuntimeServices()
    context = runtime.create_execution_context(ExecutionMode.AGENT)

    code = """
    agent.mode = "active"
    agent.start()
    agent.add_goal("Complete testing")
    agent.status()
    agent.stop()
    """

    result = runtime.execute_code(code, context)

    assert result.is_success()
    assert context.metrics.agent_operations >= 4
    assert "Agent operation" in result.get_output_text()

    print("✓ Agent operations test passed")


def test_error_handling():
    """Test error handling and reporting"""
    runtime = RuntimeServices()
    context = runtime.create_execution_context(ExecutionMode.DEBUG)

    # Test undefined function call
    code = """
    run undefined_function("test")
    """

    result = runtime.execute_code(code, context)

    assert not result.is_success()
    assert result.status == ExecutionStatus.ERROR
    assert "Undefined function" in result.error
    assert len(context.metrics.errors) > 0

    print("✓ Error handling test passed")


def test_runtime_services():
    """Test runtime services coordination"""
    runtime = RuntimeServices()

    # Test status reporting
    status = runtime.get_runtime_status()
    assert "environment" in status
    assert "services" in status

    # Test context management
    context1 = runtime.create_execution_context(ExecutionMode.INTERACTIVE)
    context2 = runtime.create_execution_context(ExecutionMode.BATCH)

    contexts = runtime.get_context_list()
    assert len(contexts) == 2

    # Test context export
    exported = runtime.export_context(context1.session_id)
    assert exported is not None
    assert exported["session_id"] == context1.session_id
    assert exported["mode"] == ExecutionMode.INTERACTIVE.value

    print("✓ Runtime services test passed")


def test_performance():
    """Test runtime performance with larger programs"""
    runtime = RuntimeServices()
    context = runtime.create_execution_context(ExecutionMode.BATCH)

    # Generate a larger Aetherra program
    lines = []
    lines.append("goal: Performance test priority: high")

    for i in range(20):
        lines.append(f"# Test function {i}")
        lines.append(f"define test_func_{i}(param)")
        lines.append(f'    assistant: "Processing {i}"')
        lines.append(f'    remember("Function {i} executed") as "func_{i}"')
        lines.append("end")
        lines.append(f"run test_func_{i}('test')")
        lines.append("")

    code = "\n".join(lines)

    import time

    start_time = time.time()
    result = runtime.execute_code(code, context)
    execution_time = time.time() - start_time

    assert result.is_success()
    assert result.execution_time < 5.0  # Should complete within 5 seconds
    assert context.metrics.nodes_executed > 100

    print("Performance Results:")
    print(f"  Execution time: {execution_time:.3f}s")
    print(f"  Nodes executed: {context.metrics.nodes_executed}")
    print(f"  Functions defined: {len(context.functions)}")
    print(f"  Memory operations: {context.metrics.memory_operations}")

    print("✓ Performance test passed")


def test_file_execution():
    """Test file execution functionality"""
    runtime = RuntimeServices()

    # Create a test Aetherra file
    test_code = """
# Test file execution
goal: File execution test

define file_test()
    assistant: "Executing from file"
    remember("File executed successfully")
end

run file_test()
"""

    test_file = "test_runtime_file.aether"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_code)

    try:
        result = runtime.execute_file(test_file)
        assert result.is_success()
        assert "Executing from file" in result.get_output_text()
        print("✓ File execution test passed")
    finally:
        # Clean up test file
        import os

        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    print("Running Aetherra Runtime System Tests")
    print("=" * 50)

    try:
        test_runtime_environment()
        test_execution_context()
        test_code_execution()
        test_function_execution()
        test_memory_operations()
        test_agent_operations()
        test_error_handling()
        test_runtime_services()
        test_performance()
        test_file_execution()

        print("\n" + "=" * 50)
        print("🎉 All runtime tests passed! Runtime system is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
