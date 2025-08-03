#!/usr/bin/env python3
"""
🧠 PROJECT KNOWLEDGE RESPONDER
==============================

Specialized knowledge responder for project-specific and factual queries.
Integrates with the conversational engine to provide intelligent routing
for knowledge-based questions.

Features:
- Project-specific memory retrieval
- Factual question detection
- Simplified response synthesis
- Integration with LyrixaConversationalEngine
"""

import re
from typing import Any, Dict, List, Optional

try:
    from .advanced_vector_memory import AdvancedMemorySystem
except ImportError:
    # Fallback for standalone testing
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


class ProjectKnowledgeResponder:
    """
    Simplified knowledge responder focused on project-specific and factual queries.
    Designed for integration with the conversational engine.
    """

    def __init__(self, memory: AdvancedMemorySystem):
        """Initialize the Project Knowledge Responder."""
        self.memory = memory

        # Patterns for detecting factual/project questions
        self.factual_patterns = [
            r"\b(what|who|when|where|why|how)\b",
            r"\b(explain|describe|define|tell me about)\b",
            r"\b(aetherra|lyrixa|project)\b",
            r"\b(api|function|method|class|variable)\b",
            r"\b(documentation|docs|help|reference)\b",
            r"\b(error|issue|problem|bug)\b",
            r"\b(example|tutorial|guide|how to)\b",
        ]

        # Compiled regex patterns for efficiency
        self.factual_regex = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.factual_patterns
        ]

        print("🧠 Project Knowledge Responder initialized")
        print(f"   ✅ Memory system connected")
        print(f"   ✅ Factual pattern detection ready")

    def is_factual_or_project_query(self, query: str) -> bool:
        """
        Determine if the query is factual or project-related.

        Args:
            query: User's input query

        Returns:
            True if the query appears to be factual or project-related
        """
        # Check for factual patterns
        for pattern in self.factual_regex:
            if pattern.search(query):
                return True

        # Check for question marks (simple heuristic)
        if "?" in query:
            return True

        # Check for imperative verbs that suggest help requests
        imperative_words = [
            "show",
            "list",
            "find",
            "get",
            "create",
            "make",
            "build",
            "help",
        ]
        query_lower = query.lower()
        if any(word in query_lower for word in imperative_words):
            return True

        return False

    async def answer_question(self, query: str) -> str:
        """
        Generate an answer to a factual or project-related question.

        Args:
            query: The user's question

        Returns:
            A string response based on retrieved memories
        """
        try:
            # Search memory for relevant information
            results = await self._recall_memories(query, limit=5)

            if not results:
                return "I'm still learning, but I don't have an answer to that yet."

            # Get the top result
            top = results[0]

            # Extract content from the top result
            content = self._extract_content(top)

            if not content:
                return "I found some information, but it doesn't seem complete. Could you be more specific?"

            # Return the content
            return content

        except Exception as e:
            print(f"[WARN] Error in ProjectKnowledgeResponder: {e}")
            return "I encountered an issue retrieving that information. Please try rephrasing your question."

    async def _recall_memories(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories for the query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of memory dictionaries
        """
        try:
            # Use semantic search if available
            if hasattr(self.memory, "semantic_search"):
                memories = await self.memory.semantic_search(query, top_k=limit)
                return memories if memories else []

            # Fallback to other search methods
            elif hasattr(self.memory, "_fallback_search"):
                memories = await self.memory._fallback_search(query, limit, None)
                return memories if memories else []

            else:
                print("[WARN] No search methods available in memory system")
                return []

        except Exception as e:
            print(f"[WARN] Memory recall failed: {e}")
            return []

    def _extract_content(self, memory: Dict[str, Any]) -> str:
        """
        Extract meaningful content from a memory object.

        Args:
            memory: Memory dictionary from the memory system

        Returns:
            Extracted content string
        """
        # Try different content field names
        content = (
            memory.get("content", "")
            or memory.get("text", "")
            or memory.get("summary", "")
            or ""
        )

        # If content is a dictionary, extract text from it
        if isinstance(content, dict):
            content = (
                content.get("summary", "")
                or content.get("text", "")
                or content.get("content", "")
                or str(content)
            )

        return str(content).strip()

    async def get_enhanced_response(self, query: str) -> Dict[str, Any]:
        """
        Get an enhanced response with metadata.

        Args:
            query: The user's question

        Returns:
            Dictionary with response, confidence, and metadata
        """
        try:
            # Get memories
            results = await self._recall_memories(query, limit=5)

            # Calculate confidence based on number and quality of results
            confidence = 0.0
            if results:
                # Simple confidence calculation
                confidence = min(0.9, len(results) * 0.15 + 0.3)
                if len(results) >= 3:
                    confidence = min(0.9, confidence + 0.1)

            # Generate response
            response_text = await self.answer_question(query)

            return {
                "response": response_text,
                "confidence": confidence,
                "sources_count": len(results),
                "is_knowledge_based": len(results) > 0,
                "query_type": "factual"
                if self.is_factual_or_project_query(query)
                else "general",
            }

        except Exception as e:
            return {
                "response": "I encountered an error processing your question.",
                "confidence": 0.0,
                "sources_count": 0,
                "is_knowledge_based": False,
                "error": str(e),
            }


# Integration helper functions
def is_knowledge_query(user_input: str) -> bool:
    """
    Helper function to determine if a query should be routed to knowledge responder.
    Can be used by the conversational engine for routing decisions.
    """
    # Create a temporary responder instance for pattern matching
    # In practice, this would be done more efficiently
    knowledge_patterns = [
        r"\b(what|who|when|where|why|how)\b",
        r"\b(explain|describe|define|tell me about)\b",
        r"\b(aetherra|lyrixa|project)\b",
        r"\b(api|function|method|class|variable)\b",
        r"\b(documentation|docs|help|reference)\b",
        r"\b(example|tutorial|guide|how to)\b",
    ]

    for pattern in knowledge_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return True

    return "?" in user_input


async def create_project_knowledge_responder(
    memory_system: AdvancedMemorySystem,
) -> ProjectKnowledgeResponder:
    """
    Factory function to create a Project Knowledge Responder.

    Args:
        memory_system: The memory system to use

    Returns:
        Initialized ProjectKnowledgeResponder instance
    """
    responder = ProjectKnowledgeResponder(memory_system)
    print("🧠 Project Knowledge Responder ready")
    return responder


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def demo():
        """Demo the Project Knowledge Responder."""
        print("🧠 PROJECT KNOWLEDGE RESPONDER DEMO")
        print("=" * 45)

        # Create memory system (for demo)
        memory = AdvancedMemorySystem()
        responder = await create_project_knowledge_responder(memory)

        # Test queries
        test_queries = [
            "What is Aetherra?",
            "How do I use the API?",
            "Explain the memory system",
            "Hello there!",  # Not factual
            "I love this project",  # Not factual
            "What functions are available?",
            "Tell me about Lyrixa",
        ]

        for query in test_queries:
            is_factual = responder.is_factual_or_project_query(query)
            print(f"\n🔍 Query: {query}")
            print(f"📊 Factual: {is_factual}")

            if is_factual:
                response = await responder.get_enhanced_response(query)
                print(f"📝 Response: {response['response']}")
                print(f"📈 Confidence: {response['confidence']:.2f}")

    # Run demo
    asyncio.run(demo())
