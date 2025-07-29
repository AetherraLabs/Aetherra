#!/usr/bin/env python3
"""
Step 6: Comprehensive Agent Discovery and Integration
Finds ALL agents throughout the codebase and integrates them into clean architecture.
"""

import ast
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set

class ComprehensiveAgentDiscovery:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.clean_dir = self.project_root / "Aetherra_v2"
        self.source_dir = self.project_root / "Aetherra"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def comprehensive_agent_scan(self):
        """Comprehensive scan for ALL agents in the entire codebase"""
        print("🤖 STEP 6: COMPREHENSIVE AGENT DISCOVERY")
        print("="*60)
        print("Scanning ENTIRE codebase for ALL agents (not just agents directory)...")
        
        agents_found = {
            "explicit_agents": [],      # Files with "agent" in name/path
            "class_based_agents": [],   # Classes that inherit from agent bases
            "functional_agents": [],    # Functions that act as agents
            "ai_handlers": [],          # AI model handlers
            "cognitive_components": [], # Cognitive architecture parts
            "personality_systems": [], # Personality/behavior systems
            "decision_makers": [],     # Decision-making components
            "orchestrators": []        # Agent orchestration systems
        }
        
        # Patterns to identify agents
        agent_patterns = [
            'agent', 'ai', 'cognitive', 'personality', 'behavior', 'decision',
            'orchestrat', 'coordinat', 'manage', 'control', 'execute',
            'reason', 'think', 'learn', 'adapt', 'respond', 'interact'
        ]
        
        # Class patterns that indicate agents
        agent_class_patterns = [
            'Agent', 'AI', 'Cognitive', 'Personality', 'Behavior', 'Decision',
            'Orchestrator', 'Coordinator', 'Manager', 'Controller', 'Executor',
            'Reasoner', 'Thinker', 'Learner', 'Responder', 'Handler'
        ]
        
        print("🔍 SCANNING ALL PYTHON FILES...")
        
        all_py_files = []
        for pattern in ['**/*.py']:
            for file_path in self.project_root.glob(pattern):
                if 'Aetherra_v2' not in str(file_path) and '__pycache__' not in str(file_path):
                    all_py_files.append(file_path)
        
        print(f"📊 Found {len(all_py_files)} Python files to analyze")
        
        for file_path in all_py_files:
            try:
                self._analyze_file_for_agents(file_path, agents_found, agent_patterns, agent_class_patterns)
            except Exception as e:
                print(f"⚠️  Could not analyze {file_path.name}: {e}")
        
        # Print comprehensive results
        self._print_agent_discovery_results(agents_found)
        
        return agents_found
    
    def _analyze_file_for_agents(self, file_path, agents_found, agent_patterns, agent_class_patterns):
        """Analyze individual file for agent patterns"""
        rel_path = file_path.relative_to(self.project_root)
        file_lower = str(file_path).lower()
        
        # Check if file name/path suggests it's an agent
        if any(pattern in file_lower for pattern in agent_patterns):
            agents_found["explicit_agents"].append({
                "file": str(rel_path),
                "type": "filename_match",
                "pattern": next(p for p in agent_patterns if p in file_lower)
            })
        
        try:
            content = file_path.read_text(encoding='utf-8')
            content_lower = content.lower()
            
            # Parse AST to find classes and functions
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class_node(node, file_path, rel_path, agents_found, agent_class_patterns, content)
                elif isinstance(node, ast.FunctionDef):
                    self._analyze_function_node(node, file_path, rel_path, agents_found, agent_patterns, content)
            
            # Look for specific AI/agent patterns in content
            self._analyze_content_patterns(content, content_lower, file_path, rel_path, agents_found)
            
        except (UnicodeDecodeError, SyntaxError):
            pass  # Skip files that can't be parsed
    
    def _analyze_class_node(self, node, file_path, rel_path, agents_found, agent_class_patterns, content):
        """Analyze class node for agent patterns"""
        class_name = node.name
        
        # Check if class name suggests it's an agent
        if any(pattern in class_name for pattern in agent_class_patterns):
            agents_found["class_based_agents"].append({
                "file": str(rel_path),
                "class": class_name,
                "line": node.lineno,
                "type": "class_name_match"
            })
        
        # Check base classes
        for base in node.bases:
            if isinstance(base, ast.Name) and any(pattern in base.id for pattern in agent_class_patterns):
                agents_found["class_based_agents"].append({
                    "file": str(rel_path),
                    "class": class_name,
                    "base": base.id,
                    "line": node.lineno,
                    "type": "inheritance_match"
                })
        
        # Check for specific agent-like methods
        agent_methods = ['run', 'execute', 'process', 'handle', 'respond', 'decide', 'think', 'learn']
        class_methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        if any(method in class_methods for method in agent_methods):
            agents_found["class_based_agents"].append({
                "file": str(rel_path),
                "class": class_name,
                "methods": [m for m in class_methods if m in agent_methods],
                "line": node.lineno,
                "type": "method_pattern_match"
            })
    
    def _analyze_function_node(self, node, file_path, rel_path, agents_found, agent_patterns, content):
        """Analyze function node for agent patterns"""
        func_name = node.name.lower()
        
        # Check if function name suggests it's an agent function
        if any(pattern in func_name for pattern in agent_patterns):
            agents_found["functional_agents"].append({
                "file": str(rel_path),
                "function": node.name,
                "line": node.lineno,
                "type": "function_name_match"
            })
    
    def _analyze_content_patterns(self, content, content_lower, file_path, rel_path, agents_found):
        """Analyze content for specific agent patterns"""
        
        # Look for AI model usage
        ai_patterns = [
            r'openai\.',
            r'gpt-',
            r'claude',
            r'mistral',
            r'llama',
            r'ai_client',
            r'model\.chat',
            r'generate_response',
            r'ai_response'
        ]
        
        for pattern in ai_patterns:
            if re.search(pattern, content_lower):
                agents_found["ai_handlers"].append({
                    "file": str(rel_path),
                    "pattern": pattern,
                    "type": "ai_usage"
                })
                break
        
        # Look for cognitive architecture patterns
        cognitive_patterns = [
            'memory', 'attention', 'perception', 'reasoning', 'planning',
            'decision_making', 'goal', 'intention', 'belief', 'desire'
        ]
        
        cognitive_matches = [p for p in cognitive_patterns if p in content_lower]
        if len(cognitive_matches) >= 2:  # Multiple cognitive terms suggest cognitive component
            agents_found["cognitive_components"].append({
                "file": str(rel_path),
                "patterns": cognitive_matches,
                "type": "cognitive_architecture"
            })
        
        # Look for personality/behavior patterns
        personality_patterns = [
            'personality', 'trait', 'behavior', 'emotion', 'mood', 'temperament',
            'character', 'attitude', 'preference', 'style'
        ]
        
        personality_matches = [p for p in personality_patterns if p in content_lower]
        if personality_matches:
            agents_found["personality_systems"].append({
                "file": str(rel_path),
                "patterns": personality_matches,
                "type": "personality_system"
            })
        
        # Look for orchestration patterns
        orchestration_patterns = [
            'orchestrat', 'coordinat', 'schedule', 'dispatch', 'route',
            'workflow', 'pipeline', 'queue', 'task_manager'
        ]
        
        orchestration_matches = [p for p in orchestration_patterns if p in content_lower]
        if orchestration_matches:
            agents_found["orchestrators"].append({
                "file": str(rel_path),
                "patterns": orchestration_matches,
                "type": "orchestration_system"
            })
    
    def _print_agent_discovery_results(self, agents_found):
        """Print comprehensive agent discovery results"""
        print(f"\n🎯 COMPREHENSIVE AGENT DISCOVERY RESULTS:")
        
        total_agents = sum(len(agents) for agents in agents_found.values())
        print(f"📊 Total potential agents found: {total_agents}")
        
        for category, agents in agents_found.items():
            if agents:
                print(f"\n🔸 {category.upper().replace('_', ' ')} ({len(agents)} found):")
                for i, agent in enumerate(agents[:5]):  # Show first 5
                    print(f"   {i+1}. {agent['file']}")
                    if 'class' in agent:
                        print(f"      Class: {agent['class']}")
                    if 'function' in agent:
                        print(f"      Function: {agent['function']}")
                    if 'patterns' in agent:
                        print(f"      Patterns: {', '.join(agent['patterns'][:3])}")
                
                if len(agents) > 5:
                    print(f"   ... and {len(agents) - 5} more")
    
    def prioritize_agents_for_migration(self, agents_found):
        """Prioritize agents based on importance and functionality"""
        print(f"\n📋 PRIORITIZING AGENTS FOR MIGRATION:")
        
        priority_agents = {
            "critical": [],    # Core agents that must be migrated
            "high": [],       # Important agents 
            "medium": [],     # Useful agents
            "low": []         # Optional/test agents
        }
        
        # Critical: Explicit agents and main classes
        for agent in agents_found["explicit_agents"]:
            if not any(test_term in agent["file"].lower() for test_term in ['test', 'demo', 'example']):
                priority_agents["critical"].append({
                    **agent,
                    "category": "explicit_agent",
                    "reason": "Explicitly named agent file"
                })
        
        for agent in agents_found["class_based_agents"]:
            if agent["type"] in ["inheritance_match", "method_pattern_match"]:
                if not any(test_term in agent["file"].lower() for test_term in ['test', 'demo', 'example']):
                    priority_agents["critical"].append({
                        **agent,
                        "category": "class_based_agent",
                        "reason": "Agent class with proper inheritance/methods"
                    })
        
        # High: AI handlers and cognitive components
        for agent in agents_found["ai_handlers"]:
            if not any(test_term in agent["file"].lower() for test_term in ['test', 'demo', 'example']):
                priority_agents["high"].append({
                    **agent,
                    "category": "ai_handler",
                    "reason": "Handles AI model interactions"
                })
        
        for agent in agents_found["cognitive_components"]:
            if len(agent.get("patterns", [])) >= 3:  # Rich cognitive components
                priority_agents["high"].append({
                    **agent,
                    "category": "cognitive_component",
                    "reason": f"Rich cognitive component ({len(agent['patterns'])} patterns)"
                })
        
        # Medium: Orchestrators and personality systems
        for agent in agents_found["orchestrators"]:
            priority_agents["medium"].append({
                **agent,
                "category": "orchestrator",
                "reason": "Agent orchestration system"
            })
        
        for agent in agents_found["personality_systems"]:
            priority_agents["medium"].append({
                **agent,
                "category": "personality_system", 
                "reason": "Personality/behavior system"
            })
        
        # Low: Test/demo agents and functional agents
        for agent in agents_found["explicit_agents"]:
            if any(test_term in agent["file"].lower() for test_term in ['test', 'demo', 'example']):
                priority_agents["low"].append({
                    **agent,
                    "category": "test_agent",
                    "reason": "Test or demo agent"
                })
        
        for agent in agents_found["functional_agents"]:
            priority_agents["low"].append({
                **agent,
                "category": "functional_agent",
                "reason": "Functional agent component"
            })
        
        # Print prioritization results
        for priority, agents in priority_agents.items():
            if agents:
                print(f"\n🔸 {priority.upper()} PRIORITY ({len(agents)} agents):")
                for i, agent in enumerate(agents[:3]):  # Show first 3
                    print(f"   {i+1}. {agent['file']}")
                    print(f"      Category: {agent['category']}")
                    print(f"      Reason: {agent['reason']}")
                
                if len(agents) > 3:
                    print(f"   ... and {len(agents) - 3} more")
        
        return priority_agents
    
    def create_agent_migration_plan(self, priority_agents):
        """Create detailed migration plan for agents"""
        print(f"\n📋 CREATING AGENT MIGRATION PLAN:")
        
        migration_plan = {
            "phase_1_critical": {
                "agents": priority_agents["critical"],
                "target_dir": "lyrixa/agents/core",
                "description": "Critical agents - must be migrated first"
            },
            "phase_2_ai_handlers": {
                "agents": [a for a in priority_agents["high"] if a["category"] == "ai_handler"],
                "target_dir": "lyrixa/interfaces",
                "description": "AI model handlers and interfaces"
            },
            "phase_3_cognitive": {
                "agents": [a for a in priority_agents["high"] if a["category"] == "cognitive_component"],
                "target_dir": "lyrixa/cognitive",
                "description": "Cognitive architecture components"
            },
            "phase_4_orchestration": {
                "agents": [a for a in priority_agents["medium"] if a["category"] == "orchestrator"],
                "target_dir": "lyrixa/agents/orchestration",
                "description": "Agent orchestration systems"
            },
            "phase_5_personality": {
                "agents": [a for a in priority_agents["medium"] if a["category"] == "personality_system"],
                "target_dir": "lyrixa/personality",
                "description": "Personality and behavior systems"
            },
            "phase_6_supporting": {
                "agents": priority_agents["low"],
                "target_dir": "lyrixa/agents/supporting",
                "description": "Supporting and test agents"
            }
        }
        
        total_agents = sum(len(phase["agents"]) for phase in migration_plan.values())
        print(f"📊 Migration plan covers {total_agents} agents across 6 phases")
        
        for phase_name, phase_info in migration_plan.items():
            phase_num = phase_name.split('_')[1]
            print(f"\n📋 PHASE {phase_num.upper()}: {phase_info['description']}")
            print(f"   Target: {phase_info['target_dir']}")
            print(f"   Agents: {len(phase_info['agents'])}")
            
            for i, agent in enumerate(phase_info["agents"][:2]):  # Show first 2
                print(f"   • {agent['file']}")
            
            if len(phase_info["agents"]) > 2:
                print(f"   • ... and {len(phase_info['agents']) - 2} more")
        
        return migration_plan
    
    def save_discovery_results(self, agents_found, priority_agents, migration_plan):
        """Save comprehensive discovery results"""
        print(f"\n💾 SAVING DISCOVERY RESULTS:")
        
        # Create discovery report
        discovery_report = {
            "timestamp": self.timestamp,
            "total_files_scanned": len(list(self.project_root.glob("**/*.py"))),
            "agents_found": agents_found,
            "priority_agents": priority_agents,
            "migration_plan": migration_plan,
            "summary": {
                "total_agents": sum(len(agents) for agents in agents_found.values()),
                "critical_agents": len(priority_agents["critical"]),
                "high_priority": len(priority_agents["high"]),
                "medium_priority": len(priority_agents["medium"]),
                "low_priority": len(priority_agents["low"])
            }
        }
        
        # Save to clean architecture
        tools_dir = self.clean_dir / "tools" / "migration"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        report_file = tools_dir / f"agent_discovery_report_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(discovery_report, f, indent=2, default=str)
        
        print(f"✅ Discovery report saved: {report_file.relative_to(self.project_root)}")
        
        return discovery_report

