#!/usr/bin/env python3
"""
Simple Warning Analysis Tool
Quick analysis of common code patterns without external dependencies.
"""

import re
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

def analyze_file(file_path):
    """Analyze a single Python file for common issues."""
    warnings = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except (UnicodeDecodeError, PermissionError):
        return warnings

    # Pattern-based analysis
    patterns = {
        'unused_import': re.compile(r'^import\s+(\w+)(?:\s*,\s*\w+)*\s*$'),
        'from_import': re.compile(r'^from\s+[\w.]+\s+import\s+(.+)$'),
        'print_debug': re.compile(r'^\s*print\s*\('),
        'long_line': re.compile(r'^.{120,}$'),
        'trailing_space': re.compile(r'\s+$'),
        'todo_fixme': re.compile(r'#\s*(TODO|FIXME|XXX|HACK)', re.IGNORECASE),
        'bare_except': re.compile(r'except\s*:'),
        'global_var': re.compile(r'^\s*global\s+'),
    }

    imports_found = set()
    names_used = set()

    # First pass: collect imports and usage
    for line_num, line in enumerate(lines, 1):
        # Track imports
        import_match = patterns['unused_import'].match(line.strip())
        if import_match:
            imports_found.add(import_match.group(1))

        from_match = patterns['from_import'].match(line.strip())
        if from_match:
            imported_names = [name.strip() for name in from_match.group(1).split(',')]
            imports_found.update(imported_names)

        # Track name usage (simple heuristic)
        words = re.findall(r'\b\w+\b', line)
        names_used.update(words)

    # Second pass: find issues
    for line_num, line in enumerate(lines, 1):
        # Check each pattern
        for pattern_name, pattern in patterns.items():
            if pattern.search(line):
                if pattern_name == 'unused_import':
                    match = patterns['unused_import'].match(line.strip())
                    if match and match.group(1) not in names_used:
                        warnings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'unused_import',
                            'message': f'Unused import: {match.group(1)}',
                            'severity': 'medium'
                        })
                elif pattern_name == 'print_debug':
                    if 'print(' in line and ('debug' in line.lower() or 'test' in line.lower()):
                        warnings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'debug_print',
                            'message': 'Debug print statement',
                            'severity': 'low'
                        })
                elif pattern_name == 'long_line':
                    if not line.strip().startswith('#'):
                        warnings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'long_line',
                            'message': f'Line too long ({len(line)} characters)',
                            'severity': 'low'
                        })
                elif pattern_name == 'trailing_space':
                    warnings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'trailing_whitespace',
                        'message': 'Trailing whitespace',
                        'severity': 'low'
                    })
                elif pattern_name == 'todo_fixme':
                    warnings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'todo_comment',
                        'message': f'TODO/FIXME comment: {line.strip()}',
                        'severity': 'low'
                    })
                elif pattern_name == 'bare_except':
                    warnings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'bare_except',
                        'message': 'Bare except clause',
                        'severity': 'medium'
                    })
                elif pattern_name == 'global_var':
                    warnings.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'global_variable',
                        'message': 'Global variable usage',
                        'severity': 'medium'
                    })

    return warnings

def main():
    """Main analysis function."""
    print("🔍 Quick Warning Analysis Starting...")

    project_root = Path('.')
    python_files = list(project_root.rglob("*.py"))

    all_warnings = []
    category_counts = defaultdict(int)

    files_processed = 0
    for py_file in python_files:
        if any(exclude in str(py_file) for exclude in ['__pycache__', '.git', 'venv', 'env', 'backup']):
            continue

        warnings = analyze_file(py_file)
        all_warnings.extend(warnings)
        files_processed += 1

        for warning in warnings:
            category_counts[warning['type']] += 1

        if warnings:
            print(f"📁 {py_file.relative_to(project_root)}: {len(warnings)} warnings")

    # Generate summary
    total_warnings = len(all_warnings)
    severity_counts = defaultdict(int)
    for warning in all_warnings:
        severity_counts[warning['severity']] += 1

    print("\n" + "="*60)
    print("📊 QUICK WARNING ANALYSIS RESULTS")
    print("="*60)
    print(f"📁 Files Analyzed: {files_processed}")
    print(f"⚠️ Total Warnings: {total_warnings}")

    print(f"\n🎯 BY SEVERITY:")
    print(f"🔴 High:   {severity_counts['high']:4d} warnings")
    print(f"🟡 Medium: {severity_counts['medium']:4d} warnings")
    print(f"🟢 Low:    {severity_counts['low']:4d} warnings")

    print(f"\n📋 BY CATEGORY:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            category_name = category.replace('_', ' ').title()
            print(f"  {category_name:<20}: {count:4d} warnings")

    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'files_analyzed': files_processed,
        'total_warnings': total_warnings,
        'severity_breakdown': dict(severity_counts),
        'category_breakdown': dict(category_counts),
        'detailed_warnings': all_warnings
    }

    with open('quick_warning_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Detailed report: quick_warning_report.json")

    # Recommendations
    print(f"\n💡 QUICK FIXES AVAILABLE:")
    if category_counts['unused_import'] > 0:
        print(f"  🔧 {category_counts['unused_import']} unused imports can be removed automatically")
    if category_counts['trailing_whitespace'] > 0:
        print(f"  🧹 {category_counts['trailing_whitespace']} trailing whitespace issues can be fixed")
    if category_counts['long_line'] > 0:
        print(f"  📏 {category_counts['long_line']} long lines could be reformatted")

    print("\n🚀 Run 'python warning_fixer.py' to apply automated fixes!")
    print("="*60)

if __name__ == "__main__":
    main()
