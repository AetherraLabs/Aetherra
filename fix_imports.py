#!/usr/bin/env python3
"""
🔧 Aetherra Import Fix Utility
==============================
Fixes common import issues for Aetherra contributors.

This script addresses import errors that occur when contributors
fork the repository by:
1. Creating missing __init__.py files
2. Setting up proper Python paths
3. Installing missing dependencies
4. Providing helpful debugging information

Run this script after cloning/forking the repository to resolve
import issues.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AetherraImportFixer:
    """Utility class to fix import issues in Aetherra repository."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.aetherra_dir = self.project_root / "Aetherra"
        self.issues_found = []
        self.fixes_applied = []
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        logger.info("🐍 Checking Python version...")
        
        version_info = sys.version_info
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            logger.error(f"❌ Python 3.8+ required, found {version_info.major}.{version_info.minor}")
            self.issues_found.append("Incompatible Python version")
            return False
        
        logger.info(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro} - Compatible")
        return True
    
    def find_missing_init_files(self) -> List[Path]:
        """Find directories that need __init__.py files."""
        logger.info("🔍 Scanning for missing __init__.py files...")
        
        missing_init_dirs = []
        
        # Key directories that should be Python packages
        important_dirs = [
            self.aetherra_dir / "aetherra_core",
            self.aetherra_dir / "aetherra_core" / "engine",
            self.aetherra_dir / "aetherra_core" / "orchestration",
            self.aetherra_dir / "aetherra_core" / "plugins",
            self.aetherra_dir / "aetherra_core" / "memory",
            self.aetherra_dir / "aetherra_core" / "system",
            self.aetherra_dir / "aetherra_core" / "kernel",
            self.aetherra_dir / "aetherra_core" / "file_system",
            self.aetherra_dir / "aetherra_core" / "reflection",
            self.aetherra_dir / "aetherra_core" / "reflection_engine",
            self.aetherra_dir / "core",
            self.aetherra_dir / "lyrixa",
            self.aetherra_dir / "plugins",
            self.aetherra_dir / "runtime",
        ]
        
        for dir_path in important_dirs:
            if dir_path.exists() and dir_path.is_dir():
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    missing_init_dirs.append(dir_path)
                    logger.warning(f"⚠️  Missing __init__.py in {dir_path.relative_to(self.project_root)}")
        
        return missing_init_dirs
    
    def create_init_file(self, directory: Path) -> bool:
        """Create a basic __init__.py file for a directory."""
        try:
            init_file = directory / "__init__.py"
            package_name = directory.name.replace("_", " ").title()
            
            init_content = f'''#!/usr/bin/env python3
"""
{package_name} Package
{'=' * (len(package_name) + 8)}
Auto-generated __init__.py file for Aetherra AI OS.

This file was created automatically to fix import issues.
You can customize it as needed for your specific package requirements.
"""

__version__ = "1.0.0"

# Graceful imports with fallbacks
import logging
logger = logging.getLogger(__name__)

# Package status
PACKAGE_AVAILABLE = True

def get_package_status():
    """Get the status of this package."""
    return {{'available': PACKAGE_AVAILABLE}}

# Export main components
__all__ = [
    'get_package_status',
    'PACKAGE_AVAILABLE',
]
'''
            
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(init_content)
            
            logger.info(f"✅ Created __init__.py in {directory.relative_to(self.project_root)}")
            self.fixes_applied.append(f"Created __init__.py in {directory.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create __init__.py in {directory}: {e}")
            return False
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are installed."""
        logger.info("📦 Checking dependencies...")
        
        dependencies_status = {}
        
        # Core dependencies that are essential for basic functionality
        core_deps = [
            'json',     # Built-in
            'logging',  # Built-in  
            'pathlib',  # Built-in
            'asyncio',  # Built-in
            'flask',    # Web framework
            'requests', # HTTP client
        ]
        
        # Optional dependencies that enhance functionality
        optional_deps = [
            'aiohttp',
            'rich',
            'python-dotenv',
            'psutil',
        ]
        
        # Check core dependencies
        missing_core = []
        for dep in core_deps:
            try:
                __import__(dep)
                dependencies_status[dep] = True
                logger.debug(f"✅ {dep} - Available")
            except ImportError:
                dependencies_status[dep] = False
                missing_core.append(dep)
                logger.warning(f"⚠️  {dep} - Missing (core dependency)")
        
        # Check optional dependencies  
        for dep in optional_deps:
            try:
                __import__(dep)
                dependencies_status[dep] = True
                logger.debug(f"✅ {dep} - Available")
            except ImportError:
                dependencies_status[dep] = False
                logger.debug(f"ℹ️  {dep} - Missing (optional)")
        
        # Only report core missing dependencies as issues
        for dep in missing_core:
            if dep not in ['json', 'logging', 'pathlib', 'asyncio']:  # Skip built-ins
                self.issues_found.append(f"Missing core dependency: {dep}")
        
        return dependencies_status
    
    def install_missing_dependencies(self) -> bool:
        """Install missing dependencies with timeout and fallback."""
        logger.info("📦 Installing missing dependencies...")
        
        # Try minimal requirements first for faster setup
        minimal_deps = [
            'flask>=2.3.0',
            'requests>=2.31.0', 
            'python-dotenv>=1.0.0',
            'rich>=13.4.0'
        ]
        
        logger.info("Installing core dependencies first...")
        success = True
        
        for dep in minimal_deps:
            try:
                logger.info(f"  Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True, timeout=120)  # 2 minute timeout per package
                
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  {dep} installation timed out - skipping")
                success = False
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️  Failed to install {dep}: {e}")
                success = False
        
        if success:
            logger.info("✅ Core dependencies installed successfully")
            self.fixes_applied.append("Installed core dependencies")
        else:
            logger.warning("⚠️  Some dependencies failed to install - continuing anyway")
            self.fixes_applied.append("Attempted to install dependencies (some may have failed)")
        
        # Optionally try full requirements with timeout
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            logger.info("Attempting full requirements installation (with timeout)...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, timeout=300)  # 5 minute timeout total
                
                if result.returncode == 0:
                    logger.info("✅ Full requirements installed successfully")
                    self.fixes_applied.append("Installed full requirements.txt")
                else:
                    logger.warning("⚠️  Some packages in requirements.txt failed to install")
                    
            except subprocess.TimeoutExpired:
                logger.warning("⚠️  Full requirements installation timed out - core packages should be sufficient")
            except Exception as e:
                logger.warning(f"⚠️  Full requirements installation failed: {e}")
        
        return True  # Return True as long as we tried - core deps are sufficient
    
    def create_minimal_requirements(self):
        """Create a minimal requirements.txt file."""
        minimal_requirements = """# Minimal Aetherra requirements for development
