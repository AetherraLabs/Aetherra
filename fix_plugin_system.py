#!/usr/bin/env python3
"""
Plugin System Diagnostic and Repair Tool
=========================================

Comprehensive fix for plugin discovery and chain loading issues.
Addresses the following problems:
1. Auto-discovery finding 0 plugins
2. Plugin Chain Loader missing required fields
3. Corrupted plugin chains in memory
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PluginSystemRepair:
    """Plugin system diagnostic and repair tool."""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.plugin_directories = [
            self.project_root / "plugins",
            self.project_root / "lyrixa" / "plugins",
            self.project_root / "src" / "aetherra" / "plugins",
            self.project_root / "sdk" / "plugins",
        ]
        self.memory_db_paths = [
            self.project_root / "lyrixa_context_memory.db",
            self.project_root / "lyrixa_plugin_memory.db",
            self.project_root / "plugin_state_memory.db",
        ]
        self.required_fields = [
            "name",
            "description",
            "input_schema",
            "output_schema",
            "created_by",
            "plugins",
        ]
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": [],
            "fixes_applied": [],
            "plugins_discovered": [],
            "chains_repaired": 0,
            "status": "unknown",
        }

    def diagnose_plugin_discovery(self):
        """Diagnose plugin discovery issues."""
        print("🔍 Step 1: Diagnosing Plugin Discovery Issues...")

        discovered_plugins = []

        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                self.report["issues_found"].append(
                    f"Plugin directory not found: {plugin_dir}"
                )
                continue

            print(f"   Scanning: {plugin_dir}")

            for file_path in plugin_dir.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue

                plugin_info = self._analyze_plugin_file(file_path)
                if plugin_info:
                    discovered_plugins.append(plugin_info)
                    print(f"   ✅ Found valid plugin: {plugin_info['name']}")
                else:
                    self.report["issues_found"].append(
                        f"Invalid plugin file: {file_path}"
                    )
                    print(f"   ❌ Invalid plugin: {file_path}")

        self.report["plugins_discovered"] = discovered_plugins
        print(f"   📊 Total valid plugins found: {len(discovered_plugins)}")

        if len(discovered_plugins) == 0:
            self.report["issues_found"].append(
                "No valid plugins discovered in any directory"
            )
            return False

        return True

    def _analyze_plugin_file(self, file_path: Path) -> Optional[Dict]:
        """Analyze a Python file to determine if it's a valid plugin."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for plugin class patterns
            has_plugin_class = any(
                pattern in content.lower()
                for pattern in [
                    "class.*plugin",
                    "baseplugin",
                    "lyrixaplugin",
                    "def execute",
                    "def run",
                ]
            )

            if not has_plugin_class:
                return None

            # Extract basic metadata
            plugin_info = {
                "file_path": str(file_path),
                "name": file_path.stem,
                "description": "Auto-detected plugin",
                "input_schema": {"type": "object", "properties": {}},
                "output_schema": {"type": "object", "properties": {}},
                "created_by": "Auto-discovery",
                "category": "utility",
                "has_required_fields": False,
            }

            # Look for explicit metadata
            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("name =") or line.startswith('"name":'):
                    try:
                        plugin_info["name"] = line.split("=")[1].strip().strip("\"'")
                    except:
                        pass
                elif line.startswith("description =") or line.startswith(
                    '"description":'
                ):
                    try:
                        plugin_info["description"] = (
                            line.split("=")[1].strip().strip("\"'")
                        )
                    except:
                        pass

            # Check if it has all required fields defined
            required_patterns = ["name", "description", "input_schema", "output_schema"]
            plugin_info["has_required_fields"] = all(
                pattern in content.lower() for pattern in required_patterns
            )

            return plugin_info

        except Exception as e:
            print(f"   ⚠️ Error analyzing {file_path}: {e}")
            return None

    def diagnose_memory_corruption(self):
        """Diagnose corrupted plugin chains in memory databases."""
        print("\n🔍 Step 2: Diagnosing Memory Database Corruption...")

        corrupted_chains = []

        for db_path in self.memory_db_paths:
            if not db_path.exists():
                print(f"   📂 Database not found: {db_path}")
                continue

            print(f"   Checking: {db_path}")

            try:
                chains = self._extract_plugin_chains_from_db(db_path)
                print(f"   📊 Found {len(chains)} plugin chains")

                for chain in chains:
                    missing_fields = [
                        field for field in self.required_fields if field not in chain
                    ]
                    if missing_fields:
                        corrupted_chains.append(
                            {
                                "database": str(db_path),
                                "chain_id": chain.get("id", "unknown"),
                                "missing_fields": missing_fields,
                                "data": chain,
                            }
                        )
                        print(f"   ❌ Corrupted chain: missing {missing_fields}")

            except Exception as e:
                self.report["issues_found"].append(f"Database error {db_path}: {e}")
                print(f"   ⚠️ Database error: {e}")

        if corrupted_chains:
            self.report["issues_found"].append(
                f"Found {len(corrupted_chains)} corrupted plugin chains"
            )
            self.corrupted_chains = corrupted_chains

        return len(corrupted_chains) == 0

    def _extract_plugin_chains_from_db(self, db_path: Path) -> List[Dict]:
        """Extract plugin chains from a SQLite database."""
        chains = []

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Try different table structures
            table_queries = [
                "SELECT * FROM plugin_chains",
                "SELECT * FROM memory WHERE type='plugin_chain'",
                "SELECT * FROM memories WHERE category='plugin_chain'",
                "SELECT content FROM memories WHERE content LIKE '%plugin_chain%'",
            ]

            for query in table_queries:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            # Try to parse JSON content
                            if isinstance(row, tuple) and len(row) > 0:
                                # Find JSON-like content
                                for item in row:
                                    if isinstance(item, str) and (
                                        item.startswith("{") or "plugin_chain" in item
                                    ):
                                        chain_data = json.loads(item)
                                        if isinstance(chain_data, dict):
                                            chains.append(chain_data)
                                            break
                        except json.JSONDecodeError:
                            continue

                except sqlite3.Error:
                    continue

            conn.close()

        except Exception as e:
            print(f"   Database connection error: {e}")

        return chains

    def create_valid_plugin_templates(self):
        """Create valid plugin templates with all required fields."""
        print("\n🔧 Step 3: Creating Valid Plugin Templates...")

        template_dir = self.project_root / "plugins" / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)

        # Base plugin template
        base_template = '''"""
{name} Plugin
{description}
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PluginInfo:
    """Plugin metadata information."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    created_by: str
    version: str = "1.0.0"
    category: str = "utility"


class {class_name}:
    """
    {description}
    """

    # Required plugin metadata
    name = "{name}"
    description = "{description}"
    input_schema = {{
        "type": "object",
        "properties": {{
            "input": {{"type": "string", "description": "Input text to process"}}
        }},
        "required": ["input"]
    }}
    output_schema = {{
        "type": "object",
        "properties": {{
            "result": {{"type": "string", "description": "Processed output"}},
            "status": {{"type": "string", "description": "Processing status"}}
        }}
    }}
    created_by = "Plugin Generator"
    version = "1.0.0"
    category = "utility"

    def __init__(self):
        """Initialize the plugin."""
        self.plugin_info = PluginInfo(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            created_by=self.created_by,
            version=self.version,
            category=self.category
        )

    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the plugin with given input.

        Args:
            input_data: Input data matching input_schema
            context: Optional execution context

        Returns:
            Output data matching output_schema
        """
        try:
            # Plugin implementation goes here
            input_text = input_data.get("input", "")

            # Example processing
            result = f"Processed: {{input_text}}"

            return {{
                "result": result,
                "status": "success"
            }}

        except Exception as e:
            return {{
                "result": "",
                "status": f"error: {{str(e)}}"
            }}

    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata."""
        return {{
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "created_by": self.created_by,
            "version": self.version,
            "category": self.category
        }}


# Plugin instance for discovery
plugin_instance = {class_name}()
'''

        # Create sample plugins
        sample_plugins = [
            {
                "name": "text_processor",
                "class_name": "TextProcessorPlugin",
                "description": "Processes text input with various transformations",
            },
            {
                "name": "data_analyzer",
                "class_name": "DataAnalyzerPlugin",
                "description": "Analyzes data patterns and provides insights",
            },
            {
                "name": "memory_organizer",
                "class_name": "MemoryOrganizerPlugin",
                "description": "Organizes and categorizes memory entries",
            },
        ]

        for plugin_config in sample_plugins:
            plugin_content = base_template.format(**plugin_config)
            plugin_file = template_dir / f"{plugin_config['name']}.py"

            with open(plugin_file, "w", encoding="utf-8") as f:
                f.write(plugin_content)

            print(f"   ✅ Created: {plugin_file}")
            self.report["fixes_applied"].append(
                f"Created valid plugin template: {plugin_config['name']}"
            )

    def repair_corrupted_chains(self):
        """Repair corrupted plugin chains in memory databases."""
        print("\n🔧 Step 4: Repairing Corrupted Plugin Chains...")

        if not hasattr(self, "corrupted_chains"):
            print("   ✅ No corrupted chains found to repair")
            return True

        repaired_count = 0

        for chain_info in self.corrupted_chains:
            try:
                # Create a valid chain structure
                chain_data = chain_info["data"]

                # Fill in missing required fields with defaults
                for field in self.required_fields:
                    if field not in chain_data:
                        if field == "name":
                            chain_data[field] = f"repaired_chain_{repaired_count}"
                        elif field == "description":
                            chain_data[field] = "Auto-repaired plugin chain"
                        elif field == "input_schema":
                            chain_data[field] = {"type": "object", "properties": {}}
                        elif field == "output_schema":
                            chain_data[field] = {"type": "object", "properties": {}}
                        elif field == "created_by":
                            chain_data[field] = "Auto-repair System"
                        elif field == "plugins":
                            chain_data[field] = []

                # Update the database
                db_path = Path(chain_info["database"])
                if self._update_chain_in_database(db_path, chain_data):
                    repaired_count += 1
                    print(f"   ✅ Repaired chain: {chain_data['name']}")

            except Exception as e:
                print(f"   ❌ Failed to repair chain: {e}")

        self.report["chains_repaired"] = repaired_count
        self.report["fixes_applied"].append(
            f"Repaired {repaired_count} corrupted plugin chains"
        )

        return repaired_count > 0

    def _update_chain_in_database(self, db_path: Path, chain_data: Dict) -> bool:
        """Update a plugin chain in the database."""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Try to update existing record or insert new one
            chain_json = json.dumps(chain_data)
            chain_id = chain_data.get("id", f"repaired_{datetime.now().timestamp()}")

            # Update queries for different table structures
            update_queries = [
                f"UPDATE plugin_chains SET data=? WHERE id=?",
                f"UPDATE memory SET content=? WHERE id=? AND type='plugin_chain'",
                f"UPDATE memories SET content=? WHERE id=? OR content LIKE '%{chain_id}%'",
            ]

            updated = False
            for query in update_queries:
                try:
                    cursor.execute(query, (chain_json, chain_id))
                    if cursor.rowcount > 0:
                        updated = True
                        break
                except sqlite3.Error:
                    continue

            # If no update, try to insert
            if not updated:
                insert_queries = [
                    "INSERT INTO plugin_chains (id, data) VALUES (?, ?)",
                    "INSERT INTO memory (id, type, content) VALUES (?, 'plugin_chain', ?)",
                    "INSERT INTO memories (id, category, content) VALUES (?, 'plugin_chain', ?)",
                ]

                for query in insert_queries:
                    try:
                        cursor.execute(query, (chain_id, chain_json))
                        updated = True
                        break
                    except sqlite3.Error:
                        continue

            conn.commit()
            conn.close()

            return updated

        except Exception as e:
            print(f"   Database update error: {e}")
            return False

    def create_plugin_discovery_config(self):
        """Create plugin discovery configuration."""
        print("\n🔧 Step 5: Creating Plugin Discovery Configuration...")

        config = {
            "plugin_directories": [
                str(d) for d in self.plugin_directories if d.exists()
            ],
            "required_fields": self.required_fields,
            "discovery_patterns": ["*.py", "*plugin*.py", "*_plugin.py"],
            "validation_rules": {
                "must_have_class": True,
                "must_have_execute_method": True,
                "must_have_metadata": True,
            },
            "auto_repair": True,
            "last_updated": datetime.now().isoformat(),
        }

        config_file = self.project_root / "plugin_discovery_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"   ✅ Created: {config_file}")
        self.report["fixes_applied"].append("Created plugin discovery configuration")

    def generate_repair_report(self):
        """Generate comprehensive repair report."""
        print("\n📊 Step 6: Generating Repair Report...")

        # Determine overall status
        if len(self.report["issues_found"]) == 0:
            self.report["status"] = "healthy"
        elif len(self.report["fixes_applied"]) > 0:
            self.report["status"] = "repaired"
        else:
            self.report["status"] = "needs_attention"

        # Create detailed report
        report_content = f"""# Plugin System Repair Report

## 📊 Summary
- **Status**: {self.report["status"].upper()}
- **Generated**: {self.report["timestamp"]}
- **Issues Found**: {len(self.report["issues_found"])}
- **Fixes Applied**: {len(self.report["fixes_applied"])}
- **Plugins Discovered**: {len(self.report["plugins_discovered"])}
- **Chains Repaired**: {self.report["chains_repaired"]}

## ❌ Issues Found
{chr(10).join(f"- {issue}" for issue in self.report["issues_found"]) or "None"}

## ✅ Fixes Applied
{chr(10).join(f"- {fix}" for fix in self.report["fixes_applied"]) or "None"}

## 🔌 Discovered Plugins
{chr(10).join(f"- **{p['name']}**: {p['description']} ({p['file_path']})" for p in self.report["plugins_discovered"]) or "None"}

## 📋 Required Plugin Fields
All plugins must have these fields:
{chr(10).join(f"- `{field}`" for field in self.required_fields)}

## 🔧 Plugin Template Example
```python
class YourPlugin:
    name = "your_plugin"
    description = "Description of your plugin"
    input_schema = {{"type": "object", "properties": {{"input": {{"type": "string"}}}}}}
    output_schema = {{"type": "object", "properties": {{"result": {{"type": "string"}}}}}}
    created_by = "Your Name"

    def execute(self, input_data, context=None):
        # Your plugin logic here
        return {{"result": "processed"}}
```

## 📂 Plugin Directory Structure
```
plugins/
├── templates/          # Auto-generated templates
├── your_plugin.py      # Your custom plugins
└── README.md           # Plugin documentation
```

## 🚀 Next Steps
1. Review discovered plugins for required fields
2. Test plugin loading with: `python test_plugin_discovery.py`
3. Add any missing metadata to existing plugins
4. Clear corrupted chains: `python clear_plugin_chains.py`
5. Restart the plugin system to reload everything
"""

        report_file = self.project_root / "plugin_repair_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"   ✅ Created: {report_file}")

        # Also save JSON report
        json_report_file = self.project_root / "plugin_repair_report.json"
        with open(json_report_file, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2)

        print(f"   ✅ Created: {json_report_file}")

    def run_full_repair(self):
        """Run the complete repair process."""
        print("🔧 PLUGIN SYSTEM REPAIR TOOL")
        print("=" * 50)

        try:
            # Step 1: Diagnose plugin discovery
            discovery_ok = self.diagnose_plugin_discovery()

            # Step 2: Diagnose memory corruption
            memory_ok = self.diagnose_memory_corruption()

            # Step 3: Create templates if needed
            if not discovery_ok:
                self.create_valid_plugin_templates()

            # Step 4: Repair corrupted chains
            if not memory_ok:
                self.repair_corrupted_chains()

            # Step 5: Create configuration
            self.create_plugin_discovery_config()

            # Step 6: Generate report
            self.generate_repair_report()

            print("\n" + "=" * 50)
            print("🎉 REPAIR PROCESS COMPLETE")
            print(f"📊 Status: {self.report['status'].upper()}")
            print(f"🔌 Plugins Found: {len(self.report['plugins_discovered'])}")
            print(f"🔧 Fixes Applied: {len(self.report['fixes_applied'])}")
            print(f"📋 Report: plugin_repair_report.md")

            return self.report["status"] in ["healthy", "repaired"]

        except Exception as e:
            print(f"\n❌ REPAIR FAILED: {e}")
            return False


def main():
    """Main repair function."""
    repair_tool = PluginSystemRepair()
    success = repair_tool.run_full_repair()

    if success:
        print("\n✅ Plugin system repair completed successfully!")
        print("🚀 You can now restart your application to test the fixes.")
    else:
        print("\n❌ Plugin system repair encountered issues.")
        print("📋 Check the repair report for details.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
