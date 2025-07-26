#!/usr/bin/env python3
"""
🎯 AETHERRA QFAC: Dashboard Interface
==============================================================

Interactive dashboard for monitoring and controlling the
Quantum Fractal Adaptive Compression (QFAC) memory system.

Features:
• Real-time compression metrics visualization
• Memory type performance monitoring
• Interactive compression strategy adjustment
• Historical trend analysis
• System health monitoring
"""

import asyncio
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    pass  # Matplotlib availability check only
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️ Matplotlib not available - using text-based dashboard")

from .compression_analyzer import MemoryCompressionAnalyzer


class QFACDashboard:
    """
    Interactive dashboard for QFAC memory compression system
    """

    def __init__(self, analyzer: MemoryCompressionAnalyzer):
        self.analyzer = analyzer
        self.dashboard_data_dir = Path("qfac_dashboard_data")
        self.dashboard_data_dir.mkdir(exist_ok=True)

        # Dashboard state
        self.is_running = False
        self.refresh_interval = 5.0  # seconds

        # Visualization state
        self.figures = {}
        self.animations = {}

        print("🎯 QFAC Dashboard initialized")
        print(f"   📊 Matplotlib available: {HAS_MATPLOTLIB}")
        print(f"   🔄 Refresh interval: {self.refresh_interval}s")

    async def start_dashboard(self, mode: str = "interactive"):
        """
        Start the dashboard in specified mode

        Args:
            mode: "interactive", "text", or "web"
        """
        print(f"🚀 Starting QFAC Dashboard in {mode} mode...")

        self.is_running = True

        if mode == "interactive" and HAS_MATPLOTLIB:
            await self._start_interactive_dashboard()
        elif mode == "text":
            await self._start_text_dashboard()
        elif mode == "web":
            await self._start_web_dashboard()
        else:
            print("⚠️ Falling back to text mode")
            await self._start_text_dashboard()

    async def stop_dashboard(self):
        """Stop the dashboard"""
        print("🛑 Stopping QFAC Dashboard...")
        self.is_running = False

        # Stop animations
        for animation in self.animations.values():
            if hasattr(animation, "event_source"):
                animation.event_source.stop()

        # Close figures
        if HAS_MATPLOTLIB:
            import matplotlib.pyplot as plt

            plt.close("all")

    async def _start_interactive_dashboard(self):
        """Start interactive matplotlib dashboard"""
        if not HAS_MATPLOTLIB:
            print("⚠️ Matplotlib not available - falling back to text mode")
            await self._start_text_dashboard()
            return

        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        print("🎨 Launching interactive dashboard...")

        # Create dashboard layout
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(
            "🎯 AETHERRA QFAC: Memory Compression Dashboard",
            fontsize=16,
            fontweight="bold",
        )

        # Create subplots
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Compression ratio over time
        self.ax_compression_ratio = fig.add_subplot(gs[0, 0])
        self.ax_compression_ratio.set_title("📈 Compression Ratios by Memory Type")
        self.ax_compression_ratio.set_xlabel("Time")
        self.ax_compression_ratio.set_ylabel("Compression Ratio")

        # Fidelity distribution
        self.ax_fidelity = fig.add_subplot(gs[0, 1])
        self.ax_fidelity.set_title("🎭 Fidelity Distribution")

        # Performance metrics
        self.ax_performance = fig.add_subplot(gs[0, 2])
        self.ax_performance.set_title("⚡ Performance Metrics")

        # Memory type distribution
        self.ax_memory_types = fig.add_subplot(gs[1, 0])
        self.ax_memory_types.set_title("🗂️ Memory Type Distribution")

        # System health over time
        self.ax_health = fig.add_subplot(gs[1, 1:])
        self.ax_health.set_title("🏥 System Health Timeline")
        self.ax_health.set_xlabel("Time")
        self.ax_health.set_ylabel("Health Score")

        # Recent activity log
        self.ax_activity = fig.add_subplot(gs[2, :])
        self.ax_activity.set_title("📋 Recent Compression Activity")
        self.ax_activity.axis("off")

        # Store figure reference
        self.figures["main"] = fig

        # Start animation
        self.animations["main"] = FuncAnimation(
            fig,
            self._update_dashboard_plots,
            interval=int(self.refresh_interval * 1000),
            blit=False,
            cache_frame_data=False,
        )

        plt.show(block=False)

        # Keep dashboard running
        while self.is_running:
            await asyncio.sleep(self.refresh_interval)
            plt.pause(0.1)

    async def _start_text_dashboard(self):
        """Start text-based dashboard"""
        print("📺 Launching text dashboard...")

        while self.is_running:
            # Clear screen (Windows compatible)
            import os

            os.system("cls" if os.name == "nt" else "clear")

            # Display dashboard
            await self._display_text_dashboard()

            # Wait for next refresh
            await asyncio.sleep(self.refresh_interval)

    async def _start_web_dashboard(self):
        """Start web-based quantum dashboard"""
        print("🌐 Starting Quantum Web Dashboard...")

        try:
            # Import quantum web dashboard
            from .quantum_web_dashboard import QuantumWebDashboard

            # Check if we have a quantum-enhanced memory system
            quantum_engine = None
            if hasattr(self.analyzer, 'memory_system') and hasattr(self.analyzer.memory_system, 'quantum_available'):
                quantum_engine = self.analyzer.memory_system
                print("✅ Quantum-enhanced memory system detected")
            else:
                print("⚠️ Standard memory system - quantum features will show mock data")

            # Create and start web dashboard
            web_dashboard = QuantumWebDashboard(quantum_engine, port=8080)
            dashboard_url = await web_dashboard.start()

            print(f"� Quantum Web Dashboard started!")
            print(f"📱 Open in browser: {dashboard_url}")
            print(f"💡 Features:")
            print(f"   • Real-time quantum coherence monitoring")
            print(f"   • Quantum operation statistics")
            print(f"   • Performance comparison (classical vs quantum)")
            print(f"   • Interactive quantum circuit visualization")
            print(f"   • System health alerts and recommendations")
            print()
            print("Press Ctrl+C to stop the dashboard")

            # Keep the dashboard running
            try:
                while self.is_running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping web dashboard...")
                await web_dashboard.stop()

        except ImportError as e:
            print(f"❌ Cannot start web dashboard: {e}")
            print("🔄 Falling back to text mode...")
            await self._start_text_dashboard()
        except Exception as e:
            print(f"❌ Web dashboard error: {e}")
            print("🔄 Falling back to text mode...")
            await self._start_text_dashboard()

    async def _display_text_dashboard(self):
        """Display text-based dashboard"""
        print("🎯 AETHERRA QFAC: Memory Compression Dashboard")
        print("=" * 60)
        print(f"⏰ Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Get current performance data
        performance = await self.analyzer.monitor_compression_performance()

        # System health
        health = performance.get("overall_health", 0.0)
        health_bar = "█" * int(health * 20) + "▒" * (20 - int(health * 20))
        print(f"🏥 System Health: [{health_bar}] {health:.1%}")
        print()

        # Performance by memory type
        print("📊 Performance by Memory Type:")
        performance_by_type = performance.get("performance_by_type", {})

        for memory_type, metrics in performance_by_type.items():
            ratio = metrics.get("avg_compression_ratio", 0)
            time_ms = metrics.get("avg_compression_time", 0) * 1000
            count = metrics.get("sample_count", 0)

            print(
                f"   🗂️ {memory_type:12s}: {ratio:5.1f}x ratio | {time_ms:5.1f}ms | {count:3d} samples"
            )

        print()

        # Recent compression activity
        recent_data = await self._get_recent_activity()
        print("📋 Recent Compression Activity:")

        for i, activity in enumerate(recent_data[:5]):
            fragment_id = activity.get("fragment_id", "unknown")[:20]
            memory_type = activity.get("memory_type", "unknown")
            ratio = activity.get("compression_ratio", 0)
            fidelity = activity.get("fidelity_level", "unknown")

            print(
                f"   {i + 1}. {fragment_id:20s} | {memory_type:12s} | {ratio:5.1f}x | {fidelity}"
            )

        print()

        # Performance issues
        issues = performance.get("performance_issues", [])
        if issues:
            print("⚠️ Performance Issues:")
            for issue in issues:
                print(f"   • {issue}")
            print()

        # Optimization suggestions
        suggestions = performance.get("optimization_suggestions", [])
        if suggestions:
            print("💡 Optimization Suggestions:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
            print()

        # Controls
        print("🎛️ Controls: Ctrl+C to stop dashboard")
        print("=" * 60)

    def _update_dashboard_plots(self, frame):
        """Update dashboard plots (for matplotlib animation)"""
        if not self.is_running:
            return

        try:
            # This would be called by matplotlib animation
            # For now, just update the plots with current data
            asyncio.create_task(self._async_update_plots())
        except Exception as e:
            print(f"Error updating plots: {e}")

    async def _async_update_plots(self):
        """Async update for plots"""
        # Get current data
        performance = await self.analyzer.monitor_compression_performance()
        recent_data = await self._get_recent_activity()

        # Update compression ratio plot
        await self._update_compression_ratio_plot(performance)

        # Update fidelity distribution
        await self._update_fidelity_plot(recent_data)

        # Update performance metrics
        await self._update_performance_plot(performance)

        # Update memory type distribution
        await self._update_memory_type_plot(recent_data)

        # Update system health
        await self._update_health_plot(performance)

        # Update activity log
        await self._update_activity_plot(recent_data)

    async def _update_compression_ratio_plot(self, performance: Dict[str, Any]):
        """Update compression ratio plot"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_compression_ratio.clear()
        self.ax_compression_ratio.set_title("📈 Compression Ratios by Memory Type")
        self.ax_compression_ratio.set_ylabel("Compression Ratio")

        performance_by_type = performance.get("performance_by_type", {})
        memory_types = list(performance_by_type.keys())
        ratios = [
            metrics.get("avg_compression_ratio", 0)
            for metrics in performance_by_type.values()
        ]

        if memory_types and ratios:
            bars = self.ax_compression_ratio.bar(
                memory_types, ratios, color="skyblue", alpha=0.7
            )

            # Add value labels on bars
            for bar, ratio in zip(bars, ratios):
                height = bar.get_height()
                self.ax_compression_ratio.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.1,
                    f"{ratio:.1f}x",
                    ha="center",
                    va="bottom",
                )

        self.ax_compression_ratio.tick_params(axis="x", rotation=45)

    async def _update_fidelity_plot(self, recent_data: List[Dict[str, Any]]):
        """Update fidelity distribution plot"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_fidelity.clear()
        self.ax_fidelity.set_title("🎭 Fidelity Distribution")

        # Count fidelity levels
        fidelity_counts = {}
        for item in recent_data:
            fidelity = item.get("fidelity_level", "unknown")
            fidelity_counts[fidelity] = fidelity_counts.get(fidelity, 0) + 1

        if fidelity_counts:
            labels = list(fidelity_counts.keys())
            sizes = list(fidelity_counts.values())
            colors = ["green", "yellow", "orange", "red"][: len(labels)]

            self.ax_fidelity.pie(
                sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
            )

    async def _update_performance_plot(self, performance: Dict[str, Any]):
        """Update performance metrics plot"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_performance.clear()
        self.ax_performance.set_title("⚡ Performance Metrics")

        performance_by_type = performance.get("performance_by_type", {})
        memory_types = list(performance_by_type.keys())
        comp_times = [
            metrics.get("avg_compression_time", 0) * 1000
            for metrics in performance_by_type.values()
        ]  # ms

        if memory_types and comp_times:
            bars = self.ax_performance.bar(
                memory_types, comp_times, color="lightcoral", alpha=0.7
            )
            self.ax_performance.set_ylabel("Compression Time (ms)")

            # Add value labels
            for bar, time_ms in zip(bars, comp_times):
                height = bar.get_height()
                self.ax_performance.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.1,
                    f"{time_ms:.1f}ms",
                    ha="center",
                    va="bottom",
                )

        self.ax_performance.tick_params(axis="x", rotation=45)

    async def _update_memory_type_plot(self, recent_data: List[Dict[str, Any]]):
        """Update memory type distribution plot"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_memory_types.clear()
        self.ax_memory_types.set_title("🗂️ Memory Type Distribution")

        # Count memory types
        type_counts = {}
        for item in recent_data:
            mem_type = item.get("memory_type", "unknown")
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1

        if type_counts:
            labels = list(type_counts.keys())
            sizes = list(type_counts.values())

            self.ax_memory_types.pie(
                sizes, labels=labels, autopct="%1.1f%%", startangle=90
            )

    async def _update_health_plot(self, performance: Dict[str, Any]):
        """Update system health timeline"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_health.clear()
        self.ax_health.set_title("🏥 System Health Timeline")
        self.ax_health.set_ylabel("Health Score")

        # For now, just show current health as a single point
        current_health = performance.get("overall_health", 0.0)
        current_time = time.time()

        self.ax_health.plot([current_time], [current_health], "go", markersize=10)
        self.ax_health.set_ylim(0, 1)
        self.ax_health.axhline(
            y=0.8, color="orange", linestyle="--", alpha=0.5, label="Warning threshold"
        )
        self.ax_health.axhline(
            y=0.6, color="red", linestyle="--", alpha=0.5, label="Critical threshold"
        )
        self.ax_health.legend()

        # Simple time formatting
        self.ax_health.set_xlabel("Time (seconds since epoch)")
        self.ax_health.tick_params(axis="x", rotation=45)

    async def _update_activity_plot(self, recent_data: List[Dict[str, Any]]):
        """Update activity log"""
        if not HAS_MATPLOTLIB:
            return

        self.ax_activity.clear()
        self.ax_activity.set_title("📋 Recent Compression Activity")
        self.ax_activity.axis("off")

        # Show recent activities as text
        activity_text = ""
        for i, activity in enumerate(recent_data[:10]):
            fragment_id = activity.get("fragment_id", "unknown")[:15]
            memory_type = activity.get("memory_type", "unknown")[:10]
            ratio = activity.get("compression_ratio", 0)
            fidelity = activity.get("fidelity_level", "unknown")[:8]

            activity_text += f"{i + 1:2d}. {fragment_id:15s} | {memory_type:10s} | {ratio:5.1f}x | {fidelity:8s}\n"

        self.ax_activity.text(
            0.05,
            0.95,
            activity_text,
            transform=self.ax_activity.transAxes,
            fontfamily="monospace",
            fontsize=10,
            verticalalignment="top",
        )

    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent compression activity from database"""
        db_path = self.analyzer.db_path

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get recent compression scores
        cursor.execute("""
            SELECT fragment_id, memory_type, compression_ratio, fidelity_level, timestamp
            FROM compression_scores
            ORDER BY timestamp DESC
            LIMIT 50
        """)

        rows = cursor.fetchall()
        conn.close()

        # Convert to dictionaries
        activities = []
        for row in rows:
            activities.append(
                {
                    "fragment_id": row[0],
                    "memory_type": row[1],
                    "compression_ratio": row[2],
                    "fidelity_level": row[3],
                    "timestamp": row[4],
                }
            )

        return activities

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        print("📊 Generating dashboard summary...")

        # Get performance data
        performance = await self.analyzer.monitor_compression_performance()
        recent_activity = await self._get_recent_activity()

        # Calculate summary statistics
        total_fragments = len(recent_activity)
        avg_compression_ratio = sum(
            a.get("compression_ratio", 0) for a in recent_activity
        ) / max(total_fragments, 1)

        # Fidelity distribution
        fidelity_dist = {}
        for activity in recent_activity:
            fidelity = activity.get("fidelity_level", "unknown")
            fidelity_dist[fidelity] = fidelity_dist.get(fidelity, 0) + 1

        # Memory type distribution
        type_dist = {}
        for activity in recent_activity:
            mem_type = activity.get("memory_type", "unknown")
            type_dist[mem_type] = type_dist.get(mem_type, 0) + 1

        summary = {
            "timestamp": time.time(),
            "system_health": performance.get("overall_health", 0.0),
            "total_fragments_analyzed": total_fragments,
            "average_compression_ratio": avg_compression_ratio,
            "fidelity_distribution": fidelity_dist,
            "memory_type_distribution": type_dist,
            "performance_by_type": performance.get("performance_by_type", {}),
            "performance_issues": performance.get("performance_issues", []),
            "optimization_suggestions": performance.get("optimization_suggestions", []),
            "recent_activity_count": len(recent_activity),
        }

        return summary

    async def export_dashboard_report(
        self, output_file: str = "qfac_dashboard_report.json"
    ):
        """Export comprehensive dashboard report"""
        print(f"📄 Exporting dashboard report to {output_file}...")

        # Get comprehensive summary
        summary = await self.get_dashboard_summary()

        # Add detailed analysis
        detailed_report = {
            "report_metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "qfac_version": "1.0.0",
                "analyzer_version": "1.0.0",
            },
            "executive_summary": summary,
            "detailed_analysis": {
                "compression_effectiveness": self._analyze_compression_effectiveness(
                    summary
                ),
                "performance_analysis": self._analyze_performance_trends(summary),
                "recommendations": self._generate_recommendations(summary),
            },
        }

        # Save to file
        import json

        output_path = self.dashboard_data_dir / output_file
        with open(output_path, "w") as f:
            json.dump(detailed_report, f, indent=2, default=str)

        print(f"   ✅ Report exported to {output_path}")
        return detailed_report

    def _analyze_compression_effectiveness(
        self, summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze compression effectiveness"""
        avg_ratio = summary.get("average_compression_ratio", 0)

        effectiveness = {
            "overall_rating": "excellent"
            if avg_ratio > 5
            else "good"
            if avg_ratio > 3
            else "fair"
            if avg_ratio > 2
            else "poor",
            "compression_ratio_analysis": {
                "average": avg_ratio,
                "rating": "excellent"
                if avg_ratio > 5
                else "good"
                if avg_ratio > 3
                else "needs_improvement",
            },
            "fidelity_analysis": {
                "distribution": summary.get("fidelity_distribution", {}),
                "quality_score": self._calculate_fidelity_quality_score(
                    summary.get("fidelity_distribution", {})
                ),
            },
        }

        return effectiveness

    def _analyze_performance_trends(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends"""
        performance_by_type = summary.get("performance_by_type", {})

        trends = {"speed_analysis": {}, "efficiency_analysis": {}, "bottlenecks": []}

        for mem_type, metrics in performance_by_type.items():
            comp_time = metrics.get("avg_compression_time", 0)
            comp_ratio = metrics.get("avg_compression_ratio", 0)

            trends["speed_analysis"][mem_type] = {
                "compression_time_ms": comp_time * 1000,
                "rating": "fast"
                if comp_time < 0.1
                else "acceptable"
                if comp_time < 0.5
                else "slow",
            }

            trends["efficiency_analysis"][mem_type] = {
                "compression_ratio": comp_ratio,
                "efficiency_score": comp_ratio
                / max(comp_time, 0.001),  # ratio per second
            }

            if comp_time > 0.5:
                trends["bottlenecks"].append(
                    f"Slow compression for {mem_type}: {comp_time * 1000:.1f}ms"
                )

        return trends

    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        avg_ratio = summary.get("average_compression_ratio", 0)
        health = summary.get("system_health", 0)

        if avg_ratio < 3.0:
            recommendations.append(
                "Consider more aggressive compression strategies for better space savings"
            )

        if health < 0.8:
            recommendations.append(
                "System health is below optimal - investigate performance issues"
            )

        fidelity_dist = summary.get("fidelity_distribution", {})
        degraded_count = fidelity_dist.get("degraded", 0)
        total_count = sum(fidelity_dist.values())

        if degraded_count > total_count * 0.1:
            recommendations.append(
                "High degraded fidelity rate - review compression parameters"
            )

        if not recommendations:
            recommendations.append(
                "System is performing optimally - maintain current configuration"
            )

        return recommendations

    def _calculate_fidelity_quality_score(self, fidelity_dist: Dict[str, int]) -> float:
        """Calculate overall fidelity quality score (0-1)"""
        if not fidelity_dist:
            return 0.0

        total = sum(fidelity_dist.values())
        if total == 0:
            return 0.0

        # Weight fidelity levels
        weights = {
            "lossless": 1.0,
            "lossy_safe": 0.8,
            "lossy_risky": 0.5,
            "degraded": 0.1,
        }

        weighted_sum = 0.0
        for fidelity, count in fidelity_dist.items():
            weight = weights.get(fidelity, 0.5)
            weighted_sum += weight * count

        return weighted_sum / total


# Example usage and testing
async def demo_qfac_dashboard():
    """Demonstrate QFAC dashboard capabilities"""
    print("🎯 QFAC DASHBOARD DEMONSTRATION")
    print("=" * 60)

    # Initialize analyzer and dashboard
    from .compression_analyzer import MemoryCompressionAnalyzer

    analyzer = MemoryCompressionAnalyzer()
    dashboard = QFACDashboard(analyzer)

    # Add some test data first
    test_fragments = [
        {
            "id": "test_conversation",
            "data": {
                "type": "conversation",
                "messages": [{"role": "user", "content": "Hello"}],
            },
            "access_history": [time.time()],
        },
        {
            "id": "test_narrative",
            "data": "This is a test narrative for compression analysis.",
            "access_history": [],
        },
    ]

    # Analyze fragments to populate database
    print("📊 Analyzing test fragments...")
    for fragment in test_fragments:
        await analyzer.analyze_memory_fragment(
            fragment["data"], fragment["id"], fragment["access_history"]
        )

    # Get dashboard summary
    print("\n📋 Dashboard Summary:")
    summary = await dashboard.get_dashboard_summary()
    print(f"   🏥 System health: {summary['system_health']:.1%}")
    print(f"   📊 Fragments analyzed: {summary['total_fragments_analyzed']}")
    print(f"   📈 Average compression: {summary['average_compression_ratio']:.1f}x")

    # Export report
    print("\n📄 Exporting dashboard report...")
    await dashboard.export_dashboard_report("demo_qfac_report.json")

    # Start text dashboard for demo (5 seconds)
    print("\n📺 Starting text dashboard demo (5 seconds)...")
    await asyncio.create_task(dashboard.start_dashboard("text"))

    # Let it run briefly
    await asyncio.sleep(5)

    # Stop dashboard
    await dashboard.stop_dashboard()

    print("\n✅ QFAC Dashboard demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demo_qfac_dashboard())
