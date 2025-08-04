#!/usr/bin/env python3
"""
Directory Documentation Generator - Creates README.md files for each major directory
"""

import json
from pathlib import Path

def load_analysis():
    """Load the updated project analysis"""
    with open('aetherra_project_analysis.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_directory_readme(dir_path, dir_info):
    """Generate README.md content for a directory"""

    readme_content = f"""# {Path(dir_path).name}

## Purpose
{dir_info['purpose']}

## Contents
This directory contains **{dir_info['total_files']} files** organized as follows:

"""

    # File type breakdown
    if dir_info['file_counts']:
        readme_content += "### File Types\n\n"
        for file_type, count in sorted(dir_info['file_counts'].items(), key=lambda x: x[1], reverse=True):
            readme_content += f"- **{file_type.replace('_', ' ').title()}**: {count} files\n"
        readme_content += "\n"

    # Subdirectories
    if dir_info['subdirectories']:
        readme_content += "### Subdirectories\n\n"
        for subdir in sorted(dir_info['subdirectories']):
            readme_content += f"- `{subdir}/`\n"
        readme_content += "\n"

    # Notable files (first 10)
    if dir_info['files']:
        readme_content += "### Key Files\n\n"

        # Group files by category
        files_by_category = {}
        for file_info in dir_info['files']:
            category = file_info['category']
            if category not in files_by_category:
                files_by_category[category] = []
            files_by_category[category].append(file_info)

        for category, files in sorted(files_by_category.items()):
            if category == 'other':
                continue  # Skip 'other' category for now

            readme_content += f"#### {category.replace('_', ' ').title()}\n\n"
            for file_info in files[:5]:  # Show first 5 files per category
                file_name = file_info['name']

                # Add description based on file analysis
                description = ""
                if 'python_analysis' in file_info and file_info['python_analysis'].get('docstring'):
                    description = f" - {file_info['python_analysis']['docstring'][:100]}..."
                elif file_name.lower().startswith('test_'):
                    description = " - Test file"
                elif file_name.lower().startswith('demo_'):
                    description = " - Demonstration/example file"
                elif file_name == '__init__.py':
                    description = " - Python package initialization"
                elif file_name.endswith('.md'):
                    description = " - Documentation file"
                elif file_name.endswith('.json'):
                    description = " - Configuration file"

                readme_content += f"- `{file_name}`{description}\n"

            if len(files) > 5:
                readme_content += f"- ... and {len(files) - 5} more {category} files\n"
            readme_content += "\n"

    # Usage information
    readme_content += """## Usage

This directory is part of the Aetherra OS project. Files in this directory should be:

- **Documented**: Each significant file should have clear documentation
- **Tested**: Critical functionality should have corresponding tests
- **Maintained**: Regular review and updates as needed

## Development Notes

When working with files in this directory:

1. Follow the established naming conventions
2. Add appropriate documentation for new files
3. Update tests when modifying functionality
4. Consider the impact on other system components

---
*This README was automatically generated. Last updated: {Path().cwd().name} project analysis*
"""

    return readme_content

def create_directory_readmes():
    """Create README.md files for major directories"""
    analysis = load_analysis()
    directories = analysis.get('directories', {})

    created_count = 0
    skipped_count = 0

    print("📝 Generating directory README files...")
    print("=" * 50)

    for dir_path, dir_info in directories.items():
        # Skip certain directories
        skip_dirs = [
            'frontend/Lib',
            'frontend/Scripts',
            '.git',
            '__pycache__',
            'node_modules'
        ]

        if any(skip in dir_path for skip in skip_dirs):
            continue

        # Only create READMEs for directories with a reasonable number of files
        if dir_info['total_files'] == 0 or dir_info['total_files'] > 50:
            skipped_count += 1
            continue

        # Check if README already exists
        readme_path = Path(dir_path) / 'README.md'
        if readme_path.exists():
            print(f"⏭️ Skipped (exists): {dir_path}")
            skipped_count += 1
            continue

        try:
            # Generate README content
            readme_content = generate_directory_readme(dir_path, dir_info)

            # Create the README file
            readme_path.write_text(readme_content, encoding='utf-8')
            print(f"✅ Created: {readme_path}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating README for {dir_path}: {e}")

    print()
    print(f"🎯 README Generation Summary:")
    print(f"   Created: {created_count} README files")
    print(f"   Skipped: {skipped_count} directories")
    print("✅ Directory documentation complete!")

def create_main_project_breakdown():
    """Create the main project breakdown document"""
    analysis = load_analysis()

    breakdown_content = f"""# 🏗️ Aetherra Project Breakdown

*Complete file and directory analysis*

## 📊 Project Overview

**Analysis Date:** {analysis['timestamp']}
**Project Root:** {analysis['project_root']}

### Statistics
- **Total Files:** {analysis['summary']['total_files']}
- **Total Directories:** {analysis['summary']['total_directories']}
- **File Categories:** {len(analysis['summary']['file_categories'])}

### File Distribution
"""

    # Add file category breakdown
    for category, count in sorted(analysis['summary']['file_categories'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / analysis['summary']['total_files']) * 100
        breakdown_content += f"- **{category.replace('_', ' ').title()}**: {count} files ({percentage:.1f}%)\n"

    breakdown_content += f"""

## 🗂️ Directory Structure

### Major Components

"""

    # Add major directory information
    directories = analysis.get('directories', {})
    major_dirs = {k: v for k, v in directories.items() if v['total_files'] > 5 and '/' not in k.strip('.').replace('\\', '/')}

    for dir_path, dir_info in sorted(major_dirs.items()):
        breakdown_content += f"""#### `{dir_path}`
**Purpose:** {dir_info['purpose']}
**Files:** {dir_info['total_files']} total
**Key Types:** {', '.join(f"{k} ({v})" for k, v in sorted(dir_info['file_counts'].items(), key=lambda x: x[1], reverse=True)[:3])}

"""

    breakdown_content += """## 🎯 File Utilization

### Core System Files
Files essential for Aetherra OS operation:

- **Python Modules**: Core functionality and system components
- **Configuration Files**: System and component configuration
- **Database Files**: Data storage and memory systems
- **API Components**: Interface and communication modules

### Development Files
Files supporting development and testing:

- **Test Files**: Automated testing and validation
- **Demo Files**: Examples and demonstrations
- **Documentation**: Project documentation and guides
- **Tools**: Development utilities and scripts

### Support Files
Files supporting the project ecosystem:

- **Build Files**: Compilation and deployment
- **Environment Files**: Development environment setup
- **Log Files**: System and application logs
- **Metadata**: Project metadata and package information

## 📋 Maintenance Guidelines

### File Organization
1. **Core components** should remain in `Aetherra/` directory
2. **Tests** are organized in `tests/` directory
3. **Documentation** is organized in `docs-organized/` directory
4. **Database files** are centralized in `Aetherra/data/databases/`

### Development Practices
1. **Add documentation** for new significant files
2. **Include tests** for critical functionality
3. **Follow naming conventions** established in each directory
4. **Update README files** when directory contents change significantly

### Regular Maintenance
- **Monthly review** of file organization
- **Quarterly cleanup** of unused files
- **Annual architecture review** for structural improvements

---

## 🔍 Detailed Analysis

For detailed information about specific directories and files, see:

- Individual directory `README.md` files
- `DUPLICATE_FILES_REPORT.md` - Analysis of duplicate files
- `FILE_CATEGORY_ANALYSIS.md` - Detailed file type breakdown
- `CONSOLIDATION_PLAN.md` - File consolidation recommendations

---
*This breakdown provides a comprehensive view of the Aetherra project structure and file organization.*
"""

    # Save the breakdown
    with open('PROJECT_BREAKDOWN.md', 'w', encoding='utf-8') as f:
        f.write(breakdown_content)

    print("📋 Created PROJECT_BREAKDOWN.md")

def main():
    """Main execution function"""
    print("🏗️ Creating comprehensive project documentation...")
    print()

    # Create directory READMEs
    create_directory_readmes()
    print()

    # Create main project breakdown
    create_main_project_breakdown()
    print()

    print("🎉 Project documentation system complete!")
    print()
    print("📚 Documentation created:")
    print("   - Individual directory README.md files")
    print("   - PROJECT_BREAKDOWN.md (master overview)")
    print("   - Analysis reports (already generated)")

if __name__ == "__main__":
    main()
