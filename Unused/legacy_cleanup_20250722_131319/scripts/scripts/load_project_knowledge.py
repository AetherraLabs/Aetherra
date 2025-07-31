#!/usr/bin/env python3
"""
🧠 LYRIXA PROJECT KNOWLEDGE LOADER
==================================

Loads project knowledge from JSON seed files into Lyrixa's memory system.
Designed to ingest structured knowledge about Aetherra, Lyrixa, and the platform
to enable intelligent responses to project-related queries.

Features:
- Loads JSON knowledge seed files
- Processes content and summaries
- Tags and categorizes knowledge
- Bulk import with progress tracking
- Deduplication and validation
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem


class ProjectKnowledgeLoader:
    """
    Loads project knowledge from JSON files into the memory system.
    """

    def __init__(self, memory_system: Optional[AdvancedMemorySystem] = None):
        """Initialize the knowledge loader."""
        self.memory_system = memory_system or AdvancedMemorySystem()
        self.loaded_ids = set()
        self.stats = {"total_items": 0, "loaded": 0, "skipped": 0, "errors": 0}

    async def load_from_json(
        self, json_path: str, verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Load knowledge from a JSON seed file.

        Args:
            json_path: Path to the JSON file
            verbose: Whether to print progress information

        Returns:
            Dictionary with loading statistics
        """
        if verbose:
            print(f"🧠 LOADING PROJECT KNOWLEDGE FROM {json_path}")
            print("=" * 60)

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of knowledge items")

            self.stats["total_items"] = len(data)

            if verbose:
                print(f"📚 Found {len(data)} knowledge items to process...")

            # Process each knowledge item
            for i, item in enumerate(data, 1):
                if verbose and i % 10 == 0:
                    print(f"   📥 Processing item {i}/{len(data)}...")

                try:
                    await self._process_knowledge_item(item)
                    self.stats["loaded"] += 1
                except Exception as e:
                    self.stats["errors"] += 1
                    if verbose:
                        print(f"   ⚠️ Error processing item {i}: {e}")

            if verbose:
                print(f"\n✅ KNOWLEDGE LOADING COMPLETE")
                print(f"   📊 Loaded: {self.stats['loaded']}")
                print(f"   ⏭️ Skipped: {self.stats['skipped']}")
                print(f"   ❌ Errors: {self.stats['errors']}")
                print(
                    f"   📈 Success Rate: {(self.stats['loaded'] / self.stats['total_items'] * 100):.1f}%"
                )

            return self.stats

        except FileNotFoundError:
            raise FileNotFoundError(f"Knowledge file not found: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    async def _process_knowledge_item(self, item: Dict[str, Any]) -> None:
        """
        Process a single knowledge item from the JSON.

        Args:
            item: Knowledge item dictionary
        """
        # Extract fields
        item_id = item.get("id", "unknown")
        content = item.get("content", "")
        summary = item.get("summary", "")
        tags = item.get("tags", [])

        # Skip if already loaded
        if item_id in self.loaded_ids:
            self.stats["skipped"] += 1
            return

        # Use summary if content is empty, or content if summary is empty
        if not content and not summary:
            raise ValueError(f"Item {item_id} has no content or summary")

        # Prefer content over summary, but use summary if content is missing
        main_content = content if content else summary

        # Clean up content (remove excessive whitespace)
        main_content = self._clean_content(main_content)

        # Determine memory type based on tags
        memory_type = self._determine_memory_type(tags)

        # Set confidence based on content quality
        confidence = self._calculate_confidence(main_content, summary)

        # Create context
        context = {
            "source": "project_knowledge_seed",
            "item_id": item_id,
            "has_summary": bool(summary),
            "original_tags": tags,
        }

        # Store in memory system
        await self.memory_system.store_memory(
            content=main_content,
            memory_type=memory_type,
            tags=self._normalize_tags(tags),
            confidence=confidence,
            context=context,
        )

        # Track loaded items
        self.loaded_ids.add(item_id)

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text."""
        # Remove excessive whitespace
        cleaned = " ".join(content.split())

        # Remove markdown artifacts that don't add meaning
        cleaned = cleaned.replace("\\n", " ")
        cleaned = cleaned.replace("<!--", "")
        cleaned = cleaned.replace("-->", "")

        # Ensure reasonable length (truncate if too long)
        if len(cleaned) > 2000:
            cleaned = cleaned[:1900] + "..."

        return cleaned.strip()

    def _determine_memory_type(self, tags: List[str]) -> str:
        """Determine appropriate memory type based on tags."""
        if "aetherra" in tags:
            return "project_info"
        elif "lyrixa" in tags:
            return "assistant_info"
        elif any(tag in ["technical", "api", "development"] for tag in tags):
            return "technical_info"
        elif any(tag in ["tutorial", "guide", "documentation"] for tag in tags):
            return "documentation"
        else:
            return "general_knowledge"

    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """Normalize and enhance tags."""
        normalized = []

        for tag in tags:
            # Convert to lowercase
            tag = tag.lower().strip()

            # Add to normalized list
            if tag and tag not in normalized:
                normalized.append(tag)

        # Add automatic tags
        if "aetherra" in normalized or "project_knowledge" in normalized:
            if "platform" not in normalized:
                normalized.append("platform")

        if "lyrixa" in normalized:
            if "assistant" not in normalized:
                normalized.append("assistant")

        return normalized

    def _calculate_confidence(self, content: str, summary: str) -> float:
        """Calculate confidence score based on content quality."""
        base_confidence = 0.8

        # Increase confidence for longer, more detailed content
        if len(content) > 500:
            base_confidence += 0.1

        # Increase confidence if both content and summary exist
        if content and summary and content != summary:
            base_confidence += 0.1

        # Decrease confidence for very short content
        if len(content) < 100:
            base_confidence -= 0.2

        return max(0.3, min(1.0, base_confidence))


async def load_project_knowledge(
    json_path: str = "lyrixa_project_knowledge_seed.json", verbose: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to load project knowledge.

    Args:
        json_path: Path to the knowledge JSON file
        verbose: Whether to show progress information

    Returns:
        Loading statistics
    """
    loader = ProjectKnowledgeLoader()
    return await loader.load_from_json(json_path, verbose=verbose)


async def test_knowledge_loading():
    """Test the knowledge loading process."""
    print("🧪 TESTING KNOWLEDGE LOADING")
    print("=" * 50)

    # Check if the knowledge file exists
    knowledge_file = Path("lyrixa_project_knowledge_seed.json")
    if not knowledge_file.exists():
        # Try the Desktop location
        knowledge_file = Path("../lyrixa_project_knowledge_seed.json")
        if not knowledge_file.exists():
            print("❌ Knowledge seed file not found!")
            print("   Expected: lyrixa_project_knowledge_seed.json")
            return

    print(f"📁 Found knowledge file: {knowledge_file}")

    # Load the knowledge
    try:
        stats = await load_project_knowledge(str(knowledge_file))

        print(f"\n🎯 LOADING TEST COMPLETE")
        print(f"   Success rate: {(stats['loaded'] / stats['total_items'] * 100):.1f}%")

        # Test knowledge retrieval
        print(f"\n🔍 TESTING KNOWLEDGE RETRIEVAL")

        memory = AdvancedMemorySystem()

        test_queries = [
            "What is Aetherra?",
            "Who is Lyrixa?",
            "How does .aether work?",
            "What makes this platform unique?",
        ]

        for query in test_queries:
            results = await memory.semantic_search(query, top_k=2)
            print(f"\nQuery: {query}")
            if results:
                print(f"Found: {len(results)} relevant items")
                print(f"Best match: {results[0]['content'][:150]}...")
            else:
                print("No results found")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            asyncio.run(test_knowledge_loading())
        else:
            # Load specific file
            asyncio.run(load_project_knowledge(sys.argv[1]))
    else:
        # Default: try to load from standard location
        asyncio.run(test_knowledge_loading())
