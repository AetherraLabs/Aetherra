#!/usr/bin/env python3
"""
Complete File Path Readout for Aetherra Project
Generates a comprehensive listing of all files and directories with full paths.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ProjectFileMapper:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.file_tree = {}
        self.all_files = []
        self.statistics = {
            "total_files": 0,
            "total_directories": 0,
            "by_extension": {},
            "largest_files": [],
            "directory_counts": {},
        }

    def scan_project(self):
        """Scan the entire project and build file tree"""
        print("🔍 Scanning project for complete file listing...")

        for item in self.root.rglob("*"):
            relative_path = item.relative_to(self.root)
            full_path = str(item.resolve())

            if item.is_file():
                self.statistics["total_files"] += 1

                # Get file info
                try:
                    size = item.stat().st_size
                    modified = datetime.fromtimestamp(item.stat().st_mtime)
                    extension = item.suffix.lower()

                    # Track by extension
                    if extension:
                        self.statistics["by_extension"][extension] = (
                            self.statistics["by_extension"].get(extension, 0) + 1
                        )
                    else:
                        self.statistics["by_extension"]["(no extension)"] = (
                            self.statistics["by_extension"].get("(no extension)", 0) + 1
                        )

                    # Track largest files
                    self.statistics["largest_files"].append(
                        {
                            "path": str(relative_path),
                            "size": size,
                            "size_mb": round(size / (1024 * 1024), 2),
                        }
                    )

                    file_info = {
                        "type": "file",
                        "relative_path": str(relative_path),
                        "full_path": full_path,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "extension": extension,
                        "modified": modified.isoformat(),
                        "parent_dir": str(relative_path.parent),
                    }

                except (OSError, PermissionError):
                    file_info = {
                        "type": "file",
                        "relative_path": str(relative_path),
                        "full_path": full_path,
                        "size_bytes": 0,
                        "size_mb": 0,
                        "extension": item.suffix.lower(),
                        "modified": "unknown",
                        "parent_dir": str(relative_path.parent),
                        "error": "Permission denied or file not accessible",
                    }

                self.all_files.append(file_info)

            elif item.is_dir():
                self.statistics["total_directories"] += 1

                # Count files in directory
                try:
                    dir_file_count = len([f for f in item.iterdir() if f.is_file()])
                    self.statistics["directory_counts"][str(relative_path)] = (
                        dir_file_count
                    )
                except (OSError, PermissionError):
                    self.statistics["directory_counts"][str(relative_path)] = 0

        # Sort largest files
        self.statistics["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        self.statistics["largest_files"] = self.statistics["largest_files"][
            :20
        ]  # Top 20

    def generate_tree_structure(self):
        """Generate a tree-like structure"""
        tree_lines = []

        def add_directory_tree(directory, prefix=""):
            items = []
            try:
                items = sorted(
                    directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                )
            except (OSError, PermissionError):
                tree_lines.append(f"{prefix}[Permission Denied]")
                return

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "

                relative_path = item.relative_to(self.root)

                if item.is_file():
                    try:
                        size = item.stat().st_size
                        size_str = f" ({self._format_size(size)})" if size > 0 else ""
                        tree_lines.append(
                            f"{prefix}{current_prefix}{item.name}{size_str}"
                        )
                    except (OSError, PermissionError):
                        tree_lines.append(
                            f"{prefix}{current_prefix}{item.name} [Error]"
                        )
                elif item.is_dir():
                    tree_lines.append(f"{prefix}{current_prefix}{item.name}/")
                    add_directory_tree(item, prefix + next_prefix)

        tree_lines.append(f"{self.root.name}/")
        add_directory_tree(self.root)

        return tree_lines

    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f}MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

    def save_complete_listing(self):
        """Save comprehensive file listing to multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 1. JSON format with all details
        json_file = self.root / f"complete_file_listing_{timestamp}.json"
        listing_data = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.root),
            "statistics": self.statistics,
            "all_files": self.all_files,
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(listing_data, f, indent=2, ensure_ascii=False)

        # 2. Text format with paths only
        text_file = self.root / f"complete_file_paths_{timestamp}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(f"AETHERRA PROJECT - COMPLETE FILE LISTING\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Root: {self.root}\n")
            f.write("=" * 80 + "\n\n")

            f.write("ALL FILE PATHS:\n")
            f.write("-" * 40 + "\n")
            for file_info in sorted(self.all_files, key=lambda x: x["relative_path"]):
                f.write(f"{file_info['relative_path']}\n")

        # 3. Tree structure format
        tree_file = self.root / f"project_tree_structure_{timestamp}.txt"
        tree_lines = self.generate_tree_structure()

        with open(tree_file, "w", encoding="utf-8") as f:
            f.write(f"AETHERRA PROJECT - TREE STRUCTURE\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            for line in tree_lines:
                f.write(line + "\n")

        # 4. Markdown format for documentation
        md_file = self.root / f"PROJECT_FILE_LISTING_{timestamp}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# Aetherra Project - Complete File Listing\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Project Root:** `{self.root}`\n\n")

            f.write(f"## 📊 Project Statistics\n\n")
            f.write(f"- **Total Files:** {self.statistics['total_files']:,}\n")
            f.write(
                f"- **Total Directories:** {self.statistics['total_directories']:,}\n\n"
            )

            f.write(f"### File Types\n\n")
            sorted_extensions = sorted(
                self.statistics["by_extension"].items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for ext, count in sorted_extensions[:20]:
                f.write(f"- `{ext}`: {count:,} files\n")

            f.write(f"\n### Largest Files\n\n")
            for file_info in self.statistics["largest_files"][:10]:
                f.write(f"- `{file_info['path']}` ({file_info['size_mb']} MB)\n")

            f.write(f"\n## 📁 Complete File Listing\n\n")
            f.write(f"```\n")
            for line in tree_lines[:500]:  # First 500 lines to avoid huge file
                f.write(line + "\n")
            if len(tree_lines) > 500:
                f.write(f"... and {len(tree_lines) - 500} more lines\n")
            f.write(f"```\n\n")

            f.write(f"## 📄 All File Paths\n\n")
            current_dir = ""
            for file_info in sorted(self.all_files, key=lambda x: x["relative_path"]):
                file_dir = file_info["parent_dir"]
                if file_dir != current_dir:
                    f.write(
                        f"\n### {file_dir if file_dir != '.' else 'Root Directory'}\n\n"
                    )
                    current_dir = file_dir

                file_name = Path(file_info["relative_path"]).name
                size_str = (
                    f" ({file_info['size_mb']} MB)"
                    if file_info["size_mb"] > 0.1
                    else ""
                )
                f.write(f"- `{file_name}`{size_str}\n")

        return {
            "json_file": str(json_file),
            "text_file": str(text_file),
            "tree_file": str(tree_file),
            "markdown_file": str(md_file),
        }

    def print_summary(self):
        """Print a summary of the scan"""
        print("\n" + "=" * 80)
        print("📁 AETHERRA PROJECT - COMPLETE FILE LISTING")
        print("=" * 80)

        print(f"\n📊 STATISTICS:")
        print(f"   Total Files: {self.statistics['total_files']:,}")
        print(f"   Total Directories: {self.statistics['total_directories']:,}")

        print(f"\n📁 TOP FILE TYPES:")
        sorted_extensions = sorted(
            self.statistics["by_extension"].items(), key=lambda x: x[1], reverse=True
        )[:15]
        for ext, count in sorted_extensions:
            print(f"   {ext}: {count:,}")

        print(f"\n[DISC] LARGEST FILES:")
        for file_info in self.statistics["largest_files"][:10]:
            print(f"   {file_info['path']} ({file_info['size_mb']} MB)")

        print("\n" + "=" * 80)


def main():
    """Generate complete file listing for Aetherra project"""
    root_path = Path.cwd()

    print("📁 Starting Complete File Path Readout...")
    print(f"🔍 Scanning: {root_path}")

    mapper = ProjectFileMapper(root_path)
    mapper.scan_project()

    # Save all formats
    output_files = mapper.save_complete_listing()

    # Print summary
    mapper.print_summary()

    print(f"\n✅ Complete file listing generated!")
    print(f"\n📄 Output Files:")
    for format_name, file_path in output_files.items():
        print(f"   {format_name}: {Path(file_path).name}")

    print(f"\n🎯 Use these files for:")
    print(f"   • JSON format: Programming/automation")
    print(f"   • Text format: Simple path listing")
    print(f"   • Tree format: Visual directory structure")
    print(f"   • Markdown format: Documentation")


if __name__ == "__main__":
    main()
