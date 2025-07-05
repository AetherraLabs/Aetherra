"""
🚀 Phase 2 Comprehensive Demo
============================

Demonstrates all Phase 2 enhancements:
- Stability & Error Handling
- Introspective Logging
- Conversational AI with Personas
- Enhanced Plugin Registry

This demo showcases the complete integration of all new systems.
"""

import time
import traceback

from core.conversational_ai import (
    PersonaMode,
    chat,
    conversational_ai,
    get_available_personas,
    switch_persona,
)
from core.introspective_logger import (
    ActivityType,
    PerformanceMetrics,
    get_activity_dashboard,
    introspective_logger,
    log_aethercode_execution,
)
from core.plugin_registry import (
    get_plugin_catalog,
    get_plugin_suggestions,
    plugin_registry,
    search_plugins,
)

# Import all our new Phase 2 systems
from core.stability import (
    ErrorSeverity,
    degradation_manager,
    performance_monitor,
    safe_execute,
    stability_context,
    stability_manager,
)

# Also import existing UI system from Phase 1
from core.ui.interface import InterfaceConfig, AetherraPlexInterface
from core.ui.themes import UITheme


class Phase2Demo:
    """Comprehensive demonstration of Phase 2 features"""

    def __init__(self):
        self.ui = AetherraPlexInterface(
            InterfaceConfig(
                theme=UITheme.CYBERPUNK,
                auto_suggestions=True,
                rich_formatting=True,
                animations_enabled=True,
            )
        )

        # Start a conversational session
        conversational_ai.start_new_session()

        print("🚀 Phase 2 AetherraCode & Neuroplex Enhancement Demo")
        print("=" * 60)

    def demo_stability_system(self):
        """Demonstrate the stability and error handling system"""
        print("\n🛡️ STABILITY & ERROR HANDLING DEMO")
        print("-" * 40)

        # Demo 1: Safe execution with retry
        print("1. Safe Execution with Automatic Retry:")

        @safe_execute(
            component="demo_operation",
            user_message="Demo operation encountered an issue",
            severity=ErrorSeverity.MEDIUM,
            max_retries=3,
        )
        def flaky_operation(failure_rate=0.7):
            """Simulates an operation that sometimes fails"""
            import random

            if random.random() < failure_rate:
                raise Exception("Simulated network timeout")
            return "Operation completed successfully!"

        # Try the flaky operation
        with stability_context("demo", "flaky network operation"):
            result = flaky_operation(0.3)  # 30% failure rate
            print(f"   Result: {result}")

        # Demo 2: Circuit breaker pattern
        print("\n2. Circuit Breaker Pattern:")

        @safe_execute(component="unreliable_service", max_retries=2)
        def unreliable_service():
            raise Exception("Service is down")

        # Try multiple times to trigger circuit breaker
        for i in range(7):
            result = unreliable_service()
            status = "Success" if result else "Failed/Blocked"
            print(f"   Attempt {i + 1}: {status}")

        # Demo 3: Graceful degradation
        print("\n3. Graceful Degradation:")
        print(
            f"   UI animations available: {degradation_manager.is_feature_available('ui', 'animations')}"
        )

        # Simulate performance issue
        performance_monitor.record_performance(
            "ui",
            {
                "response_time": 3.0,  # Above threshold
                "error_rate": 0.05,
            },
        )

        print(
            f"   After performance issue - animations: {degradation_manager.is_feature_available('ui', 'animations')}"
        )

        # Restore feature
        degradation_manager.restore_component("ui", "animations")
        print(
            f"   After restoration - animations: {degradation_manager.is_feature_available('ui', 'animations')}"
        )

    def demo_introspective_logging(self):
        """Demonstrate the introspective logging system"""
        print("\n🔍 INTROSPECTIVE LOGGING DEMO")
        print("-" * 40)

        # Demo 1: Log some AetherraCode executions
        print("1. Logging AetherraCode Executions:")

        # Simulate successful execution
        start_time = time.time()
        aethercode_1 = "think 'Hello, AetherraCode world!'"
        result_1 = "Hello, AetherraCode world!"
        execution_time_1 = time.time() - start_time

        reflection_id_1 = log_aethercode_execution(
            aethercode_1,
            result_1,
            execution_time_1,
            context={"user_intent": "greeting", "complexity": "simple"},
        )
        print(f"   Logged successful execution: {reflection_id_1}")

        # Simulate execution with error
        start_time = time.time()
        aethercode_2 = "calculate sqrt(-1)"
        result_2 = Exception("Math domain error: negative square root")
        execution_time_2 = time.time() - start_time

        reflection_id_2 = log_aethercode_execution(
            aethercode_2,
            result_2,
            execution_time_2,
            context={"user_intent": "calculation", "complexity": "error"},
        )
        print(f"   Logged failed execution: {reflection_id_2}")

        # Demo 2: Manual reflection logging
        print("\n2. Manual Activity Logging:")

        introspective_logger.log_execution(
            operation="plugin_discovery",
            code=None,
            result={"plugins_found": 5, "categories": ["utility", "development"]},
            activity_type=ActivityType.LEARNING,
            performance=PerformanceMetrics(execution_time=0.15),
            context={"search_query": "data analysis"},
        )
        print("   Logged plugin discovery activity")

        # Demo 3: Today's activity dashboard
        print("\n3. Today's Activity Dashboard:")
        dashboard = get_activity_dashboard()

        today_activity = dashboard["todays_activity"]
        print(f"   Total activities today: {today_activity['total_activities']}")
        print(f"   Success rate: {today_activity['success_rate']}%")
        print(f"   Summary: {today_activity['summary']}")

        if today_activity["insights"]:
            print("   Key insights:")
            for insight in today_activity["insights"][:3]:
                print(f"     • {insight}")

        # Demo 4: Auto-reflection
        print("\n4. Auto-Reflection Analysis:")
        reflection = dashboard["recent_reflection"]
        if "activities_analyzed" in reflection:
            print(f"   Analyzed {reflection['activities_analyzed']} recent activities")
            print(f"   Overall assessment: {reflection['overall_assessment']}")

            if reflection.get("optimization_suggestions"):
                print("   Optimization suggestions:")
                for suggestion in reflection["optimization_suggestions"][:2]:
                    print(f"     • {suggestion}")

    def demo_conversational_ai(self):
        """Demonstrate the conversational AI system with personas"""
        print("\n💬 CONVERSATIONAL AI DEMO")
        print("-" * 40)

        # Demo 1: Available personas
        print("1. Available AI Personas:")
        personas = get_available_personas()
        for persona in personas:
            print(f"   • {persona['name']}: {persona['description']}")

        # Demo 2: Context-aware responses
        print("\n2. Context-Aware Conversations:")

        # Technical coding question
        response1 = chat("How do I implement a binary search algorithm?")
        print(f"   Coding Query -> Persona: {response1['persona']}")
        print(f"   Context: {response1['context']}")
        print(f"   Response: {response1['response'][:80]}...")

        # Learning question
        response2 = chat("Can you explain how machine learning works?")
        print(f"   Learning Query -> Persona: {response2['persona']}")
        print(f"   Context: {response2['context']}")
        print(f"   Response: {response2['response'][:80]}...")

        # Creative question
        response3 = chat("Help me brainstorm ideas for a sci-fi story")
        print(f"   Creative Query -> Persona: {response3['persona']}")
        print(f"   Context: {response3['context']}")
        print(f"   Response: {response3['response'][:80]}...")

        # Demo 3: Manual persona switching
        print("\n3. Manual Persona Switching:")

        print("   Switching to Teacher persona...")
        switch_persona("teacher")

        response4 = chat("What is recursion?")
        print(f"   Teacher Response: {response4['response'][:80]}...")

        # Demo 4: Memory-driven responses
        print("\n4. Memory Integration:")
        print(
            f"   Memory context used in last response: {response4['memory_context_used']} memories"
        )

        if response4.get("follow_up_suggestions"):
            print("   Follow-up suggestions:")
            for suggestion in response4["follow_up_suggestions"]:
                print(f"     • {suggestion}")

        # Demo 5: Conversation summary
        print("\n5. Conversation Summary:")
        summary = conversational_ai.get_conversation_summary(days=1)
        print(f"   Total conversations today: {summary['total_conversations']}")
        if summary.get("primary_contexts"):
            print(f"   Primary context: {summary['primary_contexts'][0][0]}")

    def demo_plugin_registry(self):
        """Demonstrate the enhanced plugin registry system"""
        print("\n🔌 ENHANCED PLUGIN REGISTRY DEMO")
        print("-" * 40)

        # Demo 1: Plugin catalog overview
        print("1. Plugin Catalog Overview:")
        catalog = get_plugin_catalog()
        print(f"   Total plugins: {catalog['stats']['total_plugins']}")
        print(f"   Installed plugins: {catalog['stats']['installed_plugins']}")
        print(f"   Active plugins: {catalog['stats']['active_plugins']}")

        print("\n   Available categories:")
        for category, plugins in catalog["categories"].items():
            print(f"     • {category}: {len(plugins)} plugins")

        # Demo 2: Plugin search
        print("\n2. Plugin Search:")

        # Search for data analysis plugins
        data_plugins = search_plugins("data analysis", "data_analysis")
        print(f"   Found {len(data_plugins)} data analysis plugins")
        if data_plugins:
            for plugin in data_plugins[:2]:
                print(f"     • {plugin['name']}: {plugin['description'][:50]}...")

        # Search for UI plugins
        ui_plugins = search_plugins("theme", "ui_theme")
        print(f"   Found {len(ui_plugins)} UI theme plugins")
        if ui_plugins:
            for plugin in ui_plugins[:2]:
                print(f"     • {plugin['name']}: {plugin['description'][:50]}...")

        # Demo 3: Plugin suggestions
        print("\n3. Context-Based Plugin Suggestions:")

        coding_suggestions = get_plugin_suggestions("debugging Python code")
