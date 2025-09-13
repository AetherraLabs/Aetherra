#!/usr/bin/env python3
"""
Aetherra Development Environment Setup Script

This script sets up a complete development environment for Aetherra,
including dependencies, pre-commit hooks, and validation.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command with proper error handling."""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        check=check,
        capture_output=capture_output,
        text=True
    )
    if capture_output:
        return result.stdout.strip()
    return result


def check_python_version():
    """Ensure Python version is 3.11+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")


def setup_virtual_environment():
    """Set up virtual environment if not already in one."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return
    
    print("📦 Setting up virtual environment...")
    venv_path = Path(".venv")
    if not venv_path.exists():
        run_command("python -m venv .venv")
        print("✅ Virtual environment created at .venv")
        print("⚠️  Please activate the virtual environment and run this script again:")
        if os.name == 'nt':
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")
        sys.exit(0)


def install_dependencies():
    """Install all required dependencies."""
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    run_command("python -m pip install --upgrade pip")
    
    # Install main requirements
    if Path("requirements.txt").exists():
        run_command("pip install -r requirements.txt")
        print("✅ Main dependencies installed")
    
    # Install development dependencies
    if Path("requirements/dev.txt").exists():
        run_command("pip install -r requirements/dev.txt")
        print("✅ Development dependencies installed")
    
    # Install pre-commit
    run_command("pip install pre-commit")
    print("✅ Pre-commit installed")


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")
    
    if Path(".pre-commit-config.yaml").exists():
        run_command("pre-commit install --install-hooks")
        print("✅ Pre-commit hooks installed")
        
        # Run pre-commit on all files to ensure everything works
        try:
            run_command("pre-commit run --all-files", check=False)
            print("✅ Pre-commit validation completed")
        except subprocess.CalledProcessError:
            print("⚠️  Pre-commit found issues that were auto-fixed")
    else:
        print("⚠️  No .pre-commit-config.yaml found")


def validate_environment():
    """Validate that the environment is properly set up."""
    print("🔍 Validating environment...")
    
    # Check if pytest can run
    try:
        result = run_command("python -m pytest --version", capture_output=True)
        print(f"✅ Pytest available: {result}")
    except subprocess.CalledProcessError:
        print("❌ Pytest not available")
        return False
    
    # Check if key modules can be imported
    try:
        import flask
        import pytest
        import black
        import ruff
        print("✅ Key development packages available")
    except ImportError as e:
        print(f"❌ Missing key package: {e}")
        return False
    
    return True


def run_basic_tests():
    """Run a quick test to ensure everything is working."""
    print("🧪 Running basic tests...")
    
    try:
        # Run a quick subset of tests
        run_command("python -m pytest tests/capabilities/ -v --tb=short -x", check=False)
        print("✅ Basic tests completed")
    except subprocess.CalledProcessError:
        print("⚠️  Some tests failed - this may be expected in development")


def main():
    """Main setup function."""
    print("🚀 Aetherra Development Environment Setup")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Setup steps
    check_python_version()
    setup_virtual_environment()
    install_dependencies()
    setup_pre_commit()
    
    if validate_environment():
        print("\n🎉 Development environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Run tests: python -m pytest tests/capabilities/")
        print("2. Start development: python main.py")
        print("3. Check code quality: pre-commit run --all-files")
        
        # Optionally run basic tests
        if "--test" in sys.argv:
            run_basic_tests()
    else:
        print("\n❌ Environment setup completed with issues")
        print("Please check the error messages above and resolve them.")
        sys.exit(1)


if __name__ == "__main__":
    main()