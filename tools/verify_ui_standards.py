#!/usr/bin/env python
"""
Verification tool for UI standards compliance.

This script checks the codebase for remaining instances of:
1. Emojis
2. Unsupported Qt CSS styling
3. Inconsistent styling patterns
4. Chat bubble styling
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Define patterns to search for
EMOJI_PATTERN = re.compile(
    r"[^\x00-\x7F]+"
)  # Non-ASCII characters that might be emojis
UNSUPPORTED_CSS_PATTERNS = [
    r"box-shadow\s*:",
    r"text-shadow\s*:",
    r"-webkit-",
    r"-moz-",
    r"gradient\s*\(",
    r"animation\s*:",
    r"transform\s*:",
]
CHAT_BUBBLE_PATTERNS = [
    r"border-radius\s*:\s*[2-9][0-9]px",  # Large border radius suggesting bubble
    r"chat[\-_]?bubble",
    r"message[\-_]?bubble",
]
# Define allowed standard spacing values
ALLOWED_SPACING = [0, 1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48]
ALLOWED_VALUES_REGEX = "|".join([f"{val}" for val in ALLOWED_SPACING])

# Completely rewrite the regex to properly handle multiple values and dynamic values
INCONSISTENT_SPACING = [
    # Ignore dynamic spacing values (containing get_spacing) and values from our allowed list
    # Also ignore rem-based values that follow our standards (they should be converted to px)
    r"margin\s*:\s*(?!(?:(?:"
    + ALLOWED_VALUES_REGEX
    + r")px|0px?|auto|\{[^}]*get_spacing[^}]*\}px|\d+px \d+px|\d+px \d+px \d+px \d+px))[^;]*;",
    r"padding\s*:\s*(?!(?:(?:"
    + ALLOWED_VALUES_REGEX
    + r")px|0px?|\{[^}]*get_spacing[^}]*\}px|\d+px \d+px|\d+px \d+px \d+px \d+px))[^;]*;",
]


class UiStandardVerifier:
    """Verifies UI standards compliance across the codebase."""

    def __init__(self, root_dir: str, exclude_dirs: Optional[List[str]] = None):
        """Initialize the verifier.

        Args:
            root_dir: Root directory to scan
            exclude_dirs: List of directories to exclude
        """
        self.root_dir = Path(root_dir)
        self.exclude_dirs = exclude_dirs or [
            ".git",
            "venv",
            ".venv",
            "__pycache__",
            "node_modules",
        ]
        self.issues_found = {
            "emoji": [],
            "unsupported_css": [],
            "chat_bubble": [],
            "inconsistent_spacing": [],
        }

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if a file should be checked."""
        # Skip excluded directories
        for excluded in self.exclude_dirs:
            if excluded in str(file_path):
                return False

        # Only check certain file types
        extensions = [
            ".py",
            ".qss",
            ".css",
            ".html",
            ".md",
            ".txt",
            ".json",
            ".js",
            ".ts",
        ]
        return file_path.suffix in extensions

    def check_file(self, file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
        """Check a single file for UI standards violations."""
        file_issues = {
            "emoji": [],
            "unsupported_css": [],
            "chat_bubble": [],
            "inconsistent_spacing": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check for emojis
                if EMOJI_PATTERN.search(line):
                    file_issues["emoji"].append((i, line.strip()))

                # Check for unsupported CSS
                for pattern in UNSUPPORTED_CSS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        file_issues["unsupported_css"].append((i, line.strip()))
                        break

                # Check for chat bubbles
                for pattern in CHAT_BUBBLE_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        file_issues["chat_bubble"].append((i, line.strip()))
                        break

                # Skip inconsistent spacing check for lines with dynamic spacing
                if "get_spacing" in line:
                    continue

                # Skip for standard spacing formats (px units with standard values)
                skip_check = False
                for val in ALLOWED_SPACING:
                    if f"{val}px" in line:
                        skip_check = True
                        break

                if skip_check:
                    continue

                # Only check lines that actually contain margin or padding
                if "margin:" in line.lower() or "padding:" in line.lower():
                    # Special cases
                    if "0px" in line or "0;" in line or "0 0" in line:
                        continue

                    file_issues["inconsistent_spacing"].append((i, line.strip()))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return file_issues

    def scan_directory(self) -> Dict[str, List[Tuple[Path, int, str]]]:
        """Scan the entire directory structure for issues."""
        all_issues = {
            "emoji": [],
            "unsupported_css": [],
            "chat_bubble": [],
            "inconsistent_spacing": [],
        }

        print(f"[INFO] Scanning directory: {self.root_dir}")

        files_checked = 0
        for root, dirs, files in os.walk(self.root_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                if self.should_check_file(file_path):
                    files_checked += 1
                    if files_checked % 100 == 0:
                        print(f"[INFO] Checked {files_checked} files...")

                    file_issues = self.check_file(file_path)

                    # Add issues to the overall list
                    for issue_type, issues in file_issues.items():
                        for line_num, line_content in issues:
                            all_issues[issue_type].append(
                                (file_path, line_num, line_content)
                            )

        print(f"[INFO] Completed scan of {files_checked} files")
        return all_issues

    def generate_report(self, issues: Dict[str, List[Tuple[Path, int, str]]]) -> str:
        """Generate a report of all issues found."""
        report = "# UI Standards Verification Report\n\n"

        total_issues = sum(len(issue_list) for issue_list in issues.values())
        report += f"Total issues found: {total_issues}\n\n"

        for issue_type, issue_list in issues.items():
            report += f"## {issue_type.replace('_', ' ').title()} Issues: {len(issue_list)}\n\n"

            if issue_list:
                report += "| File | Line | Content |\n"
                report += "| ---- | ---- | ------- |\n"

                for file_path, line_num, line_content in issue_list:
                    # Truncate long lines
                    if len(line_content) > 50:
                        line_content = line_content[:47] + "..."
                    # Escape pipe characters
                    line_content = line_content.replace("|", "\\|")

                    report += f"| {file_path.relative_to(self.root_dir)} | {line_num} | `{line_content}` |\n"
            else:
                report += "No issues found.\n"

            report += "\n"

        return report

    def run_verification(self, output_file: Optional[str] = None) -> bool:
        """Run the verification and generate a report."""
        issues = self.scan_directory()
        report = self.generate_report(issues)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"[INFO] Report written to {output_file}")
        else:
            print(report)

        total_issues = sum(len(issue_list) for issue_list in issues.values())
        return total_issues == 0


def main():
    parser = argparse.ArgumentParser(description="Verify UI standards compliance")
    parser.add_argument("--dir", default=".", help="Root directory to scan")
    parser.add_argument("--exclude", nargs="+", help="Directories to exclude")
    parser.add_argument("--output", help="Output report file")
    args = parser.parse_args()

    verifier = UiStandardVerifier(args.dir, args.exclude)
    success = verifier.run_verification(args.output)

    if success:
        print("[SUCCESS] No UI standards violations found!")
        sys.exit(0)
    else:
        print("[WARNING] UI standards violations found. See report for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
