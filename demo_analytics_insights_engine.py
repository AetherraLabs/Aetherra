"""
🚀 ANALYTICS & INSIGHTS ENGINE DEMO (#6)
=======================================

Comprehensive demonstration of the Analytics & Insights Engine,
showcasing integration with Advanced Memory Systems and Enhanced Agents.
"""

import asyncio
import logging
import time
import json
import random
from datetime import datetime
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import analytics components
try:
    from Aetherra.lyrixa.analytics_insights_engine import (
        AnalyticsEngine, InsightsEngine, AnalyticsMetric, InsightPattern,
        create_analytics_engine, create_insights_engine
    )
    ANALYTICS_AVAILABLE = True
    logger.info("[OK] Analytics & Insights Engine components available")
except ImportError as e:
    ANALYTICS_AVAILABLE = False
    logger.warning(f"[WARN] Analytics components not available: {e}")

# Try to import dashboard
try:
    from Aetherra.lyrixa.analytics_dashboard import AnalyticsDashboard, create_analytics_dashboard
    DASHBOARD_AVAILABLE = True
    logger.info("[OK] Analytics Dashboard available")
except ImportError as e:
    DASHBOARD_AVAILABLE = False
    logger.warning(f"[WARN] Dashboard not available: {e}")

# Try to import advanced memory
try:
    from Aetherra.lyrixa.advanced_memory_integration import AdvancedMemoryManager
    MEMORY_AVAILABLE = True
    logger.info("[OK] Advanced Memory Integration available")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.warning(f"[WARN] Advanced Memory not available: {e}")
    AdvancedMemoryManager = None


