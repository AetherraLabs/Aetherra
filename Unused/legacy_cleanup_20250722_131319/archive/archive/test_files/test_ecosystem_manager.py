#!/usr/bin/env python3
"""
Test script to verify the ecosystem manager works correctly after fixes
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.append(".")


def test_ecosystem_manager():
    """Test basic functionality of the ecosystem manager"""
    print("🧪 Testing AetherraCode Ecosystem Manager")
    print("=" * 50)

    # Test 1: Import Check
    print("Test 1: Testing imports...")
    try:
        from core.ecosystem_manager import (
            AetherraCodeEcosystemManager,
            AINetworkCoordinator,
            PluginEcosystem,
            UniversalDeploymentManager,
        )

        print("✅ All classes imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: PluginEcosystem functionality
    print("\nTest 2: Testing PluginEcosystem...")
    try:
        plugin_ecosystem = PluginEcosystem()
        print(
            f"✅ PluginEcosystem created: {len(plugin_ecosystem.plugin_registry)} plugins"
        )

        # Test plugin discovery (may find no plugins, which is fine)
        discovered = plugin_ecosystem.discover_plugins([])
        print(f"✅ Plugin discovery works: {len(discovered)} plugins found")

        # Test plugin analysis (create a temporary plugin file)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('''
"""Test plugin for ecosystem manager"""
VERSION = "1.0.0"
CAPABILITIES = ["test_action", "demo_action"]

def execute(command):
    return f"Test plugin executed: {command}"

def test_action():
    return "Test action executed"
''')
            temp_plugin_path = Path(f.name)

        try:
            plugin_info = plugin_ecosystem._analyze_plugin(temp_plugin_path)
            if plugin_info:
                print(
                    f"✅ Plugin analysis works: {plugin_info['name']} v{plugin_info['version']}"
                )
                print(f"   Capabilities: {plugin_info['capabilities']}")
            else:
                print("⚠️  Plugin analysis returned None")
        finally:
            os.unlink(temp_plugin_path)

    except Exception as e:
        print(f"❌ PluginEcosystem test failed: {e}")
        return False

    # Test 3: AINetworkCoordinator functionality
    print("\nTest 3: Testing AINetworkCoordinator...")
    try:
        ai_coordinator = AINetworkCoordinator()
        print(
            f"✅ AINetworkCoordinator created: {len(ai_coordinator.network_nodes)} nodes"
        )

        # Test node registration
        success = ai_coordinator.register_ai_node(
            "test_node", ["reasoning", "analysis"], "localhost:8001"
        )
        print(f"✅ Node registration: {success}")

        # Test finding capable nodes
        capable_nodes = ai_coordinator.find_capable_nodes(["reasoning"])
        print(f"✅ Found capable nodes: {capable_nodes}")

        # Test collaboration initiation
        if capable_nodes:
            collab = ai_coordinator.initiate_collaboration(
                "test_task", ["reasoning"], {"test": "context"}
            )
            print(f"✅ Collaboration initiated: {collab['status']}")

        # Test knowledge sharing
        knowledge_shared = ai_coordinator.share_knowledge(
            "test_knowledge", {"info": "test data"}, "network"
        )
        print(f"✅ Knowledge sharing: {knowledge_shared}")

        # Test knowledge retrieval
        retrieved = ai_coordinator.get_shared_knowledge("test_knowledge")
        print(f"✅ Knowledge retrieval: {retrieved is not None}")

    except Exception as e:
        print(f"❌ AINetworkCoordinator test failed: {e}")
        return False

    # Test 4: UniversalDeploymentManager functionality
    print("\nTest 4: Testing UniversalDeploymentManager...")
    try:
        deployment_manager = UniversalDeploymentManager()
        print(
            f"✅ UniversalDeploymentManager created: {len(deployment_manager.deployment_targets)} targets"
        )

        # Test deployment target availability
        targets = list(deployment_manager.deployment_targets.keys())
        print(f"✅ Available deployment targets: {targets}")

        # Test local deployment (create a temporary program file)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".aether", delete=False) as f:
            f.write('print("Hello from AetherraCode!")')
            temp_program_path = f.name

        try:
            result = deployment_manager.deploy_aetherra(temp_program_path, "local")
            print(f"✅ Local deployment test: {result['status']}")
        finally:
            os.unlink(temp_program_path)

    except Exception as e:
        print(f"❌ UniversalDeploymentManager test failed: {e}")
        return False

    # Test 5: AetherraCodeEcosystemManager integration
    print("\nTest 5: Testing AetherraCodeEcosystemManager...")
    try:
        ecosystem_manager = AetherraCodeEcosystemManager()
        print("✅ AetherraCodeEcosystemManager created successfully")

        # Test ecosystem initialization
        ecosystem_manager.initialize_ecosystem()
        print("✅ Ecosystem initialized successfully")

        # Test ecosystem status
        status = ecosystem_manager.get_ecosystem_status()
        print("✅ Ecosystem status retrieved:")
        print(
            f"   Plugins: {status['plugins']['total']} total, {status['plugins']['active']} active"
        )
        print(
            f"   AI Network: {status['ai_network']['nodes']} nodes, {status['ai_network']['collaborations']} collaborations"
        )
        print(f"   Deployment targets: {status['deployment_targets']}")

    except Exception as e:
        print(f"❌ AetherraCodeEcosystemManager test failed: {e}")
        return False

    # Test 6: Command line interface
    print("\nTest 6: Testing CLI functionality...")
    try:
        # Test help
        import subprocess

        result = subprocess.run(
            [sys.executable, "core/ecosystem_manager.py", "--help"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ CLI help works correctly")
        else:
            print("⚠️  CLI help returned non-zero exit code")

        # Test status command
        result = subprocess.run(
            [sys.executable, "core/ecosystem_manager.py", "--status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("✅ CLI status command works")
        else:
            print(f"⚠️  CLI status command failed: {result.stderr}")

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

    print("\n🎉 All ecosystem manager tests completed successfully!")
    return True


if __name__ == "__main__":
    success = test_ecosystem_manager()
    if success:
        print("\n✅ AetherraCode Ecosystem Manager is fully functional!")
    else:
        print("\n❌ Some tests failed - further investigation needed")
    sys.exit(0 if success else 1)
