#!/usr/bin/env python3
"""
Smart Agent Deduplication - Clean up the agents directory
Remove duplicates while preserving unique and important agents
"""

import ast
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple


class SmartAgentDeduplicator:
    def __init__(self, agents_dir: str):
        self.agents_dir = Path(agents_dir)
        self.core_agents_dir = Path(agents_dir).parent.parent / "core" / "agents"

        # Track what we find
        self.file_hashes = {}
        self.content_groups = {}
        self.agent_analysis = {}
        self.keep_files = set()
        self.remove_files = set()

        # Important agents that should never be removed
        self.protected_agents = {
            "agent_base.py",
            "core_agent.py",
            "lyrixa_agent_integration.py",
            "enhanced_lyrixa.py",
            "conversation_manager.py",
            "intelligence.py",
            "__init__.py",
        }

    def deduplicate_agents(self):
        """Run the complete deduplication process"""
        print("🧹 SMART AGENT DEDUPLICATION")
        print("=" * 50)
        print("🎯 Cleaning up agent duplicates while preserving unique agents")
        print()

        # Step 1: Analyze all agent files
        self._analyze_all_agents()

        # Step 2: Group by content similarity
        self._group_by_content()

        # Step 3: Select best files to keep
        self._select_best_files()

        # Step 4: Remove duplicates
        self._remove_duplicates()

        # Step 5: Generate report
        self._generate_report()

        print("\n✅ Agent deduplication complete!")

    def _analyze_all_agents(self):
        """Analyze all agent files for content, size, and quality"""
        print("🔍 ANALYZING AGENT FILES")
        print("-" * 30)

        agent_files = list(self.agents_dir.glob("*.py"))
        print(f"📊 Found {len(agent_files)} agent files to analyze")

        for file_path in agent_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Calculate content hash
                content_hash = hashlib.md5(content.encode()).hexdigest()

                # Analyze file
                analysis = self._analyze_single_file(file_path, content)
                analysis["content_hash"] = content_hash
                analysis["file_size"] = len(content)

                self.agent_analysis[str(file_path)] = analysis

                # Group by hash
                if content_hash not in self.file_hashes:
                    self.file_hashes[content_hash] = []
                self.file_hashes[content_hash].append(file_path)

            except Exception as e:
                print(f"  ⚠️ Error analyzing {file_path.name}: {e}")

        print(f"  ✅ Analyzed {len(self.agent_analysis)} files")
        print(f"  🔍 Found {len(self.file_hashes)} unique content hashes")

    def _analyze_single_file(self, file_path: Path, content: str) -> Dict:
        """Analyze a single agent file for quality metrics"""
        analysis = {
            "base_name": self._get_base_name(file_path.name),
            "is_numbered_duplicate": self._is_numbered_duplicate(file_path.name),
            "protected": file_path.name in self.protected_agents,
            "classes": [],
            "functions": [],
            "imports": [],
            "lines_of_code": len(
                [
                    l
                    for l in content.split("\n")
                    if l.strip() and not l.strip().startswith("#")
                ]
            ),
            "has_docstring": '"""' in content or "'''" in content,
            "quality_score": 0,
        }

        try:
            # Parse AST to get structure
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)

        except SyntaxError:
            analysis["syntax_error"] = True

        # Calculate quality score
        analysis["quality_score"] = self._calculate_quality_score(analysis)

        return analysis

    def _get_base_name(self, filename: str) -> str:
        """Get the base name without numbered suffix"""
        # Remove .py extension
        name = filename[:-3] if filename.endswith(".py") else filename

        # Remove numbered suffixes like _1, _2, etc.
        import re

        base_name = re.sub(r"_\d+$", "", name)
        return base_name

    def _is_numbered_duplicate(self, filename: str) -> bool:
        """Check if filename has numbered suffix indicating duplicate"""
        import re

        return bool(re.search(r"_\d+\.py$", filename))

    def _calculate_quality_score(self, analysis: Dict) -> int:
        """Calculate quality score for file selection"""
        score = 0

        # Base score from lines of code
        score += min(analysis["lines_of_code"], 100)  # Max 100 points

        # Bonus for classes (agents should have classes)
        score += len(analysis["classes"]) * 20

        # Bonus for functions
        score += len(analysis["functions"]) * 5

        # Bonus for docstrings
        if analysis["has_docstring"]:
            score += 30

        # Penalty for numbered duplicates
        if analysis["is_numbered_duplicate"]:
            score -= 50

        # Big bonus for protected files
        if analysis["protected"]:
            score += 200

        # Penalty for syntax errors
        if analysis.get("syntax_error", False):
            score -= 100

        return max(0, score)

    def _group_by_content(self):
        """Group files by content similarity"""
        print("\n🔗 GROUPING BY CONTENT")
        print("-" * 30)

        # Group identical files
        identical_groups = []
        for content_hash, files in self.file_hashes.items():
            if len(files) > 1:
                identical_groups.append(files)
                print(f"  📎 Found {len(files)} identical files: {files[0].name}")

        # Group by base name (similar files with different versions)
        base_name_groups = {}
        for file_path in self.agent_analysis.keys():
            path = Path(file_path)
            analysis = self.agent_analysis[file_path]
            base_name = analysis["base_name"]

            if base_name not in base_name_groups:
                base_name_groups[base_name] = []
            base_name_groups[base_name].append(path)

        # Find groups with multiple versions
        version_groups = []
        for base_name, files in base_name_groups.items():
            if len(files) > 1:
                version_groups.append(files)
                print(f"  🔄 Found {len(files)} versions of {base_name}")

        self.content_groups = {
            "identical": identical_groups,
            "versions": version_groups,
        }

    def _select_best_files(self):
        """Select the best files to keep from each group"""
        print("\n🎯 SELECTING BEST FILES")
        print("-" * 30)

        # For identical files, keep the one with the best name (non-numbered)
        for identical_group in self.content_groups["identical"]:
            best_file = self._select_best_from_group(identical_group)
            self.keep_files.add(best_file)

            for file_path in identical_group:
                if file_path != best_file:
                    self.remove_files.add(file_path)

            print(f"  ✅ Keeping: {best_file.name}")
            print(
                f"     🗑️ Removing: {[f.name for f in identical_group if f != best_file]}"
            )

        # For version groups, keep the best version
        for version_group in self.content_groups["versions"]:
            # Skip if already processed in identical groups
            if any(
                f in self.keep_files or f in self.remove_files for f in version_group
            ):
                continue

            best_file = self._select_best_from_group(version_group)
            self.keep_files.add(best_file)

            for file_path in version_group:
                if file_path != best_file:
                    self.remove_files.add(file_path)

            print(f"  ✅ Keeping best version: {best_file.name}")
            if len(version_group) > 1:
                print(
                    f"     🗑️ Removing versions: {[f.name for f in version_group if f != best_file]}"
                )

        # Keep all other files that aren't in any group
        for file_path_str in self.agent_analysis.keys():
            file_path = Path(file_path_str)
            if file_path not in self.keep_files and file_path not in self.remove_files:
                self.keep_files.add(file_path)

    def _select_best_from_group(self, file_group: List[Path]) -> Path:
        """Select the best file from a group"""
        if len(file_group) == 1:
            return file_group[0]

        # Score each file
        file_scores = []
        for file_path in file_group:
            analysis = self.agent_analysis[str(file_path)]
            score = analysis["quality_score"]

            # Additional selection criteria
            # Prefer non-numbered files
            if not analysis["is_numbered_duplicate"]:
                score += 100

            # Prefer shorter names (usually the original)
            score += max(0, 50 - len(file_path.name))

            # Prefer protected files
            if analysis["protected"]:
                score += 300

            file_scores.append((score, file_path))

        # Return the highest scoring file
        file_scores.sort(reverse=True)
        return file_scores[0][1]

    def _remove_duplicates(self):
        """Actually remove the duplicate files"""
        print(f"\n🗑️ REMOVING {len(self.remove_files)} DUPLICATE FILES")
        print("-" * 30)

        # Create a backup directory for removed files (just in case)
        backup_dir = self.agents_dir / "deduplication_backup"
        backup_dir.mkdir(exist_ok=True)

        removed_count = 0
        for file_path in self.remove_files:
            try:
                # Move to backup first
                backup_file = backup_dir / file_path.name
                if backup_file.exists():
                    backup_file = (
                        backup_dir / f"{file_path.stem}_backup{file_path.suffix}"
                    )

                shutil.move(str(file_path), str(backup_file))
                removed_count += 1
                print(f"  🗑️ Removed: {file_path.name}")

            except Exception as e:
                print(f"  ❌ Error removing {file_path.name}: {e}")

        print(f"\n  ✅ Removed {removed_count} duplicate files")
        print(f"  📦 Backups saved to: {backup_dir}")

    def _generate_report(self):
        """Generate deduplication report"""
        print(f"\n📊 DEDUPLICATION REPORT")
        print("-" * 30)

        # Count final files
        remaining_files = list(self.agents_dir.glob("*.py"))

        # Create report
        report = {
            "timestamp": "20250727_deduplication",
            "original_file_count": len(self.agent_analysis),
            "final_file_count": len(remaining_files),
            "files_removed": len(self.remove_files),
            "files_kept": len(self.keep_files),
            "identical_groups": len(self.content_groups["identical"]),
            "version_groups": len(self.content_groups["versions"]),
            "protected_files_preserved": len(
                [
                    f
                    for f in self.keep_files
                    if self.agent_analysis[str(f)].get("protected", False)
                ]
            ),
            "kept_files": [f.name for f in self.keep_files],
            "removed_files": [f.name for f in self.remove_files],
        }

        # Save report
        report_file = (
            self.agents_dir.parent.parent
            / "tools"
            / "migration"
            / "agent_deduplication_report.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"  📈 Original files: {report['original_file_count']}")
        print(f"  📉 Files removed: {report['files_removed']}")
        print(f"  📊 Final files: {report['final_file_count']}")
        print(f"  🛡️ Protected files preserved: {report['protected_files_preserved']}")
        print(f"  📄 Report saved: {report_file}")

        # Show key agents kept
        print(f"\n🎯 KEY AGENTS PRESERVED:")
        key_agents = [f for f in remaining_files if f.name in self.protected_agents]
        for agent in key_agents:
            print(f"  ✅ {agent.name}")

        return report


def main():
    """Run agent deduplication"""
    agents_dir = r"c:\Users\enigm\Desktop\Aetherra Project\Aetherra_v2\lyrixa\agents"

    print("🚀 STARTING AGENT DEDUPLICATION")
    print("=" * 50)
    print(f"📁 Target directory: {agents_dir}")
    print()

    deduplicator = SmartAgentDeduplicator(agents_dir)
    deduplicator.deduplicate_agents()

    print("\n🎉 AGENT CLEANUP COMPLETE!")
    print("Your agents directory is now clean and organized!")


if __name__ == "__main__":
    main()
