#!/usr/bin/env python3
"""
🎭 NATURAL LANGUAGE → AETHER GENERATOR DEMO
===========================================

Interactive demo showcasing the Natural Language to Aether Generator.
Demonstrates conversion from plain English to executable .aether workflows.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyrixa.core.natural_language_aether_generator import NaturalLanguageAetherGenerator
from lyrixa.core.memory import LyrixaMemorySystem


class NLAetherDemo:
    """Interactive demo for Natural Language → Aether Generator"""

    def __init__(self):
        self.memory_system = LyrixaMemorySystem()
        self.generator = NaturalLanguageAetherGenerator(self.memory_system)

    async def run_demo(self):
        """Run the interactive demo"""
        print("🎭 NATURAL LANGUAGE → AETHER GENERATOR DEMO")
        print("=" * 50)
        print("🌐 Convert plain English descriptions into .aether workflows!")
        print("✨ Features: Intent analysis, parameter auto-fill, optimization")
        print("-" * 50)

        # Example scenarios
        await self.demo_example_scenarios()

        # Interactive mode
        await self.demo_interactive_mode()

    async def demo_example_scenarios(self):
        """Demonstrate with pre-defined scenarios"""
        print("\n📋 EXAMPLE SCENARIOS")
        print("-" * 30)

        examples = [
            {
                "name": "Data Processing Pipeline",
                "description": "Process customer data from CSV file, clean missing values, and export to JSON format"
            },
            {
                "name": "API Integration",
                "description": "Fetch weather data from OpenWeatherMap API and store results in database"
            },
            {
                "name": "Machine Learning",
                "description": "Train a classification model on product reviews to predict sentiment with 90% accuracy"
            },
            {
                "name": "File Operations",
                "description": "Organize photos in directory by date taken and resize them to 1920x1080"
            },
            {
                "name": "Data Analysis",
                "description": "Analyze sales data to find trends and create interactive dashboard with charts"
            }
        ]

        for i, example in enumerate(examples, 1):
            print(f"\n🎯 Example {i}: {example['name']}")
            print(f"📝 Description: {example['description']}")
            print("⚡ Generating .aether workflow...")

            result = await self.generator.generate_aether_from_natural_language(
                example['description']
            )

            await self.display_generation_result(result, example['description'])

            # Wait for user input to continue
            input("\n⏸️ Press Enter to continue to next example...")

    async def demo_interactive_mode(self):
        """Interactive mode for user input"""
        print("\n🎪 INTERACTIVE MODE")
        print("-" * 20)
        print("🗣️ Now you can try your own descriptions!")
        print("💡 Examples:")
        print("   - 'Extract text from PDF files and summarize with AI'")
        print("   - 'Monitor website uptime and send Slack notifications'")
        print("   - 'Process survey responses and generate insights report'")
        print("   - Type 'quit' to exit")
        print()

        while True:
            try:
                user_input = input("🌐 Describe your workflow: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thanks for trying the Natural Language → Aether Generator!")
                    break

                if not user_input:
                    print("⚠️ Please enter a description of your desired workflow.")
                    continue

                print("⚡ Generating .aether workflow...")

                result = await self.generator.generate_aether_from_natural_language(user_input)
                await self.display_generation_result(result, user_input)

                # Ask if user wants to try another
                print()

            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    async def display_generation_result(self, result: dict, original_description: str):
        """Display the generation result in a formatted way"""
        print("\n" + "="*60)
        print("🎯 GENERATION RESULT")
        print("="*60)

        # Basic info
        confidence = result.get("confidence", 0.0)
        complexity = result.get("complexity", 0.0)
        template_used = result.get("template_used", "Unknown")

        print(f"📊 Confidence: {confidence:.1%}")
        print(f"🔧 Complexity: {complexity:.1%}")
        print(f"📋 Template: {template_used}")

        # Intent analysis
        intent_analysis = result.get("intent_analysis", {})
        if intent_analysis:
            print(f"\n🧠 INTENT ANALYSIS")
            print(f"   Primary Intent: {intent_analysis.get('primary_intent', 'Unknown')}")
            secondary_intents = intent_analysis.get('secondary_intents', [])
            if secondary_intents:
                print(f"   Secondary Intents: {', '.join(secondary_intents)}")

        # Generated .aether code
        aether_code = result.get("aether_code", "")
        if aether_code:
            print(f"\n⚡ GENERATED .AETHER CODE")
            print("-" * 30)
            print(aether_code)

        # Parameters
        parameters = result.get("parameters", {})
        if parameters:
            print(f"\n⚙️ AUTO-FILLED PARAMETERS")
            for key, value in parameters.items():
                print(f"   {key}: {value}")

        # Suggestions
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"\n💡 IMPROVEMENT SUGGESTIONS")
            for i, suggestion in enumerate(suggestions, 1):
                if isinstance(suggestion, dict):
                    print(f"   {i}. {suggestion.get('message', suggestion)}")
                else:
                    print(f"   {i}. {suggestion}")

        # Metadata
        metadata = result.get("metadata", {})
        if metadata:
            print(f"\n📋 METADATA")
            print(f"   Generation Time: {metadata.get('generation_time', 'N/A')}")
            entities = metadata.get("entities_found", {})
            if entities:
                print(f"   Entities Found: {sum(len(v) if isinstance(v, list) else 1 for v in entities.values())}")

        # Error handling
        if "error" in result:
            print(f"\n❌ ERROR")
            print(f"   {result['error']}")

        print("="*60)


async def main():
    """Run the demo"""
    demo = NLAetherDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
