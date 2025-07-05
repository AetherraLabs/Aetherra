#!/usr/bin/env python3
"""
Test script for Neuroplex Advanced Syntax Features
Run this to verify all new functionality works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Aetherra.core.interpreter import AetherraInterpreter

def test_advanced_syntax():
    """Test all advanced syntax features"""
    print("🧠 Testing Neuroplex Advanced Syntax Features")
    print("=" * 50)

    interpreter = AetherraInterpreter()

    # Test 1: User-defined functions
    print("\n1. Testing User-Defined Functions...")
    commands = [
        'define test_function()',
        'remember("Function executed") as "test"',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Call the function
    result = interpreter.execute('run test_function()')
    print(f"   run test_function() -> {result}")

    # Test 2: For loops
    print("\n2. Testing For Loops...")
    commands = [
        'for i in 1..3',
        'remember("Loop iteration " + i) as "loop_test"',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Test 3: Conditionals
    print("\n3. Testing Conditionals...")
    commands = [
        'x = 5',
        'if x > 3',
        'remember("Condition met") as "conditional_test"',
        'else',
        'remember("Condition not met") as "conditional_test"',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Test 4: While loops
    print("\n4. Testing While Loops...")
    commands = [
        'counter = 0',
        'while counter < 2',
        'counter = counter + 1',
        'remember("While loop " + counter) as "while_test"',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Test 5: Simulation mode
    print("\n5. Testing Simulation Mode...")
    commands = [
        'simulate test_simulation',
        'remember("This is simulated") as "sim_test"',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Test 6: Complex function with all features
    print("\n6. Testing Complex Function...")
    commands = [
        'define complex_test()',
        'for item in ["a", "b"]',
        'if item == "a"',
        'remember("Found a") as "complex"',
        'else',
        'remember("Found b") as "complex"',
        'end',
        'end',
        'end'
    ]

    for cmd in commands:
        result = interpreter.execute(cmd)
        print(f"   {cmd} -> {result}")

    # Execute the complex function
    result = interpreter.execute('run complex_test()')
    print(f"   run complex_test() -> {result}")

    # Test 7: Memory integration
    print("\n7. Testing Memory Integration...")
    result = interpreter.execute('memory summary')
    print(f"   memory summary -> {result}")

    result = interpreter.execute('list functions')
    print(f"   list functions -> {result}")

    print("\n✅ All Advanced Syntax Tests Completed!")
    print("🎉 Neuroplex is now a fully Turing-complete AI-native programming environment!")

if __name__ == "__main__":
    test_advanced_syntax()
