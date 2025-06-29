#!/usr/bin/env python3
"""
🧬 NeuroCode Multi-LLM Integration Test
======================================

Test the new multi-LLM capabilities of NeuroCode:
- Model switching with `model:` statements
- AI assistance with `assistant:` statements
- Integration with the NeuroCode engine
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_multi_llm_parsing():
    """Test that multi-LLM syntax parses correctly"""
    print("🧬 Testing Multi-LLM NeuroCode Parsing")
    print("=" * 50)

    try:
        from core.neurocode_grammar import create_neurocode_parser

        parser = create_neurocode_parser()

        # Test multi-LLM NeuroCode
        multi_llm_code = """
# Multi-LLM NeuroCode Test
goal: "test multi-LLM integration" priority: high

# Switch models and use assistant
model: mistral
assistant: "analyze this test for completeness"

model: gpt-4
assistant: "provide detailed feedback on the test"

# Remember insights
remember("Multi-LLM parsing works correctly") as "test_results"

# Set agent
agent: "test_coordinator"
"""

        print("Testing NeuroCode:")
        print(multi_llm_code)
        print("-" * 50)

        result = parser.validate_syntax(multi_llm_code)

        if result["valid"]:
            print("✅ Multi-LLM syntax parsing: SUCCESS")
            ast = result["ast"]
            print(f"📊 AST contains {len(ast.children)} statements")

            # Count different statement types
            model_statements = 0
            assistant_statements = 0

            for child in ast.children:
                if child and hasattr(child, "type"):
                    if child.type == "model":
                        model_statements += 1
                        print(f"   📝 Model statement: {child.value}")
                    elif child.type == "assistant":
                        assistant_statements += 1
                        print(f"   🤖 Assistant statement: {child.value}")

            print(f"✅ Found {model_statements} model statements")
            print(f"✅ Found {assistant_statements} assistant statements")
            return True
        else:
            print("❌ Multi-LLM syntax parsing: FAILED")
            for error in result["errors"]:
                print(f"   Error: {error}")
            return False

    except Exception as e:
        print(f"❌ Parser error: {e}")
        return False


def test_multi_llm_execution():
    """Test multi-LLM execution with mock engine"""
    print("\n🚀 Testing Multi-LLM Execution Engine")
    print("=" * 50)

    try:
        # Import with fallback for missing dependencies
        try:
            from neurocode_engine import NeuroCodeEngine

            has_engine = True
        except ImportError as e:
            print(f"⚠️ NeuroCode engine not available: {e}")
            has_engine = False
            return False

        if not has_engine:
            print("❌ Multi-LLM engine not available")
            return False

        engine = NeuroCodeEngine()

        # Test simple multi-LLM code
        test_code = """
goal: "test execution" priority: medium

model: gpt-3.5-turbo
assistant: "Hello from NeuroCode multi-LLM system"

remember("Execution test completed") as "test_status"
agent: "execution_monitor"
"""

        print("Executing NeuroCode:")
        print(test_code)
        print("-" * 50)

        result = engine.execute_neurocode(test_code)

        if result["status"] == "success":
            print("✅ Multi-LLM execution: SUCCESS")
            print(f"📊 Executed {len(result['results'])} statements")

            for i, stmt_result in enumerate(result["results"], 1):
                status = stmt_result.get("status", "unknown")
                message = stmt_result.get("message", str(stmt_result))
                print(f"   {i}. [{status}] {message}")

            # Check current model
            current_model = engine.get_current_model()
            print(f"✅ Current model: {current_model}")

            # Check available models
            available = engine.list_available_models()
            print(f"✅ Available models: {len(available)}")

            return True
        else:
            print("❌ Multi-LLM execution: FAILED")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False


def test_model_availability():
    """Test what LLM models are available"""
    print("\n🧠 Testing Model Availability")
    print("=" * 50)

    try:
        from core.multi_llm_manager import llm_manager

        available_models = llm_manager.list_available_models()

        print(f"📊 Found {len(available_models)} available models:")

        for model_name, info in available_models.items():
            provider = info.get("provider", "unknown")
            is_local = "🏠 Local" if info.get("is_local") else "☁️ Cloud"
            context_window = info.get("context_window", "unknown")

            print(f"   • {model_name}")
            print(f"     Provider: {provider} ({is_local})")
            print(f"     Context: {context_window} tokens")

        if len(available_models) > 0:
            print("✅ Model availability test: SUCCESS")
            return True
        else:
            print("⚠️ No models available - install dependencies")
            return False

    except Exception as e:
        print(f"❌ Model availability error: {e}")
        return False


def main():
    """Run all multi-LLM tests"""
    print("🧬 NeuroCode Multi-LLM Integration Test Suite")
    print("=" * 60)
    print("Testing NeuroCode's new multi-LLM capabilities...")
    print()

    tests = [
        ("Multi-LLM Parsing", test_multi_llm_parsing),
        ("Model Availability", test_model_availability),
        ("Multi-LLM Execution", test_multi_llm_execution),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
        print()

    print("=" * 60)
    print(f"🧬 Multi-LLM Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! NeuroCode Multi-LLM integration is working!")
        print("\n🚀 Ready for:")
        print("   • Model switching with 'model: mistral', 'model: gpt-4', etc.")
        print("   • AI assistance with 'assistant: your task here'")
        print("   • Privacy-focused local models (Mistral, LLaMA, Mixtral)")
        print("   • Cloud models for advanced reasoning (GPT-4, Claude, Gemini)")
        print("   • Seamless model swapping in NeuroCode programs")
    elif passed > 0:
        print(f"⚠️ {total - passed} tests failed - partial functionality available")
        print("   Install missing dependencies with: python setup_multi_llm.py")
    else:
        print("❌ All tests failed - setup required")
        print("   Run: python setup_multi_llm.py")

    print("\n🧬 NeuroCode: Where AI models unite under one syntax!")


if __name__ == "__main__":
    main()
