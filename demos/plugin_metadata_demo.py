#!/usr/bin/env python3
"""
Plugin Manager Enhancement Demo
================================

This demo showcases the enhanced plugin system with metadata support
and UI integration capabilities.

Features demonstrated:
- Enhanced plugin registration with metadata
- Plugin discovery and categorization
- UI-ready plugin information
- Plugin search and filtering
- Dependency validation
- Status tracking and management
"""

import os
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))


def colorize(text, color):
    """Add color to text for better output readability"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "end": "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors.get('end', '')}"


def print_section(title, content=""):
    """Print a formatted section header"""
    print(f"\n{colorize('=' * 60, 'cyan')}")
    print(f"{colorize(title, 'bold')}")
    print(f"{colorize('=' * 60, 'cyan')}")
    if content:
        print(content)


def demo_plugin_metadata():
    """Demonstrate the enhanced plugin metadata system"""
    print_section("🔌 Plugin Manager Enhancement Demo")

    try:
        from plugin_manager import (
            get_plugin_categories,
            get_plugin_ui_data,
            get_plugins_info,
            list_plugins_by_category,
            search_plugins,
            validate_plugin_dependencies,
        )

        # Demo 1: Plugin Discovery
        print_section("📊 Plugin Discovery & Metadata")

        plugins_info = get_plugins_info()
        print(f"Total plugins discovered: {colorize(str(len(plugins_info)), 'green')}")

        for name, info in plugins_info.items():
            metadata = info["metadata"]
            available = "✅" if info["available"] else "❌"

            print(f"\n🔌 {colorize(name, 'yellow')}")
            print(f"   Status: {available}")
            print(f"   Description: {metadata['description']}")
            print(f"   Category: {colorize(metadata['category'], 'cyan')}")
            print(f"   Version: {colorize(metadata['version'], 'blue')}")
            print(f"   Author: {colorize(metadata['author'], 'magenta')}")

            if metadata["capabilities"]:
                caps = ", ".join(metadata["capabilities"])
                print(f"   Capabilities: {colorize(caps, 'white')}")

            if metadata["dependencies"]:
                deps = ", ".join(metadata["dependencies"])
                print(f"   Dependencies: {colorize(deps, 'yellow')}")

        # Demo 2: Category Organization
        print_section("📂 Plugin Categories")

        categories = get_plugin_categories()
        print(f"Available categories: {colorize(', '.join(categories), 'cyan')}")

        for category in categories:
            plugins_in_category = list_plugins_by_category(category)
            print(
                f"\n📁 {colorize(category.title(), 'yellow')}: {len(plugins_in_category)} plugins"
            )
            for plugin in plugins_in_category:
                print(f"   • {plugin}")

        # Demo 3: Plugin Search
        print_section("🔍 Plugin Search Capabilities")

        search_terms = ["math", "voice", "calculate", "whisper"]

        for term in search_terms:
            results = search_plugins(term)
            if results:
                print(f"\nSearch for '{colorize(term, 'yellow')}': {len(results)} matches")
                for result in results:
                    print(f"   • {result}")
            else:
                print(f"\nSearch for '{colorize(term, 'yellow')}': No matches")

        # Demo 4: UI Data Format
        print_section("🖥️ UI-Ready Plugin Data")

        ui_data = get_plugin_ui_data()
        print("UI Data Structure:")
        print(f"   Total plugins: {colorize(str(ui_data['total_plugins']), 'green')}")
        print(f"   Enabled plugins: {colorize(str(ui_data['enabled_plugins']), 'green')}")
        print(f"   Available plugins: {colorize(str(ui_data['available_plugins']), 'green')}")

        print("\n📊 Category breakdown:")
        for category, plugins in ui_data["categories"].items():
            print(f"   {colorize(category, 'cyan')}: {len(plugins)} plugins")

        # Demo 5: Dependency Validation
        print_section("🔗 Dependency Validation")

        for plugin_name in plugins_info.keys():
            deps = validate_plugin_dependencies(plugin_name)
            if deps:
                print(f"\n🔌 {colorize(plugin_name, 'yellow')} dependencies:")
                for dep, status in deps.items():
                    status_icon = "✅" if status else "❌"
                    status_color = "green" if status else "red"
                    print(
                        f"   {status_icon} {dep}: {colorize('Available' if status else 'Missing', status_color)}"
                    )

        # Demo 6: Plugin Enhancement Benefits
        print_section("✨ Plugin Enhancement Benefits")

        benefits = [
            "🏷️ Rich metadata for plugin discovery and transparency",
            "📂 Automatic categorization for better organization",
            "🔍 Advanced search across names, descriptions, and capabilities",
            "🖥️ UI-ready data structures for seamless integration",
            "🔗 Dependency validation for reliability",
            "📊 Comprehensive statistics and analytics",
            "⚡ Dynamic loading with status tracking",
            "🎯 Capability-based plugin matching",
        ]

        for benefit in benefits:
            print(f"  {benefit}")

        print(f"\n{colorize('Plugin metadata enhancement successfully demonstrated!', 'green')}")

    except Exception as e:
        print(f"{colorize('Error:', 'red')} {e}")
        print("Make sure the enhanced plugin_manager.py is properly loaded.")


def demo_sample_plugin():
    """Create and demonstrate a sample plugin with rich metadata"""
    print_section("🛠️ Sample Plugin Creation")

    # Create a sample plugin file to demonstrate the enhanced system
    sample_plugin_code = '''# Sample Enhanced Plugin
from core.plugin_manager import register_plugin

@register_plugin(
    name="demo_analyzer",
    description="Analyze text and provide insights with AI-powered capabilities",
    capabilities=["text_analysis", "sentiment_detection", "keyword_extraction", "ai_insights"],
    version="2.0.0",
    author="NeuroCode AI Team",
    category="analysis",
    dependencies=["re", "collections"]
)
def analyze_text(text):
    """Analyze text and return comprehensive insights"""
    import re
    from collections import Counter

    # Basic analysis
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))

    # Word frequency
    words = re.findall(r'\\b\\w+\\b', text.lower())
    common_words = Counter(words).most_common(5)

    # Sentiment simulation (simplified)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing']

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    sentiment = "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"

    return {
        "word_count": word_count,
        "character_count": char_count,
        "sentence_count": sentence_count,
        "most_common_words": common_words,
        "sentiment": sentiment,
        "sentiment_scores": {"positive": positive_count, "negative": negative_count}
    }

@register_plugin(
    name="code_formatter",
    description="Format and beautify code with intelligent indentation and styling",
    capabilities=["code_formatting", "syntax_highlighting", "style_validation"],
    version="1.5.0",
    author="NeuroCode DevTools",
    category="development",
    dependencies=["re"]
)
def format_code(code, language="python"):
    """Format code with proper indentation and styling"""
    import re

    # Simplified code formatting
    lines = code.split('\\n')
    formatted_lines = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue

        # Decrease indent for certain patterns
        if re.match(r'^(end|else|elif|except|finally|\\})', stripped):
            indent_level = max(0, indent_level - 1)

        # Add indented line
        formatted_lines.append('    ' * indent_level + stripped)

        # Increase indent for certain patterns
        if re.search(r'(:|\\{|def |class |if |for |while |try:)\\s*$', stripped):
            indent_level += 1

    return '\\n'.join(formatted_lines)
'''

    # Write sample plugin (for demonstration)
    plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
    os.makedirs(plugin_dir, exist_ok=True)

    sample_path = os.path.join(plugin_dir, "demo_plugin.py")

    try:
        with open(sample_path, "w") as f:
            f.write(sample_plugin_code)

        print(f"✅ Created sample plugin: {colorize('demo_plugin.py', 'green')}")
        print("This plugin demonstrates:")
        print("  • Rich metadata with capabilities and dependencies")
        print("  • Multiple functions per plugin")
        print("  • Different categories and versions")
        print("  • Comprehensive documentation")

        # Reload plugins to include the new sample
        print(f"\n{colorize('Note:', 'yellow')} Restart the demo to see the new plugin in action!")

    except Exception as e:
        print(f"{colorize('Error creating sample plugin:', 'red')} {e}")


if __name__ == "__main__":
    demo_plugin_metadata()
    print("\n" + "=" * 60)
    demo_sample_plugin()
