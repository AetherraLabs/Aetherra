#!/usr/bin/env python3
"""
Aetherra Core Directory Analyzer
Analyzes aetherra_core for duplicates and proper file organization
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
import re

class AetherraCoreDuplicateAnalyzer:
    def __init__(self, base_path="Aetherra/aetherra_core"):
        self.base_path = Path(base_path)
        self.files_by_hash = defaultdict(list)
        self.files_by_name = defaultdict(list)
        self.duplicate_content = []
        self.duplicate_names = []
        self.misplaced_files = []

    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of file content"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"Error: {e}"

    def analyze_file_placement(self, filepath):
        """Analyze if file is in the correct directory based on its content and name"""
        file_path = Path(filepath)
        filename = file_path.name
        directory = file_path.parent.name
        relative_path = str(file_path.relative_to(self.base_path))

        # Enhanced directory purpose mapping with priority scoring
        expected_directories = {
            'agents': ['agent', 'conversation', 'collaboration', 'multi_agent', 'goal', 'critique', 'curiosity', 'escalation', 'reflection_agent', 'self_evaluation', 'security_system'],
            'ai': ['multi_llm', 'llm_integration', 'intelligence'],
            'cognitive': ['cognitive', 'reasoning', 'thinking'],
            'config': ['config', 'settings', 'configuration'],
            'engine': ['engine', 'core_engine', 'processor', 'executor'],
            'events': ['event', 'listener', 'handler'],
            'file_system': ['file', 'filesystem', 'storage', 'io'],
            'intelligence': ['intelligence', 'ai', 'smart', 'brain'],
            'kernel': ['kernel', 'core', 'bridge', 'registry'],
            'memory': ['memory', 'storage', 'cache', 'recall', 'timeline', 'episodic', 'fractal'],
            'orchestration': ['orchestration', 'coordination', 'scheduler', 'manager'],
            'personality': ['personality', 'character', 'behavior', 'social'],
            'plugins': ['plugin', 'extension', 'addon'],
            'reflection': ['reflection', 'introspection', 'self_analysis'],
            'reflection_engine': ['reflection_engine', 'introspection_engine'],
            'self_metrics_dashboard': ['dashboard', 'metrics', 'monitoring'],
            'system': ['system', 'core', 'bootstrap', 'foundation']
        }

        issues = []

        # Check for numbered duplicates (like _1, _17 suffixes)
        if re.search(r'_\d+\.py$', filename):
            issues.append(f"Numbered duplicate: {filename}")

        # Check if file is in appropriate directory
        for expected_dir, keywords in expected_directories.items():
            if any(keyword in filename.lower() for keyword in keywords):
                if directory != expected_dir:
                    issues.append(f"Misplaced: {filename} should be in {expected_dir}/ not {directory}/")

        return issues

    def analyze_directory(self):
        """Analyze the entire aetherra_core directory for duplicates and issues"""
        print("🔍 Analyzing Aetherra Core Directory for Duplicates and Organization Issues...")
        print("=" * 80)

        # Walk through all Python files
        for root, dirs, files in os.walk(self.base_path):
            for filename in files:
                if filename.endswith('.py'):
                    filepath = Path(root) / filename

                    # Calculate hash
                    file_hash = self.calculate_file_hash(filepath)
                    if not file_hash.startswith("Error"):
                        self.files_by_hash[file_hash].append(filepath)

                    # Group by filename
                    self.files_by_name[filename].append(filepath)

                    # Check file placement
                    placement_issues = self.analyze_file_placement(filepath)
                    if placement_issues:
                        self.misplaced_files.append({
                            'file': filepath,
                            'issues': placement_issues
                        })

        # Find duplicates
        self.duplicate_content = {h: files for h, files in self.files_by_hash.items() if len(files) > 1}
        self.duplicate_names = {name: files for name, files in self.files_by_name.items() if len(files) > 1}

        self.generate_report()

    def compare_file_contents(self, file1, file2):
        """Compare two files line by line to show differences"""
        try:
            with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
                content1 = f1.readlines()
            with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
                content2 = f2.readlines()

            if content1 == content2:
                return "IDENTICAL"

            # Count different lines
            diff_count = 0
            for i, (line1, line2) in enumerate(zip(content1, content2)):
                if line1 != line2:
                    diff_count += 1

            total_lines = max(len(content1), len(content2))
            similarity = ((total_lines - diff_count) / total_lines) * 100

            return f"{similarity:.1f}% similar ({diff_count} different lines)"

        except Exception as e:
            return f"Error comparing: {e}"

    def generate_report(self):
        """Generate comprehensive analysis report"""
        report = []
        report.append("# 🔍 AETHERRA CORE DUPLICATE & ORGANIZATION ANALYSIS")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("## 📊 ANALYSIS SUMMARY")
        report.append("")
        report.append(f"- **Total Python files analyzed:** {sum(len(files) for files in self.files_by_name.values())}")
        report.append(f"- **Exact duplicate groups (same content):** {len(self.duplicate_content)}")
        report.append(f"- **Duplicate filename groups:** {len(self.duplicate_names)}")
        report.append(f"- **Files with placement issues:** {len(self.misplaced_files)}")
        report.append("")

        # Exact content duplicates
        if self.duplicate_content:
            report.append("## 🚨 EXACT CONTENT DUPLICATES (Same Hash)")
            report.append("")

            for file_hash, duplicate_files in self.duplicate_content.items():
                report.append(f"### Duplicate Group (Hash: {file_hash[:12]}...)")
                for file_path in duplicate_files:
                    rel_path = file_path.relative_to(self.base_path)
                    file_size = file_path.stat().st_size
                    report.append(f"- `{rel_path}` ({file_size:,} bytes)")

                report.append("")
                report.append("**Recommendation:** Keep one file, delete others")
                report.append("")

        # Duplicate filenames (may have different content)
        if self.duplicate_names:
            report.append("## ⚠️ DUPLICATE FILENAMES (May have different content)")
            report.append("")

            for filename, duplicate_files in self.duplicate_names.items():
                if len(duplicate_files) > 1:
                    report.append(f"### `{filename}`")

                    # Compare contents
                    if len(duplicate_files) == 2:
                        comparison = self.compare_file_contents(duplicate_files[0], duplicate_files[1])
                        report.append(f"**Content Comparison:** {comparison}")

                    for file_path in duplicate_files:
                        rel_path = file_path.relative_to(self.base_path)
                        file_size = file_path.stat().st_size
                        report.append(f"- `{rel_path}` ({file_size:,} bytes)")

                    report.append("")

        # Misplaced files
        if self.misplaced_files:
            report.append("## 📁 MISPLACED FILES & ORGANIZATION ISSUES")
            report.append("")

            for item in self.misplaced_files:
                file_path = item['file']
                issues = item['issues']
                rel_path = file_path.relative_to(self.base_path)

                report.append(f"### `{rel_path}`")
                for issue in issues:
                    report.append(f"- ⚠️ {issue}")
                report.append("")

        # Recommendations
        report.append("## 🎯 CLEANUP RECOMMENDATIONS")
        report.append("")

        if self.duplicate_content:
            report.append("### Exact Duplicates")
            duplicate_count = sum(len(files) - 1 for files in self.duplicate_content.values())
            report.append(f"- **Remove {duplicate_count} exact duplicate files**")
            report.append("- Keep the file in the most appropriate directory")
            report.append("- Update any imports that reference deleted files")
            report.append("")

        if self.duplicate_names:
            numbered_duplicates = [name for name in self.duplicate_names.keys() if re.search(r'_\d+\.py$', name)]
            if numbered_duplicates:
                report.append("### Numbered Duplicates")
                report.append(f"- **Review {len(numbered_duplicates)} numbered duplicate files**")
                report.append("- Merge changes if different, or delete if identical")
                report.append("- Remove version numbers from filenames")
                report.append("")

        if self.misplaced_files:
            report.append("### File Organization")
            report.append(f"- **Reorganize {len(self.misplaced_files)} misplaced files**")
            report.append("- Move files to appropriate directories based on functionality")
            report.append("- Update import statements after moving files")
            report.append("")

        # Save report
        report_content = "\n".join(report)

        with open("AETHERRA_CORE_ANALYSIS.md", "w", encoding='utf-8') as f:
            f.write(report_content)

        print("✅ Analysis complete!")
        print("📄 Report saved to: AETHERRA_CORE_ANALYSIS.md")
        print("")
        print("🔍 Key Findings:")
        print(f"   - {len(self.duplicate_content)} exact duplicate groups")
        print(f"   - {len(self.duplicate_names)} duplicate filename groups")
        print(f"   - {len(self.misplaced_files)} files with placement issues")

if __name__ == "__main__":
    analyzer = AetherraCoreDuplicateAnalyzer()
    analyzer.analyze_directory()