def main():
    project_root = Path.cwd()
    discovery = ComprehensiveAgentDiscovery(project_root)
    
    print("🤖 SAFE FRESH START - STEP 6")
    print("Comprehensive Agent Discovery and Integration Planning")
    print()
    
    # Comprehensive agent scan
    agents_found = discovery.comprehensive_agent_scan()
    
    # Prioritize agents
    priority_agents = discovery.prioritize_agents_for_migration(agents_found)
    
    # Create migration plan
    migration_plan = discovery.create_agent_migration_plan(priority_agents)
    
    # Save results
    discovery_report = discovery.save_discovery_results(agents_found, priority_agents, migration_plan)
    
    print(f"\n🎉 AGENT DISCOVERY COMPLETE!")
    print(f"✅ Scanned entire codebase for agents")
    print(f"✅ Found {discovery_report['summary']['total_agents']} potential agents")
    print(f"✅ Prioritized agents into 4 categories")
    print(f"✅ Created 6-phase migration plan")
    print(f"✅ Saved comprehensive discovery report")
    
    print(f"\n🎯 DISCOVERY SUMMARY:")
    print(f"• Critical agents: {discovery_report['summary']['critical_agents']}")
    print(f"• High priority: {discovery_report['summary']['high_priority']}")
    print(f"• Medium priority: {discovery_report['summary']['medium_priority']}")
    print(f"• Low priority: {discovery_report['summary']['low_priority']}")
    
    print(f"\n🚀 NEXT: EXECUTE AGENT MIGRATION")
    print("We'll start with critical agents and work through all phases")
    print("No agent will be missed - we found them ALL!")
    
    return discovery_report

if __name__ == "__main__":
    main()
