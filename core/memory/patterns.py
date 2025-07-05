"""
Memory Pattern Analysis
Advanced pattern detection and analysis for memory data
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import MemoryEntry, MemoryPattern
from .storage import FileMemoryStorage, PatternStorage


class PatternAnalyzer:
    """
    Advanced pattern analysis for memory data
    Detects recurring themes, behavioral patterns, and insights
    """

    def __init__(
        self,
        memory_storage: Optional[FileMemoryStorage] = None,
        pattern_storage: Optional[PatternStorage] = None,
    ):
        if memory_storage is None:
            memory_storage = FileMemoryStorage()
        if pattern_storage is None:
            pattern_storage = PatternStorage()

        self.memory_storage = memory_storage
        self.pattern_storage = pattern_storage

    def detect_text_patterns(
        self, min_frequency: int = 3, timeframe_days: int = 30
    ) -> List[MemoryPattern]:
        """Detect recurring text patterns in memories"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        memories = self._get_memories_since(cutoff_date)

        # Extract phrases and patterns
        phrase_patterns = defaultdict(list)
        word_patterns = defaultdict(list)

        for memory in memories:
            text = memory.text.lower()
            words = re.findall(r"\b\w+\b", text)

            # Extract 2-3 word phrases
            for i in range(len(words) - 1):
                phrase = " ".join(words[i : i + 2])
                if len(phrase) > 5:  # Skip very short phrases
                    phrase_patterns[phrase].append(memory)

            for i in range(len(words) - 2):
                phrase = " ".join(words[i : i + 3])
                if len(phrase) > 8:  # Skip very short phrases
                    phrase_patterns[phrase].append(memory)

            # Extract individual significant words
            for word in words:
                if len(word) > 4:  # Skip short common words
                    word_patterns[word].append(memory)

        # Create pattern objects for frequent patterns
        detected_patterns = []

        for phrase, memory_list in phrase_patterns.items():
            if len(memory_list) >= min_frequency:
                pattern = self._create_pattern(
                    pattern_name=f"phrase_{phrase.replace(' ', '_')}",
                    description=f"Recurring phrase: '{phrase}'",
                    frequency=len(memory_list),
                    examples=[m.text[:100] for m in memory_list[:3]],
                    pattern_type="text_phrase",
                )
                detected_patterns.append(pattern)

        for word, memory_list in word_patterns.items():
            if (
                len(memory_list) >= min_frequency * 2
            ):  # Higher threshold for single words
                pattern = self._create_pattern(
                    pattern_name=f"word_{word}",
                    description=f"Recurring word: '{word}'",
                    frequency=len(memory_list),
                    examples=[m.text[:100] for m in memory_list[:3]],
                    pattern_type="text_word",
                )
                detected_patterns.append(pattern)

        return detected_patterns

    def detect_temporal_patterns(self, timeframe_days: int = 30) -> List[MemoryPattern]:
        """Detect temporal patterns in memory creation"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        memories = self._get_memories_since(cutoff_date)

        # Analyze temporal patterns
        hourly_activity = defaultdict(list)
        daily_activity = defaultdict(list)
        category_timing = defaultdict(list)

        for memory in memories:
            try:
                memory_time = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                )

                hour = memory_time.hour
                day_of_week = memory_time.weekday()

                hourly_activity[hour].append(memory)
                daily_activity[day_of_week].append(memory)
                category_timing[memory.category].append(memory_time)

            except (ValueError, AttributeError):
                continue

        detected_patterns = []

        # Peak activity hours
        if hourly_activity:
            peak_hours = sorted(
                hourly_activity.items(), key=lambda x: len(x[1]), reverse=True
            )[:3]
            for hour, hour_memories in peak_hours:
                if len(hour_memories) >= 5:  # Minimum threshold
                    pattern = self._create_pattern(
                        pattern_name=f"peak_hour_{hour}",
                        description=f"High activity during hour {hour}:00 ({len(hour_memories)} memories)",
                        frequency=len(hour_memories),
                        examples=[],
                        pattern_type="temporal_hourly",
                    )
                    detected_patterns.append(pattern)

        # Peak activity days
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        if daily_activity:
            peak_days = sorted(
                daily_activity.items(), key=lambda x: len(x[1]), reverse=True
            )[:3]
            for day_num, day_memories in peak_days:
                if len(day_memories) >= 10:  # Minimum threshold
                    day_name = day_names[day_num]
                    pattern = self._create_pattern(
                        pattern_name=f"peak_day_{day_name.lower()}",
                        description=f"High activity on {day_name} ({len(day_memories)} memories)",
                        frequency=len(day_memories),
                        examples=[],
                        pattern_type="temporal_daily",
                    )
                    detected_patterns.append(pattern)

        return detected_patterns

    def detect_category_patterns(self, timeframe_days: int = 30) -> List[MemoryPattern]:
        """Detect patterns in category usage"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        memories = self._get_memories_since(cutoff_date)

        def create_category_analysis():
            return {
                "count": 0,
                "memories": [],
                "avg_length": 0.0,
                "common_tags": defaultdict(int),
                "time_distribution": defaultdict(int),
            }

        category_analysis = defaultdict(create_category_analysis)

        for memory in memories:
            category = memory.category
            analysis = category_analysis[category]

            analysis["count"] += 1
            analysis["memories"].append(memory)

            # Tag co-occurrence
            for tag in memory.tags:
                analysis["common_tags"][tag] += 1

            # Time distribution
            try:
                memory_time = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                )
                hour = memory_time.hour
                analysis["time_distribution"][hour] += 1
            except (ValueError, AttributeError):
                continue

        detected_patterns = []

        for category, analysis in category_analysis.items():
            if analysis["count"] >= 5:  # Minimum threshold
                # Calculate average length
                total_length = sum(len(m.text) for m in analysis["memories"])
                avg_length = total_length / len(analysis["memories"])
                analysis["avg_length"] = avg_length

                # Find most common tags
                top_tags = sorted(
                    analysis["common_tags"].items(), key=lambda x: x[1], reverse=True
                )[:3]
                tag_description = ", ".join([tag for tag, count in top_tags])

                pattern = self._create_pattern(
                    pattern_name=f"category_{category}",
                    description=(
                        f"Category '{category}' usage pattern (avg length: {avg_length:.0f}, "
                        f"common tags: {tag_description})"
                    ),
                    frequency=analysis["count"],
                    examples=[m.text[:100] for m in analysis["memories"][:3]],
                    pattern_type="category_usage",
                    metadata={
                        "avg_length": avg_length,
                        "common_tags": dict(top_tags),
                        "time_distribution": dict(analysis["time_distribution"]),
                    },
                )
                detected_patterns.append(pattern)

        return detected_patterns

    def detect_tag_patterns(self, timeframe_days: int = 30) -> List[MemoryPattern]:
        """Detect patterns in tag usage and co-occurrence"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        memories = self._get_memories_since(cutoff_date)

        tag_cooccurrence = defaultdict(lambda: defaultdict(int))
        tag_frequency = defaultdict(int)

        for memory in memories:
            memory_tags = memory.tags

            # Count individual tag frequency
            for tag in memory_tags:
                tag_frequency[tag] += 1

            # Count tag co-occurrence
            for i, tag1 in enumerate(memory_tags):
                for tag2 in memory_tags[i + 1 :]:
                    tag_cooccurrence[tag1][tag2] += 1
                    tag_cooccurrence[tag2][tag1] += 1

        detected_patterns = []

        # Frequent tags
        frequent_tags = [
            (tag, count) for tag, count in tag_frequency.items() if count >= 5
        ]
        for tag, count in frequent_tags:
            pattern = self._create_pattern(
                pattern_name=f"tag_{tag}",
                description=f"Frequent tag usage: '{tag}' ({count} occurrences)",
                frequency=count,
                examples=[],
                pattern_type="tag_frequency",
            )
            detected_patterns.append(pattern)

        # Tag co-occurrence patterns
        for tag1, cooccurrences in tag_cooccurrence.items():
            if tag_frequency[tag1] >= 3:  # Only consider reasonably frequent tags
                most_common = max(cooccurrences.items(), key=lambda x: x[1])
                tag2, cooccurrence_count = most_common

                if cooccurrence_count >= 3:  # Minimum co-occurrence threshold
                    pattern = self._create_pattern(
                        pattern_name=f"tag_pair_{tag1}_{tag2}",
                        description=f"Tag co-occurrence: '{tag1}' and '{tag2}' ({cooccurrence_count} times)",
                        frequency=cooccurrence_count,
                        examples=[],
                        pattern_type="tag_cooccurrence",
                        metadata={"tag1": tag1, "tag2": tag2},
                    )
                    detected_patterns.append(pattern)

        return detected_patterns

    def analyze_memory_evolution(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """Analyze how memory patterns evolve over time"""
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        memories = self._get_memories_since(cutoff_date)

        # Split timeframe into periods
        period_length = timeframe_days // 4  # 4 periods
        periods = []

        for i in range(4):
            period_start = cutoff_date + timedelta(days=i * period_length)
            period_end = cutoff_date + timedelta(days=(i + 1) * period_length)

            period_memories = [
                m
                for m in memories
                if period_start
                <= datetime.fromisoformat(
                    m.timestamp.replace("Z", "+00:00").split("+")[0]
                )
                < period_end
            ]

            periods.append(
                {
                    "start": period_start,
                    "end": period_end,
                    "memories": period_memories,
                    "analysis": self._analyze_memory_period(period_memories),
                }
            )

        # Compare periods
        evolution_analysis = {
            "periods": periods,
            "trends": self._identify_trends(periods),
            "emerging_patterns": self._identify_emerging_patterns(periods),
            "declining_patterns": self._identify_declining_patterns(periods),
        }

        return evolution_analysis

    def _get_memories_since(self, cutoff_date: datetime) -> List[MemoryEntry]:
        """Get memories since a specific date"""
        all_memories = self.memory_storage.load_memories()
        filtered_memories = []

        for memory in all_memories:
            try:
                memory_time = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                )
                if memory_time >= cutoff_date:
                    filtered_memories.append(memory)
            except (ValueError, AttributeError):
                continue

        return filtered_memories

    def _create_pattern(
        self,
        pattern_name: str,
        description: str,
        frequency: int,
        examples: List[str],
        pattern_type: str,
        metadata: Optional[Dict] = None,
    ) -> MemoryPattern:
        """Create a MemoryPattern object"""
        confidence = min(frequency / 10.0, 1.0)  # Simple confidence calculation

        return MemoryPattern(
            pattern_name=pattern_name,
            description=description,
            frequency=frequency,
            confidence=confidence,
            examples=examples,
            metadata=metadata or {"pattern_type": pattern_type},
        )

    def _analyze_memory_period(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """Analyze a specific period of memories"""
        if not memories:
            return {
                "count": 0,
                "avg_length": 0,
                "categories": {},
                "tags": {},
                "top_categories": [],
                "top_tags": [],
            }

        categories = defaultdict(int)
        tags = defaultdict(int)
        total_length = 0

        for memory in memories:
            categories[memory.category] += 1
            total_length += len(memory.text)

            for tag in memory.tags:
                tags[tag] += 1

        avg_length = total_length / len(memories)

        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "count": len(memories),
            "avg_length": avg_length,
            "categories": dict(categories),
            "tags": dict(tags),
            "top_categories": top_categories,
            "top_tags": top_tags,
        }

    def _identify_trends(self, periods: List[Dict]) -> List[str]:
        """Identify trends across periods"""
        trends = []

        # Memory count trend
        counts = [p["analysis"]["count"] for p in periods]
        if len(counts) >= 2:
            if counts[-1] > counts[0]:
                trends.append("Increasing memory activity over time")
            elif counts[-1] < counts[0]:
                trends.append("Decreasing memory activity over time")

        # Average length trend
        lengths = [p["analysis"]["avg_length"] for p in periods]
        if len(lengths) >= 2:
            if lengths[-1] > lengths[0] * 1.2:
                trends.append("Memory entries becoming more detailed")
            elif lengths[-1] < lengths[0] * 0.8:
                trends.append("Memory entries becoming more concise")

        return trends

    def _identify_emerging_patterns(self, periods: List[Dict]) -> List[str]:
        """Identify patterns that are emerging in recent periods"""
        if len(periods) < 2:
            return []

        emerging = []
        recent_analysis = periods[-1]["analysis"]
        earlier_analysis = periods[0]["analysis"]

        # New categories
        new_categories = set(recent_analysis["categories"].keys()) - set(
            earlier_analysis["categories"].keys()
        )
        for category in new_categories:
            if recent_analysis["categories"][category] >= 3:
                emerging.append(f"New category emerging: '{category}'")

        # New tags
        new_tags = set(recent_analysis["tags"].keys()) - set(
            earlier_analysis["tags"].keys()
        )
        for tag in new_tags:
            if recent_analysis["tags"][tag] >= 3:
                emerging.append(f"New tag pattern: '{tag}'")

        return emerging

    def _identify_declining_patterns(self, periods: List[Dict]) -> List[str]:
        """Identify patterns that are declining"""
        if len(periods) < 2:
            return []

        declining = []
        recent_analysis = periods[-1]["analysis"]
        earlier_analysis = periods[0]["analysis"]

        # Declining categories
        for category in earlier_analysis["categories"]:
            if category in recent_analysis["categories"]:
                earlier_count = earlier_analysis["categories"][category]
                recent_count = recent_analysis["categories"][category]
                if recent_count < earlier_count * 0.5 and earlier_count >= 5:
                    declining.append(f"Declining category: '{category}'")

        return declining

    def save_detected_patterns(self, patterns: List[MemoryPattern]) -> int:
        """Save detected patterns to storage"""
        saved_count = 0
        for pattern in patterns:
            if self.pattern_storage.save_pattern(pattern):
                saved_count += 1
        return saved_count

    def get_all_patterns(self) -> List[MemoryPattern]:
        """Get all stored patterns"""
        return self.pattern_storage.list_patterns()

    def run_full_analysis(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """Run comprehensive pattern analysis"""
        text_patterns = self.detect_text_patterns(timeframe_days=timeframe_days)
        temporal_patterns = self.detect_temporal_patterns(timeframe_days=timeframe_days)
        category_patterns = self.detect_category_patterns(timeframe_days=timeframe_days)
        tag_patterns = self.detect_tag_patterns(timeframe_days=timeframe_days)
        evolution_analysis = self.analyze_memory_evolution(
            timeframe_days=timeframe_days
        )

        all_patterns = (
            text_patterns + temporal_patterns + category_patterns + tag_patterns
        )

        return {
            "text_patterns": text_patterns,
            "temporal_patterns": temporal_patterns,
            "category_patterns": category_patterns,
            "tag_patterns": tag_patterns,
            "evolution_analysis": evolution_analysis,
            "total_patterns_detected": len(all_patterns),
            "analysis_date": datetime.now().isoformat(),
            "timeframe_days": timeframe_days,
        }
