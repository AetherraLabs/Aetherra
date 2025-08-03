#!/usr/bin/env python3
"""
AI Plugin Rewriter Demonstration
Shows the capabilities of Phase 5 Plugin Rewriter system
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from lyrixa.ai.plugin_rewriter import PluginRewriter


def create_sample_plugin():
    """Create a sample plugin for demonstration"""
    return '''"""
Sample Data Processor Plugin
Processes and analyzes numerical data
"""

def process_data(data):
    """Process a list of numbers"""
    if not data:
        return None

    result = {}
    total = 0
    for item in data:
        total = total + item

    result["sum"] = total
    result["average"] = total / len(data)
    result["count"] = len(data)

    return result

class DataAnalyzer:
    """Simple data analysis class"""

    def __init__(self):
        self.history = []

    def analyze(self, dataset):
        """Analyze a dataset"""
        if not dataset:
            return {"error": "Empty dataset"}

        analysis = {
            "min": min(dataset),
            "max": max(dataset),
            "length": len(dataset)
        }

        self.history.append(analysis)
        return analysis

    def get_history(self):
        """Get analysis history"""
        return self.history
'''


def mock_openai_responses():
    """Create mock responses for OpenAI API calls"""
    responses = {
        'explain': """This plugin provides data processing and analysis functionality for numerical datasets.

**Key Functionality:**
1. **process_data()** - Takes a list of numbers and calculates:
   - Sum of all values
   - Average value
   - Count of items

2. **DataAnalyzer class** - Provides advanced analysis including:
   - Finding minimum and maximum values
   - Dataset length calculation
   - Analysis history tracking

**Input Requirements:**
- process_data(): Expects a list or array of numerical values
- DataAnalyzer.analyze(): Expects a non-empty dataset

**Output:**
- Returns dictionary objects containing computed statistics
- Handles edge cases like empty datasets gracefully

This plugin is designed for basic statistical analysis and would be useful in data science workflows.""",

        'refactor': '''"""
Sample Data Processor Plugin (Refactored)
Processes and analyzes numerical data with improved code quality
"""

from typing import List, Dict, Optional, Union


def process_data(data: List[Union[int, float]]) -> Optional[Dict[str, float]]:
    """
    Process a list of numbers and calculate basic statistics.

    Args:
        data: List of numerical values to process

    Returns:
        Dictionary containing sum, average, and count, or None if empty
    """
    if not data:
        return None

    total = sum(data)  # More efficient than manual loop

    return {
        "sum": total,
        "average": total / len(data),
        "count": len(data)
    }


class DataAnalyzer:
    """
    Simple data analysis class with history tracking.

    Provides basic statistical analysis for numerical datasets
    and maintains a history of all analyses performed.
    """

    def __init__(self) -> None:
        """Initialize analyzer with empty history."""
        self.history: List[Dict[str, Union[int, float, str]]] = []

    def analyze(self, dataset: List[Union[int, float]]) -> Dict[str, Union[int, float, str]]:
        """
        Analyze a dataset and return basic statistics.

        Args:
            dataset: List of numerical values to analyze

        Returns:
            Dictionary containing min, max, and length statistics
        """
        if not dataset:
            return {"error": "Empty dataset"}

        analysis = {
            "min": min(dataset),
            "max": max(dataset),
            "length": len(dataset)
        }

        self.history.append(analysis)
        return analysis

    def get_history(self) -> List[Dict[str, Union[int, float, str]]]:
        """
        Get the complete analysis history.

        Returns:
            List of all previous analysis results
        """
        return self.history
''',

        'logging': '''"""
