#!/usr/bin/env python3
"""
aetherra Dependency Resolver
Intelligently resolves and installs dependencies with conflict prevention
"""

import subprocess
import sys
from pathlib import Path


class DependencyResolver:
    def __init__(self):
        self.workspace_path = Path(__file__).parent
        self.requirements_files = [
            "requirements_fixed.txt",  # New conflict-free requirements
            "requirements.txt",  # Original requirements
            "requirements_enhanced.txt",  # Enhancement requirements
        ]

    def check_python_version(self):
        """Ensure Python version compatibility"""
        major, minor = sys.version_info[:2]
        if major < 3 or (major == 3 and minor < 8):
            raise RuntimeError(f"aetherra requires Python 3.8+, found {major}.{minor}")
        print(f"✅ Python {major}.{minor} detected - Compatible")

    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        print("[TOOL] Upgrading pip to latest version...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True,
            )
            print("✅ pip upgraded successfully")
        except subprocess.CalledProcessError as e:
            print(f"[WARN]  pip upgrade failed: {e}")

    def uninstall_conflicting_packages(self):
        """Remove packages known to cause conflicts"""
        conflicting_packages = [
            "grpcio-status",  # Often has version mismatches
            "grpcio-health-checking",
            "opentelemetry-exporter-otlp-proto-grpc",
        ]

        print("🧹 Removing potentially conflicting packages...")
        for package in conflicting_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", package],
                    capture_output=True,
                    text=True,
                )
                print(f"   Removed {package}")
            except:
                pass  # Package might not be installed

    def install_requirements(self, requirements_file):
        """Install requirements from a specific file"""
        if not (self.workspace_path / requirements_file).exists():
            print(f"[WARN]  {requirements_file} not found, skipping...")
            return False

        print(f"[DISC] Installing from {requirements_file}...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(self.workspace_path / requirements_file),
                    "--upgrade",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            print(f"✅ Successfully installed from {requirements_file}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install from {requirements_file}")
            print(f"Error: {e.stderr}")
            return False

    def install_optional_ai_engines(self):
        """Install optional AI engines with error handling"""
        optional_packages = {
            "ollama": "Local AI with Ollama",
            "llama-cpp-python": "LLaMA C++ bindings for faster inference",
            "ctransformers": "C Transformers for efficient local models",
        }

        print("🤖 Installing optional AI engines...")
        for package, description in optional_packages.items():
            try:
                print(f"   Installing {package} ({description})...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"   ✅ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"   [WARN]  {package} installation failed (optional - continuing...)")

    def verify_installation(self):
        """Verify that key packages are installed correctly"""
        critical_packages = [
            "openai",
            "PySide6",
            "numpy",
            "transformers",
            "sentence_transformers",
            "chromadb",
            "protobuf",
            "grpcio",
        ]

        print("🔍 Verifying critical package installation...")
        failed_packages = []

        for package in critical_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   [ERROR] {package} - FAILED")
                failed_packages.append(package)

        if failed_packages:
            print(f"\n[WARN]  Some packages failed to install: {', '.join(failed_packages)}")
            print("Run this script again or install manually with:")
            for pkg in failed_packages:
                print(f"   pip install {pkg}")
            return False
        else:
            print("\n🎉 All critical packages verified successfully!")
            return True

    def create_environment_report(self):
        """Create a report of the installed environment"""
        print("📋 Creating environment report...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            with open(self.workspace_path / "environment_report.txt", "w") as f:
                f.write("aetherra Environment Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Python Version: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                f.write("\nInstalled Packages:\n")
                f.write(result.stdout)

            print("✅ Environment report saved to environment_report.txt")
        except Exception as e:
            print(f"[WARN]  Could not create environment report: {e}")

    def run_resolution(self):
        """Main dependency resolution workflow"""
        print("🚀 aetherra Dependency Resolver")
        print("=" * 50)

        try:
            # Step 1: Check Python version
            self.check_python_version()

            # Step 2: Upgrade pip
            self.upgrade_pip()

            # Step 3: Remove conflicting packages
            self.uninstall_conflicting_packages()

            # Step 4: Install from fixed requirements first
            success = False
            for req_file in self.requirements_files:
                if self.install_requirements(req_file):
                    success = True
                    break

            if not success:
                raise RuntimeError("Failed to install any requirements file")

            # Step 5: Install optional AI engines
            self.install_optional_ai_engines()

            # Step 6: Verify installation
            if self.verify_installation():
                print("\n🎉 aetherra dependency resolution completed successfully!")
                print("🧬 Ready to revolutionize programming with AI!")
            else:
                print("\n[WARN]  Some issues detected. Please review and retry.")

            # Step 7: Create environment report
            self.create_environment_report()

        except Exception as e:
            print(f"\n[ERROR] Dependency resolution failed: {e}")
            print("Please check the error messages above and try again.")
            return False

        return True


if __name__ == "__main__":
    resolver = DependencyResolver()
    success = resolver.run_resolution()
    sys.exit(0 if success else 1)
