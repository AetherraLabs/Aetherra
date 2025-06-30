#!/usr/bin/env python3
"""
Quick test to verify the multi-LLM grammar fix
"""

from core.neurocode_grammar import create_neurocode_parser


def test_grammar_fix():
    """Test that multi-LLM syntax now parses correctly"""
    print("🧬 Testing NeuroCode Multi-LLM Grammar Fix")
    print("=" * 50)

    try:
        # Create parser
        parser = create_neurocode_parser()
        print("✅ Parser created successfully!")

        # Test multi-LLM code
        test_code = """# Multi-LLM test
model: "mistral"
assistant: "analyze this code for issues"

model: "gpt-4"
assistant: "provide optimization suggestions"

goal: "test multi-LLM parsing" priority: high
remember("grammar fix works") as "test_result"
"""

        print("\n📝 Testing NeuroCode:")
        print(test_code)
        print("-" * 50)

        # Validate syntax
        result = parser.validate_syntax(test_code)

        if result["valid"]:
            print("✅ Grammar fix successful!")
            print("✅ Multi-LLM syntax parsing works correctly!")

            # Check AST
            ast = result["ast"]
            model_statements = 0
            assistant_statements = 0

            for child in ast.children:
                if child and hasattr(child, "type"):
                    if child.type == "model":
                        model_statements += 1
                    elif child.type == "assistant":
                        assistant_statements += 1

            print(f"✅ Found {model_statements} model statements")
            print(f"✅ Found {assistant_statements} assistant statements")
            print("\n🎉 Multi-LLM NeuroCode is ready!")
            return True

        else:
            print("❌ Grammar errors still present:")
            for error in result["errors"]:
                print(f"   {error}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_grammar_fix()

    if success:
        print("\n🚀 SUCCESS: NeuroCode playground should now work!")
        print("   Run: python launch_playground.py")
    else:
        print("\n❌ FAILED: Grammar issues remain")
