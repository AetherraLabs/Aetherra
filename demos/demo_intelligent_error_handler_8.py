#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[TOOL] Intelligent Error Handling Demo (#8)
=======================================

Demonstration of Lyrixa's Intelligent Error Handling system
with AI-powered diagnosis, automatic corrections, and learning capabilities.
"""

# Standard library imports
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Third party imports
from intelligent_error_handler_8 import (
    LyrixaIntelligentErrorHandler,
    error_monitor,
    get_global_error_handler,
)


class MockAnalyticsEngine:
    """Mock analytics engine for demonstration"""

    def __init__(self):
        self.metrics = []

    async def collect_metrics(self, metrics):
        """Mock metrics collection"""
        self.metrics.append(metrics)
        print(f"📊 Analytics: {metrics}")


    def create_test_errors():
    """Create various test errors for demonstration"""

    test_errors = []

    # Plugin import error
    try:
        # Third party imports
        import nonexistent_plugin_module  # noqa: F401
    except ImportError as e:
        test_errors.append(("Plugin Import Error", e))

    # Permission error simulation
    try:
        raise PermissionError("Permission denied: Access to protected resource")
    except PermissionError as e:
        test_errors.append(("Permission Error", e))

    # Syntax error simulation
    try:
        # Simulate syntax error without using exec() for security
        compile("def broken_function(\n    pass", "<demo>", "exec")
    except SyntaxError as e:
        test_errors.append(("Syntax Error", e))

    # Memory error simulation
    try:
        raise MemoryError("Cannot allocate memory: System resources exhausted")
    except MemoryError as e:
        test_errors.append(("Memory Error", e))

    # Network timeout simulation
    try:
        raise TimeoutError("Connection timed out: Server did not respond")
    except TimeoutError as e:
        test_errors.append(("Network Timeout", e))

    # Generic runtime error
    try:
        _ = 10 / 0  # Division by zero
    except ZeroDivisionError as e:
        test_errors.append(("Runtime Error", e))

    return test_errors


@error_monitor
async def monitored_function_async():
    """Example async function with error monitoring"""
    print("[TOOL] Testing async function with error monitoring...")
    raise ValueError("This is a test error in an async monitored function")


@error_monitor
def monitored_function_sync():
    """Example sync function with error monitoring"""
    print("[TOOL] Testing sync function with error monitoring...")
    raise RuntimeError("This is a test error in a sync monitored function")


async def demo_intelligent_error_handling():
    """Demonstrate Intelligent Error Handling capabilities"""

    print("[TOOL] LYRIXA INTELLIGENT ERROR HANDLING DEMO (#8)")
    print("=" * 50)
    print("Advanced features:")
    print("• Self-Correction Logic for Plugin Errors")
    print("• Real-time Plugin Execution Monitoring")
    print("• AI-powered Error Diagnosis and Fix Suggestions")
    print("• Auto-application of Corrections with User Confirmation")
    print("• Learning from Correction Patterns to Prevent Future Errors")
    print()

    # Initialize intelligent error handler
    analytics_engine = MockAnalyticsEngine()

    error_handler = LyrixaIntelligentErrorHandler(analytics_engine=analytics_engine)

    print("🎯 INTELLIGENT ERROR HANDLING DEMONSTRATION")
    print("-" * 40)

    # Create test errors
    test_errors = create_test_errors()

    for i, (error_name, error) in enumerate(test_errors, 1):
        print(f"\n🚨 Test Case {i}: {error_name}")
        print("-" * 30)
        print(f"Error: {error}")

        # Handle the error with intelligent system
        result = await error_handler.handle_error(
            error=error,
            context={
                "test_case": error_name,
                "demo_mode": True,
                "user_id": "demo_user",
            },
            user_id="demo_user",
        )

        # Display results
        print(f"[OK] Handled: {result['handled']}")
        print(f"[TOOL] Corrected: {result.get('corrected', False)}")
        print(f"📋 Strategy: {result.get('strategy_applied', 'None')}")
        print(f"📊 Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"💬 Message: {result.get('user_message', 'No message')}")

        # Small delay for demonstration
        await asyncio.sleep(0.5)

    print("\n🎮 FUNCTION MONITORING DEMONSTRATION")
    print("-" * 35)

    # Test the error monitoring decorator
    try:
        await monitored_function_async()
    except ValueError:
        print("[OK] Async monitored function error was handled")

    try:
        monitored_function_sync()
    except RuntimeError:
        print("[OK] Sync monitored function error was handled")

    print("\n📊 ERROR HANDLING STATISTICS")
    print("-" * 25)

    stats = error_handler.get_error_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        elif isinstance(value, list):
            print(f"{key}: {len(value)} items")
        else:
            print(f"{key}: {value}")

    print(f"\n📈 Analytics Engine: {len(analytics_engine.metrics)} metric events")

    # Demonstrate pattern learning
    print("\n🧠 PATTERN LEARNING DEMONSTRATION")
    print("-" * 30)

    # Simulate the same error multiple times to show learning
    for i in range(3):
        print(f"\nSimulating repeat error #{i + 1}...")
        try:
            raise ImportError("No module named 'repeated_test_plugin'")
        except ImportError as e:
            result = await error_handler.handle_error(
                error=e, context={"repeat_test": True}, user_id="pattern_demo_user"
            )
            print(
                f"Pattern recognition: {'Yes' if 'pattern' in str(result.get('strategy_applied', '')) else 'Learning...'}"
            )

    print("\n🔄 SELF-CORRECTION DEMONSTRATION")
    print("-" * 28)

    # Demonstrate auto-correction capabilities
    print("Simulating correctable errors...")

    class CorrectableError(Exception):
        """A custom error that can be auto-corrected"""

        pass

    try:
        raise CorrectableError("This is a correctable test error")
    except CorrectableError as e:
        result = await error_handler.handle_error(
            error=e, context={"auto_correctable": True}, user_id="correction_demo_user"
        )
        print(f"Auto-correction result: {result.get('corrected', False)}")

    print("\n" + "=" * 50)
    print("📊 FINAL INTELLIGENT ERROR HANDLING STATISTICS")
    print("-" * 40)

    final_stats = error_handler.get_error_statistics()
    print("\nCore Metrics:")
    print(f"  Total Errors Handled: {final_stats['total_errors_handled']}")
    print(f"  Auto-Corrections: {final_stats['successful_auto_corrections']}")
    print(f"  Suggestions Made: {final_stats['successful_suggestions']}")
    print(f"  Pattern Matches: {final_stats['pattern_matches']}")
    print(f"  Learned Patterns: {final_stats['learned_patterns']}")

    print("\nSystem Health:")
    print(
        f"  Auto-Correction: {'Enabled' if final_stats['auto_correction_enabled'] else 'Disabled'}"
    )
    print(f"  Learning: {'Enabled' if final_stats['learning_enabled'] else 'Disabled'}")
    print(f"  Average Success Rate: {final_stats['average_success_rate']:.2f}")

    print("\nMost Common Errors:")
    for error_info in final_stats["most_common_errors"]:
        print(
            f"  • {error_info['signature'][:50]}... ({error_info['occurrences']} times)"
        )

    print("\n[OK] Intelligent Error Handling Demo Complete!")
    print("🚀 Ready for production integration with:")
    print("   • Real-time plugin monitoring")
    print("   • AI-powered error diagnosis")
    print("   • Automatic correction application")
    print("   • Pattern learning and improvement")
    print("   • User communication through Enhanced Conversational AI")


async def interactive_error_handler_demo():
    """Interactive demo for testing Intelligent Error Handling"""

    print("\n🎮 INTERACTIVE ERROR HANDLER MODE")
    print("=" * 35)
    print("Commands:")
    print("  trigger [error_type] - Trigger a specific error type")
    print("  stats - Show error handling statistics")
    print("  patterns - Show learned error patterns")
    print("  cleanup - Clean up old error records")
    print("  exit - Exit interactive mode")
    print()

    # Initialize
    error_handler = get_global_error_handler()

    while True:
        try:
            user_input = input("\n[TOOL] Command: ").strip().lower()

            if user_input in ["exit", "quit"]:
                print("👋 Intelligent Error Handler demo session ended.")
                break

            if user_input == "stats":
                stats = error_handler.get_error_statistics()
                print("\n📊 Current Error Handler Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue

            if user_input == "patterns":
                stats = error_handler.get_error_statistics()
                patterns = stats.get("most_common_errors", [])
                print(f"\n🧠 Learned Error Patterns ({len(patterns)}):")
                for pattern in patterns:
                    print(f"  • {pattern['signature'][:60]}...")
                    print(
                        f"    Occurrences: {pattern['occurrences']}, Success Rate: {pattern['success_rate']:.2f}"
                    )
                continue

            if user_input == "cleanup":
                await error_handler.cleanup_old_errors(max_age_hours=1)
                print("🧹 Cleaned up old error records")
                continue

            if user_input.startswith("trigger "):
                error_type = user_input.split(" ", 1)[1]

                # Trigger different types of errors
                try:
                    if error_type == "import":
                        # Third party imports
                        import nonexistent_plugin_module  # noqa: F401
                    elif error_type == "permission":
                        raise PermissionError("Simulated permission error")
                    elif error_type == "syntax":
                        # Simulate syntax error without using exec() for security
                        compile("invalid syntax here", "<demo>", "exec")
                    elif error_type == "memory":
                        raise MemoryError("Simulated memory error")
                    elif error_type == "network":
                        raise TimeoutError("Simulated network timeout")
                    elif error_type == "runtime":
                        result = 1 / 0
                    else:
                        raise ValueError(f"Unknown error type: {error_type}")

                except Exception as e:
                    result = await error_handler.handle_error(
                        e, {"interactive": True}, "interactive_user"
                    )
                    print(f"\n[TOOL] Error handled: {result['handled']}")
                    print(f"   Strategy: {result.get('strategy_applied', 'None')}")
                    print(f"   Corrected: {result.get('corrected', False)}")

                continue

            print(
                "❓ Unknown command. Type 'exit' to quit or see available commands above."
            )

        except KeyboardInterrupt:
            print("\n\n👋 Interactive session interrupted.")
            break
        except Exception as e:
            print(f"\n❌ Command error: {e}")


if __name__ == "__main__":
    print("[TOOL] LYRIXA INTELLIGENT ERROR HANDLING (#8)")
    print("Roadmap Item #8: Intelligent Error Handling Implementation")
    print()

    # Run demo
    asyncio.run(demo_intelligent_error_handling())

    # Offer interactive mode
    try:
        choice = (
            input("\n🎮 Would you like to try interactive mode? (y/n): ")
            .strip()
            .lower()
        )
        if choice in ["y", "yes"]:
            asyncio.run(interactive_error_handler_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo session ended.")
