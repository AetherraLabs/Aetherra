#!/usr/bin/env python3
"""
Universal Directory Analyzer
Analyzes any directory for duplicates and proper file organization
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
import re
import sys

class UniversalDirectoryAnalyzer:
    def __init__(self, target_directory):
        self.target_directory = Path(target_directory)
        self.directory_name = self.target_directory.name
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
        relative_path = str(file_path.relative_to(self.target_directory))

        # Common directory purpose mappings
        common_directories = {
            'agents': ['agent', 'conversation', 'collaboration', 'multi_agent', 'goal', 'critique', 'curiosity', 'escalation', 'reflection_agent', 'self_evaluation', 'security_system'],
            'ai': ['multi_llm', 'llm_integration', 'intelligence', 'ai'],
            'api': ['api', 'endpoint', 'rest', 'graphql', 'service'],
            'auth': ['auth', 'authentication', 'authorization', 'login', 'security'],
            'cognitive': ['cognitive', 'reasoning', 'thinking', 'logic'],
            'config': ['config', 'settings', 'configuration', 'preferences'],
            'core': ['core', 'base', 'foundation', 'essential'],
            'data': ['data', 'dataset', 'storage', 'persistence'],
            'db': ['database', 'db', 'sql', 'query', 'model'],
            'docs': ['documentation', 'doc', 'guide', 'readme'],
            'engine': ['engine', 'core_engine', 'processor', 'executor'],
            'events': ['event', 'listener', 'handler', 'trigger'],
            'file_system': ['file', 'filesystem', 'storage', 'io', 'path'],
            'gui': ['gui', 'ui', 'interface', 'frontend', 'window'],
            'integration': ['integration', 'connector', 'bridge', 'adapter'],
            'intelligence': ['intelligence', 'ai', 'smart', 'brain'],
            'kernel': ['kernel', 'core', 'bridge', 'registry'],
            'memory': ['memory', 'storage', 'cache', 'recall', 'timeline', 'episodic', 'fractal'],
            'models': ['model', 'schema', 'entity', 'structure'],
            'network': ['network', 'socket', 'connection', 'protocol'],
            'orchestration': ['orchestration', 'coordination', 'scheduler', 'manager'],
            'personality': ['personality', 'character', 'behavior', 'social'],
            'plugins': ['plugin', 'extension', 'addon', 'module'],
            'reflection': ['reflection', 'introspection', 'self_analysis'],
            'runtime': ['runtime', 'execution', 'interpreter', 'vm'],
            'scripts': ['script', 'automation', 'batch', 'utility'],
            'security': ['security', 'crypto', 'encryption', 'protection'],
            'system': ['system', 'os', 'platform', 'bootstrap'],
            'tests': ['test', 'testing', 'unittest', 'spec'],
            'tools': ['tool', 'utility', 'helper', 'command'],
            'utils': ['util', 'utility', 'helper', 'common'],
            'web': ['web', 'http', 'server', 'client', 'browser']
        }

        issues = []

        # Check for numbered duplicates (like _1, _17 suffixes)
        if re.search(r'_\d+\.(py|js|ts|json)$', filename):
            issues.append(f"Numbered duplicate: {filename}")

        # Check for common problematic patterns
        if filename.lower().startswith('untitled'):
            issues.append(f"Untitled file: {filename}")

        if filename.lower().endswith('_backup'):
            issues.append(f"Backup file: {filename}")

        if filename.lower().endswith('_old'):
            issues.append(f"Old version file: {filename}")

        # Check if file is in appropriate directory
        for expected_dir, keywords in common_directories.items():
            if any(keyword in filename.lower() for keyword in keywords):
                if directory != expected_dir and expected_dir in [d.name for d in self.target_directory.iterdir() if d.is_dir()]:
                    issues.append(f"Misplaced: {filename} should be in {expected_dir}/ not {directory}/")

        return issues

    def analyze_directory(self):
        """Analyze the entire directory for duplicates and issues"""
        print(f"🔍 Analyzing {self.directory_name} Directory for Duplicates and Organization Issues...")
        print("=" * 80)

        # Count total files
        total_files = 0
        for root, dirs, files in os.walk(self.target_directory):
            total_files += len([f for f in files if f.endswith(('.py', '.js', '.ts', '.json', '.md'))])

        print(f"📁 Found {total_files} files to analyze")
        print()

        # Walk through all relevant files
        for root, dirs, files in os.walk(self.target_directory):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.vscode', 'node_modules', '.pytest_cache']]

            for filename in files:
                if filename.endswith(('.py', '.js', '.ts', '.json', '.md')):
                    filepath = Path(root) / filename

                    # Calculate hash for duplicate detection
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
            if total_lines == 0:
                return "Both files are empty"

            similarity = ((total_lines - diff_count) / total_lines) * 100
            return f"{similarity:.1f}% similar ({diff_count} different lines)"

        except Exception as e:
            return f"Error comparing: {e}"

    def generate_report(self):
        """Generate comprehensive analysis report"""
        report = []
        report.append(f"# 🔍 {self.directory_name.upper()} DIRECTORY ANALYSIS")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("## 📊 ANALYSIS SUMMARY")
        report.append("")
        report.append(f"- **Directory analyzed:** `{self.target_directory}`")
        report.append(f"- **Total files analyzed:** {sum(len(files) for files in self.files_by_name.values())}")
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
                    rel_path = file_path.relative_to(self.target_directory)
                    file_size = file_path.stat().st_size
                    report.append(f"- `{rel_path}` ({file_size:,} bytes)")

                report.append("")
                report.append("**Recommendation:** Keep one file, delete others")
                report.append("")
        else:
            report.append("## ✅ NO EXACT CONTENT DUPLICATES FOUND")
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
                        rel_path = file_path.relative_to(self.target_directory)
                        file_size = file_path.stat().st_size
                        report.append(f"- `{rel_path}` ({file_size:,} bytes)")

                    report.append("")
        else:
            report.append("## ✅ NO DUPLICATE FILENAMES FOUND")
            report.append("")

        # Misplaced files
        if self.misplaced_files:
            report.append("## 📁 POTENTIAL ORGANIZATION IMPROVEMENTS")
            report.append("")

            for item in self.misplaced_files:
                file_path = item['file']
                issues = item['issues']
                rel_path = file_path.relative_to(self.target_directory)

                report.append(f"### `{rel_path}`")
                for issue in issues:
                    report.append(f"- ⚠️ {issue}")
                report.append("")
        else:
            report.append("## ✅ NO ORGANIZATION ISSUES FOUND")
            report.append("")

        # Recommendations
        report.append("## 🎯 SUMMARY & RECOMMENDATIONS")
        report.append("")

        if self.duplicate_content or self.duplicate_names or self.misplaced_files:
            if self.duplicate_content:
                duplicate_count = sum(len(files) - 1 for files in self.duplicate_content.values())
                report.append(f"### Exact Duplicates: {duplicate_count} files can be removed")
                report.append("- Keep the file in the most appropriate directory")
                report.append("- Update any imports that reference deleted files")
                report.append("")

            if self.duplicate_names:
                numbered_duplicates = [name for name in self.duplicate_names.keys() if re.search(r'_\d+\.(py|js|ts|json)$', name)]
                if numbered_duplicates:
                    report.append(f"### Numbered Duplicates: {len(numbered_duplicates)} files to review")
                    report.append("- Merge changes if different, or delete if identical")
                    report.append("- Remove version numbers from filenames")
                    report.append("")

            if self.misplaced_files:
                report.append(f"### Organization: {len(self.misplaced_files)} files could be better organized")
                report.append("- Move files to appropriate directories based on functionality")
                report.append("- Update import statements after moving files")
                report.append("")
        else:
            report.append("### ✅ Directory is well-organized!")
            report.append("- No duplicate files found")
            report.append("- No obvious organization issues detected")
            report.append("- Structure appears clean and professional")
            report.append("")

        # Save report
        report_content = "\n".join(report)
        report_filename = f"{self.directory_name.upper()}_DIRECTORY_ANALYSIS.md"

        with open(report_filename, "w", encoding='utf-8') as f:
            f.write(report_content)

        print("✅ Analysis complete!")
        print(f"📄 Report saved to: {report_filename}")
        print("")
        print("🔍 Key Findings:")
        print(f"   - {len(self.duplicate_content)} exact duplicate groups")
        print(f"   - {len(self.duplicate_names)} duplicate filename groups")
        print(f"   - {len(self.misplaced_files)} files with potential organization improvements")

        return {
            'duplicates': len(self.duplicate_content),
            'filename_duplicates': len(self.duplicate_names),
            'misplaced': len(self.misplaced_files),
            'total_files': sum(len(files) for files in self.files_by_name.values())
        }

def suggest_next_directory():
    """Suggest which directory to analyze next"""
    base_path = Path("Aetherra")

    # Priority order for analysis
    priority_directories = [
        "lyrixa",           # Core AI system
        "plugins",          # Plugin ecosystem
        "core",             # Core functionality
        "api",              # API layer
        "gui",              # User interface
        "tools",            # Utility tools
        "scripts",          # Automation scripts
        "utils",            # Common utilities
        "integration",      # Integration layer
        "runtime",          # Runtime components
    ]

    print("\n🎯 DIRECTORY ANALYSIS SUGGESTIONS")
    print("=" * 50)
    print("\nRecommended directories to analyze next (in priority order):")

    available_dirs = []
    for priority_dir in priority_directories:
        dir_path = base_path / priority_dir
        if dir_path.exists() and dir_path.is_dir():
            # Quick count of files
            file_count = 0
            for root, dirs, files in os.walk(dir_path):
                file_count += len([f for f in files if f.endswith(('.py', '.js', '.ts', '.json'))])

            available_dirs.append((priority_dir, file_count))
            print(f"  {len(available_dirs)}. {priority_dir}/ ({file_count} files)")

    if not available_dirs:
        print("  No priority directories found!")
        return None

    print(f"\n💡 Recommendation: Start with 'Aetherra/{available_dirs[0][0]}' ({available_dirs[0][1]} files)")
    return f"Aetherra/{available_dirs[0][0]}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Show suggestions
        suggested = suggest_next_directory()
        if suggested:
            print(f"\n❓ Would you like to analyze {suggested}?")
            print("Usage: python universal_analyzer.py <directory_path>")
        sys.exit(0)

    if not Path(target_dir).exists():
        print(f"❌ Directory '{target_dir}' does not exist!")
        sys.exit(1)

    analyzer = UniversalDirectoryAnalyzer(target_dir)
    results = analyzer.analyze_directory()

    # Show suggestions for next analysis
    suggest_next_directory()
