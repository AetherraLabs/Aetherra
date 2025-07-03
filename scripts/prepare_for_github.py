#!/usr/bin/env python3
"""
aetherra GitHub Preparation Script
Prepares the project for GitHub upload by cleaning up and organizing files
"""

import json
import shutil
from pathlib import Path


def clean_runtime_files():
    """Remove runtime-generated files that shouldn't be in Git"""
    print("🧹 Cleaning runtime files...")

    files_to_clean = [
        "memory_store.json",
        "goals_store.json",
        "aetherra_functions.json",
    ]

    for file in files_to_clean:
        if Path(file).exists():
            # Create sample/template versions
            sample_file = f"{file}.example"
            if file == "memory_store.json":
                sample_data = {
                    "memory": [],
                    "tags": {},
                    "categories": {},
                    "last_updated": "2025-06-28T00:00:00",
                }
            elif file == "goals_store.json":
                sample_data = {
                    "goals": [],
                    "agent_mode": False,
                    "active_goals": [],
                    "goal_history": [],
                    "last_updated": "2025-06-28T00:00:00",
                }
            elif file == "aetherra_functions.json":
                sample_data = {"functions": {}, "last_updated": "2025-06-28T00:00:00"}

            with open(sample_file, "w") as f:
                json.dump(sample_data, f, indent=2)

            print(f"  ✅ Created template: {sample_file}")

            # Move actual file to backup
            if not Path("backups").exists():
                Path("backups").mkdir()
            shutil.move(file, f"backups/{file}")
            print(f"  📁 Moved {file} to backups/")


def organize_documentation():
    """Organize documentation files"""
    print("📚 Organizing documentation...")

    # Create docs directory if it doesn't exist
    docs_dir = Path("docs")
    if not docs_dir.exists():
        docs_dir.mkdir()
        print("  📁 Created docs/ directory")

    # Move documentation files to docs/
    doc_files = [
        "aetherra_LANGUAGE_SPEC.md",
        "aetherra_MANIFESTO.md",
        "ARCHITECTURE.md",
        "SELF_EDITING_GUIDE.md",
        "DEBUG_SYSTEM_GUIDE.md",
    ]

    for doc in doc_files:
        if Path(doc).exists():
            shutil.move(doc, f"docs/{doc}")
            print(f"  📄 Moved {doc} to docs/")


def create_github_files():
    """Create GitHub-specific files"""
    print("🐙 Creating GitHub-specific files...")

    # Create .github directory structure
    github_dir = Path(".github")
    if not github_dir.exists():
        github_dir.mkdir()

    # Issue templates
    issue_templates = github_dir / "ISSUE_TEMPLATE"
    if not issue_templates.exists():
        issue_templates.mkdir()

    # Bug report template
    bug_template = issue_templates / "bug_report.md"
    if not bug_template.exists():
        with open(bug_template, "w") as f:
            f.write("""---
name: Bug report
about: Create a report to help us improve aetherra
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**aetherra Example**
Provide the aetherra that produces the issue:
```aetherra
# Your aetherra here
```

**Expected behavior**
What you expected to happen.

**Environment:**
 - OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
 - Python version: [e.g. 3.9.7]
 - aetherra version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
""")
        print("  🐛 Created bug report template")

    # Feature request template
    feature_template = issue_templates / "feature_request.md"
    if not feature_template.exists():
        with open(feature_template, "w") as f:
            f.write("""---
name: Feature request
about: Suggest a new aetherra feature or cognitive pattern
title: '[FEATURE] '
labels: enhancement, cognitive-pattern
assignees: ''
---

**Cognitive Pattern Description**
Describe the new AI-native programming pattern you'd like to see.

**Example Syntax**
Show how you envision the aetherra syntax:
```aetherra
# Your proposed aetherra syntax
```

**Why This Improves Cognitive Programming**
Explain how this helps developers express intentions rather than implementations.

**Additional context**
Add any other context or examples about the feature request here.
""")
        print("  💡 Created feature request template")


