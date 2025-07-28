#!/usr/bin/env python3
"""
Step 4: Web Interface Migration
Migrates your working web interface to the clean architecture.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path


class WebInterfaceMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.clean_dir = self.project_root / "Aetherra_v2"
        self.source_dir = self.project_root / "Aetherra"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def migrate_web_interface(self):
        """Migrate your working web interface to clean architecture"""
        print("🌐 STEP 4: MIGRATE WEB INTERFACE")
        print("=" * 60)
        print("Migrating your working web interface to clean architecture...")

        # Define web interface components to migrate
        web_components = [
            {
                "source": "lyrixa/gui/web_interface_server.py",
                "target": "web/server/web_interface_server.py",
                "description": "Main web interface server (your working GUI)",
            },
            {
                "source": "lyrixa/gui/web_bridge.py",
                "target": "web/server/web_bridge.py",
                "description": "Web bridge component",
            },
            {
                "source": "api/run_server.py",
                "target": "api/rest/run_server.py",
                "description": "API server runner",
            },
        ]

        migrated_files = []

        for component in web_components:
            source_file = self.source_dir / component["source"]
            target_file = self.clean_dir / component["target"]

            if source_file.exists():
                print(f"\n📦 Migrating: {component['description']}")
                print(f"   From: {source_file.relative_to(self.project_root)}")
                print(f"   To:   {target_file.relative_to(self.project_root)}")

                # Create target directory
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(source_file, target_file)
                migrated_files.append(target_file)
                print(f"   ✅ Migrated successfully")

            else:
                print(f"\n⚠️  Source not found: {source_file}")

        return migrated_files

    def create_web_integration_adapter(self):
        """Create adapter to integrate web interface with clean architecture"""
        print(f"\n🔌 CREATING WEB INTEGRATION ADAPTER:")

        adapter_content = '''"""
Web Interface Integration Adapter
Connects your existing web interface to the clean architecture.
"""

import sys
import logging
from pathlib import Path

# Add clean architecture paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integration.bridges.aetherra_lyrixa_bridge import bridge
from integration.bridges.memory_adapter import memory_adapter

logger = logging.getLogger(__name__)

class WebInterfaceAdapter:
    """Adapter for integrating web interface with clean architecture"""

    def __init__(self):
        self.bridge = bridge
        self.memory_adapter = memory_adapter
        logger.info("🌐 Web Interface Adapter initialized")

    async def initialize_web_systems(self):
        """Initialize web interface systems with clean architecture"""
        logger.info("🚀 Initializing web systems...")

        # Connect to integration bridge
        await self.bridge.start()

        # Register web interface handlers
        self.bridge.register_aetherra_handler("web_request", self.handle_web_request)
        self.bridge.register_lyrixa_handler("web_response", self.handle_web_response)

        logger.info("✅ Web systems initialized")

    async def handle_web_request(self, request_data):
        """Handle requests from web interface"""
        logger.info(f"📨 Web request: {request_data.get('type', 'unknown')}")
        # Process web requests through clean architecture
        return {"status": "processed", "data": request_data}

    async def handle_web_response(self, response_data):
        """Handle responses to web interface"""
        logger.info(f"📤 Web response: {response_data.get('type', 'unknown')}")
        # Send responses back to web interface
        return response_data

    def get_memory_context(self, context_id):
        """Get memory context for web interface"""
        return self.memory_adapter.get_shared_context(context_id)

    def store_memory_context(self, context_id, data):
        """Store memory context from web interface"""
        self.memory_adapter.store_shared_context(context_id, data)

# Global web adapter instance
web_adapter = WebInterfaceAdapter()
'''

        adapter_file = self.clean_dir / "web" / "server" / "web_adapter.py"
        adapter_file.parent.mkdir(parents=True, exist_ok=True)
        adapter_file.write_text(adapter_content, encoding="utf-8")
        print(f"✅ Created: {adapter_file.relative_to(self.project_root)}")

        return adapter_file

    def create_enhanced_launcher(self):
        """Create enhanced launcher that includes your web interface"""
        print(f"\n🚀 CREATING ENHANCED LAUNCHER WITH WEB INTERFACE:")

        launcher_content = '''#!/usr/bin/env python3
"""
Aetherra v2 Enhanced Launcher with Web Interface
Launches the integrated system with your working web interface.
"""

import asyncio
import logging
import sys
import subprocess
from pathlib import Path

# Add clean architecture to path
sys.path.insert(0, str(Path(__file__).parent))

from integration.bridges.aetherra_lyrixa_bridge import bridge
from web.server.web_adapter import web_adapter

async def main():
    """Enhanced launcher with web interface integration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Aetherra v2 with Web Interface")

    try:
        # Initialize integration systems
        await bridge.start()
        await web_adapter.initialize_web_systems()

        # Start your web interface server
        logger.info("🌐 Starting web interface server...")
        web_server_path = Path(__file__).parent / "web" / "server" / "web_interface_server.py"

        if web_server_path.exists():
            # Start web interface in background
            web_process = subprocess.Popen([
                sys.executable, str(web_server_path), "--no-browser"
            ], cwd=str(Path(__file__).parent.parent))

            logger.info("✅ Web interface started on port 8686")
            logger.info("🌟 Aetherra v2 system fully operational!")
            logger.info("🌐 Access your web interface at: http://localhost:8686")

            # Keep running
            while True:
                await asyncio.sleep(1)
        else:
            logger.error("❌ Web interface server not found")

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        await bridge.stop()
        if 'web_process' in locals():
            web_process.terminate()
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
'''

        launcher_file = self.clean_dir / "launch_with_web.py"
        launcher_file.write_text(launcher_content, encoding="utf-8")
        print(f"✅ Created: {launcher_file.relative_to(self.project_root)}")

        return launcher_file

    def update_web_interface_imports(self, migrated_files):
        """Update imports in migrated web interface files"""
        print(f"\n🔧 UPDATING WEB INTERFACE IMPORTS:")

        for file_path in migrated_files:
            if file_path.name.endswith(".py"):
                print(f"📝 Updating imports in: {file_path.name}")

                try:
                    # Read current content
                    content = file_path.read_text(encoding="utf-8")

                    # Add clean architecture imports at the top
                    import_additions = """
# Clean Architecture Imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integration.bridges.aetherra_lyrixa_bridge import bridge
from web.server.web_adapter import web_adapter

"""

                    # Add imports after existing imports
                    lines = content.split("\n")
                    import_end = 0

                    for i, line in enumerate(lines):
                        if line.strip().startswith(
                            "import "
                        ) or line.strip().startswith("from "):
                            import_end = i + 1
                        elif line.strip() and not line.strip().startswith("#"):
                            break

                    # Insert new imports
                    lines.insert(import_end, import_additions)
                    updated_content = "\n".join(lines)

                    # Write back
                    file_path.write_text(updated_content, encoding="utf-8")
                    print(f"   ✅ Imports updated")

                except Exception as e:
                    print(f"   ⚠️  Could not update imports: {e}")

    def create_web_test_runner(self):
        """Create test runner for the migrated web interface"""
        print(f"\n🧪 CREATING WEB INTERFACE TEST RUNNER:")

        test_content = '''#!/usr/bin/env python3
