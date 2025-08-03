#!/usr/bin/env python3
"""
Real Agent Discovery - Find actual agents, not random files/classes
"""

import os
import ast
import json
from pathlib import Path
from typing import List, Dict, Set
import re

class RealAgentDiscovery:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.real_agents = []
        self.excluded_dirs = {
            'unused_conservative', 'Aetherra_Archive_20250726_224039',
            '__pycache__', '.git', 'node_modules', '.vscode',
            'Lib', 'site-packages'  # Exclude Python library files
        }

    def find_real_agents(self):
        """Find actual agents, not every file with 'agent' in the name"""
        print("🔍 Discovering REAL agents...")

        # First, look for agent directories and dedicated agent files
        self._find_agent_directories()
        self._find_agent_files()
        self._find_agent_classes()

        # Generate report
        self._generate_report()

    def _find_agent_directories(self):
        """Find directories that clearly contain agents"""
        print("📁 Checking for agent directories...")

        for root, dirs, files in os.walk(self.workspace_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            root_path = Path(root)
            dir_name = root_path.name.lower()

            # Look for directories named 'agents', 'agent', etc.
            if dir_name in ['agents', 'agent']:
                print(f"📂 Found agent directory: {root_path}")
                self._analyze_agent_directory(root_path)

    def _analyze_agent_directory(self, agent_dir: Path):
        """Analyze a directory that should contain agents"""
        for file_path in agent_dir.rglob("*.py"):
            if self._is_excluded_path(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse the AST to find classes
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self._analyze_potential_agent_class(file_path, node, content)

            except Exception as e:
                print(f"[WARN] Error reading {file_path}: {e}")

    def _find_agent_files(self):
        """Find files that are clearly agents based on naming and content"""
        print("📄 Checking for agent files...")

        # Look for files with clear agent naming patterns
        agent_patterns = [
            r'.*_agent\.py$',
            r'^agent_.*\.py$',
            r'.*agent.*\.py$'
        ]

        for pattern in agent_patterns:
            for file_path in self.workspace_root.rglob("*.py"):
                if self._is_excluded_path(file_path):
                    continue

                if re.match(pattern, file_path.name, re.IGNORECASE):
                    # But don't include test files or library files
                    if self._is_likely_real_agent_file(file_path):
                        self._analyze_agent_file(file_path)

    def _find_agent_classes(self):
        """Find classes that are clearly agents"""
        print("🏗️ Checking for agent classes...")

        # Search all Python files for classes with agent-like characteristics
        for file_path in self.workspace_root.rglob("*.py"):
            if self._is_excluded_path(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse the AST to find classes
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if self._is_likely_agent_class(node, content):
                            self._analyze_potential_agent_class(file_path, node, content)

            except Exception as e:
                continue  # Skip files with parsing errors

    def _is_excluded_path(self, file_path: Path) -> bool:
        """Check if path should be excluded"""
        path_str = str(file_path)
        for excluded in self.excluded_dirs:
            if excluded in path_str:
                return True
        return False

    def _is_likely_real_agent_file(self, file_path: Path) -> bool:
        """Check if this is likely a real agent file, not a test or library"""
        name = file_path.name.lower()

        # Exclude test files
        if 'test_' in name or '_test' in name or 'tests' in str(file_path):
            return False

        # Exclude demo files (unless they're actual agent demos)
        if 'demo_' in name and 'agent' not in name:
            return False

        # Exclude library/torch files
        if 'torch' in str(file_path) or 'site-packages' in str(file_path):
            return False

        return True

    def _is_likely_agent_class(self, node: ast.ClassDef, content: str) -> bool:
        """Check if a class is likely an actual agent"""
        class_name = node.name.lower()

        # Look for agent-like class names
        agent_indicators = [
            'agent', 'lyrixa', 'aetherra', 'cognitive', 'personality',
            'orchestrator', 'coordinator', 'handler'
        ]

        # But exclude manager/memory classes that aren't agents
        non_agent_patterns = [
            'manager', 'memory', 'database', 'connection', 'adapter',
            'bridge', 'client', 'server', 'config', 'settings'
        ]

        # Check class name
        has_agent_indicator = any(indicator in class_name for indicator in agent_indicators)
        has_non_agent_pattern = any(pattern in class_name for pattern in non_agent_patterns)

        # If it has non-agent patterns, it's probably not an agent
        if has_non_agent_pattern and not has_agent_indicator:
            return False

        # Look for agent-like methods or attributes
        agent_methods = [
            'think', 'reason', 'decide', 'act', 'process', 'respond',
            'handle_message', 'execute', 'run', 'start', 'stop'
        ]

        has_agent_methods = False
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_name = child.name.lower()
                if any(agent_method in method_name for agent_method in agent_methods):
                    has_agent_methods = True
                    break

        # Look for agent-like imports or inheritance
        agent_inheritance = ['agent', 'lyrixa', 'aetherra', 'cognitive']
        has_agent_inheritance = False

        for base in node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id.lower()
                if any(indicator in base_name for indicator in agent_inheritance):
                    has_agent_inheritance = True
                    break

        # Decision logic
        if has_agent_indicator and (has_agent_methods or has_agent_inheritance):
            return True

        if class_name in ['lyrixa', 'aetherra'] or 'agent' in class_name:
            return True

        return False

    def _analyze_agent_file(self, file_path: Path):
        """Analyze a file that might contain agents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the AST to find classes and functions
            tree = ast.parse(content)

            agents_in_file = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    agents_in_file.append({
                        'type': 'class',
                        'name': node.name,
                        'line': node.lineno
                    })
                elif isinstance(node, ast.FunctionDef) and node.name.startswith('agent_'):
                    agents_in_file.append({
                        'type': 'function',
                        'name': node.name,
                        'line': node.lineno
                    })

            if agents_in_file:
                self.real_agents.append({
                    'file': str(file_path.relative_to(self.workspace_root)),
                    'category': 'agent_file',
                    'agents': agents_in_file,
                    'description': f"Agent file containing {len(agents_in_file)} agents"
                })

        except Exception as e:
            print(f"[WARN] Error analyzing {file_path}: {e}")

    def _analyze_potential_agent_class(self, file_path: Path, node: ast.ClassDef, content: str):
        """Analyze a class that might be an agent"""
        # Get methods
        methods = []
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                methods.append(child.name)

        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}" if hasattr(base.value, 'id') else str(base.attr))

        # Determine category
        class_name = node.name.lower()
        if 'lyrixa' in class_name:
            category = 'lyrixa_agent'
        elif 'aetherra' in class_name:
            category = 'aetherra_agent'
        elif 'cognitive' in class_name:
            category = 'cognitive_agent'
        elif 'personality' in class_name:
            category = 'personality_agent'
        elif 'orchestrator' in class_name or 'coordinator' in class_name:
            category = 'orchestrator_agent'
        else:
            category = 'general_agent'

        self.real_agents.append({
            'file': str(file_path.relative_to(self.workspace_root)),
            'category': category,
            'class_name': node.name,
            'line': node.lineno,
            'methods': methods[:10],  # First 10 methods
            'base_classes': bases,
            'description': f"Agent class with {len(methods)} methods"
        })

    def _generate_report(self):
        """Generate the discovery report"""
        # Group by category
        by_category = {}
        for agent in self.real_agents:
            category = agent['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(agent)

        report = {
            'timestamp': '20250726_real_discovery',
            'total_real_agents': len(self.real_agents),
            'categories': by_category,
            'summary': {
                category: len(agents)
                for category, agents in by_category.items()
            }
        }

        # Save report
        report_path = self.workspace_root / "real_agent_discovery_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("🎯 REAL AGENT DISCOVERY RESULTS")
        print("="*60)
        print(f"📊 Total Real Agents Found: {len(self.real_agents)}")
        print("\n📋 By Category:")
        for category, agents in by_category.items():
            print(f"  {category}: {len(agents)} agents")

        print(f"\n📄 Full report saved to: {report_path}")

        # Show some examples
        if self.real_agents:
            print("\n🔍 Sample Real Agents Found:")
            for i, agent in enumerate(self.real_agents[:5]):
                print(f"  {i+1}. {agent.get('class_name', agent['file'])} ({agent['category']})")
                print(f"     File: {agent['file']}")

        return report

def main():
    """Run real agent discovery"""
    workspace = r"c:\Users\enigm\Desktop\Aetherra Project"

    print("🚀 Starting REAL Agent Discovery...")
    print(f"📁 Workspace: {workspace}")

    discovery = RealAgentDiscovery(workspace)
    report = discovery.find_real_agents()

    print("\n✅ Real agent discovery complete!")

    if report['total_real_agents'] == 0:
        print("[WARN] No real agents found. This might indicate:")
        print("  1. Agents are named differently than expected")
        print("  2. Agents are in unexpected locations")
        print("  3. The codebase uses a different agent architecture")
        print("\n💡 Recommendation: Manual inspection of key files")

if __name__ == "__main__":
    main()