def create_requirements_optimization():
    """Create optimized requirements.txt"""
    print("📦 Optimizing requirements.txt...")

    # Read current requirements
    if Path("requirements.txt").exists():
        with open("requirements.txt") as f:
            lines = f.readlines()

        # Clean up and optimize
        optimized_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Add version constraints if missing
                if "==" not in line and ">=" not in line:
                    # For key packages, suggest minimum versions
                    if line.startswith("PySide6"):
                        line = "PySide6>=6.4.0"
                    elif line.startswith("numpy"):
                        line = "numpy>=1.21.0"
                    elif line.startswith("requests"):
                        line = "requests>=2.25.0"
                optimized_lines.append(line)

        # Write optimized requirements
        with open("requirements_optimized.txt", "w") as f:
            f.write("# aetherra Dependencies\n")
            f.write("# Core dependencies for the AI-native programming language\n\n")
            f.write("# GUI Framework\n")
            for line in optimized_lines:
                if "PySide6" in line or "qtawesome" in line:
                    f.write(f"{line}\n")
            f.write("\n# AI and ML\n")
            for line in optimized_lines:
                if any(
                    pkg in line for pkg in ["openai", "anthropic", "numpy", "scipy"]
                ):
                    f.write(f"{line}\n")
            f.write("\n# Utilities\n")
            for line in optimized_lines:
                if not any(
                    pkg in line
                    for pkg in [
                        "PySide6",
                        "qtawesome",
                        "openai",
                        "anthropic",
                        "numpy",
                        "scipy",
                    ]
                ):
                    f.write(f"{line}\n")

        print("  ✅ Created requirements_optimized.txt")


def verify_structure():
    """Verify the project structure is GitHub-ready"""
    print("🔍 Verifying project structure...")

    required_files = [
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "INSTALLATION.md",
        ".gitignore",
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")

    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False

    # Check core directories
    required_dirs = ["core", "ui", "plugins", "stdlib"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ Missing directory: {dir_name}/")
            return False

    return True


def create_github_commands():
    """Create a file with GitHub upload commands"""
    print("📝 Creating GitHub upload commands...")

    commands = """#!/bin/bash
# aetherra GitHub Upload Commands
# Run these commands to upload your project to GitHub

echo "🧬 Uploading aetherra to GitHub..."

# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "🧬 Initial commit: aetherra - The First AI-Native Programming Language

✨ Features:
- Revolutionary cognitive programming paradigm
- AI-powered interpreter with self-awareness
- Advanced memory and goal systems
- Self-editing and auto-debug capabilities
- Modern GUI with real-time visualization
- Comprehensive plugin ecosystem

🚀 The future of programming starts here!"

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
echo "⚠️  Replace YOUR_USERNAME with your actual GitHub username:"
echo "git remote add origin https://github.com/YOUR_USERNAME/aetherra.git"

# Set main branch
git branch -M main

# Push to GitHub
echo "🚀 Ready to push with:"
echo "git push -u origin main"

# Create first release tag
echo "🏷️  After pushing, create release with:"
echo "git tag -a v1.0.0 -m '🚀 aetherra v1.0.0 - Revolutionary AI-Native Language'"
echo "git push origin v1.0.0"

echo ""
echo "🎉 aetherra will be live on GitHub!"
echo "🌟 Don't forget to:"
echo "  1. Add GitHub topics: ai-programming, cognitive-computing, programming-language"
echo "  2. Enable GitHub Discussions"
echo "  3. Star your own repo! ⭐"
"""

    with open("github_upload_commands.sh", "w") as f:
        f.write(commands)

    # Also create Windows batch version
    commands_bat = """@echo off
REM aetherra GitHub Upload Commands for Windows
REM Run these commands to upload your project to GitHub

echo 🧬 Uploading aetherra to GitHub...

REM Initialize Git repository
git init

REM Add all files
git add .

REM Create initial commit
git commit -m "🧬 Initial commit: aetherra - The First AI-Native Programming Language"

echo ⚠️  Replace YOUR_USERNAME with your actual GitHub username:
echo git remote add origin https://github.com/YOUR_USERNAME/aetherra.git

REM Set main branch
git branch -M main

echo 🚀 Ready to push with:
echo git push -u origin main

echo 🎉 aetherra will be live on GitHub!
"""

    with open("github_upload_commands.bat", "w") as f:
        f.write(commands_bat)

    print("  ✅ Created github_upload_commands.sh")
    print("  ✅ Created github_upload_commands.bat")


def main():
    """Main preparation function"""
    print("🚀 aetherra GitHub Preparation")
    print("=" * 50)

    # Run preparation steps
    clean_runtime_files()
    print()

    organize_documentation()
    print()

    create_github_files()
    print()

    create_requirements_optimization()
    print()

    create_github_commands()
    print()

    # Final verification
    if verify_structure():
        print("\n🎉 aetherra is ready for GitHub!")
        print("\n📋 Next steps:")
        print("1. Review the generated files")
        print("2. Run: github_upload_commands.sh (or .bat on Windows)")
        print("3. Create your GitHub repository")
        print("4. Push your code!")
        print("\n🌟 Your revolutionary AI-native language will be live!")
    else:
        print("\n⚠️ Some issues need to be fixed before upload.")
        print("Please address the missing files/directories above.")


if __name__ == "__main__":
    main()
