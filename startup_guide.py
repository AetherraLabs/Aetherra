#!/usr/bin/env python3
"""
Lyrixa Modular Component Launcher Guide
=======================================

How to start each modular component independently:
"""

def show_startup_guide():
    print("🚀 LYRIXA MODULAR COMPONENT STARTUP GUIDE")
    print("=" * 50)

    components = [
        {
            "name": "Core Lyrixa (GUI + Agents)",
            "command": "python Aetherra/lyrixa/launcher.py",
            "description": "Main GUI with 6-agent system, LLM manager, intelligence dashboard",
            "port": "GUI Application",
            "status": "✅ Ready"
        },
        {
            "name": "AetherHub (Web Interface)",
            "command": "cd aetherra_hub && npm install && npm start",
            "description": "Web-based plugin management and system interface",
            "port": "http://localhost:3001",
            "status": "✅ Ready"
        },
        {
            "name": "Self-Improvement Dashboard",
            "command": "python Aetherra/lyrixa/self_improvement_dashboard.py",
            "description": "CLI dashboard for performance analytics and insights",
            "port": "CLI Output",
            "status": "✅ Ready"
        },
        {
            "name": "Plugin System (Standalone)",
            "command": "python -c 'from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager; pm=PluginManager(); print(pm.list_plugins())'",
            "description": "Test plugin discovery and loading independently",
            "port": "CLI Output",
            "status": "✅ Ready"
        }
    ]

    for i, comp in enumerate(components, 1):
        print(f"\n{i}. {comp['name']} {comp['status']}")
        print(f"   Command: {comp['command']}")
        print(f"   Access:  {comp['port']}")
        print(f"   Purpose: {comp['description']}")

    print(f"\n🎯 MODULAR BENEFITS:")
    print(f"   • Start only what you need")
    print(f"   • Components work independently")
    print(f"   • No conflicts between services")
    print(f"   • Easy debugging and maintenance")

    print(f"\n💡 RECOMMENDED STARTUP SEQUENCE:")
    print(f"   1. Start Core Lyrixa for main functionality")
    print(f"   2. Start AetherHub for web-based plugin management (optional)")
    print(f"   3. Run Self-Improvement Dashboard for analytics (optional)")
    print(f"   4. Test Plugin System independently as needed")

if __name__ == "__main__":
    show_startup_guide()
