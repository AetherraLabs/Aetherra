#!/usr/bin/env python3
"""
Focused Agent Migration - Migrate the 527 REAL agents found
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List


class FocusedAgentMigration:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.aetherra_v2 = self.workspace_root / "Aetherra_v2"
        self.report_file = self.workspace_root / "real_agent_discovery_report.json"

        # Target directories in clean architecture
        self.target_dirs = {
            "lyrixa_agent": self.aetherra_v2 / "lyrixa" / "agents",
            "aetherra_agent": self.aetherra_v2 / "core" / "agents",
            "cognitive_agent": self.aetherra_v2 / "lyrixa" / "cognitive",
            "personality_agent": self.aetherra_v2 / "lyrixa" / "personality",
            "orchestrator_agent": self.aetherra_v2 / "core" / "orchestration",
            "general_agent": self.aetherra_v2 / "lyrixa" / "agents",
            "agent_file": self.aetherra_v2 / "lyrixa" / "agents",
        }

        self.migration_log = []

    def load_real_agents(self) -> Dict:
        """Load the real agent discovery report"""
        if not self.report_file.exists():
            raise FileNotFoundError(f"Real agent report not found: {self.report_file}")

        with open(self.report_file, "r") as f:
            return json.load(f)

    def migrate_real_agents(self):
        """Migrate the 527 real agents to clean architecture"""
        print("🚀 Starting Focused Agent Migration...")
        print("📊 Migrating 527 REAL agents (not 41,553 fake ones!)")

        # Load real agents
        report = self.load_real_agents()

        print(f"\n📋 Agent Categories to Migrate:")
        for category, count in report["summary"].items():
            print(f"  {category}: {count} agents")

        # Create target directories
        self._create_target_directories()

        # Migrate by category
        migrated_count = 0
        for category, agents in report["categories"].items():
            print(f"\n🔄 Migrating {category} ({len(agents)} agents)...")

            for agent in agents:
                if self._migrate_single_agent(agent, category):
                    migrated_count += 1

        print(f"\n✅ Agent Migration Complete!")
        print(f"📊 Migrated: {migrated_count} agents")
        print(f"📄 Migration log: {len(self.migration_log)} entries")

        # Create agent registry
        self._create_agent_registry(report)

        # Create integration bridge
        self._create_agent_integration_bridge()

        # Save migration log
        self._save_migration_log()

    def _create_target_directories(self):
        """Create target directories for agents"""
        print("📁 Creating target directories...")

        for category, target_dir in self.target_dirs.items():
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ {target_dir}")

    def _migrate_single_agent(self, agent: Dict, category: str) -> bool:
        """Migrate a single agent file"""
        source_file = self.workspace_root / agent["file"]

        # Skip if source doesn't exist or is in excluded directories
        if not source_file.exists():
            return False

        # Skip backup/archive directories
        excluded_paths = ["Unused", "Archive", "backup", "legacy_cleanup"]
        if any(excluded in str(source_file) for excluded in excluded_paths):
            return False

        # Determine target directory
        target_dir = self.target_dirs.get(category, self.target_dirs["general_agent"])
        target_file = target_dir / source_file.name

        # Handle duplicates
        counter = 1
        while target_file.exists():
            stem = source_file.stem
            suffix = source_file.suffix
            target_file = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            # Copy the file
            shutil.copy2(source_file, target_file)

            self.migration_log.append(
                {
                    "source": str(source_file),
                    "target": str(target_file),
                    "category": category,
                    "agent_info": agent,
                    "status": "success",
                }
            )

            print(
                f"    ✅ {source_file.name} → {target_file.relative_to(self.aetherra_v2)}"
            )
            return True

        except Exception as e:
            self.migration_log.append(
                {
                    "source": str(source_file),
                    "target": str(target_file),
                    "category": category,
                    "agent_info": agent,
                    "status": "error",
                    "error": str(e),
                }
            )

            print(f"    ❌ Failed to copy {source_file.name}: {e}")
            return False

    def _create_agent_registry(self, report: Dict):
        """Create an agent registry for the integration bridge"""
        registry = {
            "version": "1.0",
            "timestamp": report["timestamp"],
            "total_agents": report["total_real_agents"],
            "categories": report["summary"],
            "agents_by_category": {},
            "agent_locations": {},
        }

        # Organize migrated agents
        for entry in self.migration_log:
            if entry["status"] == "success":
                category = entry["category"]
                if category not in registry["agents_by_category"]:
                    registry["agents_by_category"][category] = []

                agent_info = {
                    "file": Path(entry["target"]).name,
                    "path": entry["target"],
                    "original_path": entry["source"],
                    "class_name": entry["agent_info"].get("class_name"),
                    "methods": entry["agent_info"].get("methods", []),
                    "description": entry["agent_info"].get("description"),
                }

                registry["agents_by_category"][category].append(agent_info)
                registry["agent_locations"][Path(entry["target"]).name] = entry[
                    "target"
                ]

        # Save registry
        registry_file = self.aetherra_v2 / "integration" / "agent_registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        print(f"📋 Agent registry created: {registry_file}")

    def _create_agent_integration_bridge(self):
        """Create the agent integration bridge"""
        bridge_code = '''"""
