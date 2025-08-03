#!/usr/bin/env python3
"""
[TOOL] VS Code Extensions Auto-Installer for aetherra/Lyrixa
Automatically installs essential VS Code extensions for optimal development
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"[TOOL] {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} - Failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] {description} - VS Code CLI not found in PATH")
        return False


def check_vscode_installed():
    """Check if VS Code and CLI are available"""
    try:
        result = subprocess.run(["code", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ VS Code detected: {result.stdout.split()[0]}")
            return True
    except FileNotFoundError:
        pass

    print("[ERROR] VS Code CLI not found. Please:")
    print("1. Install VS Code from https://code.visualstudio.com/")
    print("2. Enable 'Add to PATH' during installation, or")
    print("3. Manually add VS Code to your PATH")
    return False


def install_extensions():
    """Install essential VS Code extensions"""

    # Essential extensions for aetherra development
    extensions = {
        # Core Python Development
        "ms-python.python": "Python language support",
        "ms-python.vscode-pylance": "Advanced IntelliSense and type checking",
        "ms-python.black-formatter": "Code formatting with Black",
        "ms-python.debugpy": "Python debugging",
        # AI & Copilot
        "github.copilot": "AI pair programmer",
        "github.copilot-chat": "AI chat integration",
        # Git & Version Control
        "eamodio.gitlens": "Enhanced Git integration",
        # Jupyter Notebooks
        "ms-toolsai.jupyter": "Jupyter notebook support",
        "ms-toolsai.jupyter-keymap": "Jupyter keyboard shortcuts",
        # Code Quality & Linting
        "charliermarsh.ruff": "Fast Python linting and formatting",
        # Documentation & Markdown
        "yzhang.markdown-all-in-one": "Enhanced Markdown support",
        "bierner.docs-view": "Documentation viewer",
        # UI & Theme
        "dracula-theme.theme-dracula": "Beautiful dark theme",
        "vscode-icons-team.vscode-icons": "File and folder icons",
        # Productivity Tools
        "gruntfuggly.todo-tree": "TODO comment tracking",
        "continue.continue": "Local AI coding assistant",
        # Additional Helpful Extensions
        "ms-vscode.powershell": "PowerShell support (Windows)",
        "redhat.vscode-yaml": "YAML language support",
        "ms-vscode.vscode-json": "Enhanced JSON support",
    }

    print(f"\\n🚀 Installing {len(extensions)} essential VS Code extensions...")
    print("=" * 60)

    success_count = 0
    failed_extensions = []

    for ext_id, description in extensions.items():
        if run_command(
            f"code --install-extension {ext_id}", f"Installing {description}"
        ):
            success_count += 1
        else:
            failed_extensions.append((ext_id, description))

    print("\\n" + "=" * 60)
    print(f"📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(extensions)} extensions")

    if failed_extensions:
        print(f"[ERROR] Failed installations: {len(failed_extensions)}")
        print("\\n[TOOL] To manually install failed extensions:")
        for ext_id, description in failed_extensions:
            print(f"   code --install-extension {ext_id}")

    return success_count, failed_extensions


def setup_workspace_settings():
    """Apply optimal VS Code settings for aetherra development"""
    print("\\n⚙️  Applying optimal workspace settings...")

    # Workspace settings are already created in .vscode/settings.json
    settings_file = Path(".vscode/settings.json")
    if settings_file.exists():
        print("✅ Workspace settings already configured")
        return True
    else:
        print("[WARN]  Workspace settings file not found")
        return False


def recommend_additional_setup():
    """Provide additional setup recommendations"""
    print("\\n🎯 Additional Setup Recommendations:")
    print("=" * 50)

    print("1. 🔑 GitHub Copilot Setup:")
    print("   - Sign in to GitHub in VS Code")
    print("   - Activate your Copilot subscription")
    print("   - Run: Ctrl+Shift+P → 'GitHub Copilot: Sign In'")

    print("\\n2. 🐍 Python Interpreter:")
    print("   - Set Python interpreter: Ctrl+Shift+P → 'Python: Select Interpreter'")
    print("   - Choose your project's Python environment")

    print("\\n3. 🎨 Theme & Icons:")
    print("   - Theme: Ctrl+Shift+P → 'Preferences: Color Theme' → Select 'Dracula'")
    print(
        "   - Icons: Ctrl+Shift+P → 'Preferences: File Icon Theme' → Select 'VSCode Icons'"
    )

    print("\\n4. [TOOL] Terminal Setup:")
    print(
        "   - Set PowerShell as default: Ctrl+Shift+P → 'Terminal: Select Default Profile'"
    )

    print("\\n5. ✅ Verification:")
    print("   - Open a Python file to test IntelliSense")
    print("   - Try Copilot suggestions with Ctrl+Enter")
    print("   - Test formatting with Shift+Alt+F")


def main():
    """Main setup function"""
    print("🧬 aetherra/LyrixaVS Code Extension Setup")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("ui/aetherplex_gui.py").exists():
        print("[ERROR] Please run this script from the aetherra project root directory")
        sys.exit(1)

    # Check VS Code installation
    if not check_vscode_installed():
        sys.exit(1)

    # Install extensions
    success_count, failed_extensions = install_extensions()

    # Setup workspace settings
    setup_workspace_settings()

    # Provide additional recommendations
    recommend_additional_setup()

    print("\\n🎉 VS Code setup complete!")

    if success_count > 0:
        print(f"✨ {success_count} extensions installed successfully")
        print("🚀 VS Code is now optimized for aetherra development!")
        print("\\n📂 To get started:")
        print("   1. Close and reopen VS Code")
        print("   2. Open this project folder")
        print("   3. Start coding with enhanced AI assistance!")

    if failed_extensions:
        print(f"\\n[WARN]  Note: {len(failed_extensions)} extensions failed to install")
        print("You can install them manually later from the Extensions marketplace")


if __name__ == "__main__":
    main()
