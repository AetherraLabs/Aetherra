#!/usr/bin/env python3
"""
Aetherra-Lyrixa Integration Plan
Based on focused analysis results, creates a systematic plan to properly integrate the systems.
"""

import json
from pathlib import Path


def create_integration_plan():
    """Create systematic plan to fix Aetherra-Lyrixa integration"""

    print("🎯 AETHERRA-LYRIXA INTEGRATION PLAN")
    print("=" * 60)

    plan = {
        "phase_1_critical_connections": {
            "description": "Restore core integration points",
            "priority": "CRITICAL",
            "files_to_fix": [
                "Aetherra/simplified_lyrixa_aetherra_integration.py",
                "Aetherra/core/chat_router_new.py",
                "Aetherra/lyrixa/enhanced_conversation_manager.py",
                "Aetherra/lyrixa/gui/aetherra_main_window_hybrid.py",
            ],
            "broken_imports": [
                "Aetherra.core.engine.self_improvement_engine",
                "Aetherra.core.engine.introspection_controller",
                "Aetherra.core.engine.reasoning_engine",
                "memory.lyrixa_memory_engine",
                "lyrixa_connector",
            ],
            "action": "Fix import paths and ensure these files can connect Aetherra to Lyrixa",
        },
        "phase_2_memory_integration": {
            "description": "Connect memory systems",
            "priority": "HIGH",
            "orphaned_memory_files": [
                "Aetherra/lyrixa/core/plugin_intelligence_bridge.py",
                "Aetherra/plugins/memory_plugin.py",
                "Aetherra/memory/context_manager.py",
                "Aetherra/lyrixa/memory_feedback_system.py",
            ],
            "action": "Wire these memory components into the main system",
        },
        "phase_3_agent_activation": {
            "description": "Activate orphaned agent systems",
            "priority": "HIGH",
            "orphaned_agents": [
                "Aetherra/lyrixa/agents/reflection_agent.py",
                "Aetherra/lyrixa/agents/plugin_agent.py",
                "Aetherra/lyrixa/agents/goal_agent.py",
                "Aetherra/lyrixa/agents/self_evaluation_agent.py",
            ],
            "broken_agent_imports": [
                "Aetherra.lyrixa.agents.plugin_agent",
                "Aetherra.lyrixa.agents.core_agent",
                "Aetherra.lyrixa.agents.goal_agent",
                "Aetherra.lyrixa.agents.reflection_agent",
            ],
            "action": "Fix agent imports and integrate into main agent orchestrator",
        },
        "phase_4_gui_integration": {
            "description": "Connect GUI panels to live systems",
            "priority": "MEDIUM",
            "orphaned_gui": [
                "Aetherra/lyrixa/gui/real_confidence_manager.py",
                "Aetherra/lyrixa/gui/panels/developer_tools_panel.py",
                "Aetherra/lyrixa/gui/panels/intelligence_panel.py",
                "Aetherra/lyrixa/gui/real_goal_manager.py",
            ],
            "action": "Connect GUI panels to underlying data and agent systems",
        },
        "phase_5_plugin_ecosystem": {
            "description": "Activate plugin architecture",
            "priority": "MEDIUM",
            "orphaned_plugins": [
                "Aetherra/lyrixa/core/plugin_chainer.py",
                "Aetherra/plugins/math_plugin.py",
                "Aetherra/plugins/system_plugin.py",
                "Aetherra/lyrixa/plugins/assistant_trainer_plugin.py",
            ],
            "action": "Wire plugins into plugin manager and make them discoverable",
        },
        "phase_6_intelligence_systems": {
            "description": "Activate advanced intelligence features",
            "priority": "LOW",
            "orphaned_intelligence": [
                "Aetherra/lyrixa/personality/social_learning_integration.py",
                "Aetherra/lyrixa/anticipation/suggestion_generator.py",
                "Aetherra/lyrixa/ethics_agent/value_alignment.py",
                "Aetherra/lyrixa/core/world_class_goal_tracker.py",
            ],
            "action": "Integrate advanced AI capabilities once core system is stable",
        },
    }

    print("📋 INTEGRATION PHASES:")
    for phase_name, phase_info in plan.items():
        phase_num = phase_name.split("_")[1]
        print(f"\n🔸 PHASE {phase_num.upper()}: {phase_info['description']}")
        print(f"   Priority: {phase_info['priority']}")
        print(f"   Action: {phase_info['action']}")

        if "files_to_fix" in phase_info:
            print(f"   Files to fix: {len(phase_info['files_to_fix'])}")
        if "orphaned_memory_files" in phase_info:
            print(
                f"   Orphaned memory files: {len(phase_info['orphaned_memory_files'])}"
            )
        if "orphaned_agents" in phase_info:
            print(f"   Orphaned agents: {len(phase_info['orphaned_agents'])}")
        if "orphaned_gui" in phase_info:
            print(f"   Orphaned GUI: {len(phase_info['orphaned_gui'])}")
        if "orphaned_plugins" in phase_info:
            print(f"   Orphaned plugins: {len(phase_info['orphaned_plugins'])}")
        if "orphaned_intelligence" in phase_info:
            print(
                f"   Orphaned intelligence: {len(phase_info['orphaned_intelligence'])}"
            )

    # Immediate actions
    print(f"\n🚀 IMMEDIATE ACTIONS NEEDED:")
    print(
        f"   1. Fix 'simplified_lyrixa_aetherra_integration.py' - this is the main connector!"
    )
    print(
        f"   2. Repair engine imports: self_improvement_engine, introspection_controller, reasoning_engine"
    )
    print(f"   3. Fix memory engine imports: lyrixa_memory_engine")
    print(f"   4. Test basic Aetherra→Lyrixa communication")
    print(f"   5. Wire in the orphaned agent files to agent/__init__.py")

    print(f"\n💾 Saving integration plan...")
    with open("aetherra_lyrixa_integration_plan.json", "w") as f:
        json.dump(plan, f, indent=2)

    return plan


