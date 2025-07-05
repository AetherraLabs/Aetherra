#!/usr/bin/env python3
"""
Test script for Neuroplex Debug System
Demonstrates automatic error detection, fix suggestion, and self-correction
"""

import os
import sys

sys.path.append(".")

from Aetherra.core.aetherra_memory import AetherraMemory
from Aetherra.core.debug_system import AetherraDebugSystem


def test_debug_system():
    """Test the automatic debug and self-correction system"""
    #     print("🧠 NEUROPLEX DEBUG SYSTEM TEST")
    print("=" * 50)

    # Initialize system
    memory = AetherraMemory()
    debug_system = AetherraDebugSystem(memory)

    # Test 1: Error Detection
    print("\n🔍 TEST 1: Error Detection")
    print("-" * 30)

    try:
        # Simulate a syntax error
        exec("print('Hello World'")  # Missing closing parenthesis
    except SyntaxError as e:
        error_info = debug_system.detect_and_store_error(
            e, "Test script", "test_syntax.py"
        )
        print(f"✅ Error detected and stored: {error_info['type']}")

    # Test 2: Fix Suggestion
    print("\n🤖 TEST 2: AI Fix Suggestion")
    print("-" * 30)

    # Create a test file with syntax error
    test_file = "test_buggy_code.py"
    with open(test_file, "w") as f:
        f.write("""# Buggy Python code
def greet(name:
    print(f"Hello {name}")

if __name__ == "__main__":
    greet("World")
""")

    try:
        with open(test_file, "r") as f:
            code = f.read()
        compile(code, test_file, "exec")
    except SyntaxError as e:
        error_info = debug_system.detect_and_store_error(
            e, "Loading test file", test_file
        )
        fix_suggestion = debug_system.suggest_fix(error_info)

        print(f"🔧 Fix suggested: {fix_suggestion.get('fix', 'No fix available')}")
        print(f"📊 Confidence: {fix_suggestion.get('confidence', 0)}%")
        print(f"⚠️ Risk Level: {fix_suggestion.get('risk', 'unknown')}")

        # Test 3: Auto-apply (if confidence is high)
        print("\n⚡ TEST 3: Auto-Apply Fix")
        print("-" * 30)

        if fix_suggestion.get("confidence", 0) >= 70:
            print("🔄 Attempting to apply fix...")
            success = debug_system.apply_fix(fix_suggestion, force=True)
            if success:
                print("✅ Fix applied successfully!")
                # Verify the fix
                try:
                    with open(test_file, "r") as f:
                        fixed_code = f.read()
                    compile(fixed_code, test_file, "exec")
                    print("✅ Fixed code compiles successfully!")
                except:
                    print("❌ Fixed code still has issues")
            else:
                print("❌ Fix application failed")
        else:
            print(
                f"⚠️ Confidence too low ({fix_suggestion.get('confidence', 0)}%) for auto-apply"
            )

    # Test 4: Debug Settings
    #     print("\n⚙️ TEST 4: Debug System Configuration")
    print("-" * 30)

    debug_system.set_auto_apply(True, 80)
    debug_system.show_debug_status()

    # Test 5: Debug Statistics
    #     print("\n📊 TEST 5: Debug Statistics")
    print("-" * 30)

    stats = debug_system.get_debug_stats()
    print(f"Total errors detected: {stats['total_errors']}")
    print(f"Successful fixes: {stats['successful_fixes']}")
    print(f"Auto-apply enabled: {stats['auto_apply_enabled']}")

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

    #     print("\n🎉 DEBUG SYSTEM TEST COMPLETED!")
    print("=" * 50)


def demo_Aetherra_debug():
    """Demonstrate debug commands in Aetherra syntax"""
    #     print("\n🔮 Aetherra DEBUG COMMANDS DEMO")
    print("=" * 40)

    commands = [
        "debug status",
        "set auto_debug on 80",
        'load "buggy_file.py"',
        'suggest fix for "SyntaxError at line 22"',
        "apply fix",
        "apply fix force",
    ]

    for cmd in commands:
        print(f"🔮 >> {cmd}")
        print(f"   # {get_command_description(cmd)}")
        print()


def get_command_description(cmd):
    """Get description for debug commands"""
    descriptions = {
        "debug status": "Show current debug system status and statistics",
        "set auto_debug on 80": "Enable auto-debug with 80% confidence threshold",
        'load "buggy_file.py"': "Load file and automatically detect syntax errors",
        'suggest fix for "SyntaxError at line 22"': "AI suggests fix for specific error",
        "apply fix": "Apply the last suggested fix (if confidence is high enough)",
        "apply fix force": "Force apply fix even if confidence/risk is high",
    }
    return descriptions.get(cmd, "Execute debug command")


if __name__ == "__main__":
    #     print("🧠 NEUROPLEX AUTOMATIC DEBUG & SELF-CORRECTION SYSTEM")
    print("🔄 Detects errors → Suggests fixes → Applies corrections")
    print()

    test_debug_system()
    demo_Aetherra_debug()

    print("\n💡 TO USE IN NEUROPLEX:")
    print("   1. Run: python main.py")
    #     print("   2. Enable: set auto_debug on 80")
    print('   3. Load files: load "your_file.py"')
    print("   4. Errors are auto-detected and fixed!")
