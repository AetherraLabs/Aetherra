#!/usr/bin/env python3
"""
🧪 QUICK TEST FOR NATURAL LANGUAGE → AETHER GENERATOR FIXES
===========================================================

Quick test to verify the fixes for the Natural Language → Aether Generator.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyrixa.core.natural_language_aether_generator import NaturalLanguageAetherGenerator
from lyrixa.core.memory import LyrixaMemorySystem


async def test_generator_fixes():
    """Test the Natural Language → Aether Generator fixes"""
    print("🧪 Testing Natural Language → Aether Generator Fixes")
    print("=" * 60)

    # Initialize memory system and generator
    memory_system = LyrixaMemorySystem()
    generator = NaturalLanguageAetherGenerator(memory_system)

    # Test cases that previously caused errors
    test_cases = [
        "Call weather API and process the response data",
        "Process CSV data and convert to JSON format",
        "Train machine learning model on customer data",
        "Analyze sales data and create visualizations",
        "Organize files in directory by date created"
    ]

    print(f"\n[TOOL] Testing {len(test_cases)} cases that previously caused errors...")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case}")
        print("-" * 40)

        try:
            result = await generator.generate_aether_from_natural_language(test_case)

            # Check if we got a valid result
            if "error" in result:
                print(f"❌ Still has error: {result['error']}")
            else:
                aether_code = result.get("aether_code", "")
                confidence = result.get("confidence", 0.0)
                template_used = result.get("template_used", "Unknown")

                print(f"✅ Success!")
                print(f"   Template: {template_used}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Code length: {len(aether_code)} characters")
                print(f"   Nodes: {aether_code.count('node ')}")
                print(f"   Connections: {aether_code.count('->')}")

                # Check for common issues
                if "<" in aether_code and ">" in aether_code:
                    placeholders = len([p for p in aether_code.split() if p.startswith("<") and p.endswith(">")])
                    print(f"   ⚠️ Still has {placeholders} placeholder(s)")
                else:
                    print(f"   ✅ No placeholders - fully generated!")

        except Exception as e:
            print(f"❌ Exception: {str(e)}")

    print("\n" + "=" * 60)
    print("🎯 Fix Verification Complete!")
    print("\nThe fixes should resolve:")
    print("- ✅ Memory system 'semantic_search' attribute error")
    print("- ✅ Missing template parameters (api_url, api_headers, etc.)")
    print("- ✅ KeyError exceptions during template generation")
    print("- ✅ Better error handling and fallback workflows")


async def test_specific_api_case():
    """Test the specific API integration case that was failing"""
    print("\n🔍 Testing Specific API Integration Case...")

    memory_system = LyrixaMemorySystem()
    generator = NaturalLanguageAetherGenerator(memory_system)

    # This specific case was causing the api_headers error
    api_description = "Fetch user data from REST API https://jsonplaceholder.typicode.com/users and save results"

    try:
        result = await generator.generate_aether_from_natural_language(api_description)

        print(f"[TOOL] API Integration Test:")
        print(f"   Input: {api_description}")

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            aether_code = result.get("aether_code", "")
            print(f"✅ Generated successfully!")
            print(f"   Template: {result.get('template_used', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")

            # Show a preview of the generated code
            lines = aether_code.split('\n')[:10]
            print(f"\n📋 Code Preview (first 10 lines):")
            for line in lines:
                print(f"   {line}")
            if len(aether_code.split('\n')) > 10:
                print(f"   ... ({len(aether_code.split('\n')) - 10} more lines)")

    except Exception as e:
        print(f"❌ Still failing: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_generator_fixes())
    asyncio.run(test_specific_api_case())