def find_missing_files():
    """Find which core engine files are missing"""
    print(f"\n🔍 MISSING FILE ANALYSIS:")

    missing_files = [
        "Aetherra/core/engine/self_improvement_engine.py",
        "Aetherra/core/engine/introspection_controller.py",
        "Aetherra/core/engine/reasoning_engine.py",
        "Aetherra/core/engine/agent_orchestrator.py",
        "Aetherra/core/engine/goal_forecaster.py",
        "memory/lyrixa_memory_engine.py",
    ]

    project_root = Path.cwd()

    for missing_file in missing_files:
        file_path = project_root / missing_file
        exists = file_path.exists()
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"   {status}: {missing_file}")

        if not exists:
            # Try to find alternatives
            file_name = file_path.name
            print(f"      🔎 Searching for alternatives to {file_name}...")

            # Search for similar files
            alternatives = list(project_root.rglob(f"*{file_name}*"))
            alternatives.extend(list(project_root.rglob(f"*{file_path.stem}*")))

            found_alternatives = []
            for alt in alternatives:
                if alt.is_file() and alt.suffix == ".py":
                    rel_path = str(alt.relative_to(project_root))
                    if "Unused" not in rel_path and "Lib" not in rel_path:
                        found_alternatives.append(rel_path)

            if found_alternatives:
                print(f"      📁 Found alternatives:")
                for alt in found_alternatives[:3]:
                    print(f"         - {alt}")
                if len(found_alternatives) > 3:
                    print(f"         ... and {len(found_alternatives) - 3} more")
            else:
                print(f"      ❌ No alternatives found - may need to create this file")


def main():
    plan = create_integration_plan()
    find_missing_files()

    print(f"\n📄 Integration plan saved to: aetherra_lyrixa_integration_plan.json")
    print(f"\n✨ NEXT STEPS:")
    print(f"   1. Review the integration plan")
    print(f"   2. Start with Phase 1 (Critical Connections)")
    print(f"   3. Fix the missing engine files")
    print(f"   4. Test basic integration")
    print(f"   5. Move to Phase 2 (Memory Integration)")


if __name__ == "__main__":
    main()
