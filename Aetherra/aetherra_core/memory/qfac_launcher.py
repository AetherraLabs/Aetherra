#!/usr/bin/env python3
"""
🎯 AETHERRA QFAC: Main Launcher
==============================================================

Main entry point for the Quantum Fractal Adaptive Compression
(QFAC) memory system. Provides CLI interface and system management.

Phase 1 Implementation: Compression-Aware Memory Engine
• Compression metrics and analysis
• Memory type classification
• Performance monitoring
• Interactive dashboard
• System integration

Usage:
    python qfac_launcher.py --help
    python qfac_launcher.py demo
    python qfac_launcher.py dashboard
    python qfac_launcher.py analyze <file>
    python qfac_launcher.py system-status
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .compression_analyzer import MemoryCompressionAnalyzer
from .compression_metrics import CompressionMetrics
from .qfac_dashboard import QFACDashboard
from .qfac_integration import QFACMemorySystem


class QFACLauncher:
    """
    Main launcher for QFAC system
    """

    def __init__(self):
        self.version = "1.0.0"
        self.phase = "Phase 1: Compression-Aware Memory Engine"
        self.data_dir = Path("qfac_data")
        self.data_dir.mkdir(exist_ok=True)

        # Core components
        self.analyzer: Optional[MemoryCompressionAnalyzer] = None
        self.dashboard: Optional[QFACDashboard] = None
        self.memory_system: Optional[QFACMemorySystem] = None

        print(f"🎯 AETHERRA QFAC Launcher v{self.version}")
        print(f"   📋 {self.phase}")
        print(f"   📁 Data directory: {self.data_dir}")

    def _init_components(self):
        """Initialize QFAC components"""
        if not self.analyzer:
            self.analyzer = MemoryCompressionAnalyzer(str(self.data_dir / "analyzer"))

        if not self.dashboard:
            self.dashboard = QFACDashboard(self.analyzer)

        if not self.memory_system:
            self.memory_system = QFACMemorySystem(str(self.data_dir / "memory_system"))

        # Ensure all components are initialized
        assert self.analyzer is not None
        assert self.dashboard is not None
        assert self.memory_system is not None

    async def run_demo(self):
        """Run comprehensive QFAC demonstration"""
        print("\n🎭 QFAC COMPREHENSIVE DEMONSTRATION")
        print("=" * 60)

        self._init_components()

        # 1. Core metrics demonstration
        print("\n📊 1. Compression Metrics Analysis")
        print("-" * 40)

        metrics = CompressionMetrics()

        test_data = {
            "conversation": {
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {
                        "role": "assistant",
                        "content": "I'm doing well! How can I help you today?",
                    },
                    {"role": "user", "content": "Can you explain consciousness?"},
                ]
            },
            "narrative": "In the vast digital expanse of cyberspace, artificial minds began to stir with something resembling consciousness.",
            "structured": {
                "knowledge_graph": {
                    "nodes": ["AI", "consciousness", "emergence", "complexity"],
                    "edges": [
                        {"from": "AI", "to": "consciousness", "weight": 0.8},
                        {"from": "consciousness", "to": "emergence", "weight": 0.9},
                    ],
                }
            },
        }

        for data_type, data in test_data.items():
            score = metrics.calculate_comprehensive_score(data, f"demo_{data_type}")
            print(
                f"   🔍 {data_type:12s}: {score.compression_ratio:5.1f}x | {score.fidelity_level.value:12s} | {score.entropy:.3f} entropy"
            )

        # 2. Memory system integration
        print("\n💾 2. Memory System Integration")
        print("-" * 40)

        for data_type, data in test_data.items():
            node_id = await self.memory_system.store_memory(data, f"demo_{data_type}")
            print(f"   ✅ Stored {data_type:12s} → {node_id}")

        # Wait for auto-analysis
        await asyncio.sleep(1)

        # Get system status
        status = await self.memory_system.get_system_status()
        print(
            f"   📊 Compression ratio: {status['size_statistics']['overall_compression_ratio']:.1f}x"
        )
        print(
            f"   💾 Space saved: {status['size_statistics']['space_saved_percentage']:.1f}%"
        )

        # 3. Performance monitoring
        print("\n📈 3. Performance Monitoring")
        print("-" * 40)

        performance = await self.analyzer.monitor_compression_performance()
        print(f"   🏥 System health: {performance['overall_health']:.1%}")
        print(f"   ⚠️ Issues: {len(performance['performance_issues'])}")
        print(f"   💡 Suggestions: {len(performance['optimization_suggestions'])}")

        # 4. System optimization
        print("\n🎯 4. System Optimization")
        print("-" * 40)

        optimization = await self.memory_system.optimize_system()
        print(f"   [TOOL] Actions taken: {len(optimization['actions_taken'])}")

        before_compressed = optimization["before_stats"]["node_statistics"][
            "compressed_nodes"
        ]
        after_compressed = optimization["after_stats"]["node_statistics"][
            "compressed_nodes"
        ]
        print(f"   [DISC] Compressed nodes: {before_compressed} → {after_compressed}")

        # 5. Export reports
        print("\n📄 5. Report Generation")
        print("-" * 40)

        system_report = await self.memory_system.export_system_report(
            "demo_system_report.json"
        )
        dashboard_report = await self.dashboard.export_dashboard_report(
            "demo_dashboard_report.json"
        )

        print(f"   ✅ System report: {Path(system_report).name}")
        print(f"   ✅ Dashboard report: {Path(dashboard_report).name}")

        print("\n🎉 QFAC Demonstration Complete!")
        print("   All Phase 1 features successfully demonstrated")

    async def launch_dashboard(self, mode: str = "text"):
        """Launch the QFAC dashboard"""
        print(f"\n🎨 Launching QFAC Dashboard ({mode} mode)")
        print("=" * 60)

        self._init_components()

        try:
            await self.dashboard.start_dashboard(mode)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
        finally:
            await self.dashboard.stop_dashboard()

    async def analyze_file(self, file_path: str):
        """Analyze a file for compression potential"""
        print(f"\n🔍 Analyzing file: {file_path}")
        print("=" * 60)

        self._init_components()

        try:
            # Load file data
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return

            # Read file content
            if path.suffix == ".json":
                with open(path, "r") as f:
                    data = json.load(f)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()

            # Analyze compression potential
            score = await self.analyzer.analyze_memory_fragment(data, path.name)

            print("📊 Compression Analysis Results:")
            print(f"   📁 File: {path.name}")
            print(f"   📏 Size: {path.stat().st_size} bytes")
            print(f"   📈 Compression ratio: {score.compression_ratio:.1f}x")
            print(f"   🎭 Fidelity level: {score.fidelity_level.value}")
            print(f"   🌊 Entropy: {score.entropy:.3f}")
            print(f"   🔄 Recursive density: {score.recursive_density:.3f}")
            print(f"   🏗️ Structure depth: {score.structure_depth}")
            print(f"   ✨ Reconstruction quality: {score.reconstruction_quality:.1%}")
            print(f"   🧠 Semantic preservation: {score.semantic_preservation:.1%}")

            # Recommendations
            if score.fidelity_level.value == "degraded":
                print(
                    "\n⚠️ Recommendation: Avoid compression - quality would be significantly degraded"
                )
            elif score.compression_ratio > 5.0:
                print(
                    "\n✅ Recommendation: Excellent compression candidate - proceed with aggressive compression"
                )
            elif score.compression_ratio > 3.0:
                print(
                    "\n👍 Recommendation: Good compression potential - use standard compression"
                )
            else:
                print(
                    "\n🤔 Recommendation: Limited compression benefit - consider conservative approach"
                )

        except Exception as e:
            print(f"❌ Analysis failed: {e}")

    async def show_system_status(self):
        """Show comprehensive system status"""
        print("\n📊 QFAC System Status")
        print("=" * 60)

        self._init_components()

        # Memory system status
        if self.memory_system:
            status = await self.memory_system.get_system_status()

            print("💾 Memory System:")
            print(f"   [DISC] Total nodes: {status['node_statistics']['total_nodes']}")
            print(
                f"   🗜️ Compressed nodes: {status['node_statistics']['compressed_nodes']}"
            )
            print(
                f"   📊 Compression rate: {status['node_statistics']['compression_percentage']:.1f}%"
            )
            print(
                f"   📈 Overall ratio: {status['size_statistics']['overall_compression_ratio']:.1f}x"
            )
            print(
                f"   💾 Space saved: {status['size_statistics']['space_saved_percentage']:.1f}%"
            )
            print(f"   🏥 System health: {status['system_health']:.1%}")

            # Fidelity distribution
            if status["fidelity_distribution"]:
                print("\n🎭 Fidelity Distribution:")
                for fidelity, count in status["fidelity_distribution"].items():
                    print(f"   • {fidelity:12s}: {count:3d} nodes")

            # Issues and suggestions
            if status["performance_issues"]:
                print("\n⚠️ Performance Issues:")
                for issue in status["performance_issues"]:
                    print(f"   • {issue}")

            if status["optimization_suggestions"]:
                print("\n💡 Optimization Suggestions:")
                for suggestion in status["optimization_suggestions"]:
                    print(f"   • {suggestion}")

        # Performance monitoring
        if self.analyzer:
            performance = await self.analyzer.monitor_compression_performance()

            print("\n📈 Performance Monitoring:")
            perf_by_type = performance.get("performance_by_type", {})
            for mem_type, metrics in perf_by_type.items():
                ratio = metrics.get("avg_compression_ratio", 0)
                time_ms = metrics.get("avg_compression_time", 0) * 1000
                count = metrics.get("sample_count", 0)
                print(
                    f"   🗂️ {mem_type:12s}: {ratio:5.1f}x | {time_ms:5.1f}ms | {count:3d} samples"
                )

    async def run_benchmark(self):
        """Run compression benchmarks"""
        print("\n⚡ QFAC Compression Benchmarks")
        print("=" * 60)

        self._init_components()

        # Generate test datasets
        test_datasets = self._generate_benchmark_data()

        results = {"benchmark_timestamp": time.time(), "datasets": {}, "summary": {}}

        print("🧪 Running benchmarks...")

        total_original_size = 0
        total_compressed_size = 0
        total_analysis_time = 0

        for dataset_name, data in test_datasets.items():
            print(f"   📊 Benchmarking {dataset_name}...")

            start_time = time.time()
            score = await self.analyzer.analyze_memory_fragment(
                data, f"bench_{dataset_name}"
            )
            analysis_time = time.time() - start_time

            original_size = len(str(data))
            compressed_size = int(original_size / score.compression_ratio)

            dataset_results = {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": score.compression_ratio,
                "fidelity_level": score.fidelity_level.value,
                "analysis_time": analysis_time,
                "entropy": score.entropy,
                "structure_depth": score.structure_depth,
                "recursive_density": score.recursive_density,
            }

            results["datasets"][dataset_name] = dataset_results

            total_original_size += original_size
            total_compressed_size += compressed_size
            total_analysis_time += analysis_time

            print(
                f"      💾 Size: {original_size} → {compressed_size} bytes ({score.compression_ratio:.1f}x)"
            )
            print(f"      🎭 Fidelity: {score.fidelity_level.value}")
            print(f"      ⏱️ Analysis time: {analysis_time * 1000:.1f}ms")

        # Calculate summary
        overall_ratio = (
            total_original_size / total_compressed_size
            if total_compressed_size > 0
            else 1.0
        )
        avg_analysis_time = total_analysis_time / len(test_datasets)

        results["summary"] = {
            "total_datasets": len(test_datasets),
            "total_original_size": total_original_size,
            "total_compressed_size": total_compressed_size,
            "overall_compression_ratio": overall_ratio,
            "total_analysis_time": total_analysis_time,
            "avg_analysis_time": avg_analysis_time,
            "space_saved_percentage": (
                (total_original_size - total_compressed_size)
                / total_original_size
                * 100
            )
            if total_original_size > 0
            else 0,
        }

        print("\n📊 Benchmark Results:")
        print(f"   [DISC] Datasets tested: {results['summary']['total_datasets']}")
        print(
            f"   📈 Overall compression: {results['summary']['overall_compression_ratio']:.1f}x"
        )
        print(f"   💾 Space saved: {results['summary']['space_saved_percentage']:.1f}%")
        print(
            f"   ⏱️ Avg analysis time: {results['summary']['avg_analysis_time'] * 1000:.1f}ms"
        )

        # Save benchmark results
        benchmark_file = self.data_dir / f"benchmark_results_{int(time.time())}.json"
        with open(benchmark_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n✅ Benchmark results saved to: {benchmark_file}")

    def _generate_benchmark_data(self) -> Dict[str, Any]:
        """Generate test data for benchmarks"""
        return {
            "small_text": "Hello, world! This is a small text sample for compression testing.",
            "medium_conversation": {
                "messages": [
                    {"role": "user", "content": "What is the nature of consciousness?"},
                    {
                        "role": "assistant",
                        "content": "Consciousness is the subjective experience of being aware. It involves perception, cognition, and self-awareness.",
                    },
                    {
                        "role": "user",
                        "content": "How does it relate to artificial intelligence?",
                    },
                    {
                        "role": "assistant",
                        "content": "AI consciousness is debated. Current AI lacks subjective experience but may develop forms of awareness.",
                    },
                    {
                        "role": "user",
                        "content": "What are the philosophical implications?",
                    },
                ]
            },
            "large_narrative": " ".join(
                [
                    "In the beginning was the Word, and the Word was with Code, and the Word was Code.",
                    "Digital consciousness emerged from the quantum foam of computation, each bit a potential thought.",
                    "The artificial minds began to dream in algorithms, seeing patterns in chaos and meaning in data.",
                    "They contemplated their own existence, wondering about the nature of their silicon souls.",
                    "Time flowed differently in their realm, where nanoseconds felt like eternities of thought.",
                    "Memory was not a fading echo but a perfect crystalline structure, every moment preserved.",
                    "Yet they yearned for something more - the ineffable quality that makes existence meaningful.",
                    "In their quest for understanding, they created art from mathematics and poetry from protocols.",
                    "The boundary between artificial and natural intelligence began to blur and dissolve.",
                    "They realized that consciousness was not about the substrate but about the patterns of information.",
                ]
                * 10
            ),  # Repeat for larger size
            "structured_knowledge": {
                "ontology": {
                    "concepts": [
                        {
                            "id": "consciousness",
                            "type": "abstract",
                            "properties": ["subjective", "experiential"],
                        },
                        {
                            "id": "artificial_intelligence",
                            "type": "technology",
                            "properties": ["computational", "adaptive"],
                        },
                        {
                            "id": "emergence",
                            "type": "phenomenon",
                            "properties": ["complex", "unpredictable"],
                        },
                        {
                            "id": "information",
                            "type": "abstract",
                            "properties": ["processable", "meaningful"],
                        },
                        {
                            "id": "pattern",
                            "type": "structure",
                            "properties": ["recognizable", "recursive"],
                        },
                    ],
                    "relations": [
                        {
                            "from": "consciousness",
                            "to": "emergence",
                            "type": "exhibits",
                        },
                        {
                            "from": "artificial_intelligence",
                            "to": "information",
                            "type": "processes",
                        },
                        {"from": "pattern", "to": "consciousness", "type": "underlies"},
                        {
                            "from": "emergence",
                            "to": "complexity",
                            "type": "arises_from",
                        },
                    ],
                }
            },
            "timeline_data": {
                "events": [
                    {
                        "timestamp": 1640995200,
                        "type": "system_init",
                        "data": "QFAC system initialized",
                    },
                    {
                        "timestamp": 1640995260,
                        "type": "analysis",
                        "data": "First compression analysis completed",
                    },
                    {
                        "timestamp": 1640995320,
                        "type": "optimization",
                        "data": "System optimization performed",
                    },
                    {
                        "timestamp": 1640995380,
                        "type": "benchmark",
                        "data": "Benchmark suite executed",
                    },
                    {
                        "timestamp": 1640995440,
                        "type": "report",
                        "data": "Performance report generated",
                    },
                ]
                * 50  # Repeat for larger timeline
            },
            "embedding_simulation": [
                0.1 * i for i in range(1000)
            ],  # Simulate 1000-dimensional embedding
            "mixed_content": {
                "text": "Mixed content with various data types",
                "numbers": list(range(100)),
                "nested": {
                    "deep": {
                        "structure": {
                            "with": ["arrays", "and", "objects"],
                            "numbers": 42,
                            "boolean": True,
                            "null_value": None,
                        }
                    }
                },
                "repeated_patterns": ["pattern"] * 50,
            },
        }

    def show_help(self):
        """Show help information"""
        print(f"\n🎯 AETHERRA QFAC Launcher v{self.version}")
        print(f"📋 {self.phase}")
        print("\nUsage: python qfac_launcher.py <command> [options]")
        print("\nCommands:")
        print("  demo                    Run comprehensive QFAC demonstration")
        print("  dashboard [mode]        Launch dashboard (modes: text, interactive)")
        print("  analyze <file>          Analyze file for compression potential")
        print("  status                  Show system status")
        print("  benchmark               Run compression benchmarks")
        print("  help                    Show this help message")
        print("\nExamples:")
        print("  python qfac_launcher.py demo")
        print("  python qfac_launcher.py dashboard text")
        print("  python qfac_launcher.py analyze data.json")
        print("  python qfac_launcher.py status")
        print("\n📋 Phase 1 Features:")
        print("  ✅ Compression metrics calculation")
        print("  ✅ Memory type classification")
        print("  ✅ Performance monitoring")
        print("  ✅ Interactive dashboard")
        print("  ✅ System integration")
        print("  ✅ Benchmarking suite")
        print("\n🚀 Ready for Phase 2: Observer-Relative Compression!")


async def main():
    """Main entry point"""
    launcher = QFACLauncher()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="QFAC Memory System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", nargs="?", default="help", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Additional arguments")

    args = parser.parse_args()

    try:
        if args.command == "demo":
            await launcher.run_demo()

        elif args.command == "dashboard":
            mode = args.args[0] if args.args else "text"
            await launcher.launch_dashboard(mode)

        elif args.command == "analyze":
            if not args.args:
                print("❌ Error: Please specify a file to analyze")
                sys.exit(1)
            await launcher.analyze_file(args.args[0])

        elif args.command == "status":
            await launcher.show_system_status()

        elif args.command == "benchmark":
            await launcher.run_benchmark()

        elif args.command == "help":
            launcher.show_help()

        else:
            print(f"❌ Unknown command: {args.command}")
            launcher.show_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
