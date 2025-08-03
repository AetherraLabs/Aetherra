#!/usr/bin/env python3
"""
Intelligence Report Generator
Creates comprehensive reports from advanced project analysis
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import os

class IntelligenceReportGenerator:
    def __init__(self, analysis_file='advanced_project_intelligence.json'):
        self.analysis_file = analysis_file
        self.data = self.load_analysis_data()
        
    def load_analysis_data(self):
        """Load analysis data from JSON file"""
        if not Path(self.analysis_file).exists():
            print(f"❌ Analysis file {self.analysis_file} not found!")
            return None
            
        with open(self.analysis_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_complete_directory_overview(self):
        """Generate comprehensive directory overview"""
        if not self.data:
            return "No analysis data available"
        
        report = []
        report.append("# 🗂️ COMPLETE DIRECTORY INTELLIGENCE OVERVIEW")
        report.append("=" * 80)
        report.append(f"**Analysis Date:** {self.data['timestamp']}")
        report.append(f"**Project Root:** {self.data['project_root']}")
        report.append("")
        
        # Summary statistics
        summary = self.data['summary']
        report.append("## 📊 PROJECT INTELLIGENCE SUMMARY")
        report.append("")
        report.append(f"- **Total Directories:** {summary['total_directories']:,}")
        report.append(f"- **Total Files:** {summary['total_files']:,}")
        report.append(f"- **Total Project Size:** {summary.get('complexity_analysis', {}).get('total_project_size', 0):,} bytes")
        report.append(f"- **Average File Size:** {summary.get('complexity_analysis', {}).get('average_file_size', 0):.1f} bytes")
        report.append("")
        
        # Language breakdown
        report.append("### 🌐 Programming Languages")
        languages = summary.get('languages', {})
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / summary['total_files']) * 100
            report.append(f"- **{lang}:** {count} files ({percentage:.1f}%)")
        report.append("")
        
        # File type breakdown
        report.append("### 📁 File Types")
        file_types = summary.get('file_types', {})
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:20]:
            percentage = (count / summary['total_files']) * 100
            ext_display = ext if ext != 'no_extension' else '(no extension)'
            report.append(f"- **{ext_display}:** {count} files ({percentage:.1f}%)")
        report.append("")
        
        # Directory analysis
        report.append("## 📂 COMPREHENSIVE DIRECTORY ANALYSIS")
        report.append("")
        
        directories = self.data.get('directories', {})
        
        # Sort directories by path depth and name
        sorted_dirs = sorted(directories.items(), key=lambda x: (len(Path(x[0]).parts), x[0]))
        
        for dir_path, dir_data in sorted_dirs:
            self._add_directory_section(report, dir_path, dir_data)
        
        return "\n".join(report)
    
    def _add_directory_section(self, report, dir_path, dir_data):
        """Add detailed directory section to report"""
        path_obj = Path(dir_path)
        depth = len(path_obj.parts) - len(Path(self.data['project_root']).parts)
        indent = "  " * depth
        
        report.append(f"{indent}### 📁 `{dir_data['name']}`")
        report.append(f"{indent}**Path:** `{dir_path}`")
        report.append("")
        
        # Purpose and description
        report.append(f"{indent}**Purpose:** {dir_data['purpose']}")
        report.append("")
        
        # Statistics
        stats = [
            f"Files: {dir_data['total_files']}",
            f"Size: {dir_data['total_size']:,} bytes",
            f"Subdirectories: {len(dir_data['subdirectories'])}"
        ]
        
        if dir_data['complexity_score'] > 0:
            stats.append(f"Complexity: {dir_data['complexity_score']}")
        
        report.append(f"{indent}**Statistics:** {' | '.join(stats)}")
        report.append("")
        
        # File types in directory
        if dir_data['file_types']:
            file_types_str = ", ".join([f"{ext}({count})" for ext, count in dir_data['file_types'].items()])
            report.append(f"{indent}**File Types:** {file_types_str}")
            report.append("")
        
        # Programming languages
        if dir_data['programming_languages']:
            langs_str = ", ".join([f"{lang}({count})" for lang, count in dir_data['programming_languages'].items() if lang != 'Other'])
            if langs_str:
                report.append(f"{indent}**Languages:** {langs_str}")
                report.append("")
        
        # Main files and entry points
        if dir_data['main_files']:
            report.append(f"{indent}**Key Files:** {', '.join(dir_data['main_files'])}")
            report.append("")
        
        if dir_data['entry_points']:
            report.append(f"{indent}**Entry Points:** {', '.join(dir_data['entry_points'])}")
            report.append("")
        
        # Quality indicators
        quality = dir_data['quality_indicators']
        quality_items = []
        if quality.get('has_readme'): quality_items.append("✅ README")
        if quality.get('has_tests'): quality_items.append("✅ Tests")
        if quality.get('has_documentation'): quality_items.append("✅ Docs")
        if quality.get('organized_structure'): quality_items.append("✅ Organized")
        
        if quality_items:
            report.append(f"{indent}**Quality:** {' | '.join(quality_items)}")
            report.append("")
        
        # Subdirectories
        if dir_data['subdirectories']:
            subdirs_str = ", ".join(dir_data['subdirectories'])
            report.append(f"{indent}**Contains:** {subdirs_str}")
            report.append("")
        
        report.append("")
    
    def generate_detailed_file_inventory(self):
        """Generate detailed file-by-file inventory"""
        if not self.data:
            return "No analysis data available"
        
        report = []
        report.append("# 📄 COMPLETE FILE INVENTORY & INTELLIGENCE")
        report.append("=" * 80)
        report.append("")
        
        files = self.data.get('files', {})
        
        # Group files by directory
        files_by_dir = defaultdict(list)
        for file_path, file_data in files.items():
            dir_path = str(Path(file_path).parent)
            files_by_dir[dir_path].append((file_path, file_data))
        
        # Sort directories
        for dir_path in sorted(files_by_dir.keys()):
            report.append(f"## 📁 Directory: `{dir_path}`")
            report.append("")
            
            # Sort files in directory
            dir_files = sorted(files_by_dir[dir_path], key=lambda x: x[0])
            
            for file_path, file_data in dir_files:
                self._add_file_details(report, file_path, file_data)
            
            report.append("")
        
        return "\n".join(report)
    
    def _add_file_details(self, report, file_path, file_data):
        """Add detailed file information"""
        filename = Path(file_path).name
        
        report.append(f"### 📄 `{filename}`")
        report.append("")
        
        # Basic info
        report.append(f"**Path:** `{file_path}`")
        report.append(f"**Purpose:** {file_data['purpose']}")
        report.append(f"**Language:** {file_data.get('language', 'Unknown')}")
        report.append(f"**Size:** {file_data['size']:,} bytes")
        
        if file_data.get('line_count'):
            report.append(f"**Lines:** {file_data['line_count']:,}")
        
        if file_data.get('modified'):
            report.append(f"**Modified:** {file_data['modified']}")
        
        report.append("")
        
        # Python specific details
        if file_data.get('language') == 'Python':
            self._add_python_details(report, file_data)
        
        # JavaScript specific details
        elif file_data.get('language') == 'JavaScript/TypeScript':
            self._add_javascript_details(report, file_data)
        
        # Markdown specific details
        elif file_data.get('language') == 'Markdown':
            self._add_markdown_details(report, file_data)
        
        # Configuration file details
        elif file_data.get('language') == 'Configuration':
            self._add_config_details(report, file_data)
        
        report.append("")
    
    def _add_python_details(self, report, file_data):
        """Add Python-specific file details"""
        if file_data.get('docstring'):
            report.append(f"**Description:** {file_data['docstring'][:200]}...")
            report.append("")
        
        if file_data.get('classes'):
            report.append("**Classes:**")
            for cls in file_data['classes'][:5]:  # Limit to first 5
                methods_str = f" ({len(cls['methods'])} methods)" if cls['methods'] else ""
                report.append(f"- `{cls['name']}`{methods_str}")
            if len(file_data['classes']) > 5:
                report.append(f"- ... and {len(file_data['classes']) - 5} more")
            report.append("")
        
        if file_data.get('functions'):
            report.append("**Functions:**")
            for func in file_data['functions'][:5]:  # Limit to first 5
                args_str = f"({', '.join(func['args'])})" if func['args'] else "()"
                report.append(f"- `{func['name']}{args_str}`")
            if len(file_data['functions']) > 5:
                report.append(f"- ... and {len(file_data['functions']) - 5} more")
            report.append("")
        
        if file_data.get('imports'):
            imports = [imp.get('module', str(imp)) for imp in file_data['imports'][:5]]
            report.append(f"**Key Imports:** {', '.join(imports)}")
            if len(file_data['imports']) > 5:
                report.append(f" (and {len(file_data['imports']) - 5} more)")
            report.append("")
        
        if file_data.get('complexity_score', 0) > 0:
            report.append(f"**Complexity Score:** {file_data['complexity_score']}")
            report.append("")
    
    def _add_javascript_details(self, report, file_data):
        """Add JavaScript-specific file details"""
        if file_data.get('is_react'):
            report.append("**Framework:** React")
            report.append("")
        
        if file_data.get('is_typescript'):
            report.append("**Type:** TypeScript")
            report.append("")
        
        if file_data.get('components'):
            report.append(f"**Components:** {', '.join(file_data['components'][:5])}")
            if len(file_data['components']) > 5:
                report.append(f" (and {len(file_data['components']) - 5} more)")
            report.append("")
        
        if file_data.get('imports'):
            report.append(f"**Imports:** {', '.join(file_data['imports'][:5])}")
            if len(file_data['imports']) > 5:
                report.append(f" (and {len(file_data['imports']) - 5} more)")
            report.append("")
    
    def _add_markdown_details(self, report, file_data):
        """Add Markdown-specific file details"""
        report.append(f"**Word Count:** {file_data.get('word_count', 0):,}")
        
        if file_data.get('is_readme'):
            report.append("**Type:** README Documentation")
        
        if file_data.get('headings'):
            report.append(f"**Sections:** {len(file_data['headings'])} headings")
        
        if file_data.get('links'):
            report.append(f"**Links:** {len(file_data['links'])} external links")
        
        if file_data.get('code_blocks'):
            languages = [block.get('language', 'text') for block in file_data['code_blocks']]
            lang_count = Counter(languages)
            if lang_count:
                lang_str = ', '.join([f"{lang}({count})" for lang, count in lang_count.most_common(3)])
                report.append(f"**Code Blocks:** {lang_str}")
        
        report.append("")
    
    def _add_config_details(self, report, file_data):
        """Add configuration file details"""
        report.append(f"**Format:** {file_data.get('format', 'Unknown')}")
        
        if file_data.get('is_package_config'):
            report.append("**Type:** Package Configuration")
        
        if file_data.get('keys'):
            report.append(f"**Configuration Keys:** {', '.join(file_data['keys'][:5])}")
            if len(file_data['keys']) > 5:
                report.append(f" (and {len(file_data['keys']) - 5} more)")
        
        if file_data.get('package_info'):
            pkg = file_data['package_info']
            if pkg.get('name'):
                report.append(f"**Package:** {pkg['name']} v{pkg.get('version', 'unknown')}")
            if pkg.get('dependencies'):
                report.append(f"**Dependencies:** {len(pkg['dependencies'])} packages")
        
        report.append("")
    
    def generate_intelligence_insights(self):
        """Generate intelligence insights and recommendations"""
        if not self.data:
            return "No analysis data available"
        
        report = []
        report.append("# 🧠 PROJECT INTELLIGENCE INSIGHTS")
        report.append("=" * 80)
        report.append("")
        
        # Analyze project structure
        report.append("## 🏗️ ARCHITECTURE ANALYSIS")
        report.append("")
        
        directories = self.data.get('directories', {})
        
        # Identify main components
        main_components = []
        core_dirs = []
        test_dirs = []
        doc_dirs = []
        
        for dir_path, dir_data in directories.items():
            name = dir_data['name'].lower()
            purpose = dir_data['purpose'].lower()
            
            if 'core' in name or 'engine' in name or 'kernel' in name:
                core_dirs.append(dir_data['name'])
            elif 'test' in purpose or 'test' in name:
                test_dirs.append(dir_data['name'])
            elif 'doc' in purpose or 'doc' in name:
                doc_dirs.append(dir_data['name'])
            
            if dir_data['total_files'] > 5 and dir_data['complexity_score'] > 10:
                main_components.append({
                    'name': dir_data['name'],
                    'files': dir_data['total_files'],
                    'complexity': dir_data['complexity_score'],
                    'purpose': dir_data['purpose']
                })
        
        # Report main components
        if main_components:
            report.append("### 🎯 Major Components")
            main_components.sort(key=lambda x: x['complexity'], reverse=True)
            for comp in main_components[:10]:
                report.append(f"- **{comp['name']}**: {comp['purpose']} ({comp['files']} files, complexity: {comp['complexity']})")
            report.append("")
        
        # Project health assessment
        report.append("## 🏥 PROJECT HEALTH ASSESSMENT")
        report.append("")
        
        total_files = self.data['summary']['total_files']
        
        # Calculate health metrics
        test_coverage = len([d for d in directories.values() if 'test' in d['purpose'].lower()]) / len(directories) * 100
        doc_coverage = len([d for d in directories.values() if d['quality_indicators'].get('has_documentation')]) / len(directories) * 100
        organized_dirs = len([d for d in directories.values() if d['quality_indicators'].get('organized_structure')]) / len(directories) * 100
        
        report.append(f"**Test Coverage:** {test_coverage:.1f}% of directories have testing")
        report.append(f"**Documentation:** {doc_coverage:.1f}% of directories have documentation")
        report.append(f"**Organization:** {organized_dirs:.1f}% of directories are well-organized")
        report.append("")
        
        # Complexity analysis
        complexity = self.data['summary'].get('complexity_analysis', {})
        if complexity:
            avg_complexity = complexity.get('average_complexity', 0)
            report.append(f"**Average File Complexity:** {avg_complexity:.2f}")
            
            if avg_complexity > 10:
                report.append("⚠️ **High complexity detected** - Consider refactoring complex files")
            elif avg_complexity > 5:
                report.append("⚡ **Moderate complexity** - Good balance of functionality")
            else:
                report.append("✅ **Low complexity** - Well-structured, maintainable code")
            report.append("")
        
        # Technology stack analysis
        report.append("## 🔧 TECHNOLOGY STACK")
        report.append("")
        
        languages = self.data['summary'].get('languages', {})
        if languages:
            total_lang_files = sum(languages.values())
            report.append("### Programming Languages:")
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_lang_files) * 100
                report.append(f"- **{lang}:** {percentage:.1f}% ({count} files)")
            report.append("")
        
        # Recommendations
        report.append("## 🎯 RECOMMENDATIONS")
        report.append("")
        
        recommendations = []
        
        if test_coverage < 30:
            recommendations.append("📝 **Increase test coverage** - Add more test files to improve code reliability")
        
        if doc_coverage < 50:
            recommendations.append("📚 **Improve documentation** - Add README files and documentation to more directories")
        
        if avg_complexity > 15:
            recommendations.append("🔄 **Refactor complex code** - Break down large files into smaller, more manageable modules")
        
        # Check for potential duplicates
        files = self.data.get('files', {})
        file_sizes = defaultdict(list)
        for file_path, file_data in files.items():
            if file_data.get('hash'):
                file_sizes[file_data['hash']].append(file_path)
        
        duplicates = {h: paths for h, paths in file_sizes.items() if len(paths) > 1}
        if duplicates:
            recommendations.append(f"🔍 **Remove duplicates** - Found {len(duplicates)} groups of duplicate files")
        
        if not recommendations:
            recommendations.append("✅ **Project is well-structured** - Continue following current best practices")
        
        for rec in recommendations:
            report.append(f"- {rec}")
        
        report.append("")
        
        return "\n".join(report)
    
    def save_all_reports(self):
        """Generate and save all comprehensive reports"""
        print("📊 Generating comprehensive intelligence reports...")
        
        # Directory overview
        directory_report = self.generate_complete_directory_overview()
        with open('COMPLETE_DIRECTORY_INTELLIGENCE.md', 'w', encoding='utf-8') as f:
            f.write(directory_report)
        print("✅ Complete Directory Intelligence saved to COMPLETE_DIRECTORY_INTELLIGENCE.md")
        
        # File inventory
        file_report = self.generate_detailed_file_inventory()
        with open('COMPLETE_FILE_INVENTORY.md', 'w', encoding='utf-8') as f:
            f.write(file_report)
        print("✅ Complete File Inventory saved to COMPLETE_FILE_INVENTORY.md")
        
        # Intelligence insights
        insights_report = self.generate_intelligence_insights()
        with open('PROJECT_INTELLIGENCE_INSIGHTS.md', 'w', encoding='utf-8') as f:
            f.write(insights_report)
        print("✅ Project Intelligence Insights saved to PROJECT_INTELLIGENCE_INSIGHTS.md")
        
        print("\n🎉 All intelligence reports generated successfully!")
        print("📁 Files created:")
        print("   - COMPLETE_DIRECTORY_INTELLIGENCE.md")
        print("   - COMPLETE_FILE_INVENTORY.md") 
        print("   - PROJECT_INTELLIGENCE_INSIGHTS.md")

if __name__ == "__main__":
    generator = IntelligenceReportGenerator()
    generator.save_all_reports()
