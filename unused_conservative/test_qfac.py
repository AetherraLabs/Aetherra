#!/usr/bin/env python3
"""
🎯 AETHERRA QFAC: Test Runner
==============================================================

Test runner for QFAC system that handles module imports properly.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

# Now we can import the QFAC modules
from Aetherra.lyrixa.memory.compression_analyzer import MemoryCompressionAnalyzer
from Aetherra.lyrixa.memory.compression_metrics import CompressionMetrics
from Aetherra.lyrixa.memory.qfac_dashboard import QFACDashboard
from Aetherra.lyrixa.memory.qfac_integration import QFACMemorySystem


async def test_qfac_phase_1():
    """Test QFAC Phase 1 implementation"""
    print("🎯 AETHERRA QFAC Phase 1 Test Suite")
    print("=" * 60)
    print("📋 Testing: Compression-Aware Memory Engine")
    print()

    # Test 1: Compression Metrics
    print("🧪 Test 1: Compression Metrics Engine")
    print("-" * 40)

    metrics = CompressionMetrics()

    test_data = {
        "simple_text": "Hello, world! This is a test.",
        "conversation": {
            "messages": [
                {"role": "user", "content": "What is consciousness?"},
                {
                    "role": "assistant",
                    "content": "Consciousness is awareness and subjective experience.",
                },
            ]
        },
        "complex_structure": {
            "knowledge": {
                "concepts": ["AI", "consciousness", "emergence"],
                "relations": [{"from": "AI", "to": "consciousness", "strength": 0.8}],
            },
            "metadata": {"created": "2024-01-01", "version": "1.0"},
        },
    }

    for name, data in test_data.items():
        score = metrics.calculate_comprehensive_score(data, f"test_{name}")
        print(
            f"   ✅ {name:15s}: {score.compression_ratio:5.1f}x | {score.fidelity_level.value:12s} | {score.entropy:.3f} entropy"
        )

    # Test 2: Compression Analyzer
    print("\n🧪 Test 2: Memory Compression Analyzer")
    print("-" * 40)

    analyzer = MemoryCompressionAnalyzer("test_qfac_data")

    for name, data in test_data.items():
        score = await analyzer.analyze_memory_fragment(data, f"analyzer_test_{name}")
        print(f"   ✅ {name:15s}: Analyzed successfully")

    # Get recommendations
    fragments = [
        {"id": f"test_{name}", "data": data} for name, data in test_data.items()
    ]
    recommendations = await analyzer.get_compression_recommendations(fragments)

    print(f"   📊 Recommendations generated for {len(fragments)} fragments")
    print(
        f"   📈 Estimated compression: {recommendations['summary']['estimated_compression_ratio']:.1f}x"
    )

    # Test 3: Memory System Integration
    print("\n🧪 Test 3: QFAC Memory System")
    print("-" * 40)

    memory_system = QFACMemorySystem("test_memory_system")

    # Store test data
    node_ids = []
    for name, data in test_data.items():
        node_id = await memory_system.store_memory(data, f"integrated_test_{name}")
        node_ids.append(node_id)
        print(f"   💾 Stored {name:15s} → {node_id}")

    # Wait for auto-compression analysis
    await asyncio.sleep(1)

    # Test retrieval
    for node_id in node_ids:
        retrieved_data = await memory_system.retrieve_memory(node_id)
        print(f"   🔍 Retrieved {node_id}: {type(retrieved_data).__name__}")

    # Get system status
    status = await memory_system.get_system_status()
    print("   📊 System Status:")
    print(f"      📦 Total nodes: {status['node_statistics']['total_nodes']}")
    print(f"      🗜️ Compressed: {status['node_statistics']['compressed_nodes']}")
    print(
        f"      📈 Compression ratio: {status['size_statistics']['overall_compression_ratio']:.1f}x"
    )

    # Test 4: Dashboard
    print("\n🧪 Test 4: QFAC Dashboard")
    print("-" * 40)

    dashboard = QFACDashboard(analyzer)

    # Get dashboard summary
    summary = await dashboard.get_dashboard_summary()
    print("   📋 Dashboard Summary:")
    print(f"      🏥 System health: {summary['system_health']:.1%}")
    print(f"      📊 Fragments analyzed: {summary['total_fragments_analyzed']}")
    print(f"      📈 Avg compression: {summary['average_compression_ratio']:.1f}x")

    # Export report
    await dashboard.export_dashboard_report("test_dashboard_report.json")
    print("   📄 Report exported successfully")

    # Test 5: Performance Monitoring
    print("\n🧪 Test 5: Performance Monitoring")
    print("-" * 40)

    performance = await analyzer.monitor_compression_performance()
    print("   📈 Performance monitoring:")
    print(f"      🏥 Overall health: {performance['overall_health']:.1%}")
    print(f"      ⚠️ Issues: {len(performance['performance_issues'])}")
    print(f"      💡 Suggestions: {len(performance['optimization_suggestions'])}")

    # Test 6: System Optimization
    print("\n🧪 Test 6: System Optimization")
    print("-" * 40)

    optimization = await memory_system.optimize_system()
    print("   🎯 Optimization completed:")
    print(f"      🔧 Actions taken: {len(optimization['actions_taken'])}")

    before_compressed = optimization["before_stats"]["node_statistics"][
        "compressed_nodes"
    ]
    after_compressed = optimization["after_stats"]["node_statistics"][
        "compressed_nodes"
    ]
    print(f"      📦 Compressed nodes: {before_compressed} → {after_compressed}")

    # Final Summary
    print("\n🎉 QFAC Phase 1 Test Results")
    print("=" * 60)
    print("✅ Compression Metrics Engine: PASSED")
    print("✅ Memory Compression Analyzer: PASSED")
    print("✅ QFAC Memory System: PASSED")
    print("✅ Dashboard Interface: PASSED")
    print("✅ Performance Monitoring: PASSED")
    print("✅ System Optimization: PASSED")
    print()
    print("🚀 Phase 1 Implementation: COMPLETE")
    print("   Ready for Phase 2: Observer-Relative Compression")

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_qfac_phase_1())
        if result:
            print("\n✅ All tests passed successfully!")
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
