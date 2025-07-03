#!/usr/bin/env python3
"""
Aetherra Warning Analysis Tool
Comprehensive analysis and categorization of code warnings across the project.
"""

import subprocess
import json
import re
from pathlib import Path
from datetime import datetime

class WarningAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.warning_categories = {
            'unused_imports': [],
            'unused_variables': [],
            'syntax_warnings': [],
            'deprecation_warnings': [],
            'type_hints': [],
            'docstring_missing': [],
            'code_style': [],
            'potential_bugs': [],
            'security_issues': [],
            'performance_issues': [],
            'other': []
        }
        self.total_warnings = 0

    def run_pylint_analysis(self):
        """Run pylint on all Python files and collect warnings."""
        print("🔍 Running pylint analysis...")

        python_files = list(self.project_root.rglob("*.py"))
        all_warnings = []

        for py_file in python_files:
            if any(exclude in str(py_file) for exclude in ['__pycache__', '.git', 'venv', 'env']):
                continue

            try:
                result = subprocess.run(
                    ['pylint', str(py_file), '--output-format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.stdout:
                    try:
                        warnings = json.loads(result.stdout)
                        for warning in warnings:
                            warning['file'] = str(py_file)
                            all_warnings.append(warning)
                    except json.JSONDecodeError:
                        pass

            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Skip files that can't be analyzed
                continue

        return all_warnings

    def run_flake8_analysis(self):
        """Run flake8 for additional style and syntax warnings."""
        print("🔍 Running flake8 analysis...")

        try:
            result = subprocess.run(
                ['flake8', '.', '--format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️ flake8 not available, using alternative analysis")
            return []

        return []

    def categorize_warning(self, warning):
        """Categorize a warning based on its type and message."""
        message = warning.get('message', '').lower()
        symbol = warning.get('symbol', '').lower()
        type_code = warning.get('type', '').lower()

        # Unused imports and variables
        if any(keyword in message for keyword in ['unused import', 'unused variable', 'unused argument']):
            if 'import' in message:
                self.warning_categories['unused_imports'].append(warning)
            else:
                self.warning_categories['unused_variables'].append(warning)

        # Syntax and style warnings
        elif any(keyword in message for keyword in ['invalid syntax', 'syntax error', 'indentation']):
            self.warning_categories['syntax_warnings'].append(warning)

        # Deprecation warnings
        elif any(keyword in message for keyword in ['deprecated', 'deprecation']):
            self.warning_categories['deprecation_warnings'].append(warning)

        # Type hints
        elif any(keyword in message for keyword in ['type hint', 'missing type', 'annotation']):
            self.warning_categories['type_hints'].append(warning)

        # Missing docstrings
        elif any(keyword in message for keyword in ['missing docstring', 'undocumented']):
            self.warning_categories['docstring_missing'].append(warning)

        # Code style (PEP 8, naming, etc.)
        elif any(keyword in message for keyword in ['naming convention', 'line too long', 'whitespace', 'pep 8']):
            self.warning_categories['code_style'].append(warning)

        # Potential bugs
        elif any(keyword in message for keyword in ['undefined variable',
            'attribute error',
            'name error',
            'unreachable']):
            self.warning_categories['potential_bugs'].append(warning)

        # Security issues
        elif any(keyword in message for keyword in ['security', 'unsafe', 'injection', 'eval']):
            self.warning_categories['security_issues'].append(warning)

        # Performance issues
        elif any(keyword in message for keyword in ['performance', 'inefficient', 'slow']):
            self.warning_categories['performance_issues'].append(warning)

        else:
            self.warning_categories['other'].append(warning)

    def analyze_custom_warnings(self):
        """Analyze custom patterns in code that might indicate issues."""
        print("🔍 Analyzing custom warning patterns...")

        custom_warnings = []
        python_files = list(self.project_root.rglob("*.py"))

        patterns = {
            'TODO/FIXME': re.compile(r'#\s*(TODO|FIXME|XXX|HACK)', re.IGNORECASE),
            'print_statements': re.compile(r'^\s*print\s*\(', re.MULTILINE),
            'bare_except': re.compile(r'except\s*:', re.MULTILINE),
            'global_vars': re.compile(r'^\s*global\s+', re.MULTILINE),
            'long_lines': re.compile(r'^.{120,}$', re.MULTILINE),
        }

        for py_file in python_files:
            if any(exclude in str(py_file) for exclude in ['__pycache__', '.git', 'venv', 'env']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern_name, pattern in patterns.items():
                    matches = pattern.finditer(content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        custom_warnings.append({
                            'file': str(py_file),
                            'line': line_num,
                            'type': 'custom',
                            'symbol': pattern_name,
                            'message': f'{pattern_name}: {match.group().strip()[:100]}',
                            'category': 'code_style' if pattern_name in ['long_lines', 'print_statements'] else 'other'
                        })
            except (UnicodeDecodeError, PermissionError):
                continue

        return custom_warnings

    def generate_report(self):
        """Generate a comprehensive warning analysis report."""
        print("📊 Generating warning analysis report...")

        # Count warnings by category
        category_counts = {cat: len(warnings) for cat, warnings in self.warning_categories.items()}
        self.total_warnings = sum(category_counts.values())

        # Priority levels
        priority_high = ['syntax_warnings', 'potential_bugs', 'security_issues']
        priority_medium = ['unused_imports', 'unused_variables', 'deprecation_warnings', 'performance_issues']
        priority_low = ['type_hints', 'docstring_missing', 'code_style', 'other']

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_warnings': self.total_warnings,
            'categories': category_counts,
            'priority_analysis': {
                'high': sum(category_counts[cat] for cat in priority_high),
                'medium': sum(category_counts[cat] for cat in priority_medium),
                'low': sum(category_counts[cat] for cat in priority_low)
            },
            'detailed_warnings': self.warning_categories
        }

        # Save detailed report
        with open('warning_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Generate human-readable summary
        self.print_summary_report(report)

        return report

    def print_summary_report(self, report):
        """Print a human-readable summary of the warning analysis."""
        print("\n" + "="*60)
        print("🔍 AETHERRA WARNING ANALYSIS REPORT")
        print("="*60)
        print(f"📊 Total Warnings Found: {report['total_warnings']}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n🎯 PRIORITY BREAKDOWN:")
        print(f"🔴 High Priority:   {report['priority_analysis']['high']:4d} warnings")
        print(f"🟡 Medium Priority: {report['priority_analysis']['medium']:4d} warnings")
        print(f"🟢 Low Priority:    {report['priority_analysis']['low']:4d} warnings")

        print("\n📋 CATEGORY BREAKDOWN:")
        for category, count in sorted(report['categories'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                category_name = category.replace('_', ' ').title()
                priority = "🔴" if category in ['syntax_warnings', 'potential_bugs', 'security_issues'] else \
                          "🟡" if category in ['unused_imports', 'unused_variables', 'deprecation_warnings'] else "🟢"
                print(f"{priority} {category_name:<20}: {count:4d} warnings")

        print("\n💡 RECOMMENDATIONS:")
        high_priority = report['priority_analysis']['high']
        if high_priority > 0:
            print(f"🔴 URGENT: Address {high_priority} high-priority warnings immediately")

        medium_priority = report['priority_analysis']['medium']
        if medium_priority > 0:
            print(f"🟡 MEDIUM: Plan to fix {medium_priority} medium-priority warnings")

        if report['categories']['unused_imports'] > 50:
            print("🔧 Quick Win: Run automated unused import removal")

        if report['categories']['code_style'] > 100:
            print("🎨 Style: Consider running automated code formatting")

        print(f"\n📄 Detailed report saved to: warning_analysis_report.json")
        print("="*60)

    def run_analysis(self):
        """Run the complete warning analysis."""
        print("🚀 Starting Aetherra Warning Analysis...")

        # Collect warnings from multiple sources
        all_warnings = []

        # Try pylint analysis
        try:
            pylint_warnings = self.run_pylint_analysis()
            all_warnings.extend(pylint_warnings)
            print(f"✅ Pylint analysis complete: {len(pylint_warnings)} warnings")
        except Exception as e:
            print(f"⚠️ Pylint analysis failed: {e}")

        # Try flake8 analysis
        try:
            flake8_warnings = self.run_flake8_analysis()
            all_warnings.extend(flake8_warnings)
            print(f"✅ Flake8 analysis complete: {len(flake8_warnings)} warnings")
        except Exception as e:
            print(f"⚠️ Flake8 analysis failed: {e}")

        # Custom pattern analysis
        try:
            custom_warnings = self.analyze_custom_warnings()
            all_warnings.extend(custom_warnings)
            print(f"✅ Custom pattern analysis complete: {len(custom_warnings)} warnings")
        except Exception as e:
            print(f"⚠️ Custom analysis failed: {e}")

        # Categorize all warnings
        for warning in all_warnings:
            self.categorize_warning(warning)

        # Generate report
        return self.generate_report()

def main():
    """Main entry point for warning analysis."""
    print("🌟 Aetherra Code Quality Analysis Tool")
    print("Analyzing project warnings and generating improvement recommendations...\n")

    analyzer = WarningAnalyzer()
    report = analyzer.run_analysis()

    print("\n🎯 Next Steps:")
    print("1. Review warning_analysis_report.json for detailed findings")
    print("2. Run 'python warning_fixer.py' for automated fixes")
    print("3. Address high-priority warnings manually")
    print("4. Re-run analysis to track progress")

if __name__ == "__main__":
    main()
