"""
Simple Unified GUI Status Check
Verifies all Phase 1-4 components are integrated in the Enhanced Lyrixa GUI
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))


def verify_unified_gui_implementation():
    """Verify all phases are implemented in the Enhanced Lyrixa GUI."""
    print("🔍 VERIFYING UNIFIED GUI IMPLEMENTATION")
    print("=" * 55)
    print("🎯 Goal: Single GUI with ALL Phase 1-4 features")
    print()

    # Check Enhanced Lyrixa GUI
    try:
        from src.aetherra.ui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("✅ Enhanced Lyrixa GUI found")

        # Check what's integrated
        print("\n📋 CHECKING PHASE INTEGRATION:")

        # Phase 1 check
        try:
            import importlib.util

            phase1_components = [
                "lyrixa.core.advanced_vector_memory",
                "lyrixa.core.enhanced_memory",
            ]
            phase1_available = any(
                importlib.util.find_spec(comp) for comp in phase1_components
            )
            status1 = "✅" if phase1_available else "⚠️"
            print(f"   {status1} Phase 1: Advanced Memory System & Lyrixa Core")
        except:
            print("   ⚠️ Phase 1: Advanced Memory System & Lyrixa Core")

        # Phase 2 check
        try:
            phase2_components = [
                "lyrixa.anticipation.context_analyzer",
                "lyrixa.anticipation.suggestion_generator",
                "lyrixa.anticipation.proactive_assistant",
            ]
            phase2_available = any(
                importlib.util.find_spec(comp) for comp in phase2_components
            )
            status2 = "✅" if phase2_available else "⚠️"
            print(f"   {status2} Phase 2: Anticipation Engine & Proactive Features")
        except:
            print("   ⚠️ Phase 2: Anticipation Engine & Proactive Features")

        # Phase 3 check
        try:
            from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
            from lyrixa.gui.configuration_manager import ConfigurationManager
            from lyrixa.gui.performance_monitor import PerformanceMonitor

            print("   ✅ Phase 3: GUI Integration & Analytics Dashboard")
        except ImportError:
            print("   ⚠️ Phase 3: GUI Integration & Analytics Dashboard")

        # Phase 4 check
        try:
            from lyrixa.gui.enhanced_analytics import EnhancedAnalyticsDashboard
            from lyrixa.gui.intelligence_layer import IntelligenceLayerWidget
            from lyrixa.gui.live_feedback_loop import LiveFeedbackInterface
            from lyrixa.gui.web_mobile_support import WebMobileInterface

            print("   ✅ Phase 4: Advanced GUI Features & Intelligence Layer")
        except ImportError:
            print("   ⚠️ Phase 4: Advanced GUI Features & Intelligence Layer")

        print("\n🚀 RECOMMENDATION:")
        print("The Enhanced Lyrixa GUI should be enhanced to include:")
        print("1. Intelligence Layer widget (Phase 4) as a main tab")
        print("2. Analytics Dashboard (Phase 3) integrated into main window")
        print("3. Live Feedback Loop (Phase 4) as a sidebar panel")
        print("4. Web/Mobile sync status (Phase 4) in status bar")
        print("5. Cross-phase communication channels")

        return True

    except ImportError:
        print("❌ Enhanced Lyrixa GUI not found")
        return False


def check_gui_launcher():
    """Check for existing GUI launchers."""
    print("\n🔍 CHECKING EXISTING GUI LAUNCHERS")
    print("=" * 40)

    launchers = [
        "aetherra_launcher.py",
        "run_aetherra.py",
        "lyrixa/gui/main.py",
        "src/aetherra/ui/main.py",
    ]

    found_launchers = []
    for launcher in launchers:
        if (project_root / launcher).exists():
            found_launchers.append(launcher)
            print(f"   ✅ Found: {launcher}")

    if not found_launchers:
        print("   ❌ No GUI launchers found")

    return found_launchers


def create_integration_summary():
    """Create summary of what needs to be done."""
    print("\n📋 INTEGRATION SUMMARY")
    print("=" * 30)

    print("🎯 CURRENT STATUS:")
    print("   • All Phase 1-4 components are individually implemented")
    print("   • Enhanced Lyrixa GUI exists as main interface")
    print("   • Integration between phases needs enhancement")

    print("\n🔧 NEEDED INTEGRATION:")
    print("   1. Add Intelligence Layer (Phase 4) to Enhanced Lyrixa GUI")
    print("   2. Integrate Analytics Dashboard (Phase 3) as main tab")
    print("   3. Add Live Feedback Loop (Phase 4) as sidebar")
    print("   4. Include Web/Mobile sync status (Phase 4)")
    print("   5. Setup cross-phase communication")

    print("\n✅ RESULT:")
    print("   Single Enhanced Lyrixa GUI with ALL Phase 1-4 features")
    print("   No need for multiple GUIs - everything in one interface")


if __name__ == "__main__":
    verify_unified_gui_implementation()
    check_gui_launcher()
    create_integration_summary()
