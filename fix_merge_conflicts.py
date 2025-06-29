"""
Automatic merge conflict resolver for NeuroCode project.
This script removes Git merge conflict markers from all files.
"""

import glob
import re


def fix_merge_conflicts_in_file(filepath):
    """Remove merge conflict markers from a single file."""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Pattern to match merge conflict blocks
        #         # content1
        #         # content2
        #
        original_content = content

        # Remove the conflict markers and keep the content between them
        # This regex captures the content between <<<<<<< and =======, and between ======= and >>>>>>>
        pattern = r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [a-f0-9]+.*?\n"

        def replace_conflict(match):
            head_content = match.group(1)
            other_content = match.group(2)

            # If content is similar, prefer the longer/more complete version
            if len(head_content.strip()) >= len(other_content.strip()):
                return head_content + "\n"
            else:
                return other_content + "\n"

        # Replace all conflict blocks
        content = re.sub(pattern, replace_conflict, content, flags=re.DOTALL)

        # Also handle simple conflict markers without content between
        content = re.sub(r"<<<<<<< HEAD\n", "", content)
        content = re.sub(r"=======\n", "", content)
        content = re.sub(r">>>>>>> [a-f0-9]+.*?\n", "", content)

        # Write back if content changed
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed merge conflicts in: {filepath}")
            return True

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

    return False


def fix_all_merge_conflicts():
    """Fix merge conflicts in all relevant files."""

    # File extensions to process
    extensions = [
        "*.py",
        "*.md",
        "*.txt",
        "*.toml",
        "*.yaml",
        "*.yml",
        "*.json",
        "*.neuro",
        "*.js",
        "*.ts",
        "*.html",
        "*.css",
    ]

    files_fixed = 0
    total_files = 0

    print("🔧 Fixing merge conflicts in NeuroCode project...")

    for ext in extensions:
        for filepath in glob.glob(f"**/{ext}", recursive=True):
            # Skip certain directories
            if any(skip in filepath for skip in ["__pycache__", ".git", "backups", "node_modules"]):
                continue

            total_files += 1
            if fix_merge_conflicts_in_file(filepath):
                files_fixed += 1

    print("\n✅ Processing complete!")
    print(f"📁 Files checked: {total_files}")
    print(f"🔧 Files fixed: {files_fixed}")

    if files_fixed > 0:
        print("\n🚀 Ready to commit and push to GitHub!")
    else:
        print("\n✨ No merge conflicts found!")


if __name__ == "__main__":
    fix_all_merge_conflicts()
