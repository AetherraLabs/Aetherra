"""
Demonstration of Phase 2: Self-Incorporation Logic with Aether Scripts

This demo shows Lyrixa's intelligent self-incorporation capabilities and
the generated Aether scripts for component integration.
"""

import json
from pathlib import Path


def demo_phase_2_results():
    """Demonstrate the results of Phase 2 Self-Incorporation"""
    print("🧠 LYRIXA AWAKENING - PHASE 2 DEMONSTRATION")
    print("=" * 60)
    print("✨ Self-Incorporation Logic Complete!")
    print()

    # Load the incorporation results
    results_path = Path(__file__).parent / "self_incorporation_results.json"

    if not results_path.exists():
        print("❌ Results file not found. Please run self_incorporator_agent.py first.")
        print(f"Looking for: {results_path}")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    # Display summary statistics
    print("📊 INCORPORATION SUMMARY:")
    print(
        f"   • Total Components Analyzed: {results['metadata']['total_candidates_analyzed']}"
    )
    print(
        f"   • Integration Attempts: {results['metadata']['total_integrations_attempted']}"
    )
    print(
        f"   • Successful Integrations: {results['summary']['successful_integrations']}"
    )
    print(f"   • Success Rate: {results['metadata']['success_rate']:.1%}")
    print()

    # Show new capabilities
    print("🚀 NEW CAPABILITIES ACQUIRED:")
    for capability in results["summary"]["new_capabilities"]:
        print(f"   ✅ {capability.replace('_', ' ').title()}")
    print()

    # Show successfully integrated components
    print("🔗 SUCCESSFULLY INTEGRATED COMPONENTS:")
    print("   (Top 10 examples)")
    for i, integration in enumerate(
        results["integration_results"]["successful"][:10], 1
    ):
        print(f"   {i:2d}. {integration['component']} - {integration['method']}")
    print()

    # Show memory connections
    print("🧠 MEMORY CONNECTIONS ESTABLISHED:")
    memory_connections = results["memory_connections"]
    for component, connection in list(memory_connections.items())[:8]:
        tags = ", ".join(connection["tags"])
        print(f"   • {component}: [{tags}]")
    print()

    # Show learned patterns
    print("📚 LEARNED INTEGRATION PATTERNS:")
    for pattern in results["learned_patterns"]:
        print(f"   • {pattern}")
    print()

    # Generate a sample Aether script
    print("⚡ SAMPLE AETHER INTEGRATION SCRIPT:")
    print("   (Generated automatically by Lyrixa)")
    print()

    # Select a successful integration for demo
    if results["integration_results"]["successful"]:
        sample_integration = results["integration_results"]["successful"][0]
        sample_script = generate_sample_aether_script(sample_integration)
        print(sample_script)

    print()
    print("🎯 PHASE 2 ACHIEVEMENTS:")
    print("   ✅ Intelligent component analysis")
    print("   ✅ Risk assessment and safety validation")
    print("   ✅ Automated integration planning")
    print("   ✅ Memory relevance scanning")
    print("   ✅ Self-documenting integration logs")
    print("   ✅ Aether script generation")
    print()
    print("🚀 READY FOR PHASE 3: Active Integration & Monitoring!")


def generate_sample_aether_script(integration):
    """Generate a sample Aether script for demonstration"""
    component_name = integration["component"]
    method = integration["method"]
    tags = ", ".join(integration["memory_tags"])

    script = f"""
# Generated Aether Integration Script
# Component: {component_name}
# Method: {method}
# Confidence: {integration["confidence"]}

goal: analyze "{component_name}"
plugin: summarize_code("{component_name}")

# Lyrixa's analysis complete
if not connected:
"""

    if method == "register_plugin":
        script += f"""    plugin: register_plugin("{component_name}")
    remember "{component_name}" as "active_plugin"
    memory_tag: add "{component_name}" to "plugin_registry"
"""
    elif method == "agent_collaboration":
        script += f"""    agent: connect_collaboration("{component_name}")
    remember "{component_name}" as "collaborative_agent"
    memory_tag: add "{component_name}" to "agent_network"
"""
    elif method == "memory_bridge":
        script += f"""    memory: create_bridge("{component_name}")
    remember "{component_name}" as "memory_extension"
    memory_tag: add "{component_name}" to "memory_bridges"
"""
    else:
        script += f"""    system: connect_component("{component_name}")
    remember "{component_name}" as "connected_component"
    memory_tag: add "{component_name}" to "integrated_components"
"""

    script += f"""
# Validation and feedback
validate: check_integration("{component_name}")
if integration_successful:
    log: "✅ Successfully integrated {component_name}"
    confidence: update "{component_name}" to "high"
    memory_tag: add_tags [{tags}]
else:
    log: "❌ Integration failed for {component_name}"
    fallback: revert_integration("{component_name}")
    confidence: update "{component_name}" to "failed"

# Self-reflection
reflect: "I have successfully incorporated {component_name} into my capabilities"
remember: "This integration enhances my {method.replace("_", " ")} abilities"
"""

    return script


def show_integration_analytics():
    """Show detailed analytics of the integration process"""
    results_path = Path(__file__).parent / "self_incorporation_results.json"

    if not results_path.exists():
        print("❌ Results file not found.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    print("\n📈 INTEGRATION ANALYTICS:")
    print("=" * 40)

    # Method distribution
    method_counts = {}
    for integration in results["integration_results"]["successful"]:
        method = integration["method"]
        method_counts[method] = method_counts.get(method, 0) + 1

    print("Integration Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method.replace('_', ' ').title()}: {count}")

    # Confidence distribution
    confidence_counts = {}
    for integration in results["integration_results"]["successful"]:
        confidence = integration["confidence"]
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

    print("\nConfidence Levels:")
    for confidence, count in confidence_counts.items():
        print(f"   • {confidence.title()}: {count}")

    # Failed integrations analysis
    if results["integration_results"]["failed"]:
        print(f"\nFailed Integrations: {len(results['integration_results']['failed'])}")
        for failure in results["integration_results"]["failed"]:
            print(f"   • {failure['component']}: {failure['reason']}")


if __name__ == "__main__":
    demo_phase_2_results()
    show_integration_analytics()
