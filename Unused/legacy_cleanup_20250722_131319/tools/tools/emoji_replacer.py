#!/usr/bin/env python
"""
Emoji Replacement Script for aetherra UI

This script replaces all emojis in the specified file with text-based alternatives.
It maintains a mapping of common emojis to their text equivalents.
"""

import re
import sys
from pathlib import Path

# Define emoji to text mappings
EMOJI_REPLACEMENTS = {
    # Checkmarks and indicators
    "✓": "[CHECK]",
    "✅": "[CHECK]",
    "❌": "[X]",
    # Tutorial icons
    "🎯": "[TARGET]",
    "🧠": "[BRAIN]",
    "🔌": "[PLUGIN]",
    "🚀": "[ROCKET]",
    "🛠️": "[TOOLS]",
    "🤖": "[ROBOT]",
    "▶️": "[RUN]",
    # Interface elements
    "📖": "[BOOK]",
    "🔍": "[SEARCH]",
    "💾": "[SAVE]",
    "✏️": "[EDIT]",
    "🧪": "[TEST]",
    # Examples
    "📊": "[CHART]",
    "🖥️": "[COMPUTER]",
    "🔧": "[WRENCH]",
    "📈": "[GRAPH]",
    "⚡": "[LIGHTNING]",
    "📁": "[FOLDER]",
    "ℹ️": "[INFO]",
    "🧬": "[DNA]",
    "🌟": "[STAR]",
    "🔄": "[REFRESH]",
    "💡": "[IDEA]",
    # Close button
    "×": "X",
}


def replace_emojis_in_file(file_path):
    """Replace all emojis in the given file with text equivalents."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} not found.")
        return False

    try:
        # Read the file content
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count original emojis
        original_emoji_count = sum(content.count(emoji) for emoji in EMOJI_REPLACEMENTS)

        # Replace each emoji with its text equivalent
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)

        # Write the updated content back
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # Handle any other non-ASCII characters (potential emojis not in our map)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all remaining non-ASCII characters
        other_emojis = set(re.findall(r"[^\x00-\x7F]", content))
        if other_emojis:
            print(
                f"Warning: Found {len(other_emojis)} unmapped emojis/special characters."
            )
            for emoji in other_emojis:
                content = content.replace(emoji, "[SYMBOL]")

            # Write again with these replacements
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        print(f"Replaced {original_emoji_count} mapped emojis in {file_path}")
        return True

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python emoji_replacer.py <file_path>")
        return

    file_path = sys.argv[1]
    success = replace_emojis_in_file(file_path)

    if success:
        print("Emoji replacement completed successfully.")
    else:
        print("Emoji replacement failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
