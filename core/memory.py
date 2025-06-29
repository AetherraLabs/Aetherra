# core/memory.py
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Performance monitoring integration available (for future use)

MEMORY_FILE = "memory_store.json"


class NeuroMemory:
    def __init__(self):
        self.memory = []
        self.load()

    def load(self):
        """Load memories from persistent storage"""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                self.memory = json.load(f)

    def save(self):
        """Save memories to persistent storage"""
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(self.memory, f, indent=2)
        except (PermissionError, OSError):
            # Silently handle file permission issues for robustness
            pass

    def remember(self, text, tags=None, category="general"):
        """Store text in memory with optional tags and category"""
        if tags is None:
            tags = ["general"]

        memory_entry = {
            "text": text,
            "timestamp": str(datetime.now()),
            "tags": tags,
            "category": category,
        }

        self.memory.append(memory_entry)
        self.save()

    def recall(self, tags=None, category=None, limit=None, time_filter=None):
        """Recall memories, optionally filtered by tags, category, or time"""
        filtered_memories = []

        for m in self.memory:
            # Check if memory matches tag filter
            tag_match = tags is None or any(tag in m.get("tags", []) for tag in tags)
            # Check if memory matches category filter
            category_match = category is None or m.get("category") == category
            # Check if memory matches time filter
            time_match = time_filter is None or self._matches_time_filter(m, time_filter)

            if tag_match and category_match and time_match:
                filtered_memories.append(m)

        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply limit if specified
        if limit and len(filtered_memories) > limit:
            filtered_memories = filtered_memories[:limit]

        return [m["text"] for m in filtered_memories]

    def _matches_time_filter(self, memory, time_filter):
        """Check if a memory matches the time filter criteria"""
        if not time_filter:
            return True

        try:
            memory_time = datetime.fromisoformat(
                memory.get("timestamp", "").replace("Z", "+00:00").split("+")[0]
            )
        except (ValueError, AttributeError):
            return False

        now = datetime.now()

        if isinstance(time_filter, dict):
            # Advanced time filter with from/to dates
            from_time = time_filter.get("from")
            to_time = time_filter.get("to")

            if from_time:
                if isinstance(from_time, str):
                    from_time = datetime.fromisoformat(from_time)
                if memory_time < from_time:
                    return False

            if to_time:
                if isinstance(to_time, str):
                    to_time = datetime.fromisoformat(to_time)
                if memory_time > to_time:
                    return False

            return True

        elif isinstance(time_filter, str):
            # String-based time filter
            if time_filter == "today":
                return memory_time.date() == now.date()
            elif time_filter == "yesterday":
                yesterday = now - timedelta(days=1)
                return memory_time.date() == yesterday.date()
            elif time_filter == "this_week":
                week_start = now - timedelta(days=now.weekday())
                return memory_time >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_filter == "this_month":
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                return memory_time >= month_start
            elif time_filter.endswith("_hours"):
                hours = int(time_filter.split("_")[0])
                cutoff = now - timedelta(hours=hours)
                return memory_time >= cutoff
            elif time_filter.endswith("_days"):
                days = int(time_filter.split("_")[0])
                cutoff = now - timedelta(days=days)
                return memory_time >= cutoff

        return True

    def temporal_analysis(self, timeframe="30_days", granularity="daily"):
        """Analyze memory patterns over time with specified granularity"""

        now = datetime.now()
        if timeframe.endswith("_days"):
            days = int(timeframe.split("_")[0])
            cutoff = now - timedelta(days=days)
        elif timeframe.endswith("_hours"):
            hours = int(timeframe.split("_")[0])
            cutoff = now - timedelta(hours=hours)
        else:
            cutoff = now - timedelta(days=30)  # Default

        # Group memories by time periods
        time_groups = defaultdict(list)

        for m in self.memory:
            try:
                memory_time = datetime.fromisoformat(
                    m.get("timestamp", "").replace("Z", "+00:00").split("+")[0]
                )
                if memory_time >= cutoff:
                    # Determine time group key based on granularity
                    if granularity == "hourly":
                        time_key = memory_time.strftime("%Y-%m-%d %H:00")
                    elif granularity == "daily":
                        time_key = memory_time.strftime("%Y-%m-%d")
                    elif granularity == "weekly":
                        # Get start of week
                        week_start = memory_time - timedelta(days=memory_time.weekday())
                        time_key = week_start.strftime("%Y-W%U")
                    elif granularity == "monthly":
                        time_key = memory_time.strftime("%Y-%m")
                    else:
                        time_key = memory_time.strftime("%Y-%m-%d")  # Default to daily

                    time_groups[time_key].append(m)
            except (ValueError, AttributeError):
                continue

        # Analyze patterns within each time period
        analysis = {
            "timeframe": timeframe,
            "granularity": granularity,
            "total_periods": len(time_groups),
            "periods": {},
        }

        for time_key, memories in time_groups.items():
            period_analysis = {
                "memory_count": len(memories),
                "categories": defaultdict(int),
                "tags": defaultdict(int),
                "avg_length": sum(len(m["text"]) for m in memories) / len(memories)
                if memories
                else 0,
            }

            for m in memories:
                period_analysis["categories"][m.get("category", "general")] += 1
                for tag in m.get("tags", []):
                    period_analysis["tags"][tag] += 1

            analysis["periods"][time_key] = period_analysis

        return analysis

    def reflection_summary(self, period="7_days"):
        """Generate a reflection summary for a specific time period"""
        memories = self.recall(time_filter=period)
        if not memories:
            return f"No memories found for the period: {period}"

        # Analyze the content
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

        # Adjust count2 to exclude period1 if period2 includes period1
        if period1.endswith("_days") and period2.endswith("_days"):
            days1 = int(period1.split("_")[0])
            days2 = int(period2.split("_")[0])
            if days2 > days1:
                # Calculate count for period2 excluding period1
                extended_period_count = count2 - count1
                comparison = {
                    "period1": period1,
                    "period2": period2,
                    "period1_count": count1,
                    "period2_extended_count": extended_period_count,
                    "trend": "increasing"
                    if count1 > extended_period_count
                    else "decreasing"
                    if count1 < extended_period_count
                    else "stable",
                    "change_ratio": count1 / extended_period_count
                    if extended_period_count > 0
                    else float("inf"),
                }
            else:
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
        else:
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
        results = []
        search_flags = 0 if case_sensitive else re.IGNORECASE

        try:
            pattern = re.compile(query, search_flags)
        except re.error:
            # If regex compilation fails, treat as literal string
            query_lower = query.lower() if not case_sensitive else query
            for m in self.memory:
                text_to_search = m["text"].lower() if not case_sensitive else m["text"]
                if query_lower in text_to_search:
                    results.append(m["text"])
            return results

        # Use regex search
        for m in self.memory:
            if pattern.search(m["text"]):
                results.append(m["text"])

        return results

    def get_tags(self):
        """Get all unique tags from memory"""
        all_tags = set()
        for m in self.memory:
            all_tags.update(m.get("tags", []))
        return sorted(all_tags)

    def get_categories(self):
        """Get all unique categories from memory"""
        categories = set()
        for m in self.memory:
            category = m.get("category", "general")
            if category is not None:
                categories.add(category)
        return sorted(categories)

    def get_memory_summary(self):
        """Get a summary of memory organization"""
        return {
            "total_memories": len(self.memory),
            "tags": self.get_tags(),
            "categories": self.get_categories(),
        }

    def patterns(self):
        """Analyze patterns in memory organization"""
        tag_frequency = {}
        category_frequency = {}
        temporal_patterns = []

        for m in self.memory:
            # Tag patterns
            for tag in m.get("tags", []):
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

            # Category patterns
            category = m.get("category", "general")
            category_frequency[category] = category_frequency.get(category, 0) + 1

            # Temporal patterns
            temporal_patterns.append(m.get("timestamp", ""))

        return {
            "tag_frequency": tag_frequency,
            "category_frequency": category_frequency,
            "temporal_patterns": temporal_patterns,
            "most_frequent_tags": sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[
                :5
            ],
            "most_frequent_categories": sorted(
                category_frequency.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def get_memories_by_timeframe(self, hours=24):
        """Get memories from the last N hours"""
        from datetime import datetime, timedelta

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []

        for m in self.memory:
            try:
                memory_time = datetime.fromisoformat(m.get("timestamp", "").replace("Z", "+00:00"))
                if memory_time >= cutoff_time:
                    recent_memories.append(m["text"])
            except (ValueError, AttributeError):
                # Skip memories with invalid timestamps
                continue

        return recent_memories

    def delete_memories_by_tag(self, tag):
        """Delete memories containing a specific tag"""
        original_count = len(self.memory)
        self.memory = [m for m in self.memory if tag not in m.get("tags", [])]
        deleted_count = original_count - len(self.memory)

        if deleted_count > 0:
            self.save()

        return deleted_count

    def get_memory_stats(self):
        """Get detailed statistics about memory usage"""
        if not self.memory:
            return "No memories stored"

        patterns = self.patterns()
        recent_count = len(self.get_memories_by_timeframe(24))

        stats = f"""Memory Statistics:
📊 Total memories: {len(self.memory)}
🕐 Recent (24h): {recent_count}
🏷️  Unique tags: {len(self.get_tags())}
📂 Categories: {len(self.get_categories())}

Top Tags: {", ".join([f"{tag}({count})" for tag, count in patterns["most_frequent_tags"][:3]])}
Top Categories: {", ".join([f"{cat}({count})" for cat, count in patterns["most_frequent_categories"][:3]])}"""

        return stats

    def pattern_analysis(self, pattern, frequency_threshold="weekly", timeframe_days=30):
        """Analyze memory patterns and their frequency"""
        from datetime import datetime, timedelta

        # Calculate timeframe
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)

        # Find memories matching the pattern
        matching_memories = []
        for m in self.memory:
            try:
                memory_date = datetime.fromisoformat(
                    m["timestamp"].replace("Z", "+00:00").split("+")[0]
                )
                if memory_date >= cutoff_date:
                    if pattern.lower() in m["text"].lower():
                        matching_memories.append(m)
            except (ValueError, KeyError):
                # Skip memories with invalid timestamps
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
            "matching_memories": matching_memories,
            "analysis": f"Pattern '{pattern}' found {frequency_count} times in {timeframe_days} days",
        }

    def get_pattern_frequency(self, pattern, timeframe_days=30):
        """Get the frequency of a pattern in memory"""
        analysis = self.pattern_analysis(pattern, "rare", timeframe_days)
        return analysis["matches"]

    def detect_recurring_patterns(self, min_frequency=3, timeframe_days=30):
        """Detect recurring patterns in memory automatically"""

        # Extract common phrases and terms
        phrase_patterns = defaultdict(int)

        cutoff_date = datetime.now() - timedelta(days=timeframe_days)

        for m in self.memory:
            try:
                memory_date = datetime.fromisoformat(
                    m["timestamp"].replace("Z", "+00:00").split("+")[0]
                )
                if memory_date >= cutoff_date:
                    text = m["text"].lower()

                    # Extract 2-3 word phrases
                    words = re.findall(r"\b\w+\b", text)
                    for i in range(len(words) - 1):
                        phrase = " ".join(words[i : i + 2])
                        phrase_patterns[phrase] += 1

                    for i in range(len(words) - 2):
                        phrase = " ".join(words[i : i + 3])
                        phrase_patterns[phrase] += 1
            except (ValueError, KeyError):
                continue

        # Filter by minimum frequency
        recurring = {
            "phrases": {
                phrase: count for phrase, count in phrase_patterns.items() if count >= min_frequency
            },
            "analysis_date": str(datetime.now()),
            "timeframe_days": timeframe_days,
            "min_frequency": min_frequency,
        }

        return recurring

    def pattern(self, pattern_name, frequency="weekly"):
        """Check if a pattern meets the frequency threshold - simplified interface"""
        analysis = self.pattern_analysis(pattern_name, frequency)
        return analysis["meets_threshold"]
