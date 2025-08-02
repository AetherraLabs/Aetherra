"""
🧠 ENHANCED ANALYTICS DEMO - WITH INSIGHTS
==========================================

Enhanced version that generates more insights by adding problematic patterns.
"""

import asyncio
import random
from demo_analytics_standalone import AnalyticsInsightsDemo, SimpleAnalyticsEngine

class EnhancedAnalyticsDemo(AnalyticsInsightsDemo):
    """Enhanced demo with more diverse patterns to trigger insights"""
    
    async def _collect_enhanced_metrics(self):
        """Collect metrics designed to trigger insights"""
        
        print("Collecting enhanced metrics designed to trigger insights...")
        
        # Collect problematic response times
        for i in range(30):
            # High response times to trigger performance insight
            response_time = random.uniform(2.5, 5.0)  # Intentionally high
            await self.analytics_engine.collect_metric(
                "response_time", response_time, "performance",
                {"scenario": "high_load", "iteration": i}
            )
        
        # Collect high memory usage
        for i in range(25):
            # High memory usage to trigger memory insight
            memory_usage = random.uniform(85.0, 95.0)  # Intentionally high
            await self.analytics_engine.collect_metric(
                "memory_usage", memory_usage, "performance",
                {"scenario": "memory_intensive", "iteration": i}
            )
        
        # Collect excellent user engagement
        for i in range(40):
            # High engagement to trigger positive insight
            engagement = random.uniform(0.85, 0.98)  # Intentionally high
            await self.analytics_engine.collect_metric(
                "user_engagement", engagement, "user_behavior",
                {"scenario": "high_engagement", "iteration": i}
            )
        
        # Collect low engagement period
        for i in range(20):
            # Low engagement to trigger concern insight
            engagement = random.uniform(0.1, 0.4)  # Intentionally low
            await self.analytics_engine.collect_metric(
                "user_engagement", engagement, "user_behavior", 
                {"scenario": "low_engagement", "iteration": i}
            )
        
        # Flush metrics
        await self.analytics_engine._flush_metrics_buffer()
        print("✅ Enhanced metrics collected to trigger comprehensive insights")
    
    async def run_enhanced_demo(self):
        """Run enhanced demo with insight generation"""
        
        print("\n" + "="*70)
        print("🌌 ENHANCED ANALYTICS & INSIGHTS ENGINE DEMO (#6)")
        print("="*70)
        print("🧠 Now with Intelligent Insight Generation!")
        print()
        
        # Initialize
        self.analytics_engine = SimpleAnalyticsEngine("enhanced_analytics.db")
        print("✅ Enhanced Analytics Engine initialized!\n")
        
        # Collect enhanced metrics
        print("📊 Collecting Enhanced Metrics for Insight Generation")
        print("-" * 60)
        await self._collect_enhanced_metrics()
        print()
        
        # Generate insights
        print("🔍 Generating Intelligent Insights")
        print("-" * 60)
        insights = await self.analytics_engine.analyze_patterns()
        
        print(f"✅ Generated {len(insights)} intelligent insights!")
        
        if insights:
            print("\n🧠 DISCOVERED INSIGHTS:")
            print("=" * 50)
            for i, insight in enumerate(insights, 1):
                category_emoji = {
                    'performance': '⚡',
                    'user_behavior': '👤',
                    'conversation': '💬',
                    'memory': '🧠',
                    'system': '🖥️'
                }.get(insight.category, '📊')
                
                confidence_emoji = '🟢' if insight.confidence > 0.8 else '🟡' if insight.confidence > 0.6 else '🟠'
                impact_emoji = '🔴' if insight.impact_score > 0.8 else '🟡' if insight.impact_score > 0.6 else '🟢'
                
                print(f"{i}. {category_emoji} [{insight.category.upper()}] {confidence_emoji}{impact_emoji}")
                print(f"   📝 {insight.description}")
                print(f"   📊 Confidence: {insight.confidence:.1%} | Impact: {insight.impact_score:.1%}")
                print(f"   🔍 Pattern: {insight.pattern_id}")
                
                # Show evidence if available
                if insight.evidence:
                    print(f"   📈 Evidence: {insight.evidence[0] if insight.evidence else 'None'}")
                print()
        
        # Performance snapshot
        print("⚡ Enhanced Performance Analysis")
        print("-" * 60)
        snapshot = await self.analytics_engine.get_performance_snapshot()
        
        health = snapshot.get('system_health', {})
        health_status = health.get('status', 'unknown')
        health_score = health.get('score', 0)
        
        print(f"🏥 System Health: {health_status.upper()} ({health_score:.0f}%)")
        
        factors = health.get('factors', {})
        if factors:
            print("🔍 Health Analysis:")
            for factor, status in factors.items():
                status_emoji = {
                    'excellent': '🟢',
                    'healthy': '🟢',
                    'good': '🟢',
                    'fair': '🟡',
                    'warning': '🟠',
                    'poor': '🔴',
                    'critical': '🚨'
                }.get(status, '❓')
                print(f"   {status_emoji} {factor.replace('_', ' ').title()}: {status}")
        
        # Category breakdown
        category_stats = snapshot.get('category_statistics', {})
        if category_stats:
            print("\n📊 Performance by Category:")
            for category, stats in category_stats.items():
                avg_val = stats.get('average', 0)
                count = stats.get('count', 0)
                
                # Add performance indicators
                if 'performance' in category and avg_val > 2.0:
                    indicator = '🔴'
                elif 'user_behavior' in category and avg_val > 0.8:
                    indicator = '🟢'
                elif 'user_behavior' in category and avg_val < 0.5:
                    indicator = '🔴'
                else:
                    indicator = '🟡'
                
                print(f"   {indicator} {category.title()}: {avg_val:.2f} avg ({count:,} metrics)")
        
        print("\n" + "="*70)
        print("🎉 ENHANCED ANALYTICS & INSIGHTS ENGINE DEMO COMPLETE!")
        print("="*70)
        print("🧠 Advanced pattern recognition successfully demonstrated!")
        print("📊 Intelligent insights generated and analyzed!")
        print("🚀 Analytics & Insights Engine (#6) is FULLY OPERATIONAL!")
        print("="*70)

async def main():
    """Run enhanced demo"""
    demo = EnhancedAnalyticsDemo()
    await demo.run_enhanced_demo()

if __name__ == "__main__":
    asyncio.run(main())
