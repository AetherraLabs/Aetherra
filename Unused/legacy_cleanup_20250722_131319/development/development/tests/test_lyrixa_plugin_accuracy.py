#!/usr/bin/env python3
"""
Lyrixa Plugin Editor Accuracy Test
=================================
Test that Lyrixa provides accurate descriptions of the Plugin Editor
and generates real .aether content
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_lyrixa_plugin_accuracy():
    """Test Lyrixa's accurate Plugin Editor descriptions and real content generation"""
    print("🎯 LYRIXA PLUGIN EDITOR ACCURACY TEST")
    print("=" * 60)

    try:
        from Aetherra.intelligence.lyrixa_intelligence_stack import (
            LyrixaIntelligenceStack,
        )
        from Aetherra.llm.multi_llm_manager import MultiLLMManager
        from Aetherra.lyrixa.agents.core_agent import LyrixaAI
        from Aetherra.memory.base_memory import LyrixaMemory
        from Aetherra.prompt.prompt_engine import PromptEngine
        from Aetherra.runtime.aether_runtime import AetherRuntime

        print("✅ All imports successful")

        # Initialize components
        memory = LyrixaMemory()
        prompt_engine = PromptEngine()
        llm_manager = MultiLLMManager()
        workspace_path = str(Path(__file__).parent)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)
        runtime = AetherRuntime()

        # Mock GUI that captures inject_plugin calls
        class AccuracyTestGUI:
            def __init__(self):
                self.injected_calls = []

            def inject_plugin_code(
                self, code: str, filename: str = "generated_plugin.aether"
            ):
                """Capture injection calls for analysis"""
                call_data = {
                    "code": code,
                    "filename": filename,
                    "code_length": len(code),
                    "is_aether": filename.endswith(".aether"),
                    "is_python": filename.endswith(".py"),
                    "has_plugin_structure": "plugin " in code if code else False,
                }
                self.injected_calls.append(call_data)
                print(f"🎯 Captured plugin injection: {filename}")
                return True

            def get_last_injection(self):
                return self.injected_calls[-1] if self.injected_calls else None

        # Create LyrixaAI with test GUI
        test_gui = AccuracyTestGUI()
        lyrixa = LyrixaAI(
            runtime, memory, prompt_engine, llm_manager, intelligence_stack, test_gui
        )

        # Initialize system
        await lyrixa.initialize()
        await intelligence_stack.initialize_plugin_discovery_integration()

        print("✅ System initialized with accuracy test GUI")
        print()

        # Test 1: Plugin Generation Request
        print("🧪 Test 1: Plugin Generation with Real Content")
        print("-" * 50)

        request = "create a plugin for greeting users when they start Aetherra"
        print(f"📝 Request: '{request}'")

        response = await lyrixa.process_input(request)

        print(f"✅ Response generated:")
        print(f"   🎯 Agent: {response.agent_name}")
        print(f"   📊 Confidence: {response.confidence}")

        # Check for accurate Plugin Editor descriptions
        print()
        print("🔍 Checking Response Accuracy")
        print("-" * 30)

        response_text = response.content.lower()

        # Things that should be mentioned (accurate)
        accurate_terms = [
            "plugin editor",
            "code editor",
            ".aether",
            "save",
            "test",
            "native",
        ]

        # Things that should NOT be mentioned (inaccurate)
        inaccurate_terms = [
            "manifest.json",
            "install button",
            "toggle buttons",
            "left panel",
            "right panel",
            "browser",
            "javascript",
            "json config",
        ]

        accurate_score = 0
        inaccurate_score = 0

        print("✅ Accurate terms found:")
        for term in accurate_terms:
            if term in response_text:
                print(f"   ✅ '{term}' - GOOD")
                accurate_score += 1
            else:
                print(f"   ⚠️ '{term}' - missing")

        print("\n❌ Inaccurate terms found:")
        for term in inaccurate_terms:
            if term in response_text:
                print(f"   ❌ '{term}' - BAD (should not mention)")
                inaccurate_score += 1
            else:
                print(f"   ✅ '{term}' - correctly avoided")

        # Check injected content
        print()
        print("🔍 Checking Injected Plugin Content")
        print("-" * 35)

        last_injection = test_gui.get_last_injection()
        if last_injection:
            print("✅ Plugin code was injected:")
            print(f"   📄 Filename: {last_injection['filename']}")
            print(f"   📝 Code length: {last_injection['code_length']} characters")
            print(f"   🏷️  Is .aether file: {last_injection['is_aether']}")
            print(f"   🐍 Is .py file: {last_injection['is_python']}")
            print(
                f"   🔧 Has plugin structure: {last_injection['has_plugin_structure']}"
            )

            print("\n📋 Code preview:")
            code_preview = (
                last_injection["code"][:300] + "..."
                if len(last_injection["code"]) > 300
                else last_injection["code"]
            )
            print(code_preview)

            # Analyze code quality
            content_score = 0
            if last_injection["is_aether"] or last_injection["is_python"]:
                content_score += 2
                print("✅ Correct file extension")

            if last_injection["has_plugin_structure"]:
                content_score += 2
                print("✅ Contains plugin structure")

            if last_injection["code_length"] > 100:
                content_score += 1
                print("✅ Substantial code content")
        else:
            print("❌ No plugin code was injected")
            content_score = 0

        # Calculate final scores
        print()
        print("📊 ACCURACY ANALYSIS")
        print("=" * 30)

        total_possible_accurate = len(accurate_terms)
        total_possible_inaccurate = len(inaccurate_terms)
        accuracy_percentage = (accurate_score / total_possible_accurate) * 100
        avoidance_percentage = (
            (total_possible_inaccurate - inaccurate_score) / total_possible_inaccurate
        ) * 100

        print(
            f"✅ Accurate descriptions: {accurate_score}/{total_possible_accurate} ({accuracy_percentage:.1f}%)"
        )
        print(
            f"✅ Avoided inaccurate terms: {total_possible_inaccurate - inaccurate_score}/{total_possible_inaccurate} ({avoidance_percentage:.1f}%)"
        )
        print(f"✅ Content quality score: {content_score}/5")

        overall_score = (
            accuracy_percentage + avoidance_percentage + (content_score * 20)
        ) / 3

        print(f"\n🎯 Overall Accuracy Score: {overall_score:.1f}%")

        if overall_score >= 80:
            print(
                "🎉 EXCELLENT: Lyrixa provides highly accurate Plugin Editor descriptions!"
            )
        elif overall_score >= 60:
            print("✅ GOOD: Lyrixa mostly accurate, minor improvements needed")
        elif overall_score >= 40:
            print("⚠️ FAIR: Some accuracy issues, needs improvement")
        else:
            print("❌ POOR: Significant accuracy problems, needs major fixes")

        return overall_score >= 60

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_lyrixa_plugin_accuracy())
    print("\n" + "=" * 60)
    print("🎯 PLUGIN EDITOR ACCURACY TEST COMPLETE")
    print("=" * 60)
    sys.exit(0 if success else 1)
