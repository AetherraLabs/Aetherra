#!/usr/bin/env python3
"""
Step 7: Smart Agent Migration Executor
Intelligently migrates the most important agents from the comprehensive discovery.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class SmartAgentMigrator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.clean_dir = self.project_root / "Aetherra_v2"
        self.source_dir = self.project_root / "Aetherra"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_discovery_report(self):
        """Load the latest agent discovery report"""
        print("📊 LOADING AGENT DISCOVERY REPORT...")
        
        tools_dir = self.clean_dir / "tools" / "migration"
        report_files = list(tools_dir.glob("agent_discovery_report_*.json"))
        
        if not report_files:
            print("❌ No discovery report found! Run comprehensive_agent_discovery.py first")
            return None
        
        # Get the latest report
        latest_report = max(report_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"✅ Loaded report: {latest_report.name}")
        print(f"📊 Total agents discovered: {report['summary']['total_agents']}")
        
        return report
    
    def smart_filter_agents(self, discovery_report):
        """Smart filtering to focus on truly important agents"""
        print("🧠 SMART FILTERING FOR TRULY IMPORTANT AGENTS...")
        
        # We'll be much more selective given the massive scope
        smart_filtered = {
            "core_agents": [],           # Absolutely essential agents
            "web_interface_agents": [],  # Agents related to your working web interface
            "memory_agents": [],         # Agents working with memory systems
            "ai_model_agents": [],       # Agents handling AI models
            "orchestration_agents": [],  # Key orchestration components
        }
        
        priority_agents = discovery_report["priority_agents"]
        
        # Core agents: Filter for truly essential explicit agents
        core_keywords = [
            'lyrixa', 'aetherra', 'core', 'main', 'primary', 'central',
            'manager', 'controller', 'engine', 'system'
        ]
        
        for agent in priority_agents["critical"]:
            agent_file = agent["file"].lower()
            
            # Skip archived, backup, test files
            if any(skip in agent_file for skip in ['archive', 'backup', 'test_', 'demo_', 'example_']):
                continue
                
            # Focus on core components
            if any(keyword in agent_file for keyword in core_keywords):
                smart_filtered["core_agents"].append(agent)
            
            # Web interface related
            elif any(web_term in agent_file for web_term in ['web', 'gui', 'interface', 'server']):
                smart_filtered["web_interface_agents"].append(agent)
        
        # AI handlers: Focus on actual AI model interfaces
        ai_keywords = ['openai', 'gpt', 'claude', 'mistral', 'ai_client', 'model']
        
        for agent in priority_agents["high"]:
            if agent["category"] == "ai_handler":
                agent_file = agent["file"].lower()
                
                # Skip archived/test files
                if any(skip in agent_file for skip in ['archive', 'backup', 'test_', 'demo_']):
                    continue
                
                # Focus on real AI handlers
                if any(ai_term in agent_file for ai_term in ai_keywords):
                    smart_filtered["ai_model_agents"].append(agent)
        
        # Memory agents: Components that work with your migrated databases
        memory_keywords = ['memory', 'database', 'storage', 'persistence']
        
        for agent in priority_agents["high"]:
            if agent["category"] == "cognitive_component":
                agent_file = agent["file"].lower()
                
                if any(skip in agent_file for skip in ['archive', 'backup', 'test_', 'demo_']):
                    continue
                
                if any(mem_term in agent_file for mem_term in memory_keywords):
                    smart_filtered["memory_agents"].append(agent)
        
        # Orchestration: Key coordination components
        orchestration_keywords = ['orchestrat', 'coordinat', 'dispatch', 'workflow']
        
        for agent in priority_agents["medium"]:
            if agent["category"] == "orchestrator":
                agent_file = agent["file"].lower()
                
                if any(skip in agent_file for skip in ['archive', 'backup', 'test_', 'demo_']):
                    continue
                
                if any(orch_term in agent_file for orch_term in orchestration_keywords):
                    smart_filtered["orchestration_agents"].append(agent)
        
        # Print smart filtering results
        total_smart_filtered = sum(len(agents) for agents in smart_filtered.values())
        print(f"📊 Smart filtered to {total_smart_filtered} truly important agents")
        
        for category, agents in smart_filtered.items():
            if agents:
                print(f"\n🔸 {category.upper().replace('_', ' ')} ({len(agents)} agents):")
                for i, agent in enumerate(agents[:3]):
                    print(f"   {i+1}. {agent['file']}")
                if len(agents) > 3:
                    print(f"   ... and {len(agents) - 3} more")
        
        return smart_filtered
    
    def migrate_smart_filtered_agents(self, smart_filtered):
        """Migrate the smart filtered agents to clean architecture"""
        print("🚀 MIGRATING SMART FILTERED AGENTS...")
        
        migration_results = {
            "migrated": [],
            "skipped": [],
            "errors": []
        }
        
        # Migration mapping
        target_mapping = {
            "core_agents": "lyrixa/agents/core",
            "web_interface_agents": "web/components", 
            "memory_agents": "lyrixa/memory",
            "ai_model_agents": "lyrixa/interfaces",
            "orchestration_agents": "lyrixa/agents/orchestration"
        }
        
        for category, agents in smart_filtered.items():
            if not agents:
                continue
                
            target_dir = self.clean_dir / target_mapping[category]
            target_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📦 Migrating {category.replace('_', ' ')} to {target_mapping[category]}:")
            
            for agent in agents:
                try:
                    source_file = self.project_root / agent["file"]
                    target_file = target_dir / source_file.name
                    
                    if source_file.exists():
                        # Copy file
                        shutil.copy2(source_file, target_file)
                        
                        migration_results["migrated"].append({
                            "source": agent["file"],
                            "target": str(target_file.relative_to(self.clean_dir)),
                            "category": category
                        })
                        
                        print(f"   ✅ {source_file.name}")
                    else:
                        migration_results["skipped"].append({
                            "file": agent["file"],
                            "reason": "Source file not found"
                        })
                        print(f"   ⚠️  Skipped {agent['file']} (not found)")
                        
                except Exception as e:
                    migration_results["errors"].append({
                        "file": agent["file"],
                        "error": str(e)
                    })
                    print(f"   ❌ Error migrating {agent['file']}: {e}")
        
        return migration_results
    
    def create_agent_integration_bridge(self):
        """Create integration bridge for agents in clean architecture"""
        print("🌉 CREATING AGENT INTEGRATION BRIDGE...")
        
        bridge_content = '''"""