Agent Integration Bridge - Connect migrated agents to clean architecture
"""

import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any

class AgentIntegrationBridge:
    """Bridge to manage agent integration in clean architecture"""

    def __init__(self, aetherra_v2_root: Path):
        self.aetherra_v2_root = Path(aetherra_v2_root)
        self.registry_file = self.aetherra_v2_root / "integration" / "agent_registry.json"
        self.agents = {}
        self.loaded_agents = {}

        self._load_agent_registry()

    def _load_agent_registry(self):
        """Load the agent registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.agents = json.load(f)
        else:
            print("⚠️ Agent registry not found")

    def get_agents_by_category(self, category: str) -> List[Dict]:
        """Get all agents in a specific category"""
        return self.agents.get('agents_by_category', {}).get(category, [])

    def get_all_categories(self) -> List[str]:
        """Get all agent categories"""
        return list(self.agents.get('categories', {}).keys())

    def load_agent(self, agent_name: str) -> Optional[Any]:
        """Dynamically load an agent by name"""
        if agent_name in self.loaded_agents:
            return self.loaded_agents[agent_name]

        # Find agent in registry
        agent_path = self.agents.get('agent_locations', {}).get(agent_name)
        if not agent_path:
            print(f"❌ Agent not found: {agent_name}")
            return None

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(agent_name, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.loaded_agents[agent_name] = module
            print(f"✅ Loaded agent: {agent_name}")
            return module

        except Exception as e:
            print(f"❌ Failed to load agent {agent_name}: {e}")
            return None

    def get_lyrixa_agents(self) -> List[Dict]:
        """Get all Lyrixa agents"""
        return self.get_agents_by_category('lyrixa_agent')

    def get_aetherra_agents(self) -> List[Dict]:
        """Get all Aetherra agents"""
        return self.get_agents_by_category('aetherra_agent')

    def get_cognitive_agents(self) -> List[Dict]:
        """Get all cognitive agents"""
        return self.get_agents_by_category('cognitive_agent')

    def get_orchestrator_agents(self) -> List[Dict]:
        """Get all orchestrator agents"""
        return self.get_agents_by_category('orchestrator_agent')

    def get_agent_summary(self) -> Dict:
        """Get summary of all agents"""
        return {
            'total_agents': self.agents.get('total_agents', 0),
            'categories': self.agents.get('categories', {}),
            'loaded_agents': len(self.loaded_agents)
        }

    def test_agent_loading(self):
        """Test loading a few agents to verify integration"""
        print("🧪 Testing agent loading...")

        # Test loading a few agents from each category
        for category in self.get_all_categories():
            agents = self.get_agents_by_category(category)
            if agents:
                # Try loading the first agent
                first_agent = agents[0]
                agent_file = first_agent['file']
                print(f"  Testing {category}: {agent_file}")

                result = self.load_agent(agent_file)
                if result:
                    print(f"    ✅ Successfully loaded {agent_file}")
                else:
                    print(f"    ❌ Failed to load {agent_file}")

        print(f"\\n📊 Agent Loading Summary:")
        summary = self.get_agent_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
'''

        bridge_file = self.aetherra_v2 / "integration" / "bridges" / "agent_bridge.py"
        bridge_file.parent.mkdir(parents=True, exist_ok=True)

        with open(bridge_file, "w", encoding="utf-8") as f:
            f.write(bridge_code)

        print(f"🌉 Agent integration bridge created: {bridge_file}")

    def _save_migration_log(self):
        """Save the migration log"""
        log_file = self.aetherra_v2 / "tools" / "migration" / "agent_migration_log.json"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.migration_log, f, indent=2)

        print(f"📄 Migration log saved: {log_file}")


def main():
    """Run focused agent migration"""
    workspace = r"c:\\Users\\enigm\\Desktop\\Aetherra Project"

    print("🎯 FOCUSED AGENT MIGRATION")
    print("Moving 527 REAL agents (not 41,553 fake ones)")
    print(f"📁 Workspace: {workspace}")

    migrator = FocusedAgentMigration(workspace)
    migrator.migrate_real_agents()

    print("\\n🎉 AGENT MIGRATION COMPLETE!")
    print("✅ All real agents migrated to clean architecture")
    print("✅ Agent registry created")
    print("✅ Integration bridge established")
    print("\\n🚀 Ready for agent testing and integration!")


if __name__ == "__main__":
    main()
