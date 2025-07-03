#!/usr/bin/env python3
"""
COMPREHENSIVE IMPORT FIXER
Systematically fixes all imports after rebranding
"""

import os
import re
from pathlib import Path

# Define all import mappings
IMPORT_MAPPINGS = {
    # Module path mappings - from imports
    r"from\s+src\.neurocode\.ui\.neuroplex\s+import": "from src.aetherra.ui.lyrixa import",
    r"from\s+src\.neurocode\.ui\.neuro_chat\s+import": "from src.aetherra.ui.lyrixa_assistant import",
    r"from\s+src\.neurocode\.ui\.enhanced_neuroplex\s+import": "from src.aetherra.ui.enhanced_lyrixa import",
    r"from\s+src\.neurocode\.core\.interpreter\s+import": "from src.aetherra.core.aetherra_interpreter import",
    r"from\s+src\.neurocode\.core\.memory\s+import": "from src.aetherra.core.aetherra_memory import",
    r"from\s+src\.neurocode\.core\.neurocode_parser\s+import": "from src.aetherra.core.aetherra_parser import",
    r"from\s+src\.neurocode\.core\.neurocode_grammar\s+import": "from src.aetherra.core.aetherra_grammar import",
    # Without src prefix
    r"from\s+neurocode\.ui\.neuroplex\s+import": "from aetherra.ui.lyrixa import",
    r"from\s+neurocode\.ui\.neuro_chat\s+import": "from aetherra.ui.lyrixa_assistant import",
    r"from\s+neurocode\.ui\.enhanced_neuroplex\s+import": "from aetherra.ui.enhanced_lyrixa import",
    r"from\s+neurocode\.core\.interpreter\s+import": "from aetherra.core.aetherra_interpreter import",
    r"from\s+neurocode\.core\.memory\s+import": "from aetherra.core.aetherra_memory import",
    r"from\s+neurocode\.core\.neurocode_parser\s+import": "from aetherra.core.aetherra_parser import",
    r"from\s+neurocode\.core\.neurocode_grammar\s+import": "from aetherra.core.aetherra_grammar import",
    # Direct import mappings
    r"import\s+src\.neurocode\.ui\.neuroplex": "import src.aetherra.ui.lyrixa",
    r"import\s+src\.neurocode\.ui\.neuro_chat": "import src.aetherra.ui.lyrixa_assistant",
    r"import\s+src\.neurocode\.ui\.enhanced_neuroplex": "import src.aetherra.ui.enhanced_lyrixa",
    r"import\s+src\.neurocode\.core\.interpreter": "import src.aetherra.core.aetherra_interpreter",
    r"import\s+src\.neurocode\.core\.memory": "import src.aetherra.core.aetherra_memory",
    # Generic patterns
    r"from\s+src\.neurocode\s+import": "from src.aetherra import",
    r"import\s+src\.neurocode": "import src.aetherra",
    r"from\s+neurocode\s+import": "from aetherra import",
    r"import\s+neurocode": "import aetherra",
    # Relative imports
    r"from\s+\.neurocode\s+import": "from .aetherra import",
    r"from\s+\.\.neurocode\s+import": "from ..aetherra import",
    # Chat router specific
    r"from\s+core\.chat_router\s+import\s+AetherraChatRouter": "from core.chat_router import AetherraChatRouter",
    r"from\s+\.chat_router\s+import\s+AetherraChatRouter": "from .chat_router import AetherraChatRouter",
    # Memory specific
    r"from\s+core\.memory\s+import\s+AetherraMemory": "from core.aetherra_memory import AetherraMemory",
    r"from\s+\.memory\s+import\s+AetherraMemory": "from .aetherra_memory import AetherraMemory",
    # Class name mappings in imports
    r"\bNeuroCodeInterpreter\b": "AetherraInterpreter",
    r"\bEnhancedNeuroCodeInterpreter\b": "EnhancedAetherraInterpreter",
    r"\bNeuroplexWindow\b": "LyrixaWindow",
    r"\bEnhancedNeuroplexWindow\b": "EnhancedLyrixaWindow",
    r"\bNeuroCodeChatRouter\b": "AetherraChatRouter",
    r"\bNeuroMemory\b": "AetherraMemory",
    r"\bNeuroChatInterface\b": "LyrixaAssistantInterface",
    r"\bNeuroCodeParser\b": "AetherraParser",
    r"\bNeuroCodeGrammar\b": "AetherraGrammar",
    r"\bNeuroCodeLexer\b": "AetherraLexer",
}


def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Apply all mappings
        for pattern, replacement in IMPORT_MAPPINGS.items():
            matches = re.findall(pattern, content)
            if matches:
                changes_made.extend(matches)
            content = re.sub(pattern, replacement, content)

        # Write back if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes_made

        return False, []
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False, []


def fix_all_imports():
    """Fix imports in all Python files."""
    fixed_count = 0
    total_count = 0
    all_changes = []

    print("Scanning for Python files...")
    py_files = list(Path(".").rglob("*.py"))
    py_files = [
        f for f in py_files if ".git" not in str(f) and "__pycache__" not in str(f)
    ]

    print(f"Found {len(py_files)} Python files to check")
    print("=" * 50)

    for py_file in py_files:
        total_count += 1
        fixed, changes = fix_imports_in_file(py_file)
        if fixed:
            fixed_count += 1
            print(f"✅ Fixed: {py_file}")
            if changes:
                for change in changes[:3]:  # Show first 3 changes
                    print(f"   - {change}")
                if len(changes) > 3:
                    print(f"   - ... and {len(changes) - 3} more")
            all_changes.extend(changes)
        else:
            print(f"⚪ No changes: {py_file}")

    print("=" * 50)
    print(f"Summary: Fixed {fixed_count} out of {total_count} files")
    print(f"Total import changes made: {len(all_changes)}")

    return fixed_count, total_count


if __name__ == "__main__":
    print("🔧 FIXING ALL IMPORTS POST-REBRAND...")
    print("=" * 50)
    fixed, total = fix_all_imports()
    print("\n🎉 Import fixing complete!")
    print(f"Result: {fixed}/{total} files updated")
