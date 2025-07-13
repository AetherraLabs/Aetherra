#!/usr/bin/env python3
"""
🧹 COMPREHENSIVE NEURO BRANDING CLEANUP
=====================================

Remove ALL references to old branding:
- Aetherra → Aetherra
- aetherra → aetherra
- Lyrixa → Lyrixa
- lyrixa → lyrixa
- .aether → .aether
- neuro* → aetherra* (where appropriate)
"""

import re
from pathlib import Path


class NeuroBrandingFixer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.changes_made = []
        self.files_updated = 0
        self.files_renamed = 0

        # Mapping of old terms to new terms
        self.replacements = {
            # Case-sensitive replacements
            "Aetherra": "Aetherra",
            "aetherra": "aetherra",
            "Lyrixa": "Lyrixa",
            "lyrixa": "lyrixa",
            "LyrixaChat": "LyrixaChat",
            "lyrixa_chat": "lyrixa_chat",
            "AetherraMemory": "AetherraMemory",
            "AetherraAgent": "AetherraAgent",
            "AetherraFunctions": "AetherraFunctions",
            "AetherraCommand": "AetherraCommand",
            "AetherraBlock": "AetherraBlock",
            "AetherraASTParser": "AetherraASTParser",
            "AetherraTheme": "AetherraTheme",
            "AetherraAnimation": "AetherraAnimation",
            "AetherraUI": "AetherraUI",
            "BasicAetherraUI": "BasicAetherraUI",
            "EnhancedAetherraAgent": "EnhancedAetherraAgent",
            "StandaloneAetherraRunner": "StandaloneAetherraRunner",
            "NaturalToAetherraTranslator": "NaturalToAetherraTranslator",
            "aetherra_ui": "aetherra_ui",
            "aetherra_ast": "aetherra_ast",
            "aetherra_runner": "aetherra_runner",
            "aetherra_parser": "aetherra_parser",
            "test_aetherra": "test_aetherra",
            "demo_aetherra": "demo_aetherra",
            "fix_aetherra": "fix_aetherra",
            "natural_to_aetherra": "natural_to_aetherra",
            "generate_aetherra": "generate_aetherra",
            "aetherra_file": "aetherra_file",
            "aetherra_code": "aetherra_code",
            "aetherra_block": "aetherra_block",
            "aetherra_compatible": "aetherra_compatible",
            ".aether": ".aether",
            ".aetherc": ".aetherc",
        }

        # Files to skip (archives, backups, etc.)
        self.skip_patterns = [
            "*/archive/*",
            "*/backups/*",
            "*/old_*",
            "*backup*",
            "*.backup.*",
            "*/historical/*",
            "*/legacy/*",
            "*_20??_*",  # Date patterns
            "complete_file_*",
            "housekeeping_*",
            "*.json",  # Skip JSON files for now
            "*.txt",  # Skip text files for now
        ]

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        path_str = str(file_path).replace("\\", "/")

        for pattern in self.skip_patterns:
            if self._matches_pattern(path_str, pattern):
                return True

        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Simple pattern matching"""
        pattern = pattern.replace("*", ".*")
        return bool(re.match(pattern, path))

    def fix_file_content(self, file_path: Path) -> bool:
        """Fix content in a single file"""
        if self.should_skip_file(file_path):
            return False

        try:
            # Read file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            original_content = content

            # Apply replacements
            for old_term, new_term in self.replacements.items():
                if old_term in content:
                    content = content.replace(old_term, new_term)

            # Check if changes were made
            if content != original_content:
                # Write back
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.changes_made.append(f"Updated content: {file_path}")
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def rename_files_and_directories(self):
        """Rename files and directories with old branding"""
        items_to_rename = []

        # Find items to rename
        for item in self.root_path.rglob("*"):
            if self.should_skip_file(item):
                continue

            name = item.name
            new_name = name

            # Apply replacements to filename
            for old_term, new_term in self.replacements.items():
                if old_term in new_name:
                    new_name = new_name.replace(old_term, new_term)

            if new_name != name:
                items_to_rename.append((item, item.parent / new_name))

        # Rename items (files first, then directories)
        files_to_rename = [(old, new) for old, new in items_to_rename if old.is_file()]
        dirs_to_rename = [(old, new) for old, new in items_to_rename if old.is_dir()]

        # Rename files
        for old_path, new_path in files_to_rename:
            try:
                if not new_path.exists():
                    old_path.rename(new_path)
                    self.changes_made.append(f"Renamed file: {old_path} → {new_path}")
                    self.files_renamed += 1
            except Exception as e:
                print(f"Error renaming file {old_path}: {e}")

        # Rename directories (in reverse order to handle nested dirs)
        for old_path, new_path in reversed(dirs_to_rename):
            try:
                if not new_path.exists():
                    old_path.rename(new_path)
                    self.changes_made.append(
                        f"Renamed directory: {old_path} → {new_path}"
                    )
                    self.files_renamed += 1
            except Exception as e:
                print(f"Error renaming directory {old_path}: {e}")

    def fix_all_files(self):
        """Fix all Python files in the project"""
        python_files = list(self.root_path.rglob("*.py"))

        for file_path in python_files:
            if self.fix_file_content(file_path):
                self.files_updated += 1

    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🧹 Starting comprehensive neuro branding cleanup...")

        # Step 1: Fix file contents
        print("📝 Fixing file contents...")
        self.fix_all_files()

        # Step 2: Rename files and directories
        print("📂 Renaming files and directories...")
        self.rename_files_and_directories()

        # Step 3: Summary
        print("\n✅ Cleanup complete!")
        print(f"   📝 Files updated: {self.files_updated}")
        print(f"   📂 Files/dirs renamed: {self.files_renamed}")
        print(f"   📊 Total changes: {len(self.changes_made)}")

        if self.changes_made:
            print("\n📋 Summary of changes:")
            for change in self.changes_made[:20]:  # Show first 20 changes
                print(f"   • {change}")
            if len(self.changes_made) > 20:
                print(f"   ... and {len(self.changes_made) - 20} more changes")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    fixer = NeuroBrandingFixer(str(project_root))
    fixer.run_cleanup()


if __name__ == "__main__":
    main()
