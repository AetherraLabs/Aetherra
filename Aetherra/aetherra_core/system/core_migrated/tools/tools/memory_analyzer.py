"""
Memory Analyzer Tool for Lyrixa
===============================

Summarizes and scores memory patterns for intelligent insights.
"""

from typing import Dict, List

from ..models.model_router import router


class MemoryAnalyzer:
    """Analyzes memory patterns and generates insights"""

    def __init__(self, model_router=None):
        self.router = model_router or router

    def analyze_memory_patterns(self, memories: List[Dict]) -> Dict:
        """Analyze patterns in memory data"""

        if not memories:
            return {"analysis": "No memories to analyze", "patterns": []}

        # Extract memory content for analysis
        memory_texts = []
        for memory in memories:
            content = memory.get("content", memory.get("text", ""))
            if content:
                memory_texts.append(content)

        analysis_prompt = f"""Analyze these memory entries and identify patterns:

{chr(10).join([f"- {text[:200]}..." if len(text) > 200 else f"- {text}" for text in memory_texts[:20]])}

Identify:
1. Common themes or topics
2. Recurring patterns or behaviors
3. Learning progression
4. Areas of focus
5. Potential insights for improvement

Provide structured analysis:"""

        system_prompt = """You are a memory pattern analysis expert.
        Analyze the provided memories to extract meaningful patterns and insights.
        Focus on identifying learning progression, behavioral patterns, and actionable insights."""

        analysis_result = self.router.generate_response(
            prompt=analysis_prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("analysis"),
        )

        return {
            "analysis": analysis_result,
            "memory_count": len(memories),
            "patterns": self._extract_patterns(memories),
            "insights": self._generate_insights(memories),
        }

    def score_memory_importance(self, memory: Dict) -> float:
        """Score the importance of a single memory"""

        content = memory.get("content", memory.get("text", ""))
        if not content:
            return 0.0

        # Base scoring factors
        score = 0.5  # Base score

        # Length factor (longer memories often more important)
        if len(content) > 100:
            score += 0.1
        if len(content) > 500:
            score += 0.1

        # Keyword importance
        important_keywords = [
            "error",
            "problem",
            "solution",
            "learned",
            "discovered",
            "important",
            "critical",
            "breakthrough",
            "insight",
            "pattern",
            "relationship",
            "connection",
        ]

        content_lower = content.lower()
        keyword_count = sum(
            1 for keyword in important_keywords if keyword in content_lower
        )
        score += keyword_count * 0.05

        # Recency factor (newer memories slightly more important)
        if "timestamp" in memory:
            # This would need proper timestamp parsing
            score += 0.05

        # Tags factor
        tags = memory.get("tags", [])
        if tags:
            score += len(tags) * 0.02

        # Category factor
        important_categories = ["learning", "insight", "problem", "solution"]
        category = memory.get("category", "").lower()
        if category in important_categories:
            score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _extract_patterns(self, memories: List[Dict]) -> List[str]:
        """Extract common patterns from memories"""
        patterns = []

        # Category analysis
        categories = {}
        for memory in memories:
            category = memory.get("category", "uncategorized")
            categories[category] = categories.get(category, 0) + 1

        if categories:
            most_common = max(categories.keys(), key=lambda x: categories[x])
            patterns.append(
                f"Most common category: {most_common} ({categories[most_common]} memories)"
            )

        # Tag analysis
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.get("tags", []))

        if all_tags:
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[
                :3
            ]
            patterns.append(
                f"Common tags: {', '.join([f'{tag}({count})' for tag, count in common_tags])}"
            )

        return patterns

    def _generate_insights(self, memories: List[Dict]) -> List[str]:
        """Generate actionable insights from memory analysis"""
        insights = []

        # Memory count insights
        total_memories = len(memories)
        if total_memories > 100:
            insights.append(
                "Large memory collection - consider implementing memory cleanup"
            )
        elif total_memories < 10:
            insights.append(
                "Small memory collection - system is just starting to learn"
            )

        # Score distribution insights
        scores = [self.score_memory_importance(memory) for memory in memories]
        if scores:
            avg_score = sum(scores) / len(scores)
            high_value_count = len([s for s in scores if s > 0.7])

            if avg_score > 0.7:
                insights.append(
                    "High-value memory collection with many important entries"
                )
            elif high_value_count > 0:
                insights.append(
                    f"{high_value_count} high-value memories identified for priority retention"
                )

        return insights

    def cluster_memories(
        self, memories: List[Dict], max_clusters: int = 5
    ) -> Dict[str, List[Dict]]:
        """Simple clustering of memories by similarity"""

        if not memories:
            return {}

        # Simple keyword-based clustering
        clusters = {}

        for memory in memories:
            content = memory.get("content", memory.get("text", "")).lower()

            # Find best cluster or create new one
            best_cluster = None
            best_score = 0

            for cluster_name, cluster_memories in clusters.items():
                # Simple similarity based on common words
                cluster_content = " ".join(
                    [
                        m.get("content", m.get("text", "")).lower()
                        for m in cluster_memories
                    ]
                )

                common_words = len(set(content.split()) & set(cluster_content.split()))
                if common_words > best_score:
                    best_score = common_words
                    best_cluster = cluster_name

            # Add to best cluster or create new one
            if best_cluster and best_score > 2:
                clusters[best_cluster].append(memory)
            else:
                # Create new cluster
                category = memory.get("category", "general")
                cluster_key = f"{category}_{len(clusters)}"
                clusters[cluster_key] = [memory]

        return clusters


# Default instance
memory_analyzer = MemoryAnalyzer()
