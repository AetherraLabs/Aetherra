#!/usr/bin/env python3
"""
🔧 QUICK FIX FOR FLAGSHIP FEATURES
==================================

Quick fix for the string formatting issues in the flagship plugins demo.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_individual_plugins():
    """Test each plugin individually to identify issues."""

    print("🔧 Testing Workflow Builder Plugin...")
    try:
        from lyrixa.plugins.workflow_builder_plugin import WorkflowBuilderPlugin

        builder = WorkflowBuilderPlugin()
        workflow_id = builder.create_from_template("data_processing", "Test Workflow")
        print(f"✅ Workflow Builder OK: Created {workflow_id}")
    except Exception as e:
        print(f"❌ Workflow Builder Error: {e}")

    print("\n🧠 Testing Assistant Trainer Plugin...")
    try:
        from lyrixa.plugins.assistant_trainer_plugin import AssistantTrainerPlugin

        trainer = AssistantTrainerPlugin()
        dataset_id = trainer.create_dataset("Test Dataset")
        print(f"✅ Assistant Trainer OK: Created {dataset_id}")
    except Exception as e:
        print(f"❌ Assistant Trainer Error: {e}")

    print("\n🔌 Testing Plugin Generator Plugin...")
    try:
        from lyrixa.plugins.plugin_generator_plugin import PluginGeneratorPlugin

        generator = PluginGeneratorPlugin()
        templates = generator.list_templates()
        print(f"✅ Plugin Generator Basic OK: {len(templates)} templates")

        # Test generation with a simple case
        try:
            plugin_id = generator.generate_plugin(
                "ui_widget", "Simple Test", "A test plugin"
            )
            print(f"✅ Plugin Generation OK: Created {plugin_id}")
        except Exception as gen_error:
            print(f"❌ Plugin Generation Error: {gen_error}")

    except Exception as e:
        print(f"❌ Plugin Generator Error: {e}")

    print("\n🌐 Testing Remote Plugin Installation...")
    try:
        from lyrixa.gui.plugin_ui_loader import PluginUIManager

        manager = PluginUIManager()
        sources = manager.list_remote_sources()
        print(f"✅ Remote Sources OK: {len(sources)} sources available")
    except Exception as e:
        print(f"❌ Remote Plugin Installation Error: {e}")


if __name__ == "__main__":
    test_individual_plugins()
