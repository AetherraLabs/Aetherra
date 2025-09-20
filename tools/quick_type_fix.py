#!/usr/bin/env python3
"""
Quick Type Annotation Fixer
===========================

Focuses on the most common and straightforward type annotation fixes
for the Aetherra project to improve code quality quickly.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def fix_common_patterns(content: str) -> Tuple[str, bool]:
    """Fix the most common missing type annotation patterns."""
    original_content = content

    # Pattern 1: __init__ methods without return annotations
    content = re.sub(r"def __init__\(([^)]+)\):", r"def __init__(\1) -> None:", content)

    # Pattern 2: Simple setup/update/clear methods
    setup_methods = [
        "setup",
        "update",
        "clear",
        "reset",
        "initialize",
        "cleanup",
        "close",
        "save",
        "delete",
        "remove",
        "add",
        "set_",
        "enable",
        "disable",
        "start",
        "stop",
        "pause",
        "resume",
    ]

    for method in setup_methods:
        pattern = rf"def ({method}[^(]*)\(([^)]*)\):"
        replacement = rf"def \1(\2) -> None:"
        content = re.sub(pattern, replacement, content)

    # Pattern 3: Boolean methods (is_, has_, can_, should_, check_, validate_)
    bool_methods = ["is_", "has_", "can_", "should_", "check_", "validate_"]

    for method in bool_methods:
        pattern = rf"def ({method}[^(]*)\(([^)]*)\):"
        replacement = rf"def \1(\2) -> bool:"
        content = re.sub(pattern, replacement, content)

    # Pattern 4: String methods (__str__, __repr__, get_name, get_title, etc.)
    string_methods = ["__str__", "__repr__", "get_name", "get_title", "get_id"]

    for method in string_methods:
        pattern = rf"def ({method})\(([^)]*)\):"
        replacement = rf"def \1(\2) -> str:"
        content = re.sub(pattern, replacement, content)

    # Pattern 5: Common parameter types
    param_fixes = [
        (r"(\w+): str = None", r"\1: str | None = None"),
        (r"(\w+): int = None", r"\1: int | None = None"),
        (r"(\w+): bool = None", r"\1: bool | None = None"),
        (r"(\w+) = None\)", r"\1: Any = None)"),
        (r"(\w+): dict = None", r"\1: dict[str, Any] | None = None"),
        (r"(\w+): list = None", r"\1: list[Any] | None = None"),
    ]

    for pattern, replacement in param_fixes:
        content = re.sub(pattern, replacement, content)

    # Check if we need to add typing imports
    needs_any = "Any" in content and "from typing import" not in content
    needs_typing = needs_any

    if needs_typing and "from typing import" not in content:
        # Find where to insert the import
        lines = content.split("\n")
        insert_idx = 0

        # Find the best place to insert after existing imports
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")) or line.strip() == "":
                insert_idx = i + 1
            elif (
                line.strip().startswith("#")
                or line.strip().startswith('"""')
                or line.strip().startswith("'''")
            ):
                continue
            else:
                break

        # Insert the import
        imports = []
        if needs_any:
            imports.append("Any")

        if imports:
            import_line = f"from typing import {', '.join(imports)}"
            lines.insert(insert_idx, import_line)
            content = "\n".join(lines)

    return content, content != original_content


def fix_file(file_path: Path) -> bool:
    """Fix type annotations in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content, changed = fix_common_patterns(content)

        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return False


def fix_project_files(target_files: List[str]) -> Dict[str, int]:
    """Fix type annotations in specific project files."""
    results = {"fixed": 0, "errors": 0, "skipped": 0}

    for file_path in target_files:
        path = Path(file_path)
        if not path.exists():
            print(f"File not found: {file_path}")
            results["errors"] += 1
            continue

        try:
            if fix_file(path):
                print(f"✅ Fixed: {file_path}")
                results["fixed"] += 1
            else:
                print(f"⏭️  No changes: {file_path}")
                results["skipped"] += 1
        except Exception as e:
            print(f"❌ Error: {file_path}: {e}")
            results["errors"] += 1

    return results


def main():
    """Fix type annotations in key project files."""
    print("🔧 Quick Type Annotation Fixer")
    print("=" * 40)

    # Priority files that need type annotation fixes
    priority_files = [
        "Aetherra/aetherra_core/memory/world_class_memory_core.py",
        "Aetherra/aetherra_core/system/security_system.py",
        "tools/repo_security_scan.py",
        "aetherra_hub_server.py",
        "Aetherra/lyrixa/lyrixa_basic.py",
        "aetherra_os.py",
        "aetherra_kernel_loop.py",
        "tools/run_hub_ai_api.py",
        "Aetherra/cli/policy_bootstrap.py",
    ]

    results = fix_project_files(priority_files)

    print(f"\n📊 Results:")
    print(f"  ✅ Fixed: {results['fixed']} files")
    print(f"  ❌ Errors: {results['errors']} files")
    print(f"  ⏭️  Skipped: {results['skipped']} files")

    if results["fixed"] > 0:
        print(
            f"\n🎉 Successfully improved type annotations in {results['fixed']} files!"
        )
        print("💡 This should reduce lint warnings and improve code quality.")


if __name__ == "__main__":
    main()