Sample Data Processor Plugin (With Logging)
Processes and analyzes numerical data with comprehensive logging
"""

import logging
from typing import List, Dict, Optional, Union

# Set up logger
logger = logging.getLogger(__name__)


def process_data(data: List[Union[int, float]]) -> Optional[Dict[str, float]]:
    """
    Process a list of numbers and calculate basic statistics.

    Args:
        data: List of numerical values to process

    Returns:
        Dictionary containing sum, average, and count, or None if empty
    """
    logger.info(f"Processing data with {len(data) if data else 0} items")

    if not data:
        logger.warning("Empty dataset provided to process_data")
        return None

    logger.debug("Calculating sum and statistics")
    total = sum(data)

    result = {
        "sum": total,
        "average": total / len(data),
        "count": len(data)
    }

    logger.info(f"Data processing complete: sum={total}, avg={result['average']:.2f}")
    return result


class DataAnalyzer:
    """
    Simple data analysis class with history tracking.

    Provides basic statistical analysis for numerical datasets
    and maintains a history of all analyses performed.
    """

    def __init__(self) -> None:
        """Initialize analyzer with empty history."""
        logger.info("Initializing DataAnalyzer")
        self.history: List[Dict[str, Union[int, float, str]]] = []

    def analyze(self, dataset: List[Union[int, float]]) -> Dict[str, Union[int, float, str]]:
        """
        Analyze a dataset and return basic statistics.

        Args:
            dataset: List of numerical values to analyze

        Returns:
            Dictionary containing min, max, and length statistics
        """
        logger.info(f"Starting analysis of dataset with {len(dataset) if dataset else 0} items")

        if not dataset:
            logger.error("Empty dataset provided for analysis")
            return {"error": "Empty dataset"}

        try:
            logger.debug("Calculating min, max, and length statistics")
            analysis = {
                "min": min(dataset),
                "max": max(dataset),
                "length": len(dataset)
            }

            self.history.append(analysis)
            logger.info(f"Analysis complete: min={analysis['min']}, max={analysis['max']}, length={analysis['length']}")
            return analysis

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}

    def get_history(self) -> List[Dict[str, Union[int, float, str]]]:
        """
        Get the complete analysis history.

        Returns:
            List of all previous analysis results
        """
        logger.debug(f"Retrieving analysis history ({len(self.history)} entries)")
        return self.history
'''
    }
    return responses


def demonstrate_plugin_rewriter():
    """Demonstrate the Plugin Rewriter capabilities"""
    print("🚀 AI Plugin Rewriter Phase 5 Demonstration")
    print("=" * 60)

    # Set up temporary environment
    test_dir = tempfile.mkdtemp()
    plugin_dir = os.path.join(test_dir, "plugins")
    history_dir = os.path.join(test_dir, "history")

    os.makedirs(plugin_dir)
    os.makedirs(history_dir)

    try:
        # Create sample plugin
        sample_plugin_path = os.path.join(plugin_dir, "data_processor.py")
        with open(sample_plugin_path, "w") as f:
            f.write(create_sample_plugin())

        # Initialize rewriter
        rewriter = PluginRewriter(
            plugin_dir=plugin_dir,
            history_dir=history_dir
        )

        print("📝 Created sample plugin: data_processor.py")
        print(f"📁 Plugin directory: {plugin_dir}")
        print(f"📁 History directory: {history_dir}")
        print()

        # Mock OpenAI responses
        mock_responses = mock_openai_responses()

        with patch('openai.OpenAI') as mock_openai_class:

            # Mock client setup
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Demonstration 1: Explain Plugin
            print("🔍 DEMONSTRATION 1: Plugin Explanation")
            print("-" * 40)

            mock_response = MagicMock()
            mock_response.choices[0].message.content = mock_responses['explain']
            mock_client.chat.completions.create.return_value = mock_response

            explanation = rewriter.explain_plugin("data_processor")
            print("📖 Plugin Explanation:")
            print(explanation)
            print()

            # Demonstration 2: Refactor Plugin
            print("[TOOL] DEMONSTRATION 2: Plugin Refactoring")
            print("-" * 40)

            mock_response.choices[0].message.content = mock_responses['refactor']
            mock_client.chat.completions.create.return_value = mock_response

            refactor_result = rewriter.refactor_plugin("data_processor", "add type hints and improve code quality")
            print("🔄 Refactoring Result:")
            print(refactor_result)
            print()

            # Show version history
            versions = rewriter.list_plugin_versions("data_processor")
            print(f"📚 Plugin Versions: {len(versions)} backup(s) created")
            for i, version in enumerate(versions[:3]):  # Show first 3
                print(f"   {i+1}. {version}")
            print()

            # Demonstration 3: Add Logging
            print("📊 DEMONSTRATION 3: Add Logging to Plugin")
            print("-" * 40)

            mock_response.choices[0].message.content = mock_responses['logging']
            mock_client.chat.completions.create.return_value = mock_response

            logging_result = rewriter.add_logging_to_plugin("data_processor")
            print("📝 Logging Addition Result:")
            print(logging_result)
            print()

            # Show updated version history
            versions = rewriter.list_plugin_versions("data_processor")
            print(f"📚 Updated Plugin Versions: {len(versions)} backup(s) total")
            print()

            # Demonstration 4: Version Comparison
            print("🔍 DEMONSTRATION 4: Version Comparison")
            print("-" * 40)

            if len(versions) >= 2:
                diff_result = rewriter.diff_plugin_versions("data_processor", versions[1], versions[0])
                print("📊 Differences between last two versions:")
                print("```diff")
                print(diff_result[:500] + "..." if len(diff_result) > 500 else diff_result)
                print("```")
                print()

            # Demonstration 5: Rollback
            print("⏪ DEMONSTRATION 5: Plugin Rollback")
            print("-" * 40)

            if len(versions) >= 1:
                rollback_result = rewriter.rollback_plugin("data_processor", versions[-1])  # Rollback to oldest
                print("🔄 Rollback Result:")
                print(rollback_result)
                print()

        # Show final status
        print("✅ DEMONSTRATION COMPLETE")
        print("-" * 40)
        print("🎯 Plugin Rewriter successfully demonstrated:")
        print("   ✅ Plugin explanation with natural language")
        print("   ✅ Code refactoring with AI assistance")
        print("   ✅ Automatic logging injection")
        print("   ✅ Version control and history tracking")
        print("   ✅ Version comparison and diffing")
        print("   ✅ Safe rollback functionality")
        print()
        print("🚀 Phase 5 AI Plugin Rewriter is ready for production!")

    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"🧹 Cleaned up temporary directory: {test_dir}")


def show_integration_example():
    """Show how to integrate with Lyrixa's conversational interface"""
    print("\n" + "=" * 60)
    print("🤖 LYRIXA INTEGRATION EXAMPLE")
    print("=" * 60)

    integration_example = '''
# Example: Integrating Plugin Rewriter with Lyrixa Chat

from lyrixa.ai.plugin_rewriter import PluginRewriter

class LyrixaPluginRewriterIntegration:
    def __init__(self):
        self.rewriter = PluginRewriter()

    def handle_user_request(self, user_input):
        """Handle user requests for plugin operations"""

        if "explain plugin" in user_input.lower():
            plugin_name = self.extract_plugin_name(user_input)
            return self.rewriter.explain_plugin(plugin_name)

        elif "refactor plugin" in user_input.lower():
            plugin_name = self.extract_plugin_name(user_input)
            goal = self.extract_refactor_goal(user_input)
            return self.rewriter.refactor_plugin(plugin_name, goal)

        elif "add logging" in user_input.lower():
            plugin_name = self.extract_plugin_name(user_input)
            return self.rewriter.add_logging_to_plugin(plugin_name)

    def conversational_commands(self):
        """Examples of natural language commands Lyrixa can handle"""
        return [
            "Explain the data_processor plugin",
            "Refactor the analytics plugin for better performance",
            "Add logging to the file_handler plugin",
            "Show me the differences between plugin versions",
            "Rollback the calculator plugin to yesterday's version"
        ]

# Lyrixa can now respond to commands like:
# User: "Can you explain what the data_processor plugin does?"
# Lyrixa: "I'll analyze the plugin for you..." → calls explain_plugin()
#
# User: "Make the analytics plugin run faster"
# Lyrixa: "I'll refactor it for performance..." → calls refactor_plugin()
'''

    print("💡 Integration Code Example:")
    print(integration_example)

    print("🗣️  Natural Language Commands Lyrixa Can Handle:")
    commands = [
        "Explain the data_processor plugin",
        "Refactor the analytics plugin for better performance",
        "Add logging to the file_handler plugin",
        "Show me differences between plugin versions",
        "Rollback the calculator plugin to yesterday's version"
    ]

    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. \"{cmd}\"")

    print("\n🎯 This makes Lyrixa a true AI programming assistant!")


if __name__ == "__main__":
    demonstrate_plugin_rewriter()
    show_integration_example()
