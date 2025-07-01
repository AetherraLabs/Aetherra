# SPDX-License-Identifier: GPL-3.0-or-later
# core/memory.py - Compatibility Layer
"""
NeuroCode Memory System - Backward Compatibility Layer

This module provides backward compatibility for the original NeuroMemory interface
while using the new modular memory system under the hood.

For new code, consider using the modular interfaces directly:
- core.memory.BasicMemory for basic operations
- core.memory.VectorMemory for semantic search
- core.memory.UnifiedMemoryInterface for all capabilities
"""

from datetime import datetime, timedelta

# Import speed enhancement suite for memory optimization
try:
    from .speed_enhancement_suite import lightning_fast_data, optimize_memory_system, ultra_fast

    SPEED_ENHANCEMENT_AVAILABLE = True
    print("🧠 Speed Enhancement Suite integrated with memory system")
except ImportError:
    SPEED_ENHANCEMENT_AVAILABLE = False

    def ultra_fast(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def lightning_fast_data(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


MEMORY_FILE = "memory_store.json"


class NeuroMemory:
    """
    Ultra-fast legacy NeuroMemory interface - now powered by the modular memory system

    This class maintains backward compatibility while using the new modular
    memory architecture under the hood, enhanced with speed optimizations.
    """

    def __init__(self):
        from .memory import BasicMemory

        self._memory_system = BasicMemory()

        # Apply speed optimizations
        if SPEED_ENHANCEMENT_AVAILABLE:
            optimize_memory_system(self)
            print("🚀 Memory system speed optimized!")

    def load(self):
        """Load memories from persistent storage"""
        # Auto-loaded by the new system
        pass

    def save(self):
        """Save memories to persistent storage"""
        # Auto-saved by the new system
        pass

    @property
    def memory(self):
        """Legacy compatibility: return memories as list of dicts"""
        return self._memory_system.memory

    @ultra_fast("memory_remember")
    def remember(self, text, tags=None, category="general"):
        """Store text in memory with optional tags and category"""
        return self._memory_system.remember(text, tags, category)

    def recall(self, tags=None, category=None, limit=None, time_filter=None):
        """Recall memories, optionally filtered by tags, category, or time"""
        return self._memory_system.recall(tags, category, limit, time_filter)

    def temporal_analysis(self, timeframe="30_days", granularity="daily"):
        """Analyze memory patterns over time with specified granularity"""
        return self._memory_system.temporal_analysis(timeframe, granularity)

    def reflection_summary(self, period="7_days"):
        """Generate a reflection summary for a specific time period"""
        memories = self.recall(time_filter=period)
        if not memories:
            return f"No memories found for the period: {period}"

        # Basic analysis
        total_memories = len(memories)
        avg_length = sum(len(m) for m in memories) / total_memories

        # Get temporal analysis
        temporal = self.temporal_analysis(period, "daily")

        # Generate insights
        insights = []

        if total_memories > 10:
            insights.append(f"High activity period with {total_memories} memories recorded")
        elif total_memories > 5:
            insights.append(f"Moderate activity with {total_memories} memories")
        else:
            insights.append(f"Light activity with {total_memories} memories")

        if avg_length > 100:
            insights.append("Detailed memory entries suggest deep engagement")
        elif avg_length > 50:
            insights.append("Moderate detail in memory entries")
        else:
            insights.append("Brief memory entries")

        # Find most active day
        periods = temporal.get("periods", {})
        if periods:
            most_active = max(periods.items(), key=lambda x: x[1]["memory_count"])
            insights.append(
                f"Most active day: {most_active[0]} with {most_active[1]['memory_count']} memories"
            )

        summary = f"""
🔄 Memory Reflection - {period.replace("_", " ").title()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overview:
   • Total memories: {total_memories}
   • Average length: {avg_length:.1f} characters
   • Active days: {len(periods)}

💡 Insights:
   • {chr(10).join(f"   • {insight}" for insight in insights)}

🎯 Memory Highlights:
   • Recent focus areas based on activity patterns
   • Consistent engagement with the system
   • Balanced memory distribution across time periods
"""

        return summary

    def compare_periods(self, period1="7_days", period2="14_days"):
        """Compare memory patterns between two different time periods"""
        analysis1 = self.temporal_analysis(period1)
        analysis2 = self.temporal_analysis(period2)

        count1 = sum(period["memory_count"] for period in analysis1["periods"].values())
        count2 = sum(period["memory_count"] for period in analysis2["periods"].values())

        # Basic comparison logic (simplified)
        comparison = {
            "period1": period1,
            "period2": period2,
            "period1_count": count1,
            "period2_count": count2,
            "trend": "increasing"
            if count1 > count2
            else "decreasing"
            if count1 < count2
            else "stable",
            "change_ratio": count1 / count2 if count2 > 0 else float("inf"),
        }

        return comparison

    def search(self, query, case_sensitive=False):
        """Search memories by content"""
        return self._memory_system.search(query, case_sensitive)

    def get_tags(self):
        """Get all unique tags from memory"""
        return self._memory_system.get_tags()

    def get_categories(self):
        """Get all unique categories from memory"""
        return self._memory_system.get_categories()

    def get_memory_summary(self):
        """Get a summary of memory organization"""
        return self._memory_system.get_memory_summary()

    def patterns(self):
        """Analyze patterns in memory organization"""
        return self._memory_system.patterns()

    def get_memories_by_timeframe(self, hours=24):
        """Get memories from the last N hours"""
        return self._memory_system.get_memories_by_timeframe(hours)

    def delete_memories_by_tag(self, tag):
        """Delete memories containing a specific tag"""
        return self._memory_system.delete_memories_by_tag(tag)

    def get_memory_stats(self):
        """Get detailed statistics about memory usage"""
        return self._memory_system.get_memory_stats()

    def pattern_analysis(self, pattern, frequency_threshold="weekly", timeframe_days=30):
        """Analyze memory patterns and their frequency"""
        # Enhanced implementation using pattern analyzer
        try:
            from .memory import PatternAnalyzer

            analyzer = PatternAnalyzer()

            # Get memories matching the pattern
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            memories = self._memory_system.storage.load_memories()

            matching_memories = []
            for memory in memories:
                try:
                    memory_date = datetime.fromisoformat(
                        memory.timestamp.replace("Z", "+00:00").split("+")[0]
                    )
                    if memory_date >= cutoff_date:
                        if pattern.lower() in memory.text.lower():
                            matching_memories.append(memory)
                except (ValueError, AttributeError):
                    continue

            # Calculate frequency
            frequency_count = len(matching_memories)

            # Determine if pattern meets frequency threshold
            frequency_map = {
                "daily": frequency_count >= timeframe_days * 0.8,  # 80% of days
                "weekly": frequency_count >= timeframe_days / 7,  # At least weekly
                "monthly": frequency_count >= 1,  # At least once per month
                "rare": frequency_count >= 1,  # At least once
            }

            meets_threshold = frequency_map.get(frequency_threshold, False)

            return {
                "pattern": pattern,
                "matches": frequency_count,
                "timeframe_days": timeframe_days,
                "frequency_threshold": frequency_threshold,
                "meets_threshold": meets_threshold,
                "matching_memories": [m.to_dict() for m in matching_memories],
                "analysis": f"Pattern '{pattern}' found {frequency_count} times in {timeframe_days} days",
            }
        except ImportError:
            # Fallback to basic implementation
            return {
                "pattern": pattern,
                "matches": 0,
                "meets_threshold": False,
                "analysis": "Pattern analysis requires modular memory system",
            }

    def get_pattern_frequency(self, pattern, timeframe_days=30):
        """Get the frequency of a pattern in memory"""
        analysis = self.pattern_analysis(pattern, "rare", timeframe_days)
        return analysis["matches"]

    def detect_recurring_patterns(self, min_frequency=3, timeframe_days=30):
        """Detect recurring patterns in memory automatically"""
        try:
            from .memory import PatternAnalyzer

            analyzer = PatternAnalyzer()

            # Use the new pattern detection system
            patterns = analyzer.detect_text_patterns(min_frequency, timeframe_days)

            # Convert to legacy format
            recurring = {
                "phrases": {},
                "analysis_date": str(datetime.now()),
                "timeframe_days": timeframe_days,
                "min_frequency": min_frequency,
            }

            for pattern in patterns:
                if pattern.metadata.get("pattern_type") in ["text_phrase", "text_word"]:
                    phrase = (
                        pattern.pattern_name.replace("phrase_", "")
                        .replace("word_", "")
                        .replace("_", " ")
                    )
                    recurring["phrases"][phrase] = pattern.frequency

            return recurring
        except ImportError:
            # Fallback to basic implementation
            return {
                "phrases": {},
                "analysis_date": str(datetime.now()),
                "timeframe_days": timeframe_days,
                "min_frequency": min_frequency,
            }

    def pattern(self, pattern_name, frequency="weekly"):
        """Check if a pattern meets the frequency threshold - simplified interface"""
        analysis = self.pattern_analysis(pattern_name, frequency)
        return analysis["meets_threshold"]


# Legacy compatibility exports
__all__ = ["NeuroMemory"]
