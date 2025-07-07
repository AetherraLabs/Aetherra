# src/Aetherra/plugins/git_plugin.py - Git Integration Plugin
import os
import subprocess
from typing import Any, Dict

from core.plugin_manager import register_plugin


@register_plugin(
    name="git_status",
    description="Check the current Git repository status",
    capabilities=["git", "version_control", "status"],
    version="1.0.0",
    author="Aetherra Team",
    category="development",
    dependencies=["subprocess"],
    intent_purpose="git repository management and version control",
    intent_triggers=["git", "status", "commit", "version", "repository", "changes"],
    intent_scenarios=[
        "checking repository status",
        "viewing uncommitted changes",
        "managing version control",
        "development workflow automation"
    ],
    ai_description="Provides Git repository status information including tracked files,
        untracked files,
        and pending changes. Helps manage version control workflow.",

    example_usage="plugin: git_status",
    confidence_boost=1.2,
)
def git_status() -> Dict[str, Any]:
    """Get comprehensive Git repository status"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.returncode != 0:
            return {"error": "Not in a Git repository"}

        # Get status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        # Get branch info
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        # Parse status
        changes = []
        if status_result.stdout:
            for line in status_result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    filename = line[3:]
                    changes.append({
                        "file": filename,
                        "status": status_code.strip(),
                        "staged": status_code[0] != ' ' and status_code[0] != '?',
                        "modified": status_code[1] != ' '
                    })

        return {
            "success": True,
            "branch": branch_result.stdout.strip(),
            "changes": changes,
            "clean": len(changes) == 0
        }

    except FileNotFoundError:
        return {"error": "Git not found. Please install Git."}
    except Exception as e:
        return {"error": f"Git operation failed: {str(e)}"}


@register_plugin(
    name="git_commit",
    description="Create a Git commit with the provided message",
    capabilities=["git", "commit", "version_control"],
    version="1.0.0",
    author="Aetherra Team",
    category="development",
    dependencies=["subprocess"],
    intent_purpose="git commit creation and version control",
    intent_triggers=["commit", "save", "checkpoint", "version"],
    intent_scenarios=[
        "saving code changes",
        "creating version checkpoints",
        "committing development progress",
        "maintaining project history"
    ],
    ai_description="Creates Git commits with descriptive messages. Automatically stages changes and commits them to the repository.",

    example_usage="plugin: git_commit 'Add new feature implementation'",
    confidence_boost=1.1,
)
def git_commit(message: str, add_all: bool = True) -> Dict[str, Any]:
    """Create a Git commit with the provided message"""
    try:
        if not message.strip():
            return {"error": "Commit message cannot be empty"}

        # Add all files if requested
        if add_all:
            add_result = subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )

            if add_result.returncode != 0:
                return {"error": f"Failed to add files: {add_result.stderr}"}

        # Create commit
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if commit_result.returncode != 0:
            return {"error": f"Commit failed: {commit_result.stderr}"}

        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        return {
            "success": True,
            "message": message,
            "hash": hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown",
            "output": commit_result.stdout
        }

    except FileNotFoundError:
        return {"error": "Git not found. Please install Git."}
    except Exception as e:
        return {"error": f"Git commit failed: {str(e)}"}


@register_plugin(
    name="git_log",
    description="View Git commit history",
    capabilities=["git", "history", "log"],
    version="1.0.0",
    author="Aetherra Team",
    category="development",
    dependencies=["subprocess"],
    intent_purpose="git history and commit log viewing",
    intent_triggers=["history", "log", "commits", "previous"],
    intent_scenarios=[
        "viewing project history",
        "checking recent commits",
        "reviewing development progress",
        "investigating code changes"
    ],
    ai_description="Displays Git commit history with commit messages,
        authors,
        and timestamps. Shows the evolution of the project.",

    example_usage="plugin: git_log 10",
    confidence_boost=1.0,
)
def git_log(limit: int = 10) -> Dict[str, Any]:
    """View Git commit history"""
    try:
        # Get commit history
        log_result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%an|%ad|%s", "--date=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if log_result.returncode != 0:
            return {"error": f"Failed to get log: {log_result.stderr}"}

        commits = []
        if log_result.stdout:
            for line in log_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0][:8],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })

        return {
            "success": True,
            "commits": commits,
            "total_shown": len(commits)
        }

    except FileNotFoundError:
        return {"error": "Git not found. Please install Git."}
    except Exception as e:
        return {"error": f"Git log failed: {str(e)}"}
