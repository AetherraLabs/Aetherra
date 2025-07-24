"""
Aetherra Summarizer Plugin
Provides text summarization capabilities using various AI models.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SummarizerPlugin:
    """
    Plugin for text summarization with configurable methods and styles
    """

    def __init__(self):
        self.name = "summarizer"
        self.version = "1.0.0"
        self.description = "Advanced text summarization with multiple methods"
        self.capabilities = [
            "text_summarization",
            "key_points_extraction",
            "abstract_generation",
            "executive_summary",
        ]

    async def initialize(self):
        """Initialize the summarizer plugin"""
        logger.info("Summarizer plugin initialized")
        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute summarization based on the provided parameters

        Args:
            text (str): Text to summarize
            method (str): Summarization method ('extractive', 'abstractive', 'hybrid')
            length (str): Summary length ('short', 'medium', 'long')
            style (str): Summary style ('bullets', 'paragraph', 'executive')
            focus (str): Focus area ('main_points', 'technical', 'business')
        """
        text = kwargs.get("text", "")
        method = kwargs.get("method", "hybrid")
        length = kwargs.get("length", "medium")
        style = kwargs.get("style", "paragraph")
        focus = kwargs.get("focus", "main_points")

        if not text:
            return {"success": False, "error": "No text provided for summarization"}

        try:
            summary = await self._generate_summary(text, method, length, style, focus)

            return {
                "success": True,
                "summary": summary,
                "method": method,
                "length": length,
                "style": style,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_summary(
        self, text: str, method: str, length: str, style: str, focus: str
    ) -> str:
        """Generate summary based on specified parameters"""

        # Determine target length
        word_count = len(text.split())
        if length == "short":
            target_ratio = 0.15
        elif length == "medium":
            target_ratio = 0.3
        else:  # long
            target_ratio = 0.5

        target_words = max(50, int(word_count * target_ratio))

        # Apply method-specific summarization
        if method == "extractive":
            summary = await self._extractive_summary(text, target_words, focus)
        elif method == "abstractive":
            summary = await self._abstractive_summary(text, target_words, focus)
        else:  # hybrid
            summary = await self._hybrid_summary(text, target_words, focus)

        # Format according to style
        formatted_summary = await self._format_summary(summary, style)

        return formatted_summary

    async def _extractive_summary(
        self, text: str, target_words: int, focus: str
    ) -> str:
        """Extractive summarization - select key sentences"""
        sentences = self._split_sentences(text)

        # Score sentences based on focus
        scored_sentences = []
        for sentence in sentences:
            score = await self._score_sentence(sentence, focus, text)
            scored_sentences.append((score, sentence))

        # Sort by score and select top sentences
        scored_sentences.sort(reverse=True)

        selected_sentences = []
        word_count = 0

        for score, sentence in scored_sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= target_words:
                selected_sentences.append(sentence)
                word_count += sentence_words
            elif word_count >= target_words * 0.8:  # Allow 80% of target
                break

        # Maintain original order
        original_order = []
        for sentence in sentences:
            if sentence in selected_sentences:
                original_order.append(sentence)

        return " ".join(original_order)

    async def _abstractive_summary(
        self, text: str, target_words: int, focus: str
    ) -> str:
        """Abstractive summarization - generate new text"""
        # This would typically use an AI model for abstractive summarization
        # For now, implementing a simplified version

        key_points = await self._extract_key_points(text, focus)

        # Generate summary from key points
        if focus == "technical":
            summary = f"Technical overview: {'. '.join(key_points[:3])}."
        elif focus == "business":
            summary = f"Business summary: {'. '.join(key_points[:3])}."
        else:
            summary = f"Summary: {'. '.join(key_points[:3])}."

        # Trim to target length
        words = summary.split()
        if len(words) > target_words:
            summary = " ".join(words[:target_words]) + "..."

        return summary

    async def _hybrid_summary(self, text: str, target_words: int, focus: str) -> str:
        """Hybrid summarization - combine extractive and abstractive"""
        # Use extractive for 70% of content, abstractive for 30%
        extractive_words = int(target_words * 0.7)
        abstractive_words = target_words - extractive_words

        extractive_part = await self._extractive_summary(text, extractive_words, focus)
        abstractive_part = await self._abstractive_summary(
            text, abstractive_words, focus
        )

        return f"{extractive_part} {abstractive_part}"

    async def _format_summary(self, summary: str, style: str) -> str:
        """Format summary according to specified style"""
        if style == "bullets":
            sentences = self._split_sentences(summary)
            return "\n".join(
                f"• {sentence.strip()}" for sentence in sentences if sentence.strip()
            )
        elif style == "executive":
            return f"EXECUTIVE SUMMARY\n\n{summary}\n\nKey Points:\n• {summary.split('.')[0]}.\n• {summary.split('.')[1] if len(summary.split('.')) > 1 else 'Additional details provided in full text.'}"
        else:  # paragraph
            return summary

    async def _score_sentence(self, sentence: str, focus: str, full_text: str) -> float:
        """Score a sentence based on importance and focus"""
        score = 0.0
        words = sentence.lower().split()

        # Base score from sentence length (prefer medium-length sentences)
        word_count = len(words)
        if 10 <= word_count <= 25:
            score += 1.0
        elif 5 <= word_count <= 35:
            score += 0.5

        # Position score (first and last sentences get bonus)
        sentences = self._split_sentences(full_text)
        sentence_index = sentences.index(sentence) if sentence in sentences else -1
        if sentence_index == 0 or sentence_index == len(sentences) - 1:
            score += 0.5

        # Focus-specific scoring
        if focus == "technical":
            technical_terms = [
                "algorithm",
                "system",
                "method",
                "process",
                "implementation",
                "technical",
                "analysis",
            ]
            score += sum(0.1 for word in words if word in technical_terms)
        elif focus == "business":
            business_terms = [
                "revenue",
                "profit",
                "market",
                "customer",
                "business",
                "strategy",
                "growth",
                "value",
            ]
            score += sum(0.1 for word in words if word in business_terms)
        else:  # main_points
            # Look for signal words
            signal_words = [
                "important",
                "significant",
                "key",
                "main",
                "primary",
                "essential",
                "critical",
            ]
            score += sum(0.2 for word in words if word in signal_words)

        return score

    async def _extract_key_points(self, text: str, focus: str) -> List[str]:
        """Extract key points from text based on focus"""
        sentences = self._split_sentences(text)

        key_points = []
        for sentence in sentences:
            score = await self._score_sentence(sentence, focus, text)
            if score > 0.5:  # Threshold for key points
                key_points.append(sentence.strip())

        return key_points[:5]  # Return top 5 key points

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re

        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    async def get_help(self) -> Dict[str, Any]:
        """Get help information for the plugin"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "parameters": {
                "text": "Text to summarize (required)",
                "method": "Summarization method: extractive, abstractive, hybrid (default: hybrid)",
                "length": "Summary length: short, medium, long (default: medium)",
                "style": "Output style: bullets, paragraph, executive (default: paragraph)",
                "focus": "Focus area: main_points, technical, business (default: main_points)",
            },
            "examples": [
                {
                    "description": "Basic summarization",
                    "usage": 'await plugin.execute(text="Your text here")',
                },
                {
                    "description": "Technical summary with bullets",
                    "usage": 'await plugin.execute(text="Your text", method="extractive", style="bullets", focus="technical")',
                },
                {
                    "description": "Executive summary",
                    "usage": 'await plugin.execute(text="Your text", length="short", style="executive", focus="business")',
                },
            ],
        }


# Plugin factory function
def create_plugin():
    """Factory function to create plugin instance"""
    return SummarizerPlugin()


# Plugin metadata
PLUGIN_METADATA = {
    "name": "summarizer",
    "version": "1.0.0",
    "description": "Advanced text summarization plugin",
    "author": "Aetherra Team",
    "category": "text_processing",
    "tags": ["summarization", "text", "nlp", "analysis"],
    "requirements": [],
    "capabilities": [
        "text_summarization",
        "key_points_extraction",
        "abstract_generation",
        "executive_summary",
    ],
}
