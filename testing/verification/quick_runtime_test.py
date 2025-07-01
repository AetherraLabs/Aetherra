#!/usr/bin/env python3
"""Quick test of the modular runtime system"""

from core.runtime import ExecutionMode, RuntimeServices


def main():
    print("Testing NeuroCode Modular Runtime System...")

    # Create runtime services
    runtime = RuntimeServices()

    # Create execution context
    context = runtime.create_execution_context(ExecutionMode.INTERACTIVE)
    print(f"Created context: {context.session_id}")

    # Test simple execution
    code = """
    goal: Test the new runtime system
    x = "hello world"
    remember("Runtime test completed") as "test_result"
    """

    result = runtime.execute_code(code, context)
    print(f"Execution successful: {result.is_success()}")
    print(f"Nodes executed: {result.nodes_executed}")
    print(f"Execution time: {result.execution_time:.3f}s")

    if result.output:
        print("Output:")
        for line in result.output:
            print(f"  {line}")

    # Check variables
    print(f"Variables in context: {len(context.variables)}")
    for name, value in context.variables.items():
        print(f"  {name} = {value}")

    print("✓ Runtime system test completed successfully!")


if __name__ == "__main__":
    main()