class AnalyticsDemo:
    """
    📊 Analytics & Insights Engine Demo

    Demonstrates the comprehensive analytics and insights capabilities
    of Aetherra's Analytics & Insights Engine (#6).
    """

    def __init__(self):
        self.analytics_engine = None
        self.insights_engine = None
        self.dashboard = None
        self.memory_manager = None

        # Demo configuration
        self.demo_config = {
            "analytics": {
                "db_path": "demo_analytics.db",
                "buffer_size": 50,
                "insight_threshold": 0.6,
                "analysis_window_hours": 24
            },
            "dashboard": {
                "host": "localhost",
                "port": 8687,
                "debug": True,
                "cache_timeout": 60
            }
        }

        # Demo metrics to simulate
        self.demo_metrics = [
            {"name": "response_time", "category": "performance", "range": (0.1, 3.0)},
            {"name": "memory_usage", "category": "performance", "range": (30.0, 95.0)},
            {"name": "user_engagement", "category": "user_behavior", "range": (0.2, 1.0)},
            {"name": "conversation_success", "category": "conversation", "range": (0.6, 1.0)},
            {"name": "response_quality", "category": "conversation", "range": (0.5, 1.0)},
            {"name": "memory_recall_time", "category": "memory", "range": (0.005, 0.050)},
            {"name": "memory_enhancement_rate", "category": "memory", "range": (0.3, 0.9)},
            {"name": "system_load", "category": "performance", "range": (10.0, 90.0)},
            {"name": "error_rate", "category": "system", "range": (0.0, 0.1)},
            {"name": "user_satisfaction", "category": "user_behavior", "range": (0.4, 1.0)}
        ]

        logger.info("📊 Analytics Demo initialized")

    async def run_demo(self):
        """Run the complete analytics demo"""

        print("\n" + "="*60)
        print("🌌 AETHERRA ANALYTICS & INSIGHTS ENGINE DEMO (#6)")
        print("="*60)
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            demo_start = time.time()

            # Initialize components
            print("[TOOL] Initializing Analytics & Insights Engine...")
            init_success = await self._initialize_components()

            if not init_success:
                print("❌ Failed to initialize components")
                return False

            print("[OK] All components initialized successfully!\n")

            # Phase 1: Collect sample metrics
            print("📊 Phase 1: Collecting Sample Metrics")
            print("-" * 40)
            await self._collect_sample_metrics()
            print()

            # Phase 2: Analyze patterns and generate insights
            print("🔍 Phase 2: Analyzing Patterns & Generating Insights")
            print("-" * 40)
            await self._analyze_and_generate_insights()
            print()

            # Phase 3: Performance snapshot
            print("⚡ Phase 3: Performance Snapshot")
            print("-" * 40)
            await self._demonstrate_performance_snapshot()
            print()

            # Phase 4: Comprehensive insights
            if self.insights_engine:
                print("🧠 Phase 4: Comprehensive Insights Generation")
                print("-" * 40)
                await self._demonstrate_comprehensive_insights()
                print()

            # Phase 5: Dashboard demonstration
            if DASHBOARD_AVAILABLE:
                print("🖥️ Phase 5: Analytics Dashboard")
                print("-" * 40)
                await self._demonstrate_dashboard()
                print()

            # Phase 6: Memory integration
            if self.memory_manager:
                print("🧩 Phase 6: Memory System Integration")
                print("-" * 40)
                await self._demonstrate_memory_integration()
                print()

            # Phase 7: Real-time analytics simulation
            print("📈 Phase 7: Real-time Analytics Simulation")
            print("-" * 40)
            await self._simulate_realtime_analytics()
            print()

            demo_time = time.time() - demo_start

            # Demo summary
            print("📋 DEMO SUMMARY")
            print("-" * 40)
            await self._display_demo_summary(demo_time)

            print(f"\n[OK] Analytics & Insights Engine Demo completed in {demo_time:.2f}s")
            print("🌟 Analytics & Insights Engine (#6) is fully operational!")

            return True

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
            return False

    async def _initialize_components(self) -> bool:
        """Initialize all analytics components"""

        try:
            # Initialize Analytics Engine
            if ANALYTICS_AVAILABLE:
                self.analytics_engine = create_analytics_engine(self.demo_config["analytics"])
                print("[OK] Analytics Engine initialized")
            else:
                print("[WARN] Analytics Engine not available")
                return False

            # Initialize Memory Manager
            if MEMORY_AVAILABLE:
                self.memory_manager = AdvancedMemoryManager()
                await self.memory_manager.initialize()
                print("[OK] Advanced Memory Manager initialized")
            else:
                print("[WARN] Advanced Memory Manager not available")

            # Initialize Insights Engine
            if ANALYTICS_AVAILABLE:
                self.insights_engine = create_insights_engine(
                    self.analytics_engine,
                    self.memory_manager
                )
                print("[OK] Insights Engine initialized")

            # Initialize Dashboard
            if DASHBOARD_AVAILABLE:
                self.dashboard = create_analytics_dashboard(self.demo_config["dashboard"])
                await self.dashboard.initialize()
                print("[OK] Analytics Dashboard initialized")
            else:
                print("[WARN] Dashboard not available")

            return True

        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False

    async def _collect_sample_metrics(self):
        """Collect sample metrics for demonstration"""

        print("Collecting sample metrics across multiple categories...")

        metrics_collected = 0

        # Collect metrics for each category over simulated time periods
        for i in range(100):  # Simulate 100 metric collection points
            for metric_def in self.demo_metrics:
                # Generate realistic values
                min_val, max_val = metric_def["range"]
                value = random.uniform(min_val, max_val)

                # Add some patterns and trends
                if metric_def["name"] == "response_time":
                    # Simulate slow responses during "peak hours"
                    if i % 20 < 5:  # Peak period
                        value *= random.uniform(1.5, 2.5)

                if metric_def["name"] == "user_engagement":
                    # Simulate higher engagement over time
                    trend_boost = (i / 100) * 0.3
                    value = min(1.0, value + trend_boost)

                if metric_def["name"] == "memory_usage":
                    # Simulate memory buildup
                    if i > 70:
                        value = min(95.0, value + random.uniform(10, 20))

                # Collect the metric
                await self.analytics_engine.collect_metric(
                    name=metric_def["name"],
                    value=value,
                    category=metric_def["category"],
                    metadata={
                        "demo_iteration": i,
                        "simulated_timestamp": datetime.now().isoformat()
                    }
                )

                metrics_collected += 1

        # Flush any remaining metrics
        await self.analytics_engine._flush_metrics_buffer()

        print(f"[OK] Collected {metrics_collected} sample metrics")

        # Display analytics statistics
        stats = self.analytics_engine.get_analytics_statistics()
        print(f"📊 Total metrics in system: {stats['metrics_collected']}")

    async def _analyze_and_generate_insights(self):
        """Analyze patterns and generate insights"""

        print("Analyzing collected data for patterns and insights...")

        # Generate insights
        insights = await self.analytics_engine.analyze_patterns()

        print(f"[OK] Generated {len(insights)} insights")

        if insights:
            print("\n🔍 Top Insights Discovered:")
            for insight in insights[:5]:  # Show top 5
                print(f"  • [{insight.category.upper()}] {insight.description}")
                print(f"    Confidence: {insight.confidence:.1%} | Impact: {insight.impact_score:.1%}")

        # Retrieve and display stored insights
        stored_insights = await self.analytics_engine.get_insights(limit=10)
        print(f"\n📋 Retrieved {len(stored_insights)} stored insights")

        return insights

    async def _demonstrate_performance_snapshot(self):
        """Demonstrate performance snapshot functionality"""

        print("Taking system performance snapshot...")

        snapshot = await self.analytics_engine.get_performance_snapshot()

        print("[OK] Performance snapshot captured")
        print(f"📊 Total metrics: {snapshot.get('total_metrics', 0):,}")
        print(f"🔍 Total insights: {snapshot.get('total_insights', 0)}")

        # Display system health
        health = snapshot.get('system_health', {})
        print(f"🏥 System health: {health.get('status', 'unknown')} ({health.get('score', 0)}%)")

        # Display category statistics
        category_stats = snapshot.get('category_statistics', {})
        if category_stats:
            print("\n📈 Category Statistics:")
            for category, stats in category_stats.items():
                avg_val = stats.get('average', 0)
                count = stats.get('count', 0)
                print(f"  • {category.title()}: {avg_val:.2f} avg ({count} metrics)")

    async def _demonstrate_comprehensive_insights(self):
        """Demonstrate comprehensive insights generation"""

        print("Generating comprehensive insights across all categories...")

        comprehensive = await self.insights_engine.generate_comprehensive_insights()

        if 'error' in comprehensive:
            print(f"[WARN] Comprehensive insights generation failed: {comprehensive['error']}")
            return

        print(f"[OK] Comprehensive insights generated in {comprehensive.get('generation_time', 0):.2f}s")

        # Display summary
        summary = comprehensive.get('summary', {})
        print(f"📊 Total insights: {summary.get('total_insights', 0)}")
        print(f"🧠 Advanced categories: {summary.get('advanced_categories', 0)}")
        print(f"🔮 Predictions generated: {summary.get('predictions_generated', 0)}")

        # Display key findings
        key_findings = summary.get('key_findings', [])
        if key_findings:
            print("\n🎯 Key Findings:")
            for finding in key_findings[:3]:
                print(f"  • {finding}")

        # Display priority actions
        priority_actions = summary.get('priority_actions', [])
        if priority_actions:
            print("\n⚡ Priority Actions:")
            for action in priority_actions[:3]:
                print(f"  • {action}")

        print(f"\n🎯 System status: {summary.get('system_status', 'unknown')}")

    async def _demonstrate_dashboard(self):
        """Demonstrate dashboard functionality"""

        print("Setting up Analytics Dashboard...")

        if not self.dashboard:
            print("[WARN] Dashboard not available")
            return

        # Collect some dashboard metrics
        await self.dashboard.collect_system_metrics()

        # Get dashboard data
        dashboard_data = await self.dashboard._get_dashboard_data()

        print("[OK] Dashboard data prepared")
        print(f"📊 Dashboard served {dashboard_data.get('dashboard_stats', {}).get('requests_served', 0)} requests")

        # Show available components
        components = dashboard_data.get('system_available', {})
        print("\n[TOOL] Dashboard Components:")
        for component, available in components.items():
            status = "[OK] Available" if available else "❌ Unavailable"
            print(f"  • {component.replace('_', ' ').title()}: {status}")

        print(f"\n🌐 Dashboard URL: http://localhost:{self.demo_config['dashboard']['port']}")
        print("💡 Run the dashboard server separately to view the web interface")

    async def _demonstrate_memory_integration(self):
        """Demonstrate memory system integration"""

        print("Demonstrating memory system integration...")

        if not self.memory_manager:
            print("[WARN] Memory manager not available")
            return

        # Store some analytics-related memories
        analytics_memory = {
            "type": "analytics_insight",
            "content": "User engagement shows strong upward trend during evening hours",
            "metadata": {
                "category": "user_behavior",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        }

        memory_result = await self.memory_manager.store_memory(
            "analytics_insight_001",
            analytics_memory,
            {"analytics": True, "insight": True}
        )

        if memory_result:
            print("[OK] Analytics insight stored in memory system")

        # Retrieve related memories
        related_memories = await self.memory_manager.search_memories(
            "user engagement trends",
            limit=5
        )

        print(f"🔍 Found {len(related_memories)} related memories")

        # Demonstrate memory-enhanced analytics
        await self.analytics_engine.collect_metric(
            "memory_integration_test",
            1.0,
            "integration",
            {"memory_enhanced": True, "memories_found": len(related_memories)}
        )

        print("[OK] Memory-enhanced analytics metrics collected")

    async def _simulate_realtime_analytics(self):
        """Simulate real-time analytics processing"""

        print("Simulating real-time analytics processing...")

        simulation_duration = 10  # seconds
        update_interval = 1  # second

        start_time = time.time()
        updates = 0

        while time.time() - start_time < simulation_duration:
            # Simulate incoming metrics
            for metric_def in self.demo_metrics[:3]:  # Use subset for real-time
                min_val, max_val = metric_def["range"]
                value = random.uniform(min_val, max_val)

                await self.analytics_engine.collect_metric(
                    f"realtime_{metric_def['name']}",
                    value,
                    "realtime",
                    {"simulation": True, "update": updates}
                )

            updates += 1

            # Show progress
            if updates % 3 == 0:
                print(f"  📊 Real-time update #{updates} - {updates * 3} metrics processed")

            await asyncio.sleep(update_interval)

        print(f"[OK] Completed {updates} real-time updates ({updates * 3} metrics)")

        # Final metrics flush
        await self.analytics_engine._flush_metrics_buffer()

    async def _display_demo_summary(self, demo_time: float):
        """Display comprehensive demo summary"""

        # Get final statistics
        stats = self.analytics_engine.get_analytics_statistics()

        print(f"⏱️  Total demo time: {demo_time:.2f} seconds")
        print(f"📊 Total metrics collected: {stats['metrics_collected']:,}")
        print(f"🔍 Insights generated: {stats['insights_generated']}")
        print(f"🧩 Patterns discovered: {stats['patterns_discovered']}")
        print(f"⚡ Analysis runs: {stats['performance_analysis_runs']}")

        # Get final performance snapshot
        final_snapshot = await self.analytics_engine.get_performance_snapshot()
        health = final_snapshot.get('system_health', {})

        print(f"🏥 Final system health: {health.get('status', 'unknown')} ({health.get('score', 0)}%)")

        # Display component status
        print("\n[TOOL] Component Status:")
        print(f"  • Analytics Engine: {'[OK] Active' if self.analytics_engine else '❌ Inactive'}")
        print(f"  • Insights Engine: {'[OK] Active' if self.insights_engine else '❌ Inactive'}")
        print(f"  • Memory Manager: {'[OK] Active' if self.memory_manager else '❌ Inactive'}")
        print(f"  • Dashboard: {'[OK] Ready' if self.dashboard else '❌ Unavailable'}")

        # Display capabilities
        print("\n🌟 Demonstrated Capabilities:")
        print("  [OK] Multi-category metrics collection")
        print("  [OK] Pattern analysis and insight generation")
        print("  [OK] Performance monitoring and health assessment")
        print("  [OK] Real-time analytics processing")
        print("  [OK] Comprehensive insights with predictions")

        if self.memory_manager:
            print("  [OK] Memory system integration")

        if DASHBOARD_AVAILABLE:
            print("  [OK] Web-based analytics dashboard")

        print("\n💡 Next Steps:")
        print("  • Run dashboard server for web interface")
        print("  • Integrate with existing Aetherra components")
        print("  • Set up automated analytics collection")
        print("  • Configure custom insight generation rules")
        print("  • Enable real-time monitoring and alerts")


async def main():
    """Main demo function"""

    print("🚀 Starting Analytics & Insights Engine Demo...")

    demo = AnalyticsDemo()
    success = await demo.run_demo()

    if success:
        print("\n🎉 Demo completed successfully!")
        print("📊 Analytics & Insights Engine (#6) is ready for integration!")
    else:
        print("\n❌ Demo encountered issues")
        print("[TOOL] Check component availability and configuration")

    return success


if __name__ == "__main__":
    asyncio.run(main())
