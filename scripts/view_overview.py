#!/usr/bin/env python3
"""
Quick Project Overview Viewer

A simple script to display the current project overview in the terminal
with key highlights and status information.

Usage:
    python scripts/view_overview.py [--full] [--stats-only]
"""

import re
from pathlib import Path


def extract_section(content: str, section_name: str) -> str:
    """Extract a specific section from the overview content."""
    pattern = rf"## {section_name}.*?(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(0) if match else ""


def format_for_terminal(text: str, max_width: int = 80) -> str:
    """Format text for better terminal display."""
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        if len(line) <= max_width:
            formatted_lines.append(line)
        else:
            # Simple word wrapping
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line + word) <= max_width:
                    current_line += word + " "
                else:
                    if current_line:
                        formatted_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                formatted_lines.append(current_line.strip())

    return "\n".join(formatted_lines)


def show_quick_overview():
    """Display a condensed overview with key information."""
    project_root = Path(".").resolve()
    overview_file = project_root / "PROJECT_OVERVIEW.md"

    if not overview_file.exists():
        print("❌ PROJECT_OVERVIEW.md not found!")
        return

    with open(overview_file, encoding="utf-8") as f:
        content = f.read()

    print("🧬 " + "=" * 70)
    print("🧬 NEUROCODE PROJECT OVERVIEW - QUICK VIEW")
    print("🧬 " + "=" * 70)

    # Extract header information
    header_match = re.search(r"> \*\*Last Updated\*\*: ([^\n]+)", content)
    status_match = re.search(r"> \*\*Status\*\*: ([^\n]+)", content)
    version_match = re.search(r"> \*\*Version\*\*: ([^\n]+)", content)

    if header_match:
        print(f"📅 Last Updated: {header_match.group(1)}")
    if status_match:
        print(f"🚀 Status: {status_match.group(1)}")
    if version_match:
        print(f"📦 Version: {version_match.group(1)}")

    print()

    # Extract key achievements
    achievements_section = extract_section(content, "🚀 \\*\\*WHAT IS NEUROCODE\\?\\*\\*")
    if achievements_section:
        print("🏆 BREAKTHROUGH ACHIEVEMENTS:")
        # Extract bullet points
        bullet_pattern = r"- \*\*([^:]+)\*\*: ([^\n]+)"
        matches = re.findall(bullet_pattern, achievements_section)
        for title, description in matches[:5]:  # Show top 5
            print(f"   ✅ {title}: {description}")
        print()

    # Extract milestone status
    milestone_section = extract_section(content, "📊 \\*\\*PROJECT STATUS DASHBOARD\\*\\*")
    if milestone_section:
        print("📊 COMPLETED MILESTONES:")
        # Extract table rows with COMPLETE status
        table_pattern = r"\| ([^|]+) \| ✅ \*\*COMPLETE\*\* \| ([^|]+) \|"
        matches = re.findall(table_pattern, milestone_section)
        for component, description in matches:
            component_clean = re.sub(
                r"\*\*|\🧠|\🎯|\🔀|\🏗️|\🌐|\🛡️|\📁|\🔗|\s+", " ", component
            ).strip()
            print(f"   ✅ {component_clean}: {description.strip()}")
        print()

    # Extract current goals
    goals_pattern = r"\| ([^|]+) \| ([^|]+) \| Active \|"
    goals_matches = re.findall(goals_pattern, content)
    if goals_matches:
        print("🎯 CURRENT ACTIVE GOALS:")
        for goal, priority in goals_matches:
            print(f"   🎯 {goal.strip()} ({priority.strip()} priority)")
        print()

    # Extract statistics
    stats_section = extract_section(content, "📈 \\*\\*PERFORMANCE METRICS\\*\\*")
    if stats_section:
        print("📈 KEY STATISTICS:")
        # Extract key numbers
        file_match = re.search(r"\*\*Files Organized\*\*: (\d+\+[^\\n]+)", stats_section)
        modules_match = re.search(r"\*\*Core Modules\*\*: (\d+\+[^\\n]+)", stats_section)
        tests_match = re.search(r"\*\*Test Coverage\*\*: (\d+\+[^\\n]+)", stats_section)

        if file_match:
            print(f"   📁 Files: {file_match.group(1)}")
        if modules_match:
            print(f"   🧠 Core Modules: {modules_match.group(1)}")
        if tests_match:
            print(f"   🧪 Tests: {tests_match.group(1)}")
        print()

    # Show website status
    print("🌐 LIVE DEPLOYMENTS:")
    print("   🌍 Website: https://httpsneurocode.dev")
    print("   📂 Repository: https://github.com/Zyonic88/NeuroCode")
    print()

    print("🧬 " + "=" * 70)
    print("💡 Run 'python scripts/view_overview.py --full' for complete overview")
    print("🔄 Run 'python scripts/update_overview.py' to refresh data")
    print("🧬 " + "=" * 70)


def show_full_overview():
    """Display the complete overview."""
    project_root = Path(".").resolve()
    overview_file = project_root / "PROJECT_OVERVIEW.md"

    if not overview_file.exists():
        print("❌ PROJECT_OVERVIEW.md not found!")
        return

    with open(overview_file, encoding="utf-8") as f:
        content = f.read()

    # Clean up markdown for terminal display
    content = re.sub(r"#+ ", "", content)  # Remove markdown headers
    content = re.sub(r"\*\*([^*]+)\*\*", r"\1", content)  # Remove bold
    content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)  # Remove links
    content = re.sub(
        r"```[^`]*```", "[CODE BLOCK]", content, flags=re.DOTALL
    )  # Replace code blocks

    print(format_for_terminal(content))


def show_stats_only():
    """Show only the statistics section."""
    project_root = Path(".").resolve()
    overview_file = project_root / "PROJECT_OVERVIEW.md"

    if not overview_file.exists():
        print("❌ PROJECT_OVERVIEW.md not found!")
        return

    with open(overview_file, encoding="utf-8") as f:
        content = f.read()

    stats_section = extract_section(content, "📈 \\*\\*PERFORMANCE METRICS\\*\\*")
    if stats_section:
        print("📈 " + "=" * 50)
        print("📈 NEUROCODE PERFORMANCE METRICS")
        print("📈 " + "=" * 50)
        print(format_for_terminal(stats_section))
    else:
        print("❌ Statistics section not found in overview!")


def main():
    import sys

    if "--full" in sys.argv:
        show_full_overview()
    elif "--stats-only" in sys.argv:
        show_stats_only()
    else:
        show_quick_overview()


if __name__ == "__main__":
    main()
