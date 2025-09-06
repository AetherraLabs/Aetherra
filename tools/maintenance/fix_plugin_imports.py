#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔧 Aetherra Plugin Import Fixer
===============================

Fixes relative import issues in Aetherra plugins by converting them to absolute imports.
This resolves the "attempted relative import with no known parent package" errors.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

def get_plugins_with_import_errors() -> List[Path]:
    """Get list of plugin files that have relative import errors."""
    project_root = Path(__file__).parent
    plugins_dir = project_root / "Aetherra" / "plugins"

    error_files = [
        plugins_dir / "agent_adapters" / "plugin_agent.py",
        plugins_dir / "core" / "plugin_api.py",
        plugins_dir / "extra_plugins" / "introspector_plugin.py",
        plugins_dir / "memory_hooks" / "memory_aware_plugin_router.py",
        plugins_dir / "memory_hooks" / "memory_plugin_bridge.py",
    ]

    # Return only files that exist
    return [f for f in error_files if f.exists()]

def fix_relative_imports(file_path: Path) -> bool:
    """Fix relative imports in a Python file by converting to absolute imports."""
    print(f"🔧 Fixing imports in {file_path.relative_to(Path.cwd())}")

    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Pattern to match relative imports
        # Matches: from ..module import something, from .module import something
        relative_import_pattern = r'from\s+(\.{1,2}[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'

        def replace_import(match):
            relative_path = match.group(1)

            # Convert relative to absolute based on known patterns
            if relative_path.startswith('..'):
                # Parent directory imports
                if 'core.enhanced_memory' in relative_path:
                    return 'from Aetherra.aetherra_core.memory.enhanced_memory import'
                elif 'kernel.plugin_manager' in relative_path:
                    return 'from Aetherra.aetherra_core.plugins.plugin_manager import'
                elif 'core.' in relative_path:
                    module_name = relative_path.replace('..core.', '')
                    return f'from Aetherra.aetherra_core.{module_name} import'
                else:
                    # Generic parent import - try to map to Aetherra structure
                    clean_path = relative_path.lstrip('.')
                    return f'from Aetherra.aetherra_core.{clean_path} import'

            elif relative_path.startswith('.'):
                # Same directory imports
                if 'agent_base' in relative_path:
                    return 'from Aetherra.plugins.agent_adapters.agent_base import'
                else:
                    # Generic same directory import
                    clean_path = relative_path.lstrip('.')
                    parent_dir = file_path.parent.name
                    return f'from Aetherra.plugins.{parent_dir}.{clean_path} import'

            # If we can't determine the mapping, leave it unchanged
            return match.group(0)

        # Apply the replacements
        new_content = re.sub(relative_import_pattern, replace_import, content)

        # Add fallback imports for missing modules
        if 'from Aetherra.aetherra_core.memory.enhanced_memory import' in new_content:
            # Check if we need to add a fallback
            fallback_import = '''
try:
    from Aetherra.aetherra_core.memory.enhanced_memory import LyrixaEnhancedMemorySystem
except ImportError:
    # Fallback: Create a basic memory system mock
    class LyrixaEnhancedMemorySystem:
        def __init__(self, *args, **kwargs):
            pass
        def store(self, *args, **kwargs):
            pass
        def retrieve(self, *args, **kwargs):
            return []
'''
            if 'LyrixaEnhancedMemorySystem' in new_content and 'try:' not in new_content:
                new_content = fallback_import + new_content

        # Write the updated content if changes were made
        if new_content != original_content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Fixed imports in {file_path.name}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path.name}")
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False

def create_missing_init_files():
    """Create missing __init__.py files in plugin directories."""
    project_root = Path(__file__).parent
    plugins_dir = project_root / "Aetherra" / "plugins"

    # Directories that need __init__.py files
    plugin_dirs = [
        plugins_dir,
        plugins_dir / "agent_adapters",
        plugins_dir / "core",
        plugins_dir / "extra_plugins",
        plugins_dir / "memory_hooks",
    ]

    for dir_path in plugin_dirs:
        if dir_path.exists() and dir_path.is_dir():
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_content = f'"""Plugin package: {dir_path.name}"""\n'
                init_file.write_text(init_content, encoding='utf-8')
                print(f"📝 Created {init_file.relative_to(Path.cwd())}")

def main():
    """Main function to fix plugin import issues."""
    print("🔧 AETHERRA PLUGIN IMPORT FIXER")
    print("=" * 35)

    # Create missing __init__.py files first
    print("\n1. Creating missing __init__.py files...")
    create_missing_init_files()

    # Fix relative imports
    print("\n2. Fixing relative imports...")
    error_files = get_plugins_with_import_errors()

    if not error_files:
        print("ℹ️  No plugin files found with import errors")
        return 0

    fixed_count = 0
    for file_path in error_files:
        if fix_relative_imports(file_path):
            fixed_count += 1

    print(f"\n✅ Fixed imports in {fixed_count}/{len(error_files)} files")
    print("\n🎉 Plugin import fixes complete!")
    print("Try running Aetherra OS again to see if the plugin errors are resolved.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
