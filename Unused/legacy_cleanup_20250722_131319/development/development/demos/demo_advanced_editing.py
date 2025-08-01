# demo_advanced_editing.py
# 🚀 Live Demo of Advanced Code Editing Capabilities

import sys
import os

# Add paths
current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(current_dir, "Aetherra", "lyrixa", "gui"))

def demo_ast_aware_editing():
    """Demonstrate AST-aware code editing"""
    print("🧠 AST-Aware Code Editing Demo")
    print("=" * 50)

    from Aetherra.lyrixa.gui.advanced_code_editor import ASTAwareCodeEditor

    editor = ASTAwareCodeEditor()

    # Original plugin code
    original_plugin = '''# @plugin: weather_assistant
# @functions: get_weather, format_temperature
# @version: 1.0
# @description: Weather information assistant

class WeatherAssistant:
    """Simple weather assistant"""

    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city):
        """Get weather for a city"""
        # Placeholder implementation
        return {"city": city, "temp": 20, "condition": "sunny"}

    def format_temperature(self, temp, unit="C"):
        """Format temperature with unit"""
        return f"{temp}°{unit}"
'''

    print("📝 Original Plugin Code:")
    print(original_plugin[:200] + "...")

    # Parse metadata
    metadata = editor.parse_plugin_metadata(original_plugin)
    print(f"\n🔍 Parsed Metadata:")
    if metadata:
        print(f"  Plugin: {metadata.name} v{metadata.version}")
        print(f"  Functions: {metadata.functions}")
        print(f"  Classes: {metadata.classes}")
    else:
        print("  No metadata found")

    # Analyze structure
    analysis = editor.analyze_code_structure(original_plugin)
    print(f"\n🧠 AST Analysis:")
    print(f"  Valid syntax: {analysis['valid_syntax']}")
    print(f"  Functions: {len(analysis['functions'])}")
    print(f"  Classes: {len(analysis['classes'])}")
    print(f"  Complexity: {analysis['complexity_score']}")

    # New enhancement code
    enhancement = '''def get_forecast(self, city, days=5):
        """Get weather forecast for multiple days"""
        forecasts = []
        for day in range(days):
            weather = self.get_weather(city)
            weather['day'] = day + 1
            forecasts.append(weather)
        return forecasts

    def get_current_conditions(self, city):
        """Get detailed current weather conditions"""
        base_weather = self.get_weather(city)
        base_weather.update({
            'humidity': 65,
            'wind_speed': 10,
            'pressure': 1013
        })
        return base_weather'''

    print(f"\n✨ Enhancement Code:")
    print(enhancement[:150] + "...")

    # Perform intelligent merge
    print(f"\n🔄 Performing Intelligent Merge...")
    merged_code, success, message = editor.intelligent_code_merge(
        original_plugin, enhancement, "Adding forecast and detailed weather methods"
    )

    print(f"  Result: {'✅ Success' if success else '❌ Failed'}")
    print(f"  Message: {message}")
    print(f"  Original length: {len(original_plugin)} chars")
    print(f"  Merged length: {len(merged_code)} chars")

    # Analyze merged result
    merged_analysis = editor.analyze_code_structure(merged_code)
    print(f"\n📊 Merged Code Analysis:")
    print(f"  Valid syntax: {merged_analysis['valid_syntax']}")
    print(f"  Functions: {len(merged_analysis['functions'])}")
    print(f"  Function names: {[f['name'] for f in merged_analysis['functions']]}")

    # Generate test case
    if merged_analysis['functions']:
        test_func = merged_analysis['functions'][0]  # First function
        test_code = editor.generate_test_case(test_func)
        print(f"\n🧪 Generated Test Case for '{test_func['name']}':")
        print(test_code[:200] + "...")

    # Show learning insights
    insights = editor.get_learning_insights()
    print(f"\n📊 Learning Insights:")
    if 'total_edits' in insights:
        print(f"  Total edits: {insights['total_edits']}")
        print(f"  Success rate: {insights.get('success_rate', 0):.1%}")
    else:
        print(f"  {insights.get('message', 'No insights available')}")

    return merged_code

def demo_metadata_system():
    """Demonstrate metadata parsing and template generation"""
    print("\n📋 Metadata System Demo")
    print("=" * 50)

    from Aetherra.lyrixa.gui.plugin_editor_refactor import (
        parse_plugin_metadata, create_metadata_template
    )

    # Sample plugin with metadata
    plugin_with_metadata = '''# @plugin: file_manager
# @functions: list_files, read_file, write_file, delete_file
# @classes: FileManager, FileWatcher
# @version: 2.1
# @description: Advanced file management with watching capabilities
# @dependencies: watchdog, pathlib

"""
Advanced File Manager Plugin
Provides comprehensive file operations with real-time monitoring
"""

class FileManager:
    def list_files(self, path):
        pass

    def read_file(self, path):
        pass

class FileWatcher:
    def start_watching(self, path):
        pass
'''

    print("🔍 Parsing metadata from plugin:")
    metadata = parse_plugin_metadata(plugin_with_metadata)
    if metadata:
        print(f"  Name: {metadata.name}")
        print(f"  Version: {metadata.version}")
        print(f"  Description: {metadata.description}")
        print(f"  Functions: {metadata.functions}")
        print(f"  Classes: {metadata.classes}")
        print(f"  Dependencies: {metadata.dependencies}")

    # Generate new template
    print(f"\n📝 Generating new template:")
    template = create_metadata_template(
        "ai_assistant",
        functions=["chat", "analyze", "suggest"],
        classes=["AIAssistant", "ChatHandler"],
        version="3.0",
        description="AI-powered assistant with chat capabilities"
    )
    print(template)

def demo_test_generation():
    """Demonstrate test case generation"""
    print("\n🧪 Test Generation Demo")
    print("=" * 50)

    from Aetherra.lyrixa.gui.plugin_editor_refactor import generate_test_case_for_function

    # Sample function info
    function_info = {
        'name': 'calculate_discount',
        'args': ['price', 'discount_percent'],
        'docstring': 'Calculate discounted price based on percentage'
    }

    print(f"📋 Function to test: {function_info['name']}")
    print(f"   Arguments: {function_info['args']}")
    print(f"   Description: {function_info['docstring']}")

    test_code = generate_test_case_for_function(function_info)
    print(f"\n🧪 Generated test:")
    print(test_code)

def main():
    """Run all demos"""
    print("🚀 Advanced Code Editing Capabilities Demo")
    print("=" * 60)
    print("This demo showcases the enhanced code editing features:")
    print("• AST-aware intelligent merging")
    print("• Plugin metadata parsing and templates")
    print("• Automatic test case generation")
    print("• Learning and self-improvement")
    print("=" * 60)

    try:
        # Demo 1: AST-aware editing
        merged_code = demo_ast_aware_editing()

        # Demo 2: Metadata system
        demo_metadata_system()

        # Demo 3: Test generation
        demo_test_generation()

        print("\n🎉 Demo completed successfully!")
        print("The advanced code editing system is fully operational with:")
        print("✅ AST-aware parsing and merging")
        print("✅ Self-verification and error handling")
        print("✅ Plugin metadata extraction and templates")
        print("✅ Automatic test case generation")
        print("✅ Learning and improvement tracking")

        return merged_code

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n📝 Final merged code preview:")
        print("=" * 60)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("=" * 60)
