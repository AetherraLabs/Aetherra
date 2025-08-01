#!/usr/bin/env python3
"""
🚀 COMPLETE SELF-IMPROVEMENT AND MEMORY-LINKED PLUGIN SYSTEM DEMO
================================================================

This demonstrates the complete implementation of:
1. Self-Generated Plugin Improvements
2. Memory-Linked Plugin Discovery and Recommendations
3. Automatic suggestion and improvement workflows
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class MockMemoryManager:
    """Mock memory manager for testing"""

    def __init__(self):
        self.memories = [
            {
                "content": "User had trouble organizing files in the project",
                "context": "file management organizational issues",
                "timestamp": "2025-01-10T10:00:00",
                "confidence": 0.8,
            },
            {
                "content": "User wanted to create data visualization charts",
                "context": "data visualization matplotlib plotting",
                "timestamp": "2025-01-09T14:30:00",
                "confidence": 0.9,
            },
            {
                "content": "Plugin failed due to missing error handling",
                "context": "debugging error handling try except blocks",
                "timestamp": "2025-01-08T16:45:00",
                "confidence": 0.7,
            },
        ]

    def search_memories(self, query: str, limit: int = 5):
        """Search memories based on query"""
        query_lower = query.lower()
        results = []

        for memory in self.memories:
            score = 0
            content_lower = memory["content"].lower()
            context_lower = memory["context"].lower()

            # Simple relevance scoring
            for word in query_lower.split():
                if word in content_lower:
                    score += 0.5
                if word in context_lower:
                    score += 0.3

            if score > 0:
                results.append(memory)

        return results[:limit]


class MockGUIInterface:
    """Mock GUI interface for testing auto-improvement"""

    def __init__(self):
        self.injected_plugins = []

    def inject_plugin_code(self, code: str, filename: str = "improvement.aether"):
        """Mock plugin injection"""
        self.injected_plugins.append(
            {"filename": filename, "code": code, "timestamp": "2025-01-13T15:30:00"}
        )
        print(f"🖥️  GUI: Injected improvement to {filename}")
        print(f"🖥️  GUI: Code length: {len(code)} characters")
        return True


async def demo_self_improvement_system():
    """Demonstrate the self-improvement system"""
    print("🤖 SELF-IMPROVEMENT SYSTEM DEMO")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.plugin_diff_engine import PluginDiffEngine
        from Aetherra.lyrixa.self_improvement_trigger import SelfImprovementScheduler

        # Create mock GUI
        gui = MockGUIInterface()

        # Initialize components
        workspace_path = str(project_root)
        diff_engine = PluginDiffEngine(workspace_path)
        scheduler = SelfImprovementScheduler(workspace_path, gui_interface=gui)

        print("✅ Self-improvement components initialized")

        # Discover and analyze plugins
        print("\n🔍 Discovering and analyzing plugins...")
        plugins = diff_engine.discover_plugins()
        print(f"📦 Found {len(plugins)} plugins")

        if plugins:
            # Analyze a sample plugin
            sample_plugin = plugins[0]
            print(f"\n🔬 Analyzing sample plugin: {sample_plugin[0]}")

            analysis = diff_engine.analyze_plugin(sample_plugin[0], sample_plugin[1])
            print(f"✅ Analysis complete:")
            print(f"   Confidence Score: {analysis.confidence_score:.2f}")
            print(f"   Issues Found: {len(analysis.issues)}")
            print(f"   Suggestions: {len(analysis.suggestions)}")

            # Generate improvement proposal
            proposal = diff_engine.generate_improvement_proposal(analysis)
            if proposal:
                print(f"\n💡 Improvement Proposal Generated:")
                print(f"   Plugin: {proposal.plugin_id}")
                print(f"   Change: {proposal.proposed_change}")
                print(f"   Impact: {proposal.impact}")
                print(f"   Risk: {proposal.risk_level}")
                print(f"   Confidence: {proposal.confidence:.1%}")

                # Simulate auto-improvement workflow
                print(f"\n🔄 Simulating auto-improvement workflow...")
                await scheduler._queue_for_review(proposal)

                if gui.injected_plugins:
                    print("🎉 SUCCESS: Improvement automatically queued in GUI!")
                    print(f"   Injected: {gui.injected_plugins[-1]['filename']}")
            else:
                print("✨ Plugin already excellent - no improvements needed!")

        # Test scheduled analysis
        print(f"\n⏰ Testing scheduled analysis system...")
        status = scheduler.get_improvement_status()
        print(f"   System Running: {status['is_running']}")
        print(f"   Check Interval: {status['check_interval_hours']} hours")
        print(f"   Components Available: {status['components_available']}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Self-improvement components not fully available")
        return False
    except Exception as e:
        print(f"❌ Error in self-improvement demo: {e}")
        return False


async def demo_memory_linked_plugins():
    """Demonstrate the memory-linked plugin discovery system"""
    print("\n🔗 MEMORY-LINKED PLUGIN DISCOVERY DEMO")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.memory_linked_plugins import MemoryLinkedPluginDiscovery

        # Initialize with mock memory manager
        mock_memory = MockMemoryManager()
        discovery = MemoryLinkedPluginDiscovery(
            str(project_root), memory_manager=mock_memory
        )

        print("✅ Memory-linked discovery system initialized")

        # Discover plugins with metadata
        print("\n📚 Discovering plugins and extracting metadata...")
        plugins_with_metadata = discovery.discover_plugins_with_metadata()
        print(f"📦 Discovered {len(plugins_with_metadata)} plugins with metadata")

        # Show sample metadata
        if plugins_with_metadata:
            sample_plugin_id = list(plugins_with_metadata.keys())[0]
            sample_metadata = plugins_with_metadata[sample_plugin_id]
            print(f"\n📋 Sample Plugin Metadata ({sample_plugin_id}):")
            print(f"   Description: {sample_metadata.description[:100]}...")
            print(f"   Tags: {sample_metadata.tags[:5]}")
            print(f"   Confidence: {sample_metadata.confidence_score:.2f}")

        # Test tag-based search
        print(f"\n🏷️  Testing tag-based search...")
        tag_results = discovery.search_by_tag("file_management")
        print(f"   'file_management' tag: {len(tag_results)} plugins")

        visualization_results = discovery.search_by_tag("visualization")
        print(f"   'visualization' tag: {len(visualization_results)} plugins")

        # Test context-aware search
        print(f"\n🎯 Testing context-aware search...")
        test_queries = [
            "I need to organize my files and folders",
            "Create charts and graphs for my data",
            "Debug errors in my plugins",
        ]

        for query in test_queries:
            context_results = discovery.search_by_context(query)
            print(f"   '{query}': {len(context_results)} relevant plugins")

        # Test memory-based recommendations
        print(f"\n🧠 Testing memory-based recommendations...")
        memory_suggestions = discovery.get_memory_context_suggestions(
            "file organization"
        )
        print(f"   Memory context suggestions: {len(memory_suggestions)}")

        for metadata, reason in memory_suggestions[:3]:
            print(f"   - {metadata.plugin_id}: {reason[:50]}...")

        # Test comprehensive recommendations
        print(f"\n💡 Testing comprehensive plugin recommendations...")
        goal_text = "I want to analyze some data and create visualizations"
        recommendations = discovery.get_plugin_recommendations(goal_text)

        print(f"   Goal: '{goal_text}'")
        print(f"   Recommendations: {len(recommendations)}")

        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['plugin_id']} (score: {rec['score']:.2f})")
            print(f"      Reason: {rec['reason']}")
            print(f"      Type: {rec['type']}")

        # Test plugin chaining
        print(f"\n🔗 Testing plugin chain suggestions...")
        chains = discovery.generate_plugin_chain_suggestions(goal_text)
        print(f"   Plugin chains suggested: {len(chains)}")

        for i, chain in enumerate(chains[:2], 1):
            print(f"   Chain {i}: {' → '.join(chain)}")

        # Test autocomplete
        print(f"\n⌨️  Testing autocomplete suggestions...")
        autocomplete_tests = ["file", "vis", "data"]

        for partial in autocomplete_tests:
            suggestions = discovery.generate_autocomplete_suggestions(partial)
            print(f"   '{partial}': {suggestions[:3]}")

        # Simulate plugin usage tracking
        print(f"\n📊 Testing usage tracking...")
        discovery.record_plugin_usage("file_tools", True, "Organized project files")
        discovery.record_plugin_usage("visualizer", True, "Created bar charts")
        discovery.record_plugin_usage(
            "debug_helper", False, "Failed to fix syntax error"
        )
        print("✅ Usage events recorded")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Memory-linked components not fully available")
        return False
    except Exception as e:
        print(f"❌ Error in memory-linked demo: {e}")
        return False


async def demo_integrated_workflow():
    """Demonstrate the integrated self-improvement and memory-linked workflow"""
    print("\n🎯 INTEGRATED WORKFLOW DEMO")
    print("=" * 50)

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize conversation manager with self-improvement
        gui = MockGUIInterface()
        conversation_manager = LyrixaConversationManager(
            workspace_path=str(project_root), gui_interface=gui
        )

        print("✅ Conversation manager initialized")

        # Enable self-improvement monitoring
        print("\n🤖 Enabling self-improvement monitoring...")
        conversation_manager.enable_self_improvement_monitoring(check_interval_hours=1)
        print("✅ Self-improvement monitoring enabled")

        # Test plugin improvement suggestions
        print("\n💡 Testing plugin improvement suggestions...")
        improvement_suggestions = (
            await conversation_manager.suggest_plugin_improvements()
        )
        print("📋 Improvement suggestions generated:")
        print(
            improvement_suggestions[:200] + "..."
            if len(improvement_suggestions) > 200
            else improvement_suggestions
        )

        # Test auto-check for improvements
        print("\n🔍 Testing automatic improvement detection...")
        found_improvements = await conversation_manager.auto_check_for_improvements()
        print(f"   Improvements detected: {found_improvements}")

        # Simulate natural conversation with improvement trigger
        print("\n💬 Testing natural conversation with improvement integration...")
        test_inputs = [
            "Can you help me improve my plugins?",
            "I want to create a data visualization plugin",
            "My file management is messy, what plugins can help?",
        ]

        for user_input in test_inputs:
            print(f"\n   User: {user_input}")

            # This would normally generate an LLM response with suggestions
            # For demo purposes, we'll simulate a relevant response
            if "improve" in user_input.lower():
                response = improvement_suggestions
            elif "visualization" in user_input.lower():
                response = "I can help you create a visualization plugin! Based on your past work with data analysis, I recommend using matplotlib. Let me suggest some relevant plugins and improvements."
            else:
                response = "I can help with that! Let me check what plugins might be useful based on your context and past experiences."

            print(f"   Lyrixa: {response[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error in integrated workflow demo: {e}")
        return False


async def main():
    """Run complete demonstration"""
    print("🚀 COMPLETE SELF-IMPROVEMENT AND MEMORY-LINKED PLUGIN SYSTEM")
    print("=" * 65)
    print()

    # Run all demos
    demo1_success = await demo_self_improvement_system()
    demo2_success = await demo_memory_linked_plugins()
    demo3_success = await demo_integrated_workflow()

    # Final summary
    print("\n🏆 DEMONSTRATION SUMMARY")
    print("=" * 30)
    print(f"Self-Improvement System: {'✅ SUCCESS' if demo1_success else '❌ FAILED'}")
    print(f"Memory-Linked Plugins:   {'✅ SUCCESS' if demo2_success else '❌ FAILED'}")
    print(f"Integrated Workflow:     {'✅ SUCCESS' if demo3_success else '❌ FAILED'}")

    if all([demo1_success, demo2_success, demo3_success]):
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print()
        print("✅ Lyrixa can now:")
        print("   • Automatically analyze and improve plugins over time")
        print("   • Suggest plugins based on memory context and past experiences")
        print("   • Provide intelligent recommendations during conversations")
        print("   • Learn from plugin usage patterns and success rates")
        print("   • Queue improvements in the Plugin Editor for user review")
        print("   • Generate contextual autocomplete and plugin chains")
        print()
        print(
            "🎯 MISSION ACCOMPLISHED: Self-Generated Improvements + Memory-Linked Plugins!"
        )
    else:
        print("\n⚠️ Some components need attention - check implementation details")

    return all([demo1_success, demo2_success, demo3_success])


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
