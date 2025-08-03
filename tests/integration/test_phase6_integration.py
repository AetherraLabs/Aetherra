#!/usr/bin/env python3
"""
🌌 PHASE 6 COMPREHENSIVE INTEGRATION TEST
========================================

Verification script to ensure all Phase 1-6 components are properly
integrated and functioning in Lyrixa AI Operating System.

Tests:
- Phase 1: Hybrid PySide6 + Web Panel Architecture
- Phase 2: Live Context Bridge
- Phase 3: Auto-Generation System
- Phase 4: Cognitive UI Integration
- Phase 5: Plugin-Driven UI System
- Phase 6: Full GUI Personality + State Memory + AI Chat

Usage:
    python test_phase6_integration.py
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Aetherra"))

def test_phase_imports():
    """Test that all Phase components can be imported."""
    print("🧪 TESTING PHASE 1-6 COMPONENT IMPORTS")
    print("=" * 50)

    # Phase 1: Basic GUI
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebChannel import QWebChannel
        print("✅ Phase 1: PySide6 + WebEngine components available")
    except ImportError as e:
        print(f"❌ Phase 1: PySide6 components missing: {e}")
        return False

    # Phase 2: Live Context Bridge
    try:
        from Aetherra.lyrixa_core.gui.main_window import LyrixaContextBridge
        print("✅ Phase 2: Live Context Bridge available")
    except ImportError as e:
        print(f"❌ Phase 2: Context Bridge missing: {e}")

    # Phase 3: Auto-Generation System
    try:
        from Aetherra.lyrixa_core.gui.phase3_auto_generator import Phase3AutoGenerator
        print("✅ Phase 3: Auto-Generation System available")
    except ImportError as e:
        print(f"❌ Phase 3: Auto-Generation System missing: {e}")

    # Phase 4: Cognitive UI Integration
    try:
        from Aetherra.lyrixa_core.gui.phase4_cognitive_ui import CognitiveStateMonitor
        print("✅ Phase 4: Cognitive UI Integration available")
    except ImportError as e:
        print(f"❌ Phase 4: Cognitive UI Integration missing: {e}")

    # Phase 5: Plugin-Driven UI System
    try:
        from Aetherra.lyrixa_core.gui.phase5_plugin_ui import PluginUIManager
        print("✅ Phase 5: Plugin-Driven UI System available")
    except ImportError as e:
        print(f"❌ Phase 5: Plugin-Driven UI System missing: {e}")

    # Phase 6: GUI Personality + State Memory
    try:
        from Aetherra.lyrixa_core.gui.phase6_personality import GUIPersonalityManager
        print("✅ Phase 6: GUI Personality + State Memory available")
    except ImportError as e:
        print(f"❌ Phase 6: GUI Personality + State Memory missing: {e}")

    # Main Window Integration
    try:
        from Aetherra.lyrixa_core.gui.main_window import LyrixaHybridWindow
        print("✅ Main Window: LyrixaHybridWindow available")
    except ImportError as e:
        print(f"❌ Main Window: LyrixaHybridWindow missing: {e}")
        return False

    return True

def test_main_window_phases():
    """Test that main window has all phase components."""
    print("\n🔍 TESTING MAIN WINDOW PHASE INTEGRATION")
    print("=" * 50)

    try:
        from Aetherra.lyrixa_core.gui.main_window import LyrixaHybridWindow

        # Create instance (without showing)
        import sys
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)

        window = LyrixaHybridWindow()

        # Test Phase components
        phases_found = []

        if hasattr(window, 'web_bridge'):
            phases_found.append("Phase 2: Live Context Bridge")

        if hasattr(window, 'auto_generator'):
            phases_found.append("Phase 3: Auto-Generation System")

        if hasattr(window, 'cognitive_monitor'):
            phases_found.append("Phase 4: Cognitive UI Integration")

        if hasattr(window, 'plugin_ui_manager'):
            phases_found.append("Phase 5: Plugin-Driven UI System")

        if hasattr(window, 'personality_manager'):
            phases_found.append("Phase 6: GUI Personality + State Memory")

        print(f"✅ Main Window Components Found: {len(phases_found)}/5")
        for phase in phases_found:
            print(f"   ✓ {phase}")

        # Test web panel files
        gui_dir = Path(__file__).parent / "Aetherra" / "lyrixa_core" / "gui" / "web_panels"

        expected_panels = [
            "dashboard_panel.html",
            "phase4_cognitive.html",
            "phase5_plugin_demo.html",
            "phase6_chat.html"
        ]

        panels_found = []
        for panel in expected_panels:
            if (gui_dir / panel).exists():
                panels_found.append(panel)

        print(f"✅ Web Panels Found: {len(panels_found)}/{len(expected_panels)}")
        for panel in panels_found:
            print(f"   ✓ {panel}")

        return len(phases_found) >= 4 and len(panels_found) >= 3

    except Exception as e:
        print(f"❌ Main Window Test Failed: {e}")
        return False

def test_phase6_components():
    """Test Phase 6 specific components."""
    print("\n🌌 TESTING PHASE 6 SPECIFIC COMPONENTS")
    print("=" * 50)

    try:
        from Aetherra.lyrixa_core.gui.phase6_personality import (
            GUIPersonalityManager,
            EmotionalState,
            PersonalityTrait,
            LyrixaAI,
            EmotionalThemeEngine,
            LayoutMemorySystem
        )

        # Test emotional states
        emotions = list(EmotionalState)
        print(f"✅ Emotional States: {len(emotions)} defined")
        print(f"   Available: {', '.join([e.value for e in emotions[:5]])}...")

        # Test personality traits
        traits = list(PersonalityTrait)
        print(f"✅ Personality Traits: {len(traits)} defined")
        print(f"   Available: {', '.join([t.value for t in traits[:5]])}...")

        # Test theme engine
        theme_engine = EmotionalThemeEngine()
        theme = theme_engine.generate_theme(type('MockState', (), {
            'emotional_state': EmotionalState.FOCUSED,
            'energy_level': 0.8,
            'focus_level': 0.9,
            'creativity_level': 0.6,
            'social_engagement': 0.7,
            'dominant_traits': [PersonalityTrait.ANALYTICAL]
        })())
        print(f"✅ Theme Engine: Generated theme with primary color {theme.primary_color}")

        # Test memory system
        memory_system = LayoutMemorySystem(":memory:")  # Use in-memory SQLite
        print("✅ Memory System: Database initialized")

        # Test AI component
        ai = LyrixaAI()
        print(f"✅ AI Component: Initial emotional state is {ai.personality_state.emotional_state.value}")

        print("✅ Phase 6: All core components functional")
        return True

    except Exception as e:
        print(f"❌ Phase 6 Component Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_interface():
    """Test that chat interface exists and is accessible."""
    print("\n💬 TESTING CHAT INTERFACE")
    print("=" * 30)

    chat_file = Path(__file__).parent / "Aetherra" / "lyrixa_core" / "gui" / "web_panels" / "phase6_chat.html"

    if chat_file.exists():
        content = chat_file.read_text(encoding='utf-8')

        # Check for key chat components
        components = [
            "chat-container",
            "chat-messages",
            "chat-input",
            "personality-indicator",
            "emotion-badge",
            "LyrixaChatInterface"
        ]

        found_components = []
        for component in components:
            if component in content:
                found_components.append(component)

        print(f"✅ Chat Interface: {len(found_components)}/{len(components)} components found")
        for component in found_components:
            print(f"   ✓ {component}")

        return len(found_components) >= len(components) - 1
    else:
        print("❌ Chat Interface: phase6_chat.html not found")
        return False

def test_plugin_system():
    """Test that plugin system components exist."""
    print("\n🔁 TESTING PLUGIN SYSTEM")
    print("=" * 30)

    plugins_dir = Path(__file__).parent / "plugins"

    if plugins_dir.exists():
        plugin_files = list(plugins_dir.glob("*.aetherplugin"))
        print(f"✅ Plugin Files: {len(plugin_files)} found")

        for plugin_file in plugin_files:
            print(f"   ✓ {plugin_file.name}")

        # Check for plugin demo interface
        demo_file = Path(__file__).parent / "Aetherra" / "lyrixa_core" / "gui" / "web_panels" / "phase5_plugin_demo.html"
        if demo_file.exists():
            print("✅ Plugin Demo Interface: Available")
            return True
        else:
            print("❌ Plugin Demo Interface: Missing")
            return False
    else:
        print("❌ Plugins Directory: Not found")
        return False

def main():
    """Run comprehensive Phase 6 integration test."""
    print("🌌 LYRIXA PHASE 1-6 COMPREHENSIVE INTEGRATION TEST")
    print("=" * 60)
    print("Testing all phases of Lyrixa GUI evolution:")
    print("Phase 1: Hybrid PySide6 + Web Panel Architecture")
    print("Phase 2: Live Context Bridge")
    print("Phase 3: Auto-Generation System")
    print("Phase 4: Cognitive UI Integration")
    print("Phase 5: Plugin-Driven UI System")
    print("Phase 6: Full GUI Personality + State Memory + AI Chat")
    print("=" * 60)

    tests = [
        ("Component Imports", test_phase_imports),
        ("Main Window Integration", test_main_window_phases),
        ("Phase 6 Components", test_phase6_components),
        ("Chat Interface", test_chat_interface),
        ("Plugin System", test_plugin_system)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Exception occurred: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("🏆 INTEGRATION TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print("-" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL! Phase 1-6 integration complete!")
        print("🌌 Lyrixa is ready for launch with full personality and AI capabilities!")
    elif passed >= total * 0.8:
        print("⚠️  Most systems operational. Minor issues detected.")
        print("🚀 Lyrixa can launch but may have reduced functionality.")
    else:
        print("🚨 Critical issues detected. System requires attention.")
        print("🔧 Please check component installations and configurations.")

    return passed == total

if __name__ == "__main__":
    # Set working directory
    os.chdir(Path(__file__).parent)

    # Run tests
    success = main()
    sys.exit(0 if success else 1)
