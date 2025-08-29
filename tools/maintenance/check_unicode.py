#!/usr/bin/env python3
"""
Check for Unicode characters in the service registry file
"""

def check_unicode_in_file(filepath):
    """Check for Unicode characters in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find any non-ASCII characters
    for i, char in enumerate(content):
        if ord(char) > 127:
            line_num = content[:i].count('\n') + 1
            char_pos = i - content[:i].rfind('\n') - 1
            print(f"Line {line_num}, Position {char_pos}: Unicode character '{char}' (U+{ord(char):04X})")

    # Check for specific problematic characters
    problematic = ['✅', '❌', '⚠️', '🌐', '🚀', '🛑', '📝', '🗑️', '🔍', '📋', '📜', '📊', '💓', '📤', '📢', '🔔', '🔕', '🔗']
    for char in problematic:
        if char in content:
            print(f"Found problematic Unicode: {char} (U+{ord(char):04X})")

    print("Unicode check complete")

if __name__ == "__main__":
    check_unicode_in_file("aetherra_service_registry.py")
