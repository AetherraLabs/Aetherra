"""
Component Migrator
Utilities for safely migrating existing components to clean architecture.
"""

import shutil
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ComponentMigrator:
    """Migrates existing components to clean architecture"""

    def __init__(self, source_dir: Path, target_dir: Path):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.migration_log = []
        logger.info(f"🔄 Component Migrator initialized: {source_dir} → {target_dir}")

    def migrate_working_components(self, component_list: List[str]):
        """Migrate list of working components"""
        logger.info(f"[DISC] Migrating {len(component_list)} working components...")

        for component_path in component_list:
            source_file = self.source_dir / component_path

            if source_file.exists():
                # Determine target location based on component type
                target_file = self._determine_target_location(component_path)

                if target_file:
                    self._migrate_file(source_file, target_file)
                else:
                    logger.warning(f"⚠️  Could not determine target for: {component_path}")
            else:
                logger.warning(f"⚠️  Source file not found: {component_path}")

    def _determine_target_location(self, component_path: str) -> Path:
        """Determine where a component should go in clean architecture"""
        path_lower = component_path.lower()

        # Web interface components
        if any(term in path_lower for term in ['web_interface', 'gui', 'server']):
            return self.target_dir / "web" / "server" / Path(component_path).name

        # Memory components
        elif 'memory' in path_lower:
            if 'lyrixa' in path_lower:
                return self.target_dir / "lyrixa" / "memory" / Path(component_path).name
            else:
                return self.target_dir / "core" / "memory" / Path(component_path).name

        # Agent components
        elif 'agent' in path_lower:
            return self.target_dir / "lyrixa" / "agents" / Path(component_path).name

        # API components
        elif any(term in path_lower for term in ['api', 'server', 'endpoint']):
            return self.target_dir / "api" / "rest" / Path(component_path).name

        # Core components
        elif any(term in path_lower for term in ['core', 'engine']):
            return self.target_dir / "core" / "ai" / Path(component_path).name

        # Plugin components
        elif 'plugin' in path_lower:
            return self.target_dir / "core" / "plugins" / Path(component_path).name

        # Default to appropriate directory
        else:
            return None

    def _migrate_file(self, source_file: Path, target_file: Path):
        """Migrate a single file"""
        try:
            # Ensure target directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_file, target_file)

            self.migration_log.append({
                "source": str(source_file),
                "target": str(target_file),
                "status": "success"
            })

            logger.info(f"[OK] Migrated: {source_file.name}")

        except Exception as e:
            self.migration_log.append({
                "source": str(source_file),
                "target": str(target_file),
                "status": "failed",
                "error": str(e)
            })

            logger.error(f"❌ Migration failed: {source_file.name} - {e}")

    def save_migration_log(self, log_file: Path):
        """Save migration log"""
        with open(log_file, 'w') as f:
            json.dump(self.migration_log, f, indent=2)
        logger.info(f"📄 Migration log saved: {log_file}")

# Helper function for easy migration
def migrate_working_web_interface(source_dir: Path, target_dir: Path):
    """Migrate your working web interface to clean architecture"""
    migrator = ComponentMigrator(source_dir, target_dir)

    # Your working web interface components
    web_components = [
        "lyrixa/gui/web_interface_server.py",  # Your main working server
        "api/run_server.py",
        "lyrixa/gui/web_bridge.py"
    ]

    migrator.migrate_working_components(web_components)
    return migrator
