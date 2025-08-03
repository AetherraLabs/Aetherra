#!/usr/bin/env python3
"""
🕵️ AGENT DISCOVERY & INTEGRATION SYSTEM
========================================

Comprehensive discovery and integration of ALL Aetherra agents and components.
This script will find EVERY agent, chat feature, and intelligence component
to ensure nothing is missed in the web interface integration.
"""

import os
import sys
import json
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComponentInfo:
    """Information about discovered components"""
    name: str
    module_path: str
    class_name: str
    component_type: str
    status: str
    capabilities: List[str]
    dependencies: List[str]
    error_message: Optional[str] = None

class AetherraComponentDiscovery:
    """Comprehensive component discovery and integration system"""

    def __init__(self):
        self.project_root = project_root
        self.discovered_components = {}
        self.loaded_components = {}
        self.errors = []

    def discover_all_components(self) -> Dict[str, List[ComponentInfo]]:
        """Discover ALL available components in the Aetherra project"""
        logger.info("🔍 Starting comprehensive component discovery...")

        components = {
            'agents': [],
            'ethics_agents': [],
            'intelligence_systems': [],
            'memory_systems': [],
            'conversation_managers': [],
            'gui_components': [],
            'other_components': []
        }

        # Discover agents
        components['agents'] = self._discover_agents()
        components['ethics_agents'] = self._discover_ethics_agents()
        components['intelligence_systems'] = self._discover_intelligence_systems()
        components['memory_systems'] = self._discover_memory_systems()
        components['conversation_managers'] = self._discover_conversation_managers()
        components['gui_components'] = self._discover_gui_components()
        components['other_components'] = self._discover_other_components()

        self.discovered_components = components
        return components

    def _discover_agents(self) -> List[ComponentInfo]:
        """Discover all agent components"""
        logger.info("🤖 Discovering agents...")
        agents = []

        # Search in agent directories
        agent_dirs = [
            self.project_root / "Aetherra" / "lyrixa" / "agents",
            self.project_root / "Aetherra" / "agents",
            self.project_root / "agents"
        ]

        for agent_dir in agent_dirs:
            if agent_dir.exists():
                agents.extend(self._scan_directory_for_classes(
                    agent_dir,
                    'agents',
                    ['Agent', 'AI', 'Bot']
                ))

        return agents

    def _discover_ethics_agents(self) -> List[ComponentInfo]:
        """Discover all ethics agent components"""
        logger.info("🛡️ Discovering ethics agents...")
        ethics_agents = []

        # Search in ethics directories
        ethics_dirs = [
            self.project_root / "Aetherra" / "lyrixa" / "ethics_agent",
            self.project_root / "Aetherra" / "ethics",
            self.project_root / "ethics"
        ]

        for ethics_dir in ethics_dirs:
            if ethics_dir.exists():
                ethics_agents.extend(self._scan_directory_for_classes(
                    ethics_dir,
                    'ethics_agents',
                    ['Engine', 'Agent', 'Detector', 'Reasoning', 'Alignment']
                ))

        return ethics_agents

    def _discover_intelligence_systems(self) -> List[ComponentInfo]:
        """Discover intelligence system components"""
        logger.info("🧠 Discovering intelligence systems...")
        intelligence = []

        # Search for intelligence systems
        intelligence_dirs = [
            self.project_root / "Aetherra" / "lyrixa" / "intelligence",
            self.project_root / "Aetherra" / "intelligence",
            self.project_root / "Aetherra" / "lyrixa",
            self.project_root / "intelligence"
        ]

        for intel_dir in intelligence_dirs:
            if intel_dir.exists():
                intelligence.extend(self._scan_directory_for_classes(
                    intel_dir,
                    'intelligence_systems',
                    ['Intelligence', 'Stack', 'System', 'Brain', 'Cognitive']
                ))

        return intelligence

    def _discover_memory_systems(self) -> List[ComponentInfo]:
        """Discover memory system components"""
        logger.info("💾 Discovering memory systems...")
        memory = []

        # Search for memory systems
        memory_dirs = [
            self.project_root / "Aetherra" / "lyrixa" / "memory",
            self.project_root / "Aetherra" / "memory",
            self.project_root / "memory",
            self.project_root / "Aetherra" / "core" / "memory"
        ]

        for mem_dir in memory_dirs:
            if mem_dir.exists():
                memory.extend(self._scan_directory_for_classes(
                    mem_dir,
                    'memory_systems',
                    ['Memory', 'Engine', 'Core', 'System', 'Storage']
                ))

        return memory

    def _discover_conversation_managers(self) -> List[ComponentInfo]:
        """Discover conversation management components"""
        logger.info("💬 Discovering conversation managers...")
        conversation = []

        # Search for conversation systems
        conv_patterns = [
            'conversation_manager.py',
            'chat_manager.py',
            'conversation.py',
            'chat.py'
        ]

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if any(pattern in file for pattern in conv_patterns):
                    file_path = Path(root) / file
                    conversation.extend(self._scan_file_for_classes(
                        file_path,
                        'conversation_managers',
                        ['Manager', 'Handler', 'Engine', 'System']
                    ))

        return conversation

    def _discover_gui_components(self) -> List[ComponentInfo]:
        """Discover GUI components"""
        logger.info("🖥️ Discovering GUI components...")
        gui = []

        # Search for GUI systems
        gui_dirs = [
            self.project_root / "Aetherra" / "lyrixa" / "gui",
            self.project_root / "Aetherra" / "gui",
            self.project_root / "gui",
            self.project_root / "interface"
        ]

        for gui_dir in gui_dirs:
            if gui_dir.exists():
                gui.extend(self._scan_directory_for_classes(
                    gui_dir,
                    'gui_components',
                    ['Interface', 'GUI', 'Window', 'Controller', 'Manager']
                ))

        return gui

    def _discover_other_components(self) -> List[ComponentInfo]:
        """Discover other important components"""
        logger.info("[TOOL] Discovering other components...")
        other = []

        # Search for other important components
        other_patterns = [
            'runtime', 'engine', 'manager', 'system', 'core',
            'bridge', 'integration', 'orchestrator', 'coordinator'
        ]

        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py') and any(pattern in file.lower() for pattern in other_patterns):
                    file_path = Path(root) / file
                    if self._is_in_aetherra_path(file_path):
                        other.extend(self._scan_file_for_classes(
                            file_path,
                            'other_components',
                            other_patterns
                        ))

        return other

    def _scan_directory_for_classes(self, directory: Path, component_type: str, keywords: List[str]) -> List[ComponentInfo]:
        """Scan a directory for classes matching keywords"""
        components = []

        for file_path in directory.rglob("*.py"):
            if file_path.name.startswith('__'):
                continue
            components.extend(self._scan_file_for_classes(file_path, component_type, keywords))

        return components

    def _scan_file_for_classes(self, file_path: Path, component_type: str, keywords: List[str]) -> List[ComponentInfo]:
        """Scan a file for classes matching keywords"""
        components = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for class definitions
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('class ') and ':' in line:
                    class_def = line.split('class ')[1].split(':')[0].split('(')[0].strip()

                    # Check if class matches keywords
                    if any(keyword.lower() in class_def.lower() for keyword in keywords):
                        # Extract module path
                        rel_path = file_path.relative_to(self.project_root)
                        module_path = str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')

                        # Extract capabilities from docstring or comments
                        capabilities = self._extract_capabilities(content, class_def)

                        component = ComponentInfo(
                            name=class_def,
                            module_path=module_path,
                            class_name=class_def,
                            component_type=component_type,
                            status='discovered',
                            capabilities=capabilities,
                            dependencies=self._extract_dependencies(content)
                        )
                        components.append(component)

        except Exception as e:
            logger.warning(f"[WARN] Error scanning {file_path}: {e}")

        return components

    def _extract_capabilities(self, content: str, class_name: str) -> List[str]:
        """Extract capabilities from class docstring or comments"""
        capabilities = []

        # Look for docstring after class definition
        class_section = content.split(f'class {class_name}')[1] if f'class {class_name}' in content else ""

        # Extract from docstring
        if '"""' in class_section:
            docstring = class_section.split('"""')[1] if '"""' in class_section else ""
            capability_keywords = [
                'process', 'analyze', 'manage', 'handle', 'execute',
                'monitor', 'track', 'detect', 'reason', 'align',
                'memory', 'conversation', 'chat', 'intelligence'
            ]
            for keyword in capability_keywords:
                if keyword in docstring.lower():
                    capabilities.append(keyword)

        return list(set(capabilities)) if capabilities else ['general']

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from imports"""
        dependencies = []
        lines = content.split('\n')

        for line in lines[:50]:  # Check first 50 lines for imports
            line = line.strip()
            if line.startswith('from ') or line.startswith('import '):
                if 'aetherra' in line.lower() or 'lyrixa' in line.lower():
                    dependencies.append(line)

        return dependencies

    def _is_in_aetherra_path(self, file_path: Path) -> bool:
        """Check if file is in Aetherra project path"""
        path_str = str(file_path).lower()
        return 'aetherra' in path_str or 'lyrixa' in path_str

    def load_components(self) -> Dict[str, Any]:
        """Attempt to load all discovered components"""
        logger.info("🔄 Loading discovered components...")

        loaded = {
            'agents': {},
            'ethics_agents': {},
            'intelligence_systems': {},
            'memory_systems': {},
            'conversation_managers': {},
            'gui_components': {},
            'other_components': {}
        }

        for category, components in self.discovered_components.items():
            for component in components:
                try:
                    # Attempt to import and instantiate
                    module = importlib.import_module(component.module_path)
                    class_obj = getattr(module, component.class_name)

                    # Try to instantiate (some may fail due to dependencies)
                    try:
                        instance = class_obj()
                        loaded[category][component.name.lower()] = instance
                        component.status = 'loaded'
                        logger.info(f"✅ Loaded {component.name}")
                    except Exception as init_error:
                        # Mark as available but not instantiated
                        loaded[category][component.name.lower()] = class_obj
                        component.status = 'available'
                        component.error_message = str(init_error)
                        logger.warning(f"[WARN] {component.name} available but not instantiated: {init_error}")

                except Exception as e:
                    component.status = 'error'
                    component.error_message = str(e)
                    logger.error(f"❌ Failed to load {component.name}: {e}")

        self.loaded_components = loaded
        return loaded

    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        report = []
        report.append("🔍 AETHERRA COMPONENT INTEGRATION REPORT")
        report.append("=" * 50)
        report.append("")

        total_discovered = sum(len(components) for components in self.discovered_components.values())
        total_loaded = sum(len(components) for components in self.loaded_components.values())

        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Components Discovered: {total_discovered}")
        report.append(f"   Total Components Loaded: {total_loaded}")
        report.append("")

        for category, components in self.discovered_components.items():
            if components:
                report.append(f"[TOOL] {category.upper().replace('_', ' ')}:")
                for component in components:
                    status_icon = "✅" if component.status == "loaded" else "[WARN]" if component.status == "available" else "❌"
                    report.append(f"   {status_icon} {component.name} ({component.status})")
                    if component.capabilities:
                        report.append(f"      Capabilities: {', '.join(component.capabilities)}")
                    if component.error_message and len(component.error_message) < 100:
                        report.append(f"      Error: {component.error_message}")
                report.append("")

        return "\n".join(report)

    def save_discovery_results(self, filename: str = "component_discovery_results.json"):
        """Save discovery results to JSON file"""
        results = {
            'discovery_timestamp': str(Path().absolute()),
            'project_root': str(self.project_root),
            'discovered_components': {},
            'loaded_components_count': {},
            'errors': self.errors
        }

        # Convert ComponentInfo objects to dictionaries
        for category, components in self.discovered_components.items():
            results['discovered_components'][category] = []
            for component in components:
                results['discovered_components'][category].append({
                    'name': component.name,
                    'module_path': component.module_path,
                    'class_name': component.class_name,
                    'component_type': component.component_type,
                    'status': component.status,
                    'capabilities': component.capabilities,
                    'dependencies': component.dependencies,
                    'error_message': component.error_message
                })

        # Count loaded components
        for category, components in self.loaded_components.items():
            results['loaded_components_count'][category] = len(components)

        # Save to file
        with open(self.project_root / filename, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"💾 Discovery results saved to {filename}")

def main():
    """Main discovery and integration function"""
    print("🕵️ AETHERRA AGENT DISCOVERY & INTEGRATION")
    print("=" * 50)

    discovery = AetherraComponentDiscovery()

    # Discover all components
    discovered = discovery.discover_all_components()

    # Attempt to load components
    loaded = discovery.load_components()

    # Generate and display report
    report = discovery.generate_integration_report()
    print(report)

    # Save results
    discovery.save_discovery_results()

    print("\n🎯 INTEGRATION RECOMMENDATIONS:")
    print("=" * 35)
    print("1. Use discovered agents in web interface agent management")
    print("2. Wire ethics components into decision-making systems")
    print("3. Connect memory systems to conversation manager")
    print("4. Integrate intelligence systems for enhanced capabilities")
    print("5. Review 'available' components for potential dependency fixes")

    return discovery

if __name__ == "__main__":
    discovery_system = main()
