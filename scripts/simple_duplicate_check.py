#!/usr/bin/env python3
"""
Simple duplicate file checker for NeuroCode project
"""

import hashlib
import os
from collections import defaultdict
from pathlib import Path


def get_file_hash(file_path):
    """Get MD5 hash of file content."""
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def find_duplicates():
    """Find exact duplicate files."""
    project_root = Path(".")
    file_hashes = defaultdict(list)

    # Skip these directories
    skip_dirs = {".git", "__pycache__", "node_modules", ".vscode", "logs", "temp"}

    print("🔍 Scanning for duplicate files...")

    for root, dirs, files in os.walk(project_root):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = Path(root) / file

            # Skip binary files and cache files
            if file_path.suffix.lower() in {".pyc", ".pyo", ".exe", ".dll", ".ico"}:
                continue

            file_hash = get_file_hash(file_path)
            if file_hash:
                file_hashes[file_hash].append(file_path)

    # Find duplicates
    duplicates = {hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1}

    if duplicates:
        print(f"\n📋 Found {len(duplicates)} sets of duplicate files:")

        for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
            print(f"\n{i}. Duplicate set (hash: {hash_val[:8]}...):")
            for path in sorted(paths):
                size = path.stat().st_size if path.exists() else 0
                print(f"   📁 {path} ({size} bytes)")
    else:
        print("\n✅ No exact duplicate files found!")

    # Look for potential similar files by name
    print("\n🔍 Looking for similar file names...")

    name_groups = defaultdict(list)
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if not file.endswith((".pyc", ".pyo")):
                file_path = Path(root) / file
                # Group by base name (without extension)
                base_name = file_path.stem.lower()
                name_groups[base_name].append(file_path)

    similar_names = {
        name: paths for name, paths in name_groups.items() if len(paths) > 1 and len(name) > 3
    }

    if similar_names:
        print(f"\n📋 Found {len(similar_names)} groups of similarly named files:")
        for name, paths in sorted(similar_names.items()):
            if len(paths) > 1:
                print(f"\n'{name}' files:")
                for path in sorted(paths):
                    print(f"   📄 {path}")


if __name__ == "__main__":
    find_duplicates()
