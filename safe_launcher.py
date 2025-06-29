#!/usr/bin/env python3
"""
NeuroCode Safe Launcher
Windows-compatible launcher that avoids Unicode encoding issues
"""

import os
import subprocess
import sys
from pathlib import Path


def safe_print(message):
    """Print safely without Unicode errors"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Strip all non-ASCII characters if needed
        ascii_message = "".join(char for char in message if ord(char) < 128)
        print(ascii_message)


def setup_unicode_environment():
    """Configure Windows for better Unicode support"""
    if sys.platform.startswith("win"):
        try:
            # Set console to UTF-8
            os.system("chcp 65001 > nul 2>&1")
            # Set environment variables for Python
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["PYTHONLEGACYWINDOWSSTDIO"] = "0"
        except:
            pass  # Continue if we can't set encoding


def main():
    """Main launcher function"""
    setup_unicode_environment()

    safe_print("=" * 60)
    safe_print("NEUROCODE DEPENDENCY RESOLVER")
    safe_print("=" * 60)

    safe_print("[INFO] Starting dependency resolution...")
    safe_print("[INFO] This will fix protobuf/gRPC conflicts")

    # Get the workspace path
    workspace_path = Path(__file__).parent

    # Try to run the dependency resolver
    try:
        safe_print("[EXEC] Running dependency resolver...")

        # Use subprocess to avoid Unicode issues in the main process
        result = subprocess.run(
            [sys.executable, str(workspace_path / "resolve_dependencies_clean.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        # Print output safely
        if result.stdout:
            # Replace emoji with safe text
            safe_output = (
                result.stdout.replace("🔧", "[CONFIG]")
                .replace("✅", "[OK]")
                .replace("❌", "[ERROR]")
                .replace("⚠️", "[WARNING]")
                .replace("🧹", "[CLEANUP]")
                .replace("📦", "[INSTALL]")
                .replace("🤖", "[AI]")
                .replace("🔍", "[VERIFY]")
                .replace("🎉", "[SUCCESS]")
                .replace("📋", "[REPORT]")
                .replace("🚀", "[LAUNCH]")
                .replace("🧬", "[NEUROCODE]")
            )
            safe_print(safe_output)

        if result.stderr:
            safe_print("[ERROR] " + result.stderr)

        if result.returncode == 0:
            safe_print("[SUCCESS] Dependency resolution completed!")
            safe_print("[INFO] NeuroCode is ready for AI-native programming")
        else:
            safe_print("[ERROR] Dependency resolution failed")
            safe_print("[INFO] Check error messages above")

    except Exception as e:
        safe_print(f"[ERROR] Failed to run dependency resolver: {e}")
        safe_print("[INFO] Try running manually: python resolve_dependencies_clean.py")

    safe_print("=" * 60)


if __name__ == "__main__":
    main()
