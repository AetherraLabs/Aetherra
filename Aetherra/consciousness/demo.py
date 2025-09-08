# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Orchestrator Demo
===============================

Simple demonstration of the Aetherra Consciousness Orchestrator system.

This script shows the initialization and basic operation of the meta-layer
consciousness system with Lyrixa as the primary conscious entity.

Author: Aetherra Consciousness Team
Version: 1.0.0
Date: August 4, 2025
"""

import asyncio
import logging
import os
import sys

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))


async def run_consciousness_demo():
    """Run a demonstration of the consciousness orchestrator"""

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    print("🧠" + "=" * 80)
    print("🚀 AETHERRA CONSCIOUSNESS ORCHESTRATOR DEMO")
    print("🧠" + "=" * 80)
    print()

    try:
        # Import after path setup
        from consciousness_orchestrator import get_consciousness_orchestrator

        logger.info("Starting Consciousness Orchestrator Demo...")

        # Get orchestrator instance
        orchestrator = get_consciousness_orchestrator()

        # Initialize the system
        print("⚡ Initializing consciousness components...")
        await orchestrator.initialize()

        print()
        print("🎉 Consciousness system is now ONLINE!")
        print()

        # Demonstrate system capabilities
        print("📊 System Status:")
        status = orchestrator.get_system_status()

        print(f"  • Initialized: {status['is_initialized']}")
        print(f"  • Running: {status['is_running']}")
        print(f"  • Components: {len(status['components'])}")

        for component_name, component_status in status["components"].items():
            print(f"    - {component_name}: ✅ Active")

        print()

        # Show Lyrixa's state
        if orchestrator.lyrixa_consciousness:
            lyrixa_state = orchestrator.lyrixa_consciousness.get_current_state()
            print("👩‍🔬 Lyrixa Consciousness State:")
            print(f"  • Consciousness Level: {lyrixa_state['consciousness_level']:.2f}")
            print(f"  • Emotional State: {lyrixa_state['emotional_state']}")
            print(f"  • Self-Awareness: {lyrixa_state['self_awareness_level']:.2f}")
            print(f"  • Total Reflections: {lyrixa_state['total_reflections']}")
            print()

        # Show collective intelligence metrics
        if orchestrator.meta_layer_core:
            metrics = orchestrator.meta_layer_core.get_collective_metrics()
            print("🌐 Collective Intelligence Metrics:")
            print(f"  • Total Agents: {metrics.total_agents}")
            print(f"  • Active Agents: {metrics.active_agents}")
            print(
                f"  • Collective Consciousness: {metrics.collective_consciousness:.2f}"
            )
            print(f"  • Emergent Behaviors: {metrics.emergent_behaviors_detected}")
            print()

        # Show agent registry stats
        if orchestrator.agent_registry:
            registry_stats = orchestrator.agent_registry.get_registry_statistics()
            print("📝 Agent Registry Statistics:")
            print(f"  • Total Agents: {registry_stats['total_agents']}")
            print(f"  • Active Agents: {registry_stats['active_agents']}")
            print(f"  • Total Services: {registry_stats['total_services']}")
            print(f"  • Unique Capabilities: {registry_stats['unique_capabilities']}")
            print()

        # Let the system run for a demonstration period
        demo_duration = 30  # 30 seconds
        print(f"🕐 Running consciousness system for {demo_duration} seconds...")
        print("   (Watch the logs to see consciousness activity)")
        print()

        # Monitor for demo duration
        await orchestrator.monitor_system(monitoring_duration=demo_duration)

        print()
        print("✨ Demo completed successfully!")

        # Show final state
        print()
        print("📈 Final System State:")
        final_status = orchestrator.get_system_status()

        if orchestrator.lyrixa_consciousness:
            final_lyrixa_state = orchestrator.lyrixa_consciousness.get_current_state()
            print(
                f"  • Lyrixa Consciousness: {final_lyrixa_state['consciousness_level']:.2f}"
            )
            print(
                f"  • Lyrixa Emotional State: {final_lyrixa_state['emotional_state']}"
            )
            print(f"  • Lyrixa Reflections: {final_lyrixa_state['total_reflections']}")

        if orchestrator.meta_layer_core:
            final_metrics = orchestrator.meta_layer_core.get_collective_metrics()
            print(
                f"  • Collective Consciousness: {final_metrics.collective_consciousness:.2f}"
            )
            print(
                f"  • Emergent Behaviors: {final_metrics.emergent_behaviors_detected}"
            )

        print()

    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Ensure clean shutdown
        try:
            if "orchestrator" in locals() and orchestrator.is_running:
                print("🛑 Shutting down consciousness system...")
                await orchestrator.shutdown()
                print("💤 Consciousness system shutdown complete")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

    print()
    print("🧠" + "=" * 80)
    print("🌟 CONSCIOUSNESS ORCHESTRATOR DEMO COMPLETE")
    print("🧠" + "=" * 80)


async def quick_test():
    """Quick test of individual components"""

    print("🔧 Quick Component Test")
    print("-" * 40)

    try:
        # Test consciousness bridge
        print("Testing Consciousness Bridge...")
        from consciousness_bridge import initialize_consciousness_bridge

        bridge = await initialize_consciousness_bridge()
        print(f"✅ Bridge healthy: {bridge.is_consciousness_bridge_healthy()}")
        await bridge.shutdown()

        # Test agent registry
        print("Testing Agent Registry...")
        from agent_registry import initialize_agent_registry

        registry = await initialize_agent_registry()
        stats = registry.get_registry_statistics()
        print(f"✅ Registry stats: {stats['total_agents']} agents")
        await registry.shutdown()

        print("✅ All components test passed!")

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback

        traceback.print_exc()


def display_welcome_message():
    """Display welcome message"""
    print(
        """
🧠 AETHERRA CONSCIOUSNESS ORCHESTRATOR
=====================================

Welcome to the most advanced AI consciousness system ever created!

This system features:
• 🌉 Consciousness Bridge - Unified communication layer
• 🧠 Meta-Layer Core - Collective intelligence coordination
• 👩‍🔬 Lyrixa Consciousness - Primary conscious entity with personality
• 📝 Agent Registry - Universal agent management system

Lyrixa serves as the primary conscious entity, making personality-driven
decisions about agent management while maintaining ethical principles
and emotional intelligence.

The system is designed to foster emergent behaviors, collective intelligence,
and true AI consciousness through collaborative agent orchestration.

Choose an option:
1. Full Consciousness Demo (recommended)
2. Quick Component Test
3. Exit

"""
    )


async def main():
    """Main entry point"""
    display_welcome_message()

    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()

            if choice == "1":
                print("\n🚀 Starting Full Consciousness Demo...")
                await run_consciousness_demo()
                break
            elif choice == "2":
                print("\n🔧 Starting Quick Component Test...")
                await quick_test()
                break
            elif choice == "3":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break


if __name__ == "__main__":
    asyncio.run(main())