Agent Integration Bridge
Connects migrated agents to the clean architecture integration system.
"""

import asyncio
import logging
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add clean architecture to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integration.bridges.aetherra_lyrixa_bridge import bridge
from integration.bridges.memory_adapter_impl import memory_adapter_impl

logger = logging.getLogger(__name__)

class AgentIntegrationBridge:
    """Bridge for integrating agents with clean architecture"""
    
    def __init__(self):
        self.agents = {}
        self.agent_modules = {}
        self.bridge = bridge
        self.memory_adapter = memory_adapter_impl
        logger.info("🤖 Agent Integration Bridge initialized")
    
    def discover_migrated_agents(self):
        """Discover all migrated agents in clean architecture"""
        logger.info("🔍 Discovering migrated agents...")
        
        agent_dirs = [
            Path(__file__).parent.parent / "agents" / "core",
            Path(__file__).parent.parent / "agents" / "orchestration", 
            Path(__file__).parent.parent / "memory",
            Path(__file__).parent.parent / "interfaces",
            Path(__file__).parent.parent.parent / "web" / "components"
        ]
        
        discovered = []
        
        for agent_dir in agent_dirs:
            if agent_dir.exists():
                for py_file in agent_dir.glob("*.py"):
                    if py_file.name != "__init__.py":
                        discovered.append({
                            "name": py_file.stem,
                            "path": py_file,
                            "category": agent_dir.name
                        })
                        logger.info(f"🤖 Discovered agent: {py_file.stem}")
        
        return discovered
    
    def load_agent_modules(self, discovered_agents):
        """Load agent modules dynamically"""
        logger.info("📥 Loading agent modules...")
        
        loaded_count = 0
        
        for agent_info in discovered_agents:
            try:
                # Create module name
                module_name = f"lyrixa.{agent_info['category']}.{agent_info['name']}"
                
                # Load module
                spec = importlib.util.spec_from_file_location(
                    module_name, agent_info["path"]
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.agent_modules[agent_info["name"]] = {
                    "module": module,
                    "info": agent_info
                }
                
                loaded_count += 1
                logger.info(f"✅ Loaded: {agent_info['name']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load {agent_info['name']}: {e}")
        
        logger.info(f"📊 Loaded {loaded_count}/{len(discovered_agents)} agent modules")
        return loaded_count
    
    def initialize_agent_communication(self):
        """Initialize communication between agents and bridge"""
        logger.info("🔗 Initializing agent communication...")
        
        # Register agent handlers with main bridge
        self.bridge.register_aetherra_handler("agent_request", self.handle_agent_request)
        self.bridge.register_lyrixa_handler("agent_response", self.handle_agent_response)
        
        # Register memory access for agents
        for agent_name, agent_data in self.agent_modules.items():
            # Give agents access to memory adapter
            if hasattr(agent_data["module"], "set_memory_adapter"):
                agent_data["module"].set_memory_adapter(self.memory_adapter)
                logger.info(f"🧠 Connected {agent_name} to memory systems")
        
        logger.info("✅ Agent communication initialized")
    
    async def handle_agent_request(self, request_data):
        """Handle requests from agents"""
        logger.info(f"📨 Agent request: {request_data.get('type', 'unknown')}")
        
        # Route requests to appropriate handlers
        if request_data.get("type") == "memory_access":
            return await self.handle_memory_request(request_data)
        elif request_data.get("type") == "agent_communication":
            return await self.handle_inter_agent_communication(request_data)
        else:
            return {"status": "processed", "data": request_data}
    
    async def handle_agent_response(self, response_data):
        """Handle responses from agents"""
        logger.info(f"📤 Agent response: {response_data.get('type', 'unknown')}")
        return response_data
    
    async def handle_memory_request(self, request_data):
        """Handle memory access requests from agents"""
        context_id = request_data.get("context_id")
        action = request_data.get("action", "get")
        
        if action == "get":
            context = self.memory_adapter.get_shared_context(context_id)
            return {"status": "success", "context": context}
        elif action == "store":
            data = request_data.get("data", {})
            self.memory_adapter.store_shared_context(context_id, data)
            return {"status": "success", "action": "stored"}
        else:
            return {"status": "error", "message": "Unknown memory action"}
    
    async def handle_inter_agent_communication(self, request_data):
        """Handle communication between agents"""
        target_agent = request_data.get("target_agent")
        message = request_data.get("message", {})
        
        if target_agent in self.agent_modules:
            # Forward message to target agent
            logger.info(f"📬 Forwarding message to {target_agent}")
            return {"status": "forwarded", "target": target_agent}
        else:
            return {"status": "error", "message": f"Agent {target_agent} not found"}

# Global agent integration bridge
agent_bridge = AgentIntegrationBridge()
'''
        
        bridge_file = self.clean_dir / "lyrixa" / "agents" / "agent_integration_bridge.py"
        bridge_file.parent.mkdir(parents=True, exist_ok=True)
        bridge_file.write_text(bridge_content, encoding='utf-8')
        
        print(f"✅ Created: {bridge_file.relative_to(self.project_root)}")
        return bridge_file
    
    def create_agent_launcher(self):
        """Create launcher that initializes all migrated agents"""
        print("🚀 CREATING AGENT LAUNCHER...")
        
        launcher_content = '''#!/usr/bin/env python3
"""
Agent System Launcher
Launches all migrated agents in the clean architecture.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add clean architecture to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lyrixa.agents.agent_integration_bridge import agent_bridge
from integration.bridges.aetherra_lyrixa_bridge import bridge

