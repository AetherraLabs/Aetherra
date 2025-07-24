#!/usr/bin/env python3
"""
🚀 aetherra/LyrixaQuick Setup Script
Automatically installs essential packages for optimal performance
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def main():
    """Main setup function"""
    print("🧬 aetherra/LyrixaOptimization Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check if we're in the right directory
    if not Path("ui/aetherplex_gui.py").exists():
        print("❌ Please run this script from the aetherra project root directory")
        sys.exit(1)

    print("🎯 Installing essential packages for peak performance...")

    # Phase 1: Essential packages
    essential_packages = [
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "psutil>=5.9.0",
        "loguru>=0.7.0",
        "rich>=13.0.0",
        "qdarkstyle>=3.2.0",
        "pygments>=2.15.0",
    ]

    print("\\n📋 Phase 1: Installing essential packages...")
    for package in essential_packages:
        run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}")

    # Phase 2: AI/ML packages (optional, might be large downloads)
    print("\\n🤖 Phase 2: Installing AI/ML packages (this may take a while)...")
    ai_packages = [
        "transformers>=4.30.0",
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
    ]

    for package in ai_packages:
        choice = input(
            f"Install {package.split('>=')[0]}? This may be a large download. (y/N): "
        ).lower()
        if choice in ["y", "yes"]:
            run_command(
                f"pip install {package}", f"Installing {package.split('>=')[0]}"
            )
        else:
            print(f"⏭️  Skipping {package.split('>=')[0]}")

    # Phase 3: Advanced packages
    print("\\n🚀 Phase 3: Installing advanced packages...")
    advanced_packages = [
        "networkx>=3.1.0",
        "textblob>=0.17.0",
        "memory-profiler>=0.61.0",
    ]

    for package in advanced_packages:
        run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}")

    # Verify installation
    print("\\n🔍 Verifying installation...")

    test_imports = [
        ("numpy", "import numpy; print(f'NumPy {numpy.__version__}')"),
        (
            "matplotlib",
            "import matplotlib; print(f'Matplotlib {matplotlib.__version__}')",
        ),
        (
            "rich",
            "from rich.console import Console; Console().print('Rich working!', style='bold green')",
        ),
        ("loguru", "from loguru import logger; print('Loguru working!')"),
        ("psutil", "import psutil; print(f'PSUtil {psutil.__version__}')"),
    ]

    for name, test_code in test_imports:
        try:
            subprocess.run(
                [sys.executable, "-c", test_code], check=True, capture_output=True
            )
            print(f"✅ {name} working correctly")
        except subprocess.CalledProcessError:
            print(f"⚠️  {name} installation may have issues")

    print("\\n🎉 Setup complete!")
    print("\\n📚 Next steps:")
    print("1. Install VS Code extensions (see COMPLETE_OPTIMIZATION_GUIDE.md)")
    print("2. Run: python check_qt.py (to verify GUI)")
    print("3. Run: python ui/aetherplex_gui.py (to launch GUI)")
    print("4. Check COMPLETE_OPTIMIZATION_GUIDE.md for advanced features")

    # Test GUI import
    print("\\n🎨 Testing GUI import...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-c",
                "from ui.aetherplex_gui import main; print('✅ GUI ready!')",
            ],
            check=True,
            capture_output=True,
            cwd=Path.cwd(),
        )
        print("✅ aetherra GUI is ready to launch!")
    except subprocess.CalledProcessError as e:
        print(
            "⚠️  GUI import test failed - but this may be normal if display is not available"
        )

    print("\\n🚀 aetherra/Lyrixais optimized and ready!")


if __name__ == "__main__":
    main()
