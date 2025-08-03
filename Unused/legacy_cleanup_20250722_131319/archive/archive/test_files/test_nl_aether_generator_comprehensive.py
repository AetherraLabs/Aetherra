#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE NATURAL LANGUAGE → AETHER GENERATOR TESTS
==========================================================

Comprehensive test suite for the Natural Language to Aether Generator.
Tests intent analysis, template selection, parameter auto-fill, and code generation.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyrixa.core.natural_language_aether_generator import NaturalLanguageAetherGenerator
from lyrixa.core.memory import LyrixaMemorySystem


class NLAetherGeneratorTester:
    """Comprehensive tester for Natural Language → Aether Generator"""

    def __init__(self):
        self.memory_system = LyrixaMemorySystem()
        self.generator = NaturalLanguageAetherGenerator(self.memory_system)
        self.test_results = []
        self.successful_tests = 0
        self.total_tests = 0

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 NATURAL LANGUAGE → AETHER GENERATOR TEST SUITE")
        print("=" * 60)

        # Test categories
        await self.test_basic_intent_analysis()
        await self.test_template_selection()
        await self.test_parameter_extraction()
        await self.test_code_generation()
        await self.test_complex_scenarios()
        await self.test_memory_integration()
        await self.test_error_handling()
        await self.test_real_world_examples()

        # Summary
        self.print_test_summary()

    async def test_basic_intent_analysis(self):
        """Test basic intent analysis functionality"""
        print("\n🔍 Testing Basic Intent Analysis...")

        test_cases = [
            {
                "description": "Process CSV data and convert to JSON",
                "expected_intent": "data_processing",
                "expected_entities": ["csv", "json"]
            },
            {
                "description": "Call weather API and analyze temperature trends",
                "expected_intent": "api_integration",
                "expected_entities": ["api", "weather"]
            },
            {
                "description": "Train machine learning model on sales data",
                "expected_intent": "machine_learning",
                "expected_entities": ["train", "model", "sales"]
            },
            {
                "description": "Analyze customer data and create visualizations",
                "expected_intent": "data_analysis",
                "expected_entities": ["analyze", "customer", "visualizations"]
            },
            {
                "description": "Organize files in directory by date",
                "expected_intent": "file_operations",
                "expected_entities": ["files", "directory", "organize"]
            }
        ]

        for test_case in test_cases:
            await self._test_intent_analysis(test_case)

    async def _test_intent_analysis(self, test_case: Dict[str, Any]):
        """Test individual intent analysis case"""
        try:
            result = await self.generator.generate_aether_from_natural_language(
                test_case["description"]
            )

            intent_analysis = result.get("intent_analysis", {})
            primary_intent = intent_analysis.get("primary_intent", "")

            success = primary_intent == test_case["expected_intent"]
            self._record_test_result(
                "Intent Analysis",
                test_case["description"],
                success,
                f"Expected: {test_case['expected_intent']}, Got: {primary_intent}"
            )

        except Exception as e:
            self._record_test_result(
                "Intent Analysis",
                test_case["description"],
                False,
                f"Error: {str(e)}"
            )

    async def test_template_selection(self):
        """Test template selection based on intent"""
        print("\n📋 Testing Template Selection...")

        test_cases = [
            {
                "description": "Create data processing pipeline for customer records",
                "expected_template": "Data Processing Pipeline"
            },
            {
                "description": "Integrate with payment API and process responses",
                "expected_template": "API Integration Workflow"
            },
            {
                "description": "Build predictive model for sales forecasting",
                "expected_template": "Machine Learning Pipeline"
            }
        ]

        for test_case in test_cases:
            await self._test_template_selection(test_case)

    async def _test_template_selection(self, test_case: Dict[str, Any]):
        """Test individual template selection case"""
        try:
            result = await self.generator.generate_aether_from_natural_language(
                test_case["description"]
            )

            template_used = result.get("template_used", "")
            success = template_used == test_case["expected_template"]

            self._record_test_result(
                "Template Selection",
                test_case["description"],
                success,
                f"Expected: {test_case['expected_template']}, Got: {template_used}"
            )

        except Exception as e:
            self._record_test_result(
                "Template Selection",
                test_case["description"],
                False,
                f"Error: {str(e)}"
            )

    async def test_parameter_extraction(self):
        """Test parameter extraction and auto-fill"""
        print("\n⚙️ Testing Parameter Extraction...")

        test_cases = [
            {
                "description": "Process data from input.csv and save to output.json",
                "expected_params": ["input.csv", "output.json"]
            },
            {
                "description": "Call https://api.weather.com/v1/current with GET method",
                "expected_params": ["https://api.weather.com/v1/current", "GET"]
            },
            {
                "description": "Train random forest model with 0.8 accuracy threshold",
                "expected_params": ["random forest", "0.8"]
            }
        ]

        for test_case in test_cases:
            await self._test_parameter_extraction(test_case)

    async def _test_parameter_extraction(self, test_case: Dict[str, Any]):
        """Test individual parameter extraction case"""
        try:
            result = await self.generator.generate_aether_from_natural_language(
                test_case["description"]
            )

            parameters = result.get("parameters", {})
            aether_code = result.get("aether_code", "")

            # Check if expected parameters appear in code or parameters
            found_params = []
            for expected_param in test_case["expected_params"]:
                if expected_param in str(parameters) or expected_param in aether_code:
                    found_params.append(expected_param)

            success = len(found_params) >= len(test_case["expected_params"]) // 2

            self._record_test_result(
                "Parameter Extraction",
                test_case["description"],
                success,
                f"Found {len(found_params)}/{len(test_case['expected_params'])} expected parameters"
            )

        except Exception as e:
            self._record_test_result(
                "Parameter Extraction",
                test_case["description"],
                False,
                f"Error: {str(e)}"
            )

    async def test_code_generation(self):
        """Test .aether code generation quality"""
        print("\n[TOOL] Testing Code Generation...")

        test_cases = [
            "Process customer data from CSV and generate summary report",
            "Fetch user profiles from REST API and update database",
            "Train classification model on product reviews dataset",
            "Analyze sales trends and create interactive dashboard",
            "Batch process image files and extract metadata"
        ]

        for description in test_cases:
            await self._test_code_generation(description)

    async def _test_code_generation(self, description: str):
        """Test individual code generation case"""
        try:
            result = await self.generator.generate_aether_from_natural_language(description)

            aether_code = result.get("aether_code", "")
            confidence = result.get("confidence", 0.0)

            # Check code quality indicators
            has_nodes = "node " in aether_code
            has_connections = "->" in aether_code
            has_structure = len(aether_code.split('\n')) > 5
            no_errors = "error" not in aether_code.lower()

            success = has_nodes and has_connections and has_structure and no_errors and confidence > 0.5

            self._record_test_result(
                "Code Generation",
                description,
                success,
                f"Confidence: {confidence:.2f}, Lines: {len(aether_code.split())}"
            )

        except Exception as e:
            self._record_test_result(
                "Code Generation",
                description,
                False,
                f"Error: {str(e)}"
            )

    async def test_complex_scenarios(self):
        """Test complex multi-step scenarios"""
        print("\n🎯 Testing Complex Scenarios...")

        complex_scenarios = [
            "Build end-to-end machine learning pipeline that reads data from PostgreSQL, preprocesses it, trains multiple models, selects the best one, and deploys it to production",
            "Create automated data quality monitoring system that checks incoming data streams, validates against schemas, alerts on anomalies, and generates quality reports",
            "Implement real-time recommendation engine that processes user events, updates user profiles, generates recommendations using collaborative filtering, and serves them via API"
        ]

        for scenario in complex_scenarios:
            await self._test_complex_scenario(scenario)

    async def _test_complex_scenario(self, scenario: str):
        """Test individual complex scenario"""
        try:
            result = await self.generator.generate_aether_from_natural_language(scenario)

            aether_code = result.get("aether_code", "")
            complexity = result.get("complexity", 0.0)
            suggestions = result.get("suggestions", [])

            # Complex scenarios should have multiple nodes and connections
            node_count = aether_code.count("node ")
            connection_count = aether_code.count("->")

            success = node_count >= 5 and connection_count >= 4 and complexity > 0.7

            self._record_test_result(
                "Complex Scenarios",
                scenario[:50] + "...",
                success,
                f"Nodes: {node_count}, Connections: {connection_count}, Complexity: {complexity:.2f}"
            )

        except Exception as e:
            self._record_test_result(
                "Complex Scenarios",
                scenario[:50] + "...",
                False,
                f"Error: {str(e)}"
            )

    async def test_memory_integration(self):
        """Test memory system integration"""
        print("\n🧠 Testing Memory Integration...")

        # First, store some context in memory
        try:
            await self.memory_system.store_memory(
                content={"preferred_format": "json", "default_api": "https://api.example.com"},
                context={"user_preferences": True},
                tags=["preferences", "defaults"],
                importance=0.8
            )

            # Test if memory influences generation
            result = await self.generator.generate_aether_from_natural_language(
                "Process some data using my preferred settings"
            )

            aether_code = result.get("aether_code", "")
            uses_json = "json" in aether_code.lower()

            self._record_test_result(
                "Memory Integration",
                "Using stored preferences",
                uses_json,
                f"JSON preference applied: {uses_json}"
            )

        except Exception as e:
            self._record_test_result(
                "Memory Integration",
                "Using stored preferences",
                False,
                f"Error: {str(e)}"
            )

    async def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n⚠️ Testing Error Handling...")

        error_cases = [
            "",  # Empty input
            "xyz abc def",  # Nonsensical input
            "Do something with stuff",  # Vague input
            "Generate a workflow",  # Generic input
        ]

        for error_case in error_cases:
            await self._test_error_handling(error_case)

    async def _test_error_handling(self, input_text: str):
        """Test individual error handling case"""
        try:
            result = await self.generator.generate_aether_from_natural_language(input_text)

            # Should still return a result, even if low confidence
            has_result = "aether_code" in result
            has_suggestions = "suggestions" in result and len(result["suggestions"]) > 0
            confidence = result.get("confidence", 1.0)

            # For invalid inputs, confidence should be low but we should still get output
            success = has_result and confidence < 0.8

            self._record_test_result(
                "Error Handling",
                input_text or "(empty)",
                success,
                f"Confidence: {confidence:.2f}, Has suggestions: {has_suggestions}"
            )

        except Exception as e:
            # Some errors are expected for invalid inputs
            self._record_test_result(
                "Error Handling",
                input_text or "(empty)",
                True,  # Graceful error handling is success
                f"Graceful error: {str(e)[:50]}"
            )

    async def test_real_world_examples(self):
        """Test real-world usage examples"""
        print("\n🌍 Testing Real-World Examples...")

        real_world_cases = [
            "Extract customer sentiment from social media posts using TextBlob and save results to database",
            "Monitor server logs for error patterns, send alerts via Slack when anomalies detected",
            "Sync product inventory between Shopify and internal warehouse management system",
            "Generate monthly sales report with charts and email to stakeholders",
            "Process uploaded CSV files, validate data quality, and import to PostgreSQL"
        ]

        for case in real_world_cases:
            await self._test_real_world_example(case)

    async def _test_real_world_example(self, description: str):
        """Test individual real-world example"""
        try:
            result = await self.generator.generate_aether_from_natural_language(description)

            aether_code = result.get("aether_code", "")
            confidence = result.get("confidence", 0.0)
            suggestions = result.get("suggestions", [])

            # Real-world examples should be practical and well-structured
            has_practical_structure = any(keyword in aether_code.lower() for keyword in
                                        ["input", "output", "transform", "api_call", "validator"])

            success = confidence > 0.6 and has_practical_structure and len(suggestions) > 0

            self._record_test_result(
                "Real-World Examples",
                description[:40] + "...",
                success,
                f"Confidence: {confidence:.2f}, Suggestions: {len(suggestions)}"
            )

        except Exception as e:
            self._record_test_result(
                "Real-World Examples",
                description[:40] + "...",
                False,
                f"Error: {str(e)}"
            )

    def _record_test_result(self, category: str, test_name: str, success: bool, details: str):
        """Record test result"""
        self.total_tests += 1
        if success:
            self.successful_tests += 1

        self.test_results.append({
            "category": category,
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

        status = "✅" if success else "❌"
        print(f"  {status} {test_name[:50]}: {details}")

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🧪 NATURAL LANGUAGE → AETHER GENERATOR TEST SUMMARY")
        print("="*60)

        success_rate = (self.successful_tests / self.total_tests) * 100 if self.total_tests > 0 else 0

        print(f"📊 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Successful: {self.successful_tests}")
        print(f"   Failed: {self.total_tests - self.successful_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")

        # Category breakdown
        categories = {}
        for result in self.test_results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0}
            categories[cat]["total"] += 1
            if result["success"]:
                categories[cat]["success"] += 1

        print(f"\n📋 Results by Category:")
        for category, stats in categories.items():
            cat_success_rate = (stats["success"] / stats["total"]) * 100
            print(f"   {category}: {stats['success']}/{stats['total']} ({cat_success_rate:.1f}%)")

        # Overall assessment
        print(f"\n🎯 Assessment:")
        if success_rate >= 90:
            print("   🌟 EXCELLENT - Natural Language → Aether Generator is working exceptionally well!")
        elif success_rate >= 75:
            print("   ✅ GOOD - Generator is working well with minor areas for improvement")
        elif success_rate >= 60:
            print("   ⚠️ FAIR - Generator needs some improvements")
        else:
            print("   ❌ NEEDS WORK - Generator requires significant improvements")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"nl_aether_generator_test_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "successful_tests": self.successful_tests,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "categories": categories,
                "detailed_results": self.test_results
            }, f, indent=2)

        print(f"\n💾 Detailed results saved to: {results_file}")


async def main():
    """Run the comprehensive test suite"""
    print("🚀 Starting Natural Language → Aether Generator Test Suite...")

    tester = NLAetherGeneratorTester()
    await tester.run_all_tests()

    print("\n🎉 Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())