#         print(f"   Debugging context: {len(coding_suggestions)} suggestions")
        for suggestion in coding_suggestions[:2]:
            print(f"     • {suggestion['name']}: {suggestion['description'][:50]}...")

        analysis_suggestions = get_plugin_suggestions("data visualization and charts")
        print(f"   Data analysis context: {len(analysis_suggestions)} suggestions")
        for suggestion in analysis_suggestions[:2]:
            print(f"     • {suggestion['name']}: {suggestion['description'][:50]}...")

        # Demo 4: Simulated plugin installation
        print("\n4. Plugin Installation Simulation:")

        # Create a sample plugin entry
        if data_plugins:
            sample_plugin = data_plugins[0]
            plugin_id = sample_plugin["id"]

            print(f"   Installing plugin: {sample_plugin['name']}")

            # Simulate installation (would actually install in real system)
            success = True  # plugin_registry.install_plugin(plugin_id)
            if success:
                print("   ✅ Installation successful")

                # Track usage
                plugin_registry.track_plugin_usage(plugin_id, 0.25, success=True)
                print("   📊 Usage tracked")
            else:
                print("   ❌ Installation failed")

        # Demo 5: Plugin ratings simulation
        print("\n5. Plugin Rating System:")
        if data_plugins:
            plugin_id = data_plugins[0]["id"]

            # Simulate rating
            rating_success = plugin_registry.rate_plugin(
                plugin_id, 4.5, "Excellent plugin for data analysis!", "demo_user"
            )

            if rating_success:
                print(f"   ⭐ Rated plugin {data_plugins[0]['name']}: 4.5/5 stars")

                # Get updated metadata
                metadata = plugin_registry.available_plugins.get(plugin_id)
                if metadata:
                    print(f"   Average rating: {metadata.average_rating:.1f}/5")
                    print(f"   Total ratings: {metadata.total_ratings}")

    def demo_ui_integration(self):
        """Demonstrate UI integration with Phase 2 features"""
        print("\n🎨 UI INTEGRATION DEMO")
        print("-" * 40)

        # Demo 1: Theme with status indicators
        print("1. Enhanced UI Status Display:")

        # Show system status
        status_info = {
            "stability": "operational",
            "circuit_breakers": len(
                [cb for cb in stability_manager.circuit_breakers.values() if cb.state == "closed"]
            ),
            "active_plugins": len(plugin_registry.active_plugins),
            "current_persona": conversational_ai.current_persona.value,
            "degraded_features": len(
                [
                    f
                    for features in degradation_manager.current_degradations.values()
                    for f in features
                ]
            ),
        }

        print("   System Status:")
        for key, value in status_info.items():
            print(f"     • {key.replace('_', ' ').title()}: {value}")

        # Demo 2: Rich feedback with new systems
        print("\n2. Rich Feedback Integration:")

        # Simulate UI feedback for different scenarios
        print("   💭 AI Thinking (Introspective mode)...")
        print("   🔧 Plugin Loading...")
        print("   🛡️ Error Recovery in Progress...")
        print("   🎭 Persona Switch: Assistant → Developer")
        print("   📊 Activity Logging: Execution Reflected")

        # Demo 3: Command suggestions with context
        print("\n3. Context-Aware Command Suggestions:")

        suggestions = [
            "switch-persona developer",
            "analyze-activity today",
            "install-plugin data-viz",
            "get-suggestions 'debug python'",
            "view-circuit-breakers",
            "check-degradations",
        ]

        print("   Available commands based on current context:")
        for suggestion in suggestions:
            print(f"     • {suggestion}")

    def demo_integration_scenarios(self):
        """Demonstrate real-world integration scenarios"""
        print("\n🔗 INTEGRATION SCENARIOS DEMO")
        print("-" * 40)

        # Scenario 1: Error handling with logging and recovery
        print("1. Complete Error Handling Scenario:")

        @safe_execute(
            component="aethercode_parser",
            user_message="AetherraCode parsing failed",
            severity=ErrorSeverity.HIGH,
        )
        def parse_neurocode(code):
            if "invalid" in code:
                raise SyntaxError("Invalid AetherraCode syntax")
            return {"ast": "parsed_successfully", "nodes": 5}

        # Parse valid code
        valid_result = parse_neurocode("think 'hello world'")
        if valid_result:
            # Log successful execution
            introspective_logger.log_execution(
                operation="aethercode_parsing",
                code="think 'hello world'",
                result=valid_result,
                activity_type=ActivityType.EXECUTION,
                performance=PerformanceMetrics(execution_time=0.05),
            )
            print("   ✅ Valid code parsed and logged")

        # Parse invalid code (triggers error handling)
        invalid_result = parse_neurocode("invalid syntax here")
        if not invalid_result:
            print("   ❌ Invalid code handled gracefully")

        # Scenario 2: Persona-based plugin suggestions
        print("\n2. Persona-Based Plugin Recommendations:")

        # Switch to developer persona
        conversational_ai.set_persona(PersonaMode.DEVELOPER)
        print("   👨‍💻 Switched to Developer persona")

        # Get suggestions for coding context
        dev_suggestions = get_plugin_suggestions("debugging and code analysis")
        print(f"   🔌 Developer context suggestions: {len(dev_suggestions)} plugins")

        # Switch to analyst persona
        conversational_ai.set_persona(PersonaMode.ANALYST)
        print("   📊 Switched to Analyst persona")

        # Get suggestions for analysis context
        analyst_suggestions = get_plugin_suggestions("data visualization and statistics")
        print(f"   📈 Analyst context suggestions: {len(analyst_suggestions)} plugins")

        # Scenario 3: Activity reflection with persona insights
        print("\n3. Cross-System Activity Analysis:")

        # Get current activity
        dashboard = get_activity_dashboard()
        activity = dashboard["todays_activity"]

        # Generate persona-aware conversation about activity
        activity_summary = f"Today I completed {activity['total_activities']} activities with {activity['success_rate']}% success rate"

        response = conversational_ai.generate_response(
            f"Analyze my productivity: {activity_summary}"
        )

        print(f"   🤖 {response['persona']} analysis:")
        print(f"       {response['response'][:100]}...")

    def run_complete_demo(self):
        """Run the complete Phase 2 demonstration"""
        try:
            self.demo_stability_system()
            self.demo_introspective_logging()
            self.demo_conversational_ai()
            self.demo_plugin_registry()
            self.demo_ui_integration()
            self.demo_integration_scenarios()

            print("\n🎉 PHASE 2 DEMO COMPLETE!")
            print("=" * 60)
            print("\nPhase 2 Features Successfully Demonstrated:")
            print("✅ Stability & Error Handling with Circuit Breakers")
            print("✅ Introspective Logging & Activity Tracking")
            print("✅ Conversational AI with Multiple Personas")
            print("✅ Enhanced Plugin Registry with Discovery")
            print("✅ UI Integration with Rich Status Display")
            print("✅ Cross-System Integration Scenarios")

            # Final activity summary
            final_dashboard = get_activity_dashboard()
            final_activity = final_dashboard["todays_activity"]

            print("\n📊 Demo Session Summary:")
            print(f"    Activities logged: {final_activity['total_activities']}")
            print(f"    Success rate: {final_activity['success_rate']}%")
            print(f"    Current persona: {conversational_ai.current_persona.value}")

            # End conversation session
            session_summary = conversational_ai.end_current_session()
            if session_summary:
                print(
                    f"    Conversation session: {session_summary['conversation_count']} exchanges"
                )

        except Exception as e:
            print(f"\n❌ Demo encountered an error: {e}")
            print(f"Traceback: {traceback.format_exc()}")

            # Even in error, log the execution
            introspective_logger.log_execution(
                operation="phase2_demo",
                code=None,
                result=e,
                activity_type=ActivityType.ERROR_HANDLING,
                performance=PerformanceMetrics(execution_time=0.0),
            )


if __name__ == "__main__":
    # Create and run the comprehensive demo
    demo = Phase2Demo()
    demo.run_complete_demo()
