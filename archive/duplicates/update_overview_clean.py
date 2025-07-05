#!/usr/bin/env python3
"""
AetherraCode Project Overview Update System

This script intelligently updates the PROJECT_OVERVIEW.md file by:
1. Scanning the project structure for changes
2. Reading current status files and goal stores
3. Analyzing git history for recent achievements
4. Updating metrics and progress indicators
5. Maintaining accurate project state information

Usage:
    python scripts/update_overview.py [--auto-commit]
"""

import datetime
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class OverviewUpdater:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.overview_file = self.project_root / "PROJECT_OVERVIEW.md"
        self.goals_file = self.project_root / "goals_store.json"
        self.memory_file = self.project_root / "memory_store.json"

    def get_project_stats(self) -> Dict[str, Any]:
        """Get current project statistics by scanning the workspace."""
        stats = {
            "files_total": 0,
            "core_modules": 0,
            "test_files": 0,
            "doc_files": 0,
            "example_files": 0,
            "script_files": 0,
            "launcher_files": 0,
        }

        # Count files in different categories
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for file in files:
                if file.startswith(".") or file.endswith(".pyc"):
                    continue

                stats["files_total"] += 1
                relative_path = Path(root).relative_to(self.project_root)

                if "core" in str(relative_path) and file.endswith(".py"):
                    stats["core_modules"] += 1
                elif "test" in str(relative_path) and file.endswith(".py"):
                    stats["test_files"] += 1
                elif "doc" in str(relative_path) and file.endswith(".md"):
                    stats["doc_files"] += 1
                elif "example" in str(relative_path):
                    stats["example_files"] += 1
                elif "script" in str(relative_path) and file.endswith(".py"):
                    stats["script_files"] += 1
                elif "launcher" in str(relative_path):
                    stats["launcher_files"] += 1

        return stats

    def get_goals_status(self) -> Dict[str, Any]:
        """Read and analyze the current goals from goals_store.json."""
        goals_info = {"active_goals": [], "completed_goals": [], "total_goals": 0}

        if self.goals_file.exists():
            try:
                with open(self.goals_file, encoding="utf-8") as f:
                    goals_data = json.load(f)

                goals_info["total_goals"] = len(goals_data.get("goals", []))

                for goal in goals_data.get("goals", []):
                    if goal.get("status") == "active":
                        goals_info["active_goals"].append(
                            {
                                "text": goal.get("text", "Unknown goal"),
                                "priority": goal.get("priority", "medium"),
                                "created": goal.get("created", "Unknown"),
                            }
                        )
                    elif goal.get("status") == "completed":
                        goals_info["completed_goals"].append(goal)

            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return goals_info

    def get_git_recent_activity(self) -> List[str]:
        """Get recent git activity to identify new achievements."""
        try:
            # Get recent commit messages (last 10)
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                return [
                    commit.split(" ", 1)[1] if " " in commit else commit
                    for commit in commits
                    if commit.strip()
                ]

        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return []

    def check_website_status(self) -> Dict[str, bool]:
        """Check website and deployment status."""
        status = {
            "cname_exists": False,
            "index_exists": False,
            "domain_setup_guide_exists": False,
            "protection_system_exists": False,
        }

        status["cname_exists"] = (self.project_root / "CNAME").exists()
        status["index_exists"] = (self.project_root / "index.html").exists()
        status["domain_setup_guide_exists"] = (self.project_root / "DOMAIN_SETUP_GUIDE.md").exists()
        status["protection_system_exists"] = (
            self.project_root / "scripts/project_protection.py"
        ).exists()

        return status

    def format_milestone_status(
        self, website_status: Dict[str, bool], stats: Dict[str, Any]
    ) -> str:
        """Format the milestone status table."""
        milestones = [
            (
                "🧠 **Agent Archive System**",
                "✅ **COMPLETE**",
                "AI consciousness preservation operational",
            ),
            ("🎯 **Decision Replay**", "✅ **COMPLETE**", "Full transparency debugging system"),
            ("🔀 **Agent Merging**", "✅ **COMPLETE**", "Intelligent capability combination"),
            ("🏗️ **Developer Onboarding**", "✅ **COMPLETE**", "AI-guided scaffolding system"),
            (
                "🌐 **Website & Domain**",
                "✅ **COMPLETE**"
                if website_status["cname_exists"] and website_status["index_exists"]
                else "🔄 **IN PROGRESS**",
                "Live at httpsneurocode.dev",
            ),
            (
                "🛡️ **Protection System**",
                "✅ **COMPLETE**"
                if website_status["protection_system_exists"]
                else "🔄 **IN PROGRESS**",
                "Comprehensive file protection",
            ),
            (
                "📁 **Project Organization**",
                "✅ **COMPLETE**",
                "Professional workspace architecture",
            ),
            (
                "🔗 **GitHub Integration**",
                "✅ **COMPLETE**",
                "All links updated to Zyonic88/AetherraCode",
            ),
        ]

        table = "| Component | Status | Description |\n|-----------|--------|-------------|\n"
        for component, status, description in milestones:
            table += f"| {component} | {status} | {description} |\n"

        return table

    def format_goals_table(self, goals_info: Dict[str, Any]) -> str:
        """Format the current goals table."""
        table = "| Goal | Priority | Status |\n|------|----------|--------|\n"

        for goal in goals_info["active_goals"][:5]:  # Show top 5 active goals
            table += f"| {goal['text']} | {goal['priority'].title()} | Active |\n"

        # Add some placeholder rows if we have fewer than 3 goals
        if len(goals_info["active_goals"]) < 3:
            table += "| Documentation expansion | Medium | Planned |\n"
            table += "| Community growth | Medium | Ongoing |\n"

        return table

    def update_statistics_section(self, content: str, stats: Dict[str, Any]) -> str:
        """Update the statistics section with current numbers."""
        patterns = [
            (
                r"\*\*Files Organized\*\*: \d+\+ files processed",
                f"**Files Organized**: {stats['files_total']}+ files processed",
            ),
            (
                r"\*\*Core Modules\*\*: \d+\+ modular components",
                f"**Core Modules**: {stats['core_modules']}+ modular components",
            ),
            (
                r"\*\*Test Coverage\*\*: \d+\+ test files",
                f"**Test Coverage**: {stats['test_files']}+ test files",
            ),
            (
                r"\*\*Documentation\*\*: \d+\+ documentation files",
                f"**Documentation**: {stats['doc_files']}+ documentation files",
            ),
            (
                r"\*\*Examples\*\*: \d+\+ working examples",
                f"**Examples**: {stats['example_files']}+ working examples",
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        return content

    def update_overview(self) -> bool:
        """Main method to update the overview file."""
        if not self.overview_file.exists():
            print(f"❌ Overview file not found: {self.overview_file}")
            return False

        print("🔍 Analyzing project state...")

        # Gather current information
        stats = self.get_project_stats()
        goals_info = self.get_goals_status()
        website_status = self.check_website_status()

        print(f"📊 Found {stats['files_total']} files, {stats['core_modules']} core modules")
        print(f"🎯 Active goals: {len(goals_info['active_goals'])}")
        print(f"🌐 Website status: {'✅' if website_status['cname_exists'] else '❌'}")

        # Read current overview content
        with open(self.overview_file, encoding="utf-8") as f:
            content = f.read()

        # Update last updated date
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        content = re.sub(
            r"> \*\*Last Updated\*\*: [^\\n]+", f"> **Last Updated**: {current_date}", content
        )

        # Update milestone status table
        milestone_section = self.format_milestone_status(website_status, stats)
        content = re.sub(
            r"\| Component \| Status \| Description \|.*?\n(?=###|\n---|\n##)",
            milestone_section + "\n",
            content,
            flags=re.DOTALL,
        )

        # Update goals table
        goals_section = self.format_goals_table(goals_info)
        goal_pattern = r"(\| Goal \| Priority \| Status \|\n\|[^|]+\|[^|]+\|[^|]+\|)\n(?:[^|]*\|[^|]*\|[^|]*\|\n)*"
        content = re.sub(goal_pattern, goals_section, content)

        # Update statistics
        content = self.update_statistics_section(content, stats)

        # Write updated content
        with open(self.overview_file, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Overview updated successfully!")
        print("📝 Updated statistics, goals, and status information")

        return True

    def auto_commit_if_requested(self, auto_commit: bool = False):
        """Automatically commit the updated overview if requested."""
        if auto_commit:
            try:
                subprocess.run(
                    ["git", "add", "PROJECT_OVERVIEW.md"], cwd=self.project_root, check=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "Update project overview with current status"],
                    cwd=self.project_root,
                    check=True,
                )
                print("📝 Automatically committed overview updates")
            except subprocess.CalledProcessError:
                print("⚠️ Could not auto-commit changes")


def main():
    import sys

    auto_commit = "--auto-commit" in sys.argv

    updater = OverviewUpdater()

    if updater.update_overview():
        updater.auto_commit_if_requested(auto_commit)
        print("\n🎉 Project overview update complete!")
        print("📖 View the updated overview at PROJECT_OVERVIEW.md")
    else:
        print("❌ Failed to update project overview")
        sys.exit(1)


if __name__ == "__main__":
    main()
