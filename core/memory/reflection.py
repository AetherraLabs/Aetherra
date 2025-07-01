"""
Daily Reflection System
Automatic daily memory reflection and pattern analysis
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from .models import DailyReflection, MemoryEntry
from .storage import DailyReflectionStorage, FileMemoryStorage


class DailyReflectionManager:
    """
    Manages daily reflection generation and storage
    Automatically analyzes daily memory patterns and generates insights
    """

    def __init__(
        self,
        memory_storage: Optional[FileMemoryStorage] = None,
        reflection_storage: Optional[DailyReflectionStorage] = None,
    ):
        if memory_storage is None:
            memory_storage = FileMemoryStorage()
        if reflection_storage is None:
            reflection_storage = DailyReflectionStorage()

        self.memory_storage = memory_storage
        self.reflection_storage = reflection_storage

    def generate_daily_reflection(self, date: Optional[str] = None) -> DailyReflection:
        """Generate a daily reflection for the specified date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Get memories for the specific date
        memories = self._get_memories_for_date(date)

        # Analyze the memories
        analysis = self._analyze_daily_memories(memories)

        # Generate insights
        insights = self._generate_insights(memories, analysis)

        # Create reflection object
        reflection = DailyReflection(
            date=date,
            total_memories=len(memories),
            categories=analysis["categories"],
            tags=analysis["tags"],
            session_count=analysis["estimated_sessions"],
            insights=insights,
            key_memories=analysis["key_memories"],
            reflection_summary=self._generate_summary(memories, analysis, insights),
        )

        # Save the reflection
        self.reflection_storage.save_reflection(reflection)

        return reflection

    def _get_memories_for_date(self, date: str) -> List[MemoryEntry]:
        """Get all memories for a specific date"""
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        all_memories = self.memory_storage.load_memories()
        daily_memories = []

        for memory in all_memories:
            try:
                memory_date = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                ).date()
                if memory_date == target_date:
                    daily_memories.append(memory)
            except (ValueError, AttributeError):
                continue

        return daily_memories

    def _analyze_daily_memories(self, memories: List[MemoryEntry]) -> dict:
        """Analyze daily memory patterns"""
        analysis = {
            "categories": defaultdict(int),
            "tags": defaultdict(int),
            "hourly_distribution": defaultdict(int),
            "estimated_sessions": 0,
            "key_memories": [],
            "avg_memory_length": 0,
            "longest_memory": "",
            "most_common_category": "",
            "most_common_tags": [],
        }

        if not memories:
            return analysis

        total_length = 0
        longest_length = 0
        session_gaps = []
        last_timestamp = None

        for memory in memories:
            # Category analysis
            analysis["categories"][memory.category] += 1

            # Tag analysis
            for tag in memory.tags:
                analysis["tags"][tag] += 1

            # Length analysis
            memory_length = len(memory.text)
            total_length += memory_length

            if memory_length > longest_length:
                longest_length = memory_length
                analysis["longest_memory"] = (
                    memory.text[:100] + "..." if len(memory.text) > 100 else memory.text
                )

            # Hourly distribution and session estimation
            try:
                memory_time = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                )
                hour = memory_time.hour
                analysis["hourly_distribution"][hour] += 1

                # Session gap analysis (more than 1 hour = new session)
                if last_timestamp:
                    gap = (memory_time - last_timestamp).total_seconds() / 3600
                    session_gaps.append(gap)
                last_timestamp = memory_time

            except (ValueError, AttributeError):
                continue

        # Calculate derived metrics
        analysis["avg_memory_length"] = total_length / len(memories) if memories else 0

        # Estimate session count based on time gaps
        session_count = 1  # Start with 1 session
        for gap in session_gaps:
            if gap > 1.0:  # More than 1 hour gap = new session
                session_count += 1
        analysis["estimated_sessions"] = session_count

        # Find most common category
        if analysis["categories"]:
            analysis["most_common_category"] = max(
                analysis["categories"], key=analysis["categories"].get
            )

        # Find most common tags
        if analysis["tags"]:
            sorted_tags = sorted(analysis["tags"].items(), key=lambda x: x[1], reverse=True)
            analysis["most_common_tags"] = [tag for tag, count in sorted_tags[:5]]

        # Identify key memories (longer than average or containing important tags)
        key_memory_threshold = analysis["avg_memory_length"] * 1.5
        important_tags = {"important", "key", "insight", "discovery", "solution", "breakthrough"}

        for memory in memories:
            is_key = (
                len(memory.text) > key_memory_threshold
                or any(tag.lower() in important_tags for tag in memory.tags)
                or memory.category in ["important", "insight", "discovery"]
            )
            if is_key:
                analysis["key_memories"].append(
                    memory.text[:150] + "..." if len(memory.text) > 150 else memory.text
                )

        return analysis

    def _generate_insights(self, memories: List[MemoryEntry], analysis: dict) -> List[str]:
        """Generate insights based on memory analysis"""
        insights = []

        if not memories:
            insights.append("No memories recorded for this day")
            return insights

        # Activity level insights
        memory_count = len(memories)
        if memory_count >= 20:
            insights.append(f"High activity day with {memory_count} memories - very engaged")
        elif memory_count >= 10:
            insights.append(f"Active day with {memory_count} memories - good engagement")
        elif memory_count >= 5:
            insights.append(f"Moderate activity with {memory_count} memories")
        else:
            insights.append(f"Light activity with {memory_count} memories")

        # Memory length insights
        avg_length = analysis["avg_memory_length"]
        if avg_length > 150:
            insights.append("Detailed memory entries suggest deep thinking and reflection")
        elif avg_length > 75:
            insights.append("Moderate detail in memory entries shows good documentation")
        else:
            insights.append("Brief memory entries - quick thoughts captured")

        # Category insights
        if analysis["most_common_category"]:
            category_count = analysis["categories"][analysis["most_common_category"]]
            percentage = (category_count / memory_count) * 100
            insights.append(
                f"Primary focus on '{analysis['most_common_category']}' ({percentage:.0f}% of memories)"
            )

        # Session insights
        session_count = analysis["estimated_sessions"]
        if session_count >= 5:
            insights.append(
                f"Multiple work sessions ({session_count}) indicate sustained engagement"
            )
        elif session_count >= 3:
            insights.append(f"Several sessions ({session_count}) show good daily structure")
        else:
            insights.append(f"Focused work in {session_count} session(s)")

        # Time distribution insights
        hourly_dist = analysis["hourly_distribution"]
        if hourly_dist:
            peak_hour = max(hourly_dist, key=hourly_dist.get)
            peak_period = self._get_time_period(peak_hour)
            insights.append(f"Most active during {peak_period} (hour {peak_hour})")

        # Tag insights
        if analysis["most_common_tags"]:
            top_tags = analysis["most_common_tags"][:3]
            insights.append(f"Key themes: {', '.join(top_tags)}")

        # Key memories insight
        if analysis["key_memories"]:
            insights.append(f"Captured {len(analysis['key_memories'])} significant insights")

        return insights

    def _get_time_period(self, hour: int) -> str:
        """Convert hour to time period description"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night/early morning"

    def _generate_summary(
        self, memories: List[MemoryEntry], analysis: dict, insights: List[str]
    ) -> str:
        """Generate a comprehensive reflection summary"""
        if not memories:
            return "No memories recorded for this day. Consider engaging more with the system."

        memory_count = len(memories)
        session_count = analysis["estimated_sessions"]
        avg_length = analysis["avg_memory_length"]

        summary_parts = [
            "Daily reflection summary:",
            f"• Recorded {memory_count} memories across {session_count} sessions",
            f"• Average memory length: {avg_length:.0f} characters",
        ]

        if analysis["most_common_category"]:
            category_count = analysis["categories"][analysis["most_common_category"]]
            summary_parts.append(
                f"• Primary focus: {analysis['most_common_category']} ({category_count} memories)"
            )

        if analysis["most_common_tags"]:
            top_tags = ", ".join(analysis["most_common_tags"][:3])
            summary_parts.append(f"• Key themes: {top_tags}")

        if analysis["key_memories"]:
            summary_parts.append(f"• Captured {len(analysis['key_memories'])} significant insights")

        # Add top insight
        if insights:
            summary_parts.append(f"• Key insight: {insights[0]}")

        return "\n".join(summary_parts)

    def get_reflection(self, date: str) -> Optional[DailyReflection]:
        """Get an existing daily reflection"""
        return self.reflection_storage.load_reflection(date)

    def get_recent_reflections(self, days: int = 7) -> List[DailyReflection]:
        """Get recent daily reflections"""
        reflections = []
        end_date = datetime.now().date()

        for i in range(days):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            reflection = self.reflection_storage.load_reflection(date_str)
            if reflection:
                reflections.append(reflection)

        return reflections

    def generate_weekly_summary(self, start_date: Optional[str] = None) -> dict:
        """Generate a weekly summary from daily reflections"""
        if start_date is None:
            # Use current week
            today = datetime.now().date()
            start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")

        week_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        weekly_summary = {
            "week_start": start_date,
            "daily_reflections": [],
            "total_memories": 0,
            "total_sessions": 0,
            "common_categories": defaultdict(int),
            "common_tags": defaultdict(int),
            "key_insights": [],
            "activity_pattern": [],
        }

        # Collect 7 days of reflections
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            reflection = self.reflection_storage.load_reflection(date_str)

            if reflection:
                weekly_summary["daily_reflections"].append(reflection)
                weekly_summary["total_memories"] += reflection.total_memories
                weekly_summary["total_sessions"] += reflection.session_count

                # Aggregate categories and tags
                for category, count in reflection.categories.items():
                    weekly_summary["common_categories"][category] += count

                for tag, count in reflection.tags.items():
                    weekly_summary["common_tags"][tag] += count

                # Collect insights
                weekly_summary["key_insights"].extend(reflection.insights)

                # Track daily activity
                weekly_summary["activity_pattern"].append(
                    {
                        "date": date_str,
                        "memory_count": reflection.total_memories,
                        "session_count": reflection.session_count,
                    }
                )

        return weekly_summary

    def auto_generate_missing_reflections(self, days_back: int = 7) -> List[str]:
        """Automatically generate missing daily reflections"""
        generated_dates = []
        end_date = datetime.now().date()

        for i in range(days_back):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")

            # Check if reflection already exists
            existing_reflection = self.reflection_storage.load_reflection(date_str)
            if not existing_reflection:
                # Generate reflection for this date
                try:
                    self.generate_daily_reflection(date_str)
                    generated_dates.append(date_str)
                except Exception as e:
                    print(f"Failed to generate reflection for {date_str}: {e}")

        return generated_dates