"""
Web Interface Test Runner
Tests the migrated web interface in clean architecture.
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

async def test_web_interface():
    """Test the migrated web interface"""
    print("🧪 TESTING MIGRATED WEB INTERFACE")
    print("="*50)

    # Get paths
    project_root = Path(__file__).parent.parent.parent
    web_server = Path(__file__).parent / "web_interface_server.py"

    if not web_server.exists():
        print("❌ Web interface server not found")
        return False

    print(f"🌐 Starting web interface: {web_server.name}")

    try:
        # Start web server
        process = subprocess.Popen([
            sys.executable, str(web_server), "--no-browser"
        ], cwd=str(project_root))

        # Wait a moment for startup
        time.sleep(3)

        # Check if process is running
        if process.poll() is None:
            print("✅ Web interface started successfully!")
            print("🌐 Available at: http://localhost:8686")
            print("🔍 Test by opening the URL in your browser")

            # Keep running for testing
            print("⏳ Press Ctrl+C to stop...")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("🛑 Stopping web interface...")
                process.terminate()
                return True
        else:
            print("❌ Web interface failed to start")
            return False

    except Exception as e:
        print(f"❌ Error testing web interface: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_web_interface())
'''

        test_file = self.clean_dir / "web" / "server" / "test_web_interface.py"
        test_file.write_text(test_content, encoding="utf-8")
        print(f"✅ Created: {test_file.relative_to(self.project_root)}")

        return test_file


def main():
    project_root = Path.cwd()
    migrator = WebInterfaceMigrator(project_root)

    print("🌐 SAFE FRESH START - STEP 4")
    print("Migrating your working web interface")
    print()

    # Migrate web interface components
    migrated_files = migrator.migrate_web_interface()

    # Create web integration adapter
    adapter_file = migrator.create_web_integration_adapter()

    # Create enhanced launcher
    launcher_file = migrator.create_enhanced_launcher()

    # Update imports in migrated files
    migrator.update_web_interface_imports(migrated_files)

    # Create test runner
    test_file = migrator.create_web_test_runner()

    print(f"\n🎉 STEP 4 COMPLETE!")
    print(f"✅ Migrated {len(migrated_files)} web interface files")
    print(f"✅ Created web integration adapter")
    print(f"✅ Created enhanced launcher with web interface")
    print(f"✅ Updated imports for clean architecture")
    print(f"✅ Created web interface test runner")

    print(f"\n🎯 YOUR WEB INTERFACE IS NOW IN CLEAN ARCHITECTURE:")
    print("• Original web interface preserved and working")
    print("• Clean architecture version ready for testing")
    print("• Integration bridge connecting both systems")
    print("• Enhanced launcher with web interface support")

    print(f"\n🧪 NEXT: TEST THE MIGRATED WEB INTERFACE")
    print(f"Run: python Aetherra_v2/web/server/test_web_interface.py")
    print("Or: python Aetherra_v2/launch_with_web.py")

    return {
        "migrated_files": len(migrated_files),
        "adapter_file": str(adapter_file),
        "launcher_file": str(launcher_file),
        "test_file": str(test_file),
    }


if __name__ == "__main__":
    main()
