#!/usr/bin/env python3
"""
Enhanced Plugin Editor Demo
============================
🧠 "Incredible: drag-and-edit, execute, format, and AI-enhance"
🎯 "Feels like a dev console inside the AI"

This demo showcases all the advanced features of the enhanced plugin editor:
- AI feedback from plugin output
- Inline .aetherplugin validator
- Sandbox testing with dummy memory and simulated goals
- Real-time validation and suggestions
- Drag-and-drop editing
- AI-powered optimization
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our enhanced components
from Aetherra.lyrixa.gui.enhanced_plugin_editor import EnhancedPluginEditor
from Aetherra.lyrixa.gui.plugin_ai_feedback import PluginOutputAnalyzer, PluginOutput
from Aetherra.lyrixa.gui.aetherplugin_validator import AetherPluginValidator, InlineValidator
from Aetherra.lyrixa.gui.plugin_sandbox_tester import PluginSandboxTester, TestScenario

from datetime import datetime


def demonstrate_ai_feedback():
    """Demonstrate AI feedback system"""
    print("🧠 AI Feedback System Demo")
    print("=" * 50)

    # Create AI feedback analyzer
    analyzer = PluginOutputAnalyzer()

    # Simulate some plugin executions
    plugin_outputs = [
        PluginOutput(
            plugin_name="weather_assistant",
            input_data="New York",
            output_data={"temperature": 22, "condition": "sunny", "humidity": 65},
            execution_time=0.3,
            timestamp=datetime.now(),
            success=True
        ),
        PluginOutput(
            plugin_name="weather_assistant",
            input_data="London",
            output_data=None,
            execution_time=5.2,
            timestamp=datetime.now(),
            success=False,
            error_message="API timeout after 5 seconds"
        ),
        PluginOutput(
            plugin_name="calculator",
            input_data="2 + 2 * 3",
            output_data={"result": 8, "expression": "2 + 2 * 3", "success": True},
            execution_time=0.05,
            timestamp=datetime.now(),
            success=True
        )
    ]

    # Analyze each execution
    for output in plugin_outputs:
        analyzer.record_execution(output)
        insights = analyzer.analyze_plugin_output(output)

        print(f"\n📊 Analysis for {output.plugin_name}:")
        print(f"  Input: {output.input_data}")
        print(f"  Success: {output.success}")
        print(f"  Execution Time: {output.execution_time:.3f}s")

        if insights:
            print("  🧠 AI Insights:")
            for insight in insights:
                severity_icon = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}
                icon = severity_icon.get(insight.severity, "🔍")
                print(f"    {icon} {insight.message}")
                if insight.suggested_action:
                    print(f"      💡 Suggestion: {insight.suggested_action}")
        else:
            print("  ✅ No issues detected")

    # Get comprehensive analysis
    weather_analysis = analyzer.get_plugin_analysis("weather_assistant")
    print(f"\n📈 Weather Assistant Analysis:")
    print(f"  Total Executions: {weather_analysis.total_executions}")
    print(f"  Success Rate: {weather_analysis.success_rate:.1%}")
    print(f"  Average Execution Time: {weather_analysis.avg_execution_time:.3f}s")
    print(f"  Performance Trend: {weather_analysis.performance_trend}")
    print(f"  Reliability Score: {weather_analysis.reliability_score:.2f}")
    print(f"  Efficiency Score: {weather_analysis.efficiency_score:.2f}")

    if weather_analysis.recommendations:
        print("  📝 Recommendations:")
        for rec in weather_analysis.recommendations:
            print(f"    • {rec}")

    # Real-time feedback
    realtime_feedback = analyzer.get_real_time_feedback("weather_assistant")
    print(f"\n⚡ Real-time Status: {realtime_feedback['status']}")
    print(f"  Message: {realtime_feedback['message']}")


def demonstrate_plugin_validator():
    """Demonstrate .aetherplugin validator"""
    print("\n🔍 Plugin Validator Demo")
    print("=" * 50)

    # Create validator
    validator = AetherPluginValidator()

    # Sample plugin metadata
    sample_plugin = {
        "metadata": {
            "name": "enhanced_weather",
            "version": "2.1.0",
            "description": "Advanced weather plugin with AI-powered forecasting and real-time updates",
            "author": "Weather AI Team",
            "license": "MIT",
            "min_aetherra_version": "1.0.0",
            "platform": ["all"],
            "documentation_url": "https://docs.example.com/weather-plugin",
            "repository_url": "https://github.com/example/weather-plugin",
            "tags": ["weather", "ai", "forecasting", "real-time"]
        },
        "inputs": [
            {
                "name": "location",
                "type": "string",
                "description": "Location for weather query (city, coordinates, or address)",
                "required": True,
                "validation": {
                    "minLength": 2,
                    "maxLength": 100,
                    "pattern": "^[a-zA-Z0-9\\s,.-]+$"
                }
            },
            {
                "name": "forecast_days",
                "type": "number",
                "description": "Number of forecast days (1-7)",
                "required": False,
                "default": 3,
                "validation": {
                    "minimum": 1,
                    "maximum": 7
                }
            },
            {
                "name": "units",
                "type": "string",
                "description": "Temperature units (celsius, fahrenheit, kelvin)",
                "required": False,
                "default": "celsius",
                "validation": {
                    "enum": ["celsius", "fahrenheit", "kelvin"]
                }
            }
        ],
        "outputs": [
            {
                "name": "current_weather",
                "type": "object",
                "description": "Current weather conditions"
            },
            {
                "name": "forecast",
                "type": "array",
                "description": "Weather forecast for requested days"
            },
            {
                "name": "alerts",
                "type": "array",
                "description": "Weather alerts and warnings"
            },
            {
                "name": "success",
                "type": "boolean",
                "description": "Operation success status"
            },
            {
                "name": "error",
                "type": "string",
                "description": "Error message if operation failed"
            }
        ],
        "capabilities": [
            "network_access",
            "memory_read",
            "memory_write",
            "ai_inference"
        ],
        "permissions": [
            "weather_api_access",
            "location_services"
        ],
        "dependencies": [
            "requests >= 2.28.0",
            "json",
            "datetime"
        ],
        "configuration": {
            "timeout": 30,
            "retries": 3,
            "cache_enabled": True,
            "cache_duration": 300,
            "logging_level": "info"
        },
        "tests": [
            {
                "name": "basic_weather_query",
                "input": {
                    "location": "New York",
                    "forecast_days": 3,
                    "units": "celsius"
                },
                "expected_output": {
                    "success": True,
                    "current_weather": {"temperature": 22, "condition": "sunny"},
                    "forecast": [{"day": 1, "temperature": 24, "condition": "partly_cloudy"}]
                },
                "description": "Test basic weather query functionality"
            },
            {
                "name": "invalid_location",
                "input": {
                    "location": "",
                    "forecast_days": 3
                },
                "expected_output": {
                    "success": False,
                    "error": "Invalid location provided"
                },
                "description": "Test error handling for invalid location"
            }
        ]
    }

    # Validate the plugin
    result = validator.validate_plugin_content(json.dumps(sample_plugin, indent=2))

    print(f"✅ Validation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Quality Score: {result.score:.2f}/1.0")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")
    print(f"  Info: {len(result.info)}")

    if result.errors:
        print("  ❌ Errors:")
        for error in result.errors:
            print(f"    • {error}")

    if result.warnings:
        print("  ⚠️ Warnings:")
        for warning in result.warnings:
            print(f"    • {warning}")

    if result.info:
        print("  ℹ️ Info:")
        for info in result.info:
            print(f"    • {info}")

    # Test input/output compatibility
    io_warnings = validator.validate_io_compatibility(
        sample_plugin["inputs"],
        sample_plugin["outputs"]
    )

    if io_warnings:
        print("  🔄 I/O Compatibility:")
        for warning in io_warnings:
            print(f"    • {warning}")

    # Generate suggestions
    suggestions = validator.suggest_improvements(sample_plugin)
    if suggestions:
        print("  💡 Suggestions:")
        for suggestion in suggestions:
            print(f"    • {suggestion}")

    # Inline validator demo
    print("\n🔍 Inline Validator Demo:")
    inline_validator = InlineValidator()

    # Simulate real-time validation
    partial_content = '{"metadata": {"name": "test_plugin", "version": "1.0.0"'
    realtime_result = inline_validator.validate_real_time(partial_content, len(partial_content))

    print(f"  Real-time validation: {realtime_result['is_valid']}")
    print(f"  Current section: {realtime_result['cursor_context']['section']}")
    print(f"  Suggestions: {realtime_result['cursor_context']['suggestions']}")


def demonstrate_sandbox_testing():
    """Demonstrate sandbox testing system"""
    print("\n🧪 Sandbox Testing Demo")
    print("=" * 50)

    # Create sandbox tester
    tester = PluginSandboxTester()

    # Sample plugin code for testing
    sample_plugin = '''
plugin advanced_calculator {
    description: "Advanced calculator with memory and goal integration"
    version: "1.0.0"

    fn execute(input) {
        try {
            // Input validation
            if (!input || !input.expression) {
                throw "Expression is required"
            }

            // Log the operation
            lyrixa.log("Calculating: " + input.expression)

            // Remember the calculation
            lyrixa.remember("Calculated: " + input.expression)

            // Simple calculation simulation
            let result = eval_expression(input.expression)

            // Update goals if needed
            if (input.update_goals) {
                goals.add_goal({
                    id: "calc_" + Date.now(),
                    description: "Calculate " + input.expression,
                    status: "completed"
                })
            }

            return {
                expression: input.expression,
                result: result,
                success: true,
                timestamp: new Date().toISOString(),
                memory_used: memory.get("working_memory")
            }

        } catch (error) {
            lyrixa.log("Error: " + error)
            return {
                expression: input.expression,
                error: error,
                success: false,
                timestamp: new Date().toISOString()
            }
        }
    }

    fn eval_expression(expr) {
        // Simple expression evaluator
        if (expr == "2 + 2") return 4
        if (expr == "5 * 3") return 15
        if (expr == "10 / 2") return 5
        return 42 // Default answer
    }
}
'''

    # Run comprehensive test suite
    print("🚀 Running comprehensive test suite...")
    report = tester.run_comprehensive_test_suite(sample_plugin, "advanced_calculator")

    print(f"\n📊 Test Report for {report['plugin_name']}:")
    print(f"  Total Tests: {report['test_summary']['total_tests']}")
    print(f"  Passed: {report['test_summary']['passed']}")
    print(f"  Failed: {report['test_summary']['failed']}")
    print(f"  Success Rate: {report['test_summary']['success_rate']:.1%}")
    print(f"  Avg Execution Time: {report['test_summary']['avg_execution_time']:.3f}s")
    print(f"  Max Memory Usage: {report['test_summary']['max_memory_usage']} bytes")

    print("\n📋 Individual Test Results:")
    for result in report['test_results']:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['scenario']}: {result['execution_time']:.3f}s")
        if result['error']:
            print(f"    Error: {result['error']}")

    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

    # Custom test scenario
    print("\n🎯 Custom Test Scenario:")
    env = tester.create_sandbox("custom_test")

    custom_scenario = TestScenario(
        name="complex_calculation",
        description="Test complex calculation with goal updates",
        input_data={
            "expression": "2 + 2",
            "update_goals": True
        },
        expected_output={
            "result": 4,
            "success": True
        },
        timeout=15
    )

    custom_result = tester.run_test_scenario(env, custom_scenario, sample_plugin)

    print(f"  Scenario: {custom_result.scenario_name}")
    print(f"  Success: {custom_result.success}")
    print(f"  Execution Time: {custom_result.execution_time:.3f}s")
    if custom_result.output:
        print(f"  Output: {custom_result.output}")
    if custom_result.error_message:
        print(f"  Error: {custom_result.error_message}")

    tester.cleanup_sandbox(env)


def demonstrate_integration():
    """Demonstrate integrated workflow"""
    print("\n🔗 Integrated Workflow Demo")
    print("=" * 50)

    # Step 1: Create plugin with AI assistance
    print("1. 🤖 AI-Assisted Plugin Creation")

    plugin_template = {
        "metadata": {
            "name": "smart_assistant",
            "version": "1.0.0",
            "description": "AI-powered smart assistant with context awareness",
            "author": "AI Team",
            "license": "MIT",
            "min_aetherra_version": "1.0.0",
            "platform": ["all"],
            "tags": ["ai", "assistant", "smart"]
        },
        "inputs": [
            {
                "name": "query",
                "type": "string",
                "description": "User query or request",
                "required": True
            },
            {
                "name": "context",
                "type": "object",
                "description": "Context information",
                "required": False
            }
        ],
        "outputs": [
            {
                "name": "response",
                "type": "string",
                "description": "AI-generated response"
            },
            {
                "name": "confidence",
                "type": "number",
                "description": "Response confidence score"
            },
            {
                "name": "success",
                "type": "boolean",
                "description": "Operation success"
            }
        ],
        "capabilities": ["ai_inference", "memory_read", "memory_write"]
    }

    # Step 2: Validate plugin
    print("\n2. ✅ Plugin Validation")
    validator = AetherPluginValidator()
    validation_result = validator.validate_plugin_content(json.dumps(plugin_template, indent=2))

    print(f"  Validation: {'✅ Valid' if validation_result.is_valid else '❌ Invalid'}")
    print(f"  Score: {validation_result.score:.2f}")

    # Step 3: Generate plugin code
    print("\n3. 📝 Plugin Code Generation")

    generated_code = '''
plugin smart_assistant {
    description: "AI-powered smart assistant with context awareness"
    version: "1.0.0"

    fn execute(input) {
        try {
            // Validate input
            if (!input.query) {
                throw "Query is required"
            }

            // Process with AI
            let response = process_ai_query(input.query, input.context)

            // Store interaction
            lyrixa.remember("User asked: " + input.query)
            lyrixa.remember("AI responded: " + response.text)

            return {
                response: response.text,
                confidence: response.confidence,
                success: true,
                timestamp: new Date().toISOString()
            }

        } catch (error) {
            return {
                error: error,
                success: false,
                timestamp: new Date().toISOString()
            }
        }
    }

    fn process_ai_query(query, context) {
        // AI processing simulation
        let responses = [
            "I understand your question about " + query,
            "Based on the context, I can help you with " + query,
            "Let me process your request: " + query
        ]

        return {
            text: responses[Math.floor(Math.random() * responses.length)],
            confidence: 0.8 + Math.random() * 0.2
        }
    }
}
'''

    print("  Generated plugin code with AI assistance ✨")

    # Step 4: Test in sandbox
    print("\n4. 🧪 Sandbox Testing")
    tester = PluginSandboxTester()

    # Quick test
    test_scenarios = [
        TestScenario(
            name="basic_query",
            description="Test basic AI query",
            input_data={"query": "What is the weather like?"},
            timeout=10
        ),
        TestScenario(
            name="context_aware",
            description="Test context-aware response",
            input_data={"query": "Help me", "context": {"task": "coding"}},
            timeout=10
        )
    ]

    env = tester.create_sandbox("smart_assistant_test")
    test_results = []

    for scenario in test_scenarios:
        result = tester.run_test_scenario(env, scenario, generated_code)
        test_results.append(result)
        status = "✅" if result.success else "❌"
        print(f"  {status} {scenario.name}: {result.execution_time:.3f}s")

    tester.cleanup_sandbox(env)

    # Step 5: AI Feedback
    print("\n5. 🧠 AI Feedback Analysis")
    analyzer = PluginOutputAnalyzer()

    # Simulate plugin execution for feedback
    for result in test_results:
        if result.success:
            plugin_output = PluginOutput(
                plugin_name="smart_assistant",
                input_data={"query": "test"},
                output_data=result.output,
                execution_time=result.execution_time,
                timestamp=datetime.now(),
                success=result.success
            )
            analyzer.record_execution(plugin_output)

    # Get analysis
    analysis = analyzer.get_plugin_analysis("smart_assistant")
    print(f"  Success Rate: {analysis.success_rate:.1%}")
    print(f"  Avg Execution Time: {analysis.avg_execution_time:.3f}s")
    print(f"  Quality Score: {analysis.output_quality_score:.2f}")

    # Step 6: Final recommendations
    print("\n6. 💡 Final Recommendations")

    all_recommendations = []
    all_recommendations.extend(validation_result.info)
    all_recommendations.extend(analysis.recommendations)

    if all_recommendations:
        for rec in all_recommendations[:3]:  # Top 3
            print(f"  • {rec}")
    else:
        print("  ✅ Plugin looks great! Ready for production.")

    print("\n🎉 Integration workflow complete!")


def main():
    """Main demonstration function"""
    print("🚀 Enhanced Plugin Editor Demo")
    print("=" * 60)
    print("\"Incredible: drag-and-edit, execute, format, and AI-enhance\"")
    print("\"Feels like a dev console inside the AI\"")
    print("=" * 60)

    try:
        # Run all demonstrations
        demonstrate_ai_feedback()
        demonstrate_plugin_validator()
        demonstrate_sandbox_testing()
        demonstrate_integration()

        print("\n" + "=" * 60)
        print("🎊 Demo Complete!")
        print("=" * 60)
        print("\n✨ Enhanced Plugin Editor Features Demonstrated:")
        print("  🧠 AI Feedback System - Real-time analysis and suggestions")
        print("  🔍 Plugin Validator - Comprehensive .aetherplugin validation")
        print("  🧪 Sandbox Testing - Isolated testing with mock environment")
        print("  🔗 Integrated Workflow - Complete plugin development cycle")
        print("\n🎯 Key Benefits:")
        print("  • Real-time AI feedback on plugin performance")
        print("  • Comprehensive validation with detailed error reporting")
        print("  • Safe sandbox testing with simulated goals and memory")
        print("  • Integrated development experience")
        print("  • Production-ready plugin development")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
