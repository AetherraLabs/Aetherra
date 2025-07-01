#!/usr/bin/env python3
"""
Script to fix unsafe method calls in demo.py
"""

import re

# Read the file
with open("src/neurocode/cli/demo.py", encoding="utf-8") as f:
    content = f.read()

# Replace all direct calls with safe wrapper calls
content = re.sub(
    r"self\.contextual_adaptation\.detect_context\(", "self._safe_detect_context(", content
)
content = re.sub(
    r"self\.contextual_adaptation\.adapt_persona\(", "self._safe_adapt_persona(", content
)
content = re.sub(
    r"self\.emotional_memory\.get_emotional_guidance\(", "self._safe_get_guidance(", content
)
content = re.sub(
    r"self\.emotional_memory\.record_interaction\(", "self._safe_record_interaction(", content
)

# Fix other None accesses
content = re.sub(
    r"self\.persona_engine\.current_persona",
    "self.persona_engine.current_persona if self.persona_engine else None",
    content,
)
content = re.sub(
    r"self\.emotional_memory\.get_emotional_trends\(\)",
    "self.emotional_memory.get_emotional_trends() if self.emotional_memory else []",
    content,
)
content = re.sub(
    r"len\(self\.emotional_memory\.memories\)",
    'len(self.emotional_memory.memories) if self.emotional_memory and hasattr(self.emotional_memory, "memories") else 0',
    content,
)
content = re.sub(
    r"self\.persona_engine\.set_persona\(",
    "self.persona_engine.set_persona( if self.persona_engine else lambda x: None)(",
    content,
)

# Write the file back
with open("src/neurocode/cli/demo.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated all unsafe calls in demo.py")
