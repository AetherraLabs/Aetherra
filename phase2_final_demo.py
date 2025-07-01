#!/usr/bin/env python3
"""
🎉 Phase 2 Complete Integration Demo
===================================

Comprehensive demonstration of all Phase 2 enhancements working together:
- Stability & Error Handling
- Introspective Logging & Self-Awareness
- Conversational AI with Personas
- Plugin Registry & Management
- Chat Enhancements
- Internal Refactoring & Code Quality

This demo showcases the full integration of all Phase 2 systems and their
synergistic capabilities in the NeuroCode & Neuroplex AI OS.

Author: NeuroCode Development Team
Date: June 30, 2025
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all Phase 2 systems
try:
    from core.chat_enhancements import ChatEnhancementSystem, ChatMessageType
    from core.conversational_ai import ConversationalAI, PersonaMode
    from core.internal_refactoring import InternalRefactoringSystem
    from core.introspective_logger import IntrospectiveLogger
    from core.plugin_registry import PluginRegistry
    from core.stability import CircuitBreaker, GracefulDegradation, StabilityManager

    PHASE2_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some Phase 2 systems not available: {e}")
    PHASE2_SYSTEMS_AVAILABLE = False


class Phase2IntegratedDemo:
    """Comprehensive demo of all Phase 2 systems working together"""

    def __init__(self):
        if not PHASE2_SYSTEMS_AVAILABLE:
            print("❌ Cannot run demo - Phase 2 systems not available")
            return

        print("🚀 Initializing Phase 2 Integrated Systems...")

        # Initialize all systems with error handling
        self.stability_manager = StabilityManager()
        self.introspective_logger = IntrospectiveLogger()
        self.conversational_ai = ConversationalAI()
        self.plugin_registry = PluginRegistry()
        self.chat_system = ChatEnhancementSystem()
        self.refactoring_system = InternalRefactoringSystem()

        print("✅ All Phase 2 systems initialized successfully!")

    def demonstrate_stability_features(self):
        """Demonstrate stability and error handling capabilities"""
        print("\n🛡️ Stability & Error Handling Demo")
        print("=" * 50)

        # Test circuit breaker
        print("🔌 Testing Circuit Breaker Pattern...")
        circuit_breaker = CircuitBreaker("demo_service", failure_threshold=2)

        # Simulate some operations
        for i in range(5):
            try:
                if i < 3:
                    # Simulate failures
                    circuit_breaker.call(lambda i=i: self._simulate_failing_operation(i))
                else:
                    # Simulate recovery
                    circuit_breaker.call(lambda i=i: self._simulate_successful_operation(i))
            except Exception as e:
                print(f"  Operation {i + 1}: Failed - {e}")

        print(f"  Circuit Breaker State: {circuit_breaker.state}")
        print(f"  Failure Count: {circuit_breaker.failure_count}")

        # Test graceful degradation
        print("\n📉 Testing Graceful Degradation...")
        degradation = GracefulDegradation()

        # Simulate high CPU usage triggering degradation
        degradation.monitor_resource_usage(cpu_percent=85, memory_percent=60)
        degradation_status = degradation.get_active_degradations()

        print(f"  Active Degradations: {len(degradation_status)}")
        for deg in degradation_status:
            print(f"    • {deg['feature']}: {deg['reason']}")

        # Test safe execution
        print("\n🔒 Testing Safe Execution Wrapper...")

        @self.stability_manager.safe_execute
        def risky_operation():
            """Simulated risky operation"""
            import random

            if random.random() < 0.5:
                raise ValueError("Simulated error")
            return "Operation successful!"

        for i in range(3):
            result = risky_operation()
            print(f"  Safe Operation {i + 1}: {result}")

    def _simulate_failing_operation(self, attempt):
        """Simulate a failing operation"""
        raise ConnectionError(f"Simulated failure #{attempt + 1}")

    def _simulate_successful_operation(self, attempt):
        """Simulate a successful operation"""
        return f"Success #{attempt + 1}"

    def demonstrate_introspective_logging(self):
        """Demonstrate introspective logging and self-awareness"""
        print("\n🔍 Introspective Logging & Self-Awareness Demo")
        print("=" * 50)

        # Log some sample executions
        print("📝 Logging AI Executions...")

        sample_executions = [
            {
                "code": 'print("Hello, NeuroCode!")',
                "result": "Hello, NeuroCode!\nNone",
                "context": {"user_intent": "greeting", "complexity": "simple"},
            },
            {
                "code": "for i in range(5): calculate_fibonacci(i)",
                "result": "[0, 1, 1, 2, 3]",
                "context": {"user_intent": "computation", "complexity": "medium"},
            },
            {
                "code": 'import pandas as pd; df = pd.read_csv("data.csv")',
                "result": "DataFrame loaded successfully",
                "context": {"user_intent": "data_analysis", "complexity": "high"},
            },
        ]

        for i, execution in enumerate(sample_executions, 1):
            print(f"  Execution {i}: {execution['code'][:30]}...")

            reflection = self.introspective_logger.log_execution(
                execution["code"], execution["result"], execution["context"]
            )

            print(f"    Reflection ID: {reflection.execution_id}")
            print(f"    Performance Score: {reflection.performance_metrics.get('score', 'N/A')}")

        # Show today's activity
        print("\n📊 Today's Activity Dashboard...")
        activity = self.introspective_logger.get_todays_activity()

        print(f"  Total Executions: {activity['total_executions']}")
        print(f"  Success Rate: {activity['success_rate']:.1%}")
        print(f"  Most Common Intent: {activity.get('most_common_intent', 'N/A')}")

        # Generate insights
        print("\n💡 Auto-Generated Insights...")
        insights = self.introspective_logger.generate_insights()

        for insight in insights[:3]:  # Show top 3 insights
            print(f"  • {insight['message']}")

    def demonstrate_conversational_ai(self):
        """Demonstrate conversational AI with personas"""
        print("\n💬 Conversational AI & Personas Demo")
        print("=" * 50)

        # Test different personas
        personas_to_test = [
            (PersonaMode.ASSISTANT, "How can I help you today?"),
            (PersonaMode.DEVELOPER, "Let's debug this Python issue together."),
            (PersonaMode.TEACHER, "Let me explain how neural networks work."),
            (PersonaMode.CREATIVE, "Let's brainstorm some innovative ideas!"),
        ]

        print("🎭 Testing Different AI Personas...")
        for persona, message in personas_to_test:
            print(f"\n  {persona.value.upper()} Persona:")
            print(f"    User: {message}")

            # Set persona and get response
            self.conversational_ai.set_persona(persona)
            response = self.conversational_ai.generate_response(message, context={"demo": True})

            print(f"    AI: {response['content'][:80]}...")
            print(f"    Confidence: {response['confidence']:.1%}")

        # Test auto-persona detection
        print("\n🤖 Testing Auto-Persona Detection...")

        test_messages = [
            "Can you help me fix this bug in my code?",
            "Explain machine learning to a beginner",
            "I need creative ideas for my startup",
            "What's the weather like today?",
        ]

        for msg in test_messages:
            detected_persona = self.conversational_ai.detect_best_persona(msg)
            print(f"  Message: '{msg[:40]}...'")
            print(f"  Detected Persona: {detected_persona.value}")

        # Show conversation memory
        print("\n🧠 Conversation Memory Integration...")
        memory_stats = self.conversational_ai.get_conversation_stats()

        print(f"  Total Conversations: {memory_stats['total_conversations']}")
        print(f"  Recent Personas Used: {', '.join(memory_stats.get('recent_personas', []))}")
        print(
            f"  Memory Integration: {'✅ Active' if memory_stats.get('memory_integration') else '❌ Disabled'}"
        )

    def demonstrate_plugin_registry(self):
        """Demonstrate plugin registry and management"""
        print("\n🔌 Plugin Registry & Management Demo")
        print("=" * 50)

        # Show available plugins
        print("📦 Available Plugins in Registry...")

        available_plugins = self.plugin_registry.get_available_plugins()
        for _plugin_id, plugin in list(available_plugins.items())[:5]:  # Show first 5
            print(f"  • {plugin.name} (v{plugin.version})")
            print(f"    Category: {plugin.category}")
            print(f"    Rating: {'⭐' * int(plugin.rating)}")
            print(f"    Downloads: {plugin.download_count}")

        print(f"\n  Total Plugins Available: {len(available_plugins)}")

        # Test plugin suggestions
        print("\n💡 Plugin Suggestion Engine...")

        test_contexts = [
            {"current_task": "data_analysis", "user_level": "beginner"},
            {"current_task": "web_development", "user_level": "advanced"},
            {"current_task": "machine_learning", "user_level": "intermediate"},
        ]

        for context in test_contexts:
            suggestions = self.plugin_registry.get_plugin_suggestions(context)
            print(f"\n  Context: {context['current_task']} ({context['user_level']})")

            for suggestion in suggestions[:3]:  # Top 3 suggestions
                print(f"    → {suggestion['plugin'].name}: {suggestion['reason']}")

        # Show usage analytics
        print("\n📊 Plugin Usage Analytics...")
        analytics = self.plugin_registry.get_usage_analytics()

        print(f"  Most Popular Category: {analytics.get('popular_category', 'N/A')}")
        print(f"  Average Rating: {analytics.get('average_rating', 0):.1f}/5")
        print(f"  Total Downloads: {analytics.get('total_downloads', 0):,}")

    def demonstrate_chat_enhancements(self):
        """Demonstrate chat enhancements and streaming"""
        print("\n💫 Chat Enhancements Demo")
        print("=" * 50)

        # Test chat session management
        print("📝 Chat Session Management...")

        # Create a new session
        session_id = self.chat_system.create_new_session("Phase 2 Demo Session", ["demo", "phase2"])
        print(f"  Created Session: {session_id}")

        # Send some messages
        print("\n💬 Sending Chat Messages...")

        messages = [
            ("Hello! I'm testing the new chat system.", ChatMessageType.USER),
            (
                "Welcome to the Phase 2 chat enhancements! How can I help you explore the new features?",
                ChatMessageType.ASSISTANT,
            ),
            ("Can you show me the streaming capabilities?", ChatMessageType.USER),
        ]

        for content, msg_type in messages:
            self.chat_system.send_message(content, msg_type)
            speaker = "User" if msg_type == ChatMessageType.USER else "AI"
            print(f"  {speaker}: {content[:50]}...")

        # Simulate streaming response
        print("\n🔄 Streaming Response Demo...")

        response_id = "demo_stream_001"

        def stream_callback(chunk):
            if chunk:
                print(chunk, end="", flush=True)
            else:
                print(" [Complete]")

        print("  AI: ", end="")
        self.chat_system.start_streaming_response(response_id, stream_callback)

        # Simulate streaming chunks
        response_chunks = [
            "Streaming responses allow for real-time ",
            "interaction as the AI generates text. ",
            "This creates a more natural conversation flow ",
            "and better user experience.",
        ]

        for chunk in response_chunks:
            time.sleep(0.3)  # Simulate generation delay
            self.chat_system.update_streaming_response(response_id, chunk)

        self.chat_system.complete_streaming_response(response_id)

        # Show session summary
        print("\n📊 Session Summary...")
        summary = self.chat_system.get_session_summary()

        for key, value in summary.items():
            if key != "tags":
                print(f"  {key}: {value}")

        # Show export capabilities
        print("\n💾 Export Capabilities...")
        exported_md = self.chat_system.export_current_session("markdown")
        print(f"  Exported {len(exported_md)} characters as Markdown")

        # Search functionality
        print("\n🔍 Chat Search Demo...")
        search_results = self.chat_system.search_conversations("streaming", max_results=5)
        print(f"  Found {len(search_results)} messages containing 'streaming'")

    def demonstrate_refactoring_system(self):
        """Demonstrate internal refactoring and code quality"""
        print("\n🏗️ Internal Refactoring & Code Quality Demo")
        print("=" * 50)

        # Show system status
        print("📊 Refactoring System Status...")
        status = self.refactoring_system.get_refactoring_status()

        print(f"  Project Path: {Path(status['project_path']).name}")
        print(f"  Analyzers Available: {len(status['analyzers_available'])}")

        # Analyze current file
        print("\n🔍 Code Quality Analysis...")
        current_file = Path(__file__)

        print(f"  Analyzing: {current_file.name}")
        report = self.refactoring_system.analyzer.analyze_file(current_file)

        print(f"  Quality Score: {report.quality_score:.1f}/100")
        print(f"  Lines of Code: {report.code_lines}")
        print(f"  Functions: {len(report.functions)}")
        print(f"  Imports: {len(report.imports)}")

        if report.suggestions:
            print("\n💡 Quality Suggestions:")
            for suggestion in report.suggestions[:3]:
                print(f"    • {suggestion}")

        # Show import analysis
        print("\n📦 Import Analysis...")
        imports = self.refactoring_system.analyzer.import_organizer.analyze_imports(current_file)

        stdlib_count = sum(1 for imp in imports if imp.is_standard_library)
        third_party_count = sum(1 for imp in imports if imp.is_third_party)
        local_count = sum(1 for imp in imports if imp.is_local)

        print(f"  Standard Library: {stdlib_count}")
        print(f"  Third Party: {third_party_count}")
        print(f"  Local Imports: {local_count}")

        # Show project-wide metrics
        print("\n📈 Project-Wide Quality Metrics...")

        # Quick analysis of a few files
        python_files = list(Path(".").glob("*.py"))[:3]  # Analyze first 3 Python files
        project_reports = {}

        for file_path in python_files:
            if file_path.name != "__pycache__":
                try:
                    file_report = self.refactoring_system.analyzer.analyze_file(file_path)
                    project_reports[str(file_path)] = file_report
                except Exception:
                    continue

        if project_reports:
            avg_quality = sum(r.quality_score for r in project_reports.values()) / len(
                project_reports
            )
            total_functions = sum(len(r.functions) for r in project_reports.values())

            print(f"  Files Analyzed: {len(project_reports)}")
            print(f"  Average Quality: {avg_quality:.1f}/100")
            print(f"  Total Functions: {total_functions}")

    def demonstrate_system_integration(self):
        """Demonstrate how all systems work together"""
        print("\n🔗 Integrated System Synergies Demo")
        print("=" * 50)

        print("🤝 Cross-System Integration Examples:")

        # Example 1: Stability + Introspective Logging
        print("\n1. Stability + Introspective Logging:")
        print("   • Errors are automatically logged and reflected upon")
        print("   • Circuit breakers prevent cascade failures")
        print("   • Performance degradation triggers are logged for analysis")

        # Example 2: Persona + Plugin Suggestions
        print("\n2. Conversational AI + Plugin Registry:")
        print("   • AI personality influences plugin recommendations")
        print("   • Developer persona suggests coding plugins")
        print("   • Teacher persona suggests educational plugins")

        # Example 3: Chat + Memory Integration
        print("\n3. Chat Enhancements + Memory System:")
        print("   • Conversations are automatically stored and categorized")
        print("   • Context from previous chats influences responses")
        print("   • Search across all conversation history")

        # Example 4: Refactoring + Quality Monitoring
        print("\n4. Refactoring + Quality Monitoring:")
        print("   • Continuous code quality analysis")
        print("   • Automatic suggestion of improvements")
        print("   • Integration with development workflow")

        # Show activity summary
        print("\n📊 Overall System Activity:")

        try:
            # Get stats from each system
            chat_stats = self.chat_system.get_activity_stats()
            persona_stats = self.conversational_ai.get_conversation_stats()

            print(f"  Chat Sessions: {chat_stats.get('total_sessions', 0)}")
            print(f"  Messages Processed: {chat_stats.get('total_messages', 0)}")
            print(f"  Personas Used: {len(persona_stats.get('recent_personas', []))}")
            print(f"  Rich Formatting: {'✅' if chat_stats.get('formatting_available') else '❌'}")
            print(f"  Memory Integration: {'✅' if chat_stats.get('memory_integration') else '❌'}")

        except Exception as e:
            print(f"  Could not gather all stats: {e}")

        print("\n🎯 Key Integration Benefits:")
        print("  • Unified error handling across all components")
        print("  • Self-aware AI that learns from its own behavior")
        print("  • Context-driven interactions with full memory integration")
        print("  • Intelligent plugin ecosystem with smart recommendations")
        print("  • Rich, interactive chat experience with full history")
        print("  • Continuous code quality improvement and monitoring")

    def run_complete_demo(self):
        """Run the complete Phase 2 demonstration"""
        if not PHASE2_SYSTEMS_AVAILABLE:
            return

        print("🎉 NeuroCode & Neuroplex Phase 2 Complete Demo")
        print("=" * 60)
        print("Building on Phase 1 Success: UI Polish, Memory Logging, Plugin UX")
        print("Phase 2 Enhancements: Stability, Intelligence, Conversation, Quality")
        print("=" * 60)

        start_time = time.time()

        try:
            # Run all individual demonstrations
            self.demonstrate_stability_features()
            self.demonstrate_introspective_logging()
            self.demonstrate_conversational_ai()
            self.demonstrate_plugin_registry()
            self.demonstrate_chat_enhancements()
            self.demonstrate_refactoring_system()
            self.demonstrate_system_integration()

            # Final summary
            duration = time.time() - start_time

            print("\n🎊 Phase 2 Demo Complete!")
            print("=" * 50)
            print(f"⏱️  Demo Duration: {duration:.1f} seconds")
            print("✅ All Phase 2 systems operational and integrated")
            print("🚀 NeuroCode & Neuroplex ready for advanced AI operations!")
            print("\n🔮 Next Steps:")
            print("  • Configure file storage permissions for full functionality")
            print("  • Create and test custom plugins")
            print("  • Integrate with UI for visual plugin management")
            print("  • Deploy in production environment")
            print("  • Begin Phase 3 planning for advanced features")

        except Exception as e:
            print(f"\n❌ Demo encountered an error: {e}")
            print("This demonstrates the importance of the stability systems!")


def main():
    """Main entry point for the Phase 2 demo"""
    demo = Phase2IntegratedDemo()

    if PHASE2_SYSTEMS_AVAILABLE:
        demo.run_complete_demo()
    else:
        print("❌ Phase 2 systems not available for demonstration")
        print("Please ensure all Phase 2 modules are properly installed")


if __name__ == "__main__":
    main()
