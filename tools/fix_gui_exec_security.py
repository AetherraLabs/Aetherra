#!/usr/bin/env python3
"""Quick script to add nosec comments to legitimate Qt GUI exec() calls."""

import re
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Add nosec comments to GUI exec() calls in a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Skip if already has nosec comments
        if "nosec B102" in content:
            return False
            
        # Simple pattern replacement for Qt GUI exec() calls
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if "exec(" in line and "nosec" not in line:
                # This is a GUI exec() call, add nosec comment
                if "app.exec()" in line:
                    line = line.replace("app.exec()", "app.exec()  # nosec B102: Qt application execution")
                elif ".exec()" in line and ("menu" in line.lower() or "dialog" in line.lower() or "msg" in line.lower()):
                    line = line.replace(".exec()", ".exec()  # nosec B102: Qt GUI dialog/menu execution")
                elif ".exec()" in line:
                    line = line.replace(".exec()", ".exec()  # nosec B102: Qt GUI execution")
            new_lines.append(line)
        content = "\n".join(new_lines)
        
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
            
    except Exception as e:  # nosec B110: broad exception acceptable for utility script
        print(f"Error processing {file_path}: {e}")
    
    return False


def main() -> None:
    """Fix Qt GUI exec() calls across the project."""
    project_root = Path(__file__).parent.parent
    fixed_count = 0
    
    # Process all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip hidden directories and files
        if any(part.startswith(".") for part in py_file.parts):
            continue
            
        if fix_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files with Qt GUI exec() calls")

if __name__ == "__main__":
    main()