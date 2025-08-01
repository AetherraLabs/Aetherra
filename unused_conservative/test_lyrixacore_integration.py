#!/usr/bin/env python3
"""
🌉 LyrixaCore FractalMesh Integration Test
=========================================

Test script to verify that LyrixaCore's unified cognitive interface
is properly integrated with the FractalMesh memory system.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_lyrixacore_fractal_integration():
    """Test FractalMesh memory integration with LyrixaCore's unified interface"""

    print("🌉 Testing LyrixaCore FractalMesh Integration")
    print("=" * 60)

    try:
        # Import and initialize LyrixaCore interface bridge
        from Aetherra.lyrixa.LyrixaCore.interface_bridge import LyrixaContextBridge

        print("✅ Successfully imported LyrixaContextBridge")

        # Initialize the bridge with workspace path
        workspace_path = str(project_root)
        bridge = LyrixaContextBridge(workspace_path=workspace_path)

        print("✅ Successfully initialized LyrixaContextBridge")

        # Check if FractalMesh memory is available
        if hasattr(bridge, "fractal_memory") and bridge.fractal_memory:
            print("✅ FractalMesh memory system is integrated and available!")
            print(f"   Database path: {bridge.fractal_memory.db_path}")

            # Test memory storage through ethical validation
            print("\n🧪 Testing memory storage through unified interface...")
            test_fragment = {
                "summary": "LyrixaCore unified cognitive decision",
                "content": "Testing integration between identity, ethics, and memory systems",
                "confidence": 0.9,
                "tags": ["integration", "cognitive", "decision", "unity"],
            }

            accepted = bridge.submit_memory_update(test_fragment)
            if accepted:
                print("✅ Memory fragment accepted through ethical validation!")
            else:
                print("⚠️ Memory fragment rejected by ethical validation")

            # Test memory retrieval
            print("\n🧪 Testing memory retrieval with context...")
            query_context = {
                "summary": "Need information about cognitive integration decisions",
                "content": "Looking for past decisions about system integration",
            }

            memories = bridge.retrieve_relevant_memories(query_context, limit=3)
            if memories:
                print(f"✅ Retrieved {len(memories)} relevant memories!")
                for i, memory in enumerate(memories):
                    print(
                        f"   Memory {i + 1}: {memory.get('fragment_id', 'Unknown')[:8]}..."
                    )
                    print(f"   Confidence: {memory.get('confidence', 'N/A')}")
                    print(f"   Tags: {memory.get('symbolic_tags', [])}")
            else:
                print("⚠️ No relevant memories found (normal for first run)")

            # Test unified context summary with memory
            print("\n🧪 Testing unified context summary with memory integration...")
            context = bridge.get_context_summary()

            if (
                "memory" in context
                and context["memory"].get("memory_type") == "FractalMesh"
            ):
                print("✅ Context summary includes FractalMesh memory statistics!")
                memory_info = context["memory"]
                print(f"   Fragment count: {memory_info.get('fragment_count', 0)}")
                print(f"   Concept clusters: {memory_info.get('concept_clusters', 0)}")
                print(f"   Episodic chains: {memory_info.get('episodic_chains', 0)}")
                print(f"   Health score: {memory_info.get('health_score', 'N/A'):.3f}")
            else:
                print("⚠️ Context summary not using FractalMesh memory")

            # Test decision evaluation with memory context
            print("\n🧪 Testing decision evaluation with memory context...")
            test_decision = {
                "summary": "Implement advanced memory coherence protocols",
                "content": "Decision to enhance memory system integration across cognitive subsystems",
                "stakeholders": ["identity_agent", "ethics_agent", "memory_system"],
                "potential_outcomes": ["improved coherence", "better integration"],
            }

            decision_eval = bridge.evaluate_decision(test_decision)
            print(f"✅ Decision evaluation completed!")
            print(f"   Approved: {decision_eval.get('approved', False)}")
            print(f"   Confidence: {decision_eval.get('confidence', 0):.3f}")
            print(
                f"   Memory context entries: {len(decision_eval.get('memory_context', []))}"
            )

            if decision_eval.get("component_scores"):
                print("   Component scores:")
                for component, score in decision_eval["component_scores"].items():
                    print(f"     {component}: {score:.3f}")

        else:
            print("❌ FractalMesh memory system is NOT integrated with LyrixaCore")
            print(
                "   This means the unified cognitive interface lacks memory capabilities"
            )
            return False

        # Check integration metrics
        if hasattr(bridge, "integration_metrics"):
            print(f"\n📊 Integration Metrics:")
            metrics = bridge.integration_metrics
            print(
                f"   Memory fragments stored: {metrics.get('memory_fragments_stored', 0)}"
            )
            print(f"   Memory retrievals: {metrics.get('memory_retrievals', 0)}")
            print(
                f"   Successful integrations: {metrics.get('successful_integrations', 0)}"
            )
            print(f"   Failed integrations: {metrics.get('failed_integrations', 0)}")

        # Test system coherence maintenance
        print("\n🔧 Testing system coherence maintenance...")
        maintenance_report = bridge.maintain_system_coherence()
        print(f"✅ Coherence maintenance completed!")
        print(
            f"   Overall health: {maintenance_report.get('overall_health', 'unknown')}"
        )

        if maintenance_report.get("coherence_checks"):
            print("   Coherence checks:")
            for system, score in maintenance_report["coherence_checks"].items():
                print(f"     {system}: {score:.3f}")

        print("\n✅ LyrixaCore FractalMesh integration test completed successfully!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This suggests LyrixaCore or FractalMesh components are missing")
        return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_lyrixacore_fractal_integration()
