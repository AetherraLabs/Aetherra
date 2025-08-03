#!/usr/bin/env python3
"""
Aetherra Development Setup Script
=================================

This script helps contributors set up their development environment quickly and easily.
Run this script after cloning the repository to get everything set up.

Usage:
    python setup_dev.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class AetherraSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.env_example = self.project_root / ".env.example"
        self.env_file = self.project_root / ".env"

    def print_banner(self):
        """Print the Aetherra setup banner"""
        banner = """
🌟 ═══════════════════════════════════════════════════════════════ 🌟
   ___       _   _                             ____       _
  / _ \     | | | |                           / ___|  ___| |_ _   _ _ __
 / /_\ \____| |_| |__   ___ _ __ _ __ __ _    \___ \ / _ \ __| | | | '_ \
 |  _  |____|  _  | '_ \ / _ \ '__| '__/ _` |    ___) |  __/ |_| |_| | |_|
 | | | |    | | | | | | |  __/ |  | | | (_| |   |____/ \___|\__|\__,_| .__/
 \_| |_/    |_| |_|_| |_|\___|_|  |_|  \__,_|                       |_|

        🚀 AI Operating System Development Environment Setup 🚀
🌟 ═══════════════════════════════════════════════════════════════ 🌟
"""
        print(banner)

    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")

        if sys.version_info < (3, 8):
            print("[ERROR] Error: Python 3.8 or higher is required!")
            print(f"   Current version: {sys.version}")
            print("   Please upgrade Python and try again.")
            sys.exit(1)

        print(
            f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected"
        )

    def check_git(self):
        """Check if git is available"""
        print("🔍 Checking Git installation...")

        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"[OK] {result.stdout.strip()}")
            else:
                print("[ERROR] Git not found!")
                return False
        except FileNotFoundError:
            print("[ERROR] Git not found! Please install Git and try again.")
            return False

        return True

    def create_virtual_environment(self):
        """Create a virtual environment"""
        print("[TOOL] Creating virtual environment...")

        if self.venv_path.exists():
            print("📁 Virtual environment already exists")
            return True

        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_path)], check=True
            )
            print("[OK] Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to create virtual environment: {e}")
            return False

    def get_pip_command(self):
        """Get the pip command for the current platform"""
        if sys.platform == "win32":
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")

    def install_dependencies(self):
        """Install project dependencies"""
        print("[DISC] Installing dependencies...")

        if not self.requirements_file.exists():
            print("[ERROR] requirements.txt not found!")
            return False

        pip_cmd = self.get_pip_command()

        try:
            # Upgrade pip first
            print("🔄 Upgrading pip...")
            subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)

            # Install requirements
            print("📥 Installing project dependencies...")
            subprocess.run(
                [pip_cmd, "install", "-r", str(self.requirements_file)], check=True
            )

            print("[OK] Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            return False

    def setup_environment_file(self):
        """Set up the .env file from .env.example"""
        print("[TOOL] Setting up environment file...")

        if self.env_file.exists():
            print("📁 .env file already exists")
            return True

        if not self.env_example.exists():
            print("[ERROR] .env.example not found!")
            return False

        try:
            shutil.copy2(self.env_example, self.env_file)
            print("[OK] .env file created from .env.example")
            print("[WARN]  Please edit .env and add your API keys!")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create .env file: {e}")
            return False

    def test_installation(self):
        """Test the installation by importing key modules"""
        print("🧪 Testing installation...")

        python_cmd = sys.executable
        if sys.platform == "win32":
            python_cmd = str(self.venv_path / "Scripts" / "python.exe")
        else:
            python_cmd = str(self.venv_path / "bin" / "python")

        test_script = """
import sys
try:
    import flask
    import flask_socketio
    import openai
    print("[OK] Core dependencies imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [python_cmd, "-c", test_script], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(result.stdout.strip())
                return True
            else:
                print(result.stdout.strip())
                print(result.stderr.strip())
                return False
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            return False

    def print_next_steps(self):
        """Print next steps for the user"""
        activation_cmd = ""
        if sys.platform == "win32":
            activation_cmd = ".venv\\Scripts\\activate"
        else:
            activation_cmd = "source .venv/bin/activate"

        next_steps = f"""
🎉 ═══════════════════════════════════════════════════════════════ 🎉
                      SETUP COMPLETE!
🎉 ═══════════════════════════════════════════════════════════════ 🎉

📋 Next Steps:

1. 🔑 Add your API keys to the .env file:
   - Edit .env and add your OpenAI, Anthropic, and Google API keys
   - See .env.example for all available configuration options

2. 🚀 Activate the virtual environment:
   {activation_cmd}

3. 🌐 Start the web interface:
   python Aetherra/gui/web_interface_server.py --debug

4. 🧪 Test the AI OS launcher:
   python aetherra_os_launcher.py --mode test

5. 📖 Read the documentation:
   - README.md for project overview
   - CONTRIBUTING.md for contribution guidelines

6. 🧩 Install recommended VS Code extensions:
   - GitLens (eamodio.gitlens) - Essential for tracking code changes
   - Python (ms-python.python) - Python language support
   - Pylance (ms-python.vscode-pylance) - Fast Python IntelliSense

🔗 Useful URLs:
   - Web Interface: http://127.0.0.1:8686
   - GitHub Repo: https://github.com/AetherraLabs/Aetherra
   - Documentation: ./docs/

🤝 Need Help?
   - Check GitHub Issues: https://github.com/AetherraLabs/Aetherra/issues
   - Read CONTRIBUTING.md for detailed setup instructions
   - Join our community discussions

Happy coding! 🚀✨
"""
        print(next_steps)

    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()

        print("🚀 Starting Aetherra development environment setup...\n")

        # Check prerequisites
        self.check_python_version()
        if not self.check_git():
            return False

        # Setup steps
        if not self.create_virtual_environment():
            return False

        if not self.install_dependencies():
            return False

        if not self.setup_environment_file():
            return False

        if not self.test_installation():
            print("[WARN]  Installation test failed, but setup may still work")

        self.print_next_steps()
        return True


def main():
    """Main entry point"""
    setup = AetherraSetup()

    try:
        success = setup.run_setup()
        if success:
            print("\n[OK] Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n[ERROR] Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