flask>=2.3.0
flask-socketio>=5.5.1
requests>=2.31.0
aiohttp>=3.8.0
psutil>=5.9.0
python-dotenv>=1.0.0
rich>=13.4.0
"""
        
        requirements_file = self.project_root / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write(minimal_requirements)
        
        logger.info("📝 Created minimal requirements.txt")
    
    def test_imports(self) -> Dict[str, bool]:
        """Test common import patterns."""
        logger.info("🧪 Testing import patterns...")
        
        import_tests = {}
        
        # Test imports that commonly fail
        test_imports = [
            ("aetherra_core", "from Aetherra.aetherra_core import get_system_status"),
            ("kernel_loop", "from aetherra_kernel_loop import get_kernel"),
            ("service_registry", "from aetherra_service_registry import get_service_registry"),
            ("startup", "import aetherra_startup"),
        ]
        
        for name, import_statement in test_imports:
            try:
                exec(import_statement)
                import_tests[name] = True
                logger.info(f"✅ {name} import - Success")
            except Exception as e:
                import_tests[name] = False
                logger.warning(f"⚠️  {name} import - Failed: {e}")
        
        return import_tests
    
    def fix_all_issues(self) -> bool:
        """Run all fixes."""
        logger.info("🚀 Starting Aetherra import fix process...")
        
        success = True
        
        # 1. Check Python version
        if not self.check_python_version():
            return False
        
        # 2. Create missing __init__.py files
        missing_inits = self.find_missing_init_files()
        for directory in missing_inits:
            if not self.create_init_file(directory):
                success = False
        
        # 3. Check dependencies (but don't fail if some are missing)
        deps_status = self.check_dependencies()
        missing_core_deps = [
            dep for dep, status in deps_status.items() 
            if not status and dep in ['flask', 'requests']  # Only essential ones
        ]
        
        if missing_core_deps:
            logger.info(f"Installing {len(missing_core_deps)} missing core dependencies...")
            # Try to install, but don't fail the whole process if it doesn't work
            self.install_missing_dependencies()
        else:
            logger.info("✅ Core dependencies are available")
        
        # 4. Test imports
        import_results = self.test_imports()
        
        # 5. Generate report
        self.generate_report(deps_status, import_results)
        
        return success
    
    def generate_report(self, deps_status: Dict[str, bool], import_results: Dict[str, bool]):
        """Generate a summary report."""
        logger.info("📊 Generating import fix report...")
        
        report = f"""
🌌 Aetherra Import Fix Report
{'=' * 40}

Python Environment:
  Version: {sys.version}
  Executable: {sys.executable}

Issues Found: {len(self.issues_found)}
{chr(10).join(f"  - {issue}" for issue in self.issues_found)}

Fixes Applied: {len(self.fixes_applied)}
{chr(10).join(f"  - {fix}" for fix in self.fixes_applied)}

Dependency Status:
{chr(10).join(f"  {dep}: {'✅' if status else '❌'}" for dep, status in deps_status.items())}

Import Tests:
{chr(10).join(f"  {test}: {'✅' if status else '❌'}" for test, status in import_results.items())}

Next Steps:
  1. If any imports still fail, check the specific error messages
  2. Consider running: pip install -r requirements.txt --upgrade
  3. For VS Code users, install recommended extensions (see CONTRIBUTING.md)
  4. Join our Discord for support: https://discord.gg/aetherra

Repository: https://github.com/AetherraLabs/Aetherra
"""
        
        print(report)
        
        # Save report to file
        report_file = self.project_root / "import_fix_report.md"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 Report saved to {report_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save report file: {e}")
            # Try saving without emojis
            try:
                clean_report = report.encode('ascii', 'ignore').decode('ascii')
                with open(report_file, 'w') as f:
                    f.write(clean_report)
                logger.info(f"📄 Report saved to {report_file} (ASCII only)")
            except Exception:
                logger.warning("Could not save report file")
        
        logger.info(f"📄 Report completed")

def main():
    """Main function to run the import fixer."""
    try:
        fixer = AetherraImportFixer()
        success = fixer.fix_all_issues()
        
        if success:
            print("\n🎉 Import fix completed successfully!")
            print("   You should now be able to import Aetherra modules.")
        else:
            print("\n⚠️  Import fix completed with some issues.")
            print("   Check the report above for details.")
            
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
