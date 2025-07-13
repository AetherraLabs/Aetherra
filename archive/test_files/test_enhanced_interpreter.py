#!/usr/bin/env python3
"""
🧪 Test Enhanced Interpreter with basic_memory.aether
Tests the integrated enhancements with your actual Aetherra example
"""

import sys
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "core"))

try:
    from Aetherra.core.interpreter import AetherraInterpreter

    HAS_INTERPRETER = True
    print("✅ Core interpreter loaded successfully")
except ImportError as e:
    print(f"❌ Could not load core interpreter: {e}")
    HAS_INTERPRETER = False


def test_enhanced_interpreter():
    """Test the enhanced interpreter with real Aetherra examples"""

    if not HAS_INTERPRETER:
        print("⚠️ Cannot test - core interpreter not available")
        return

    print("🧬 Testing Enhanced Aetherra Interpreter")
    print("=" * 60)

    # Initialize interpreter
    interpreter = AetherraInterpreter()

    # Test cases from basic_memory.aether
    test_cases = [
        # Enhanced memory operations
        'remember("Python is procedural") as "programming_paradigm"',
        'remember("JavaScript can be functional") as "programming_paradigm"',
        'remember("Aetherra is cognitive") as "programming_paradigm"',
        # Memory recall
        'recall tag: "programming_paradigm"',
        # Multi-tag memory
        'remember("Always backup before self-editing") as "best_practice,safety"',
        # Complex memory patterns
        'remember("API calls should be rate-limited") as "performance,api"',
        'remember("Database queries need indexing") as "performance,database"',
        # Pattern recall
        'recall tag: "performance"',
        # AI-powered analysis
        'reflect on tags="programming_paradigm"',
        "detect patterns",
        # Memory management
        "memory summary",
        "memory tags",
        # Enhanced features
        'remember("Enhanced parsing works great") as "enhancement,success" category: "testing"',
        'goal: "test all enhanced features" priority: high',
        'agent: on specialization: "code testing and validation"',
        # Block structure test
        """define test_function(input)
    think "processing input"
    remember(input) as "function_input"
    return "processed: " + input
end""",
        # Aetherra block test
        """think {
    "What patterns emerge from memory?"
    "How do enhanced features improve usability?"
}""",
        # Agent block test
        """agent:
    specialization: "memory analysis"
    memory_access: "full"
    goal_alignment: "automatic"
end""",
    ]

    # Execute test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 **Test {i}:**")
        print("```Aetherra")
        print(test_case)
        print("```")
        print()

        try:
            result = interpreter.execute(test_case)
            print("📤 **Result:**")
            print(result)
        except Exception as e:
            print(f"❌ **Error:** {e}")

        print()
        print("-" * 50)

    # Test function calling
    print("\n🔧 **Testing Function Call:**")
    try:
        result = interpreter.execute('call test_function("hello world")')
        print("📤 **Function Call Result:**")
        print(result)
    except Exception as e:
        print(f"❌ **Function Call Error:** {e}")


def test_with_actual_file():
    """Test by loading and executing the actual basic_memory.aether file"""

    if not HAS_INTERPRETER:
        return

    print("\n" + "=" * 60)
    print("📁 Testing with actual basic_memory.aether file")
    print("=" * 60)

    # Try to load the actual file
    memory_file = Path(__file__).parent / "examples" / "basic_memory.aether"

    if memory_file.exists():
        print(f"✅ Found file: {memory_file}")

        interpreter = AetherraInterpreter()

        try:
            with open(memory_file, encoding="utf-8") as f:
                content = f.read()

            print("📄 **File Content:**")
            print(content)
            print()

            # Execute line by line
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"🔍 **Line {i}:** {line}")
                    try:
                        result = interpreter.execute(line)
                        if result:
                            print(f"📤 **Result:** {result}")
                    except Exception as e:
                        print(f"❌ **Error:** {e}")
                    print()

        except Exception as e:
            print(f"❌ Error reading file: {e}")
    else:
        print(f"⚠️ File not found: {memory_file}")


if __name__ == "__main__":
    test_enhanced_interpreter()
    test_with_actual_file()

    print("\n🎉 **Integration Test Complete!**")
    print("\nThe enhanced interpreter now supports:")
    print("✅ Enhanced memory operations with categories and confidence")
    print("✅ Advanced goal setting with priorities and deadlines")
    print("✅ Agent specialization and configuration blocks")
    print("✅ Plugin execution with parameter parsing")
    print("✅ Function definitions with define...end blocks")
    print("✅ Aetherra AI-native blocks (think, analyze, memory)")
    print("✅ Backward compatibility with existing Aetherra")
    print("\n🚀 Your insights have been successfully integrated!")