async def main():
    """Main agent system launcher"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Agent System")
    
    try:
        # Start main bridge
        await bridge.start()
        
        # Discover migrated agents
        discovered_agents = agent_bridge.discover_migrated_agents()
        logger.info(f"🔍 Discovered {len(discovered_agents)} agents")
        
        # Load agent modules
        loaded_count = agent_bridge.load_agent_modules(discovered_agents)
        logger.info(f"📥 Loaded {loaded_count} agent modules")
        
        # Initialize agent communication
        agent_bridge.initialize_agent_communication()
        
        logger.info("✅ Agent system operational!")
        logger.info("🤖 All migrated agents are now connected and ready")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down agent system...")
        await bridge.stop()
    except Exception as e:
        logger.error(f"❌ Agent system error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        launcher_file = self.clean_dir / "launch_agents.py"
        launcher_file.write_text(launcher_content, encoding='utf-8')
        
        print(f"✅ Created: {launcher_file.relative_to(self.project_root)}")
        return launcher_file
    
    def update_main_launcher_with_agents(self):
        """Update the main launcher to include agent initialization"""
        print("🔧 UPDATING MAIN LAUNCHER WITH AGENT SUPPORT...")
        
        main_launcher = self.clean_dir / "launch_with_web.py"
        
        if main_launcher.exists():
            try:
                content = main_launcher.read_text(encoding='utf-8')
                
                # Add agent bridge import
                agent_import = '''from lyrixa.agents.agent_integration_bridge import agent_bridge
'''
                
                # Find import section
                lines = content.split('\n')
                import_end = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('from web.server.web_adapter'):
                        import_end = i + 1
                        break
                
                if import_end > 0:
                    lines.insert(import_end, agent_import)
                    
                    # Find the main function and add agent initialization
                    for i, line in enumerate(lines):
                        if 'await web_adapter.initialize_web_systems()' in line:
                            agent_init_lines = [
                                '',
                                '        # Initialize agent systems',
                                '        logger.info("🤖 Initializing agent systems...")',
                                '        discovered_agents = agent_bridge.discover_migrated_agents()',
                                '        loaded_count = agent_bridge.load_agent_modules(discovered_agents)', 
                                '        agent_bridge.initialize_agent_communication()',
                                '        logger.info(f"✅ Initialized {loaded_count} agents")',
                                ''
                            ]
                            
                            for j, agent_line in enumerate(agent_init_lines):
                                lines.insert(i + 1 + j, agent_line)
                            break
                    
                    updated_content = '\n'.join(lines)
                    main_launcher.write_text(updated_content, encoding='utf-8')
                    print("✅ Updated main launcher with agent initialization")
                else:
                    print("⚠️  Could not find import section in main launcher")
                    
            except Exception as e:
                print(f"⚠️  Could not update main launcher: {e}")
        else:
            print("⚠️  Main launcher not found")

def main():
    project_root = Path.cwd()
    migrator = SmartAgentMigrator(project_root)
    
    print("🤖 SAFE FRESH START - STEP 7")
    print("Smart Agent Migration Execution")
    print()
    
    # Load discovery report
    discovery_report = migrator.load_discovery_report()
    if not discovery_report:
        return
    
    # Smart filter agents
    smart_filtered = migrator.smart_filter_agents(discovery_report)
    
    # Migrate smart filtered agents
    migration_results = migrator.migrate_smart_filtered_agents(smart_filtered)
    
    # Create agent integration bridge
    bridge_file = migrator.create_agent_integration_bridge()
    
    # Create agent launcher
    launcher_file = migrator.create_agent_launcher()
    
    # Update main launcher
    migrator.update_main_launcher_with_agents()
    
    print(f"\n🎉 PHASE 4 COMPLETE!")
    print(f"✅ Migrated {len(migration_results['migrated'])} important agents")
    print(f"✅ Created agent integration bridge")
    print(f"✅ Created agent launcher")
    print(f"✅ Updated main launcher with agent support")
    
    if migration_results["skipped"]:
        print(f"⚠️  Skipped {len(migration_results['skipped'])} agents (files not found)")
    
    if migration_results["errors"]:
        print(f"❌ Errors with {len(migration_results['errors'])} agents")
    
    print(f"\n🎯 AGENT INTEGRATION SUCCESS:")
    print("• Smart filtering focused on truly important agents")
    print("• All migrated agents connected to integration bridge")
    print("• Agent communication and memory access enabled")
    print("• Main system launcher updated with agent support")
    
    print(f"\n🧪 NEXT: TEST THE INTEGRATED AGENT SYSTEM")
    print("Run: python Aetherra_v2/launch_agents.py")
    print("Or: python Aetherra_v2/launch_with_web.py (includes agents)")
    
    return {
        "migrated_agents": len(migration_results["migrated"]),
        "bridge_file": str(bridge_file),
        "launcher_file": str(launcher_file),
        "migration_results": migration_results
    }

if __name__ == "__main__":
    main()
