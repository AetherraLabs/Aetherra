"""
Introspector Plugin for Lyrixa/Aetherra
Scans code and workflow files, summarizes, and stores self-insight.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class IntrospectorPlugin:
    name = "introspector_plugin"
    description = "Scans Lyrixa/Aetherra files and generates self-insight."
    input_schema = {
        "type": "object",
        "properties": {"target_files": {"type": "array", "items": {"type": "string"}}},
    }
    output_schema = {
        "type": "object",
        "properties": {"insights": {"type": "array", "items": {"type": "string"}}},
    }
    created_by = "Lyrixa"

    async def main(self, target_files: List[str], memory_system=None) -> Dict[str, Any]:
        insights = []
        for file_path in target_files:
            path = Path(file_path)
            if path.exists() and path.suffix in {".py", ".aether"}:
                try:
                    content = path.read_text(encoding="utf-8")
                    # Simple static analysis: look for TODO, FIXME, or suspicious patterns
                    if "TODO" in content or "FIXME" in content:
                        insights.append(f"{file_path}: Found TODO/FIXME comments.")
                    if "raise NotImplementedError" in content:
                        insights.append(
                            f"{file_path}: Unimplemented function detected."
                        )
                    # (Future: LLM-powered code review)
                except Exception as e:
                    insights.append(f"{file_path}: Error reading file: {e}")
        if memory_system and insights:
            await memory_system.store_enhanced_memory(
                content={"insights": insights, "target_files": target_files},
                context={"type": "self_insight", "source": "introspector_plugin"},
                tags=["self_insight", "introspection"],
                importance=0.8,
            )
        return {"insights": insights}
