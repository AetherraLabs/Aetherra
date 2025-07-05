#!/usr/bin/env python3
"""
🚀 LYRIXA AI ASSISTANT - UNIFIED LAUNCHER
========================================

THE SINGLE, UNIFIED LAUNCHER FOR LYRIXA AI ASSISTANT

Integrates ALL Phase 1-4 features into one comprehensive system:

PHASE 1: Advanced Memory System & Enhanced Lyrixa Core
PHASE 2: Anticipation Engine & Proactive Features
PHASE 3: GUI Integration & Analytics Dashboard
PHASE 4: Advanced GUI Features & Intelligence Layer

This is the ONLY launcher you need - it includes everything!

Usage:
    python lyrixa_unified_launcher.py
    python lyrixa_unified_launcher.py --gui        (Launch with GUI)
    python lyrixa_unified_launcher.py --console    (Console mode only)
    python lyrixa_unified_launcher.py --test       (Run system tests)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LyrixaUnifiedLauncher:
    """The single, unified launcher for Lyrixa AI Assistant."""

    def __init__(self):
        self.app = None
        self.main_window = None

        # Phase integration status
        self.phases_initialized = {
            "Phase 1": False,  # Advanced Memory System
            "Phase 2": False,  # Anticipation Engine
            "Phase 3": False,  # GUI Integration & Analytics
            "Phase 4": False,  # Advanced GUI Features
        }

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        print("🔍 Checking Lyrixa System Dependencies...")

        # Check GUI framework
        try:
            from PySide6.QtWidgets import QApplication

            print("   ✅ PySide6 GUI framework available")
            gui_available = True
        except ImportError:
            print("   ❌ PySide6 not available - GUI mode disabled")
            gui_available = False

        # Check core Lyrixa components
        core_available = True
        try:
            # Check if we can import basic Lyrixa components
            from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
            from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

            print("   ✅ Lyrixa core components available")
        except ImportError as e:
            print(f"   ⚠️ Some Lyrixa core components missing: {e}")
            core_available = False

        return gui_available or core_available

    def initialize_phase_1(self) -> bool:
        """Initialize Phase 1: Advanced Memory System & Enhanced Lyrixa Core."""
        try:
            print("🧠 Initializing Phase 1: Advanced Memory System...")

            # Import Phase 1 components
            from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
            from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

            # Initialize memory system
            self.memory_system = AdvancedMemorySystem()
            self.lyrixa_assistant = LyrixaEnhancedMemorySystem()

            print("   ✅ Advanced Memory System initialized")
            print("   ✅ Enhanced Lyrixa Memory System initialized")

            self.phases_initialized["Phase 1"] = True
            return True

        except ImportError as e:
            print(f"   ⚠️ Phase 1 components missing: {e}")
            print("   ℹ️ Phase 1 will be skipped")
            return False

    def initialize_phase_2(self) -> bool:
        """Initialize Phase 2: Anticipation Engine & Proactive Features."""
        try:
            print("🔮 Initializing Phase 2: Anticipation Engine...")

            # Import Phase 2 components
            from lyrixa.anticipation.context_analyzer import ContextAnalyzer
            from lyrixa.anticipation.proactive_assistant import ProactiveAssistant
            from lyrixa.core.anticipation_engine import AnticipationEngine

            # Initialize anticipation system
            self.anticipation_engine = AnticipationEngine()
            self.context_analyzer = ContextAnalyzer()
            self.proactive_assistant = ProactiveAssistant()

            print("   ✅ Anticipation Engine initialized")
            print("   ✅ Context Analyzer initialized")
            print("   ✅ Proactive Assistant initialized")

            self.phases_initialized["Phase 2"] = True
            return True

        except ImportError as e:
            print(f"   ⚠️ Phase 2 components missing: {e}")
            print("   ℹ️ Phase 2 will be skipped")
            return False

    def initialize_phase_3(self) -> bool:
        """Initialize Phase 3: GUI Integration & Analytics Dashboard."""
        try:
            print("📊 Initializing Phase 3: GUI Integration & Analytics...")

            # Import Phase 3 components (validate availability)
            from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
            from lyrixa.gui.configuration_manager import ConfigurationManager
            from lyrixa.gui.performance_monitor import PerformanceMonitor

            # Store classes for later instantiation (don't create widgets yet)
            self.analytics_dashboard_class = AnalyticsDashboard
            self.config_manager_class = ConfigurationManager
            self.performance_monitor_class = PerformanceMonitor

            print("   ✅ Analytics Dashboard class available")
            print("   ✅ Configuration Manager class available")
            print("   ✅ Performance Monitor class available")

            self.phases_initialized["Phase 3"] = True
            return True

        except ImportError as e:
            print(f"   ⚠️ Phase 3 components missing: {e}")
            print("   ℹ️ Phase 3 will be skipped")
            return False

    def initialize_phase_4(self) -> bool:
        """Initialize Phase 4: Advanced GUI Features & Intelligence Layer."""
        try:
            print("🚀 Initializing Phase 4: Advanced GUI Features...")

            # Import Phase 4 components
            from lyrixa.gui.enhanced_analytics import EnhancedAnalyticsDashboard
            from lyrixa.gui.intelligence_layer import IntelligenceLayerWidget
            from lyrixa.gui.live_feedback_loop import LiveFeedbackInterface
            from lyrixa.gui.web_mobile_support import WebMobileInterface

            # Store component classes for GUI creation
            self.intelligence_layer_class = IntelligenceLayerWidget
            self.enhanced_analytics_class = EnhancedAnalyticsDashboard
            self.web_mobile_class = WebMobileInterface
            self.feedback_loop_class = LiveFeedbackInterface

            print("   ✅ Intelligence Layer available")
            print("   ✅ Enhanced Analytics available")
            print("   ✅ Web/Mobile Support available")
            print("   ✅ Live Feedback Loop available")

            self.phases_initialized["Phase 4"] = True
            return True

        except ImportError as e:
            print(f"   ⚠️ Phase 4 components missing: {e}")
            print("   ℹ️ Phase 4 will be skipped")
            return False

    def initialize_all_phases(self) -> int:
        """Initialize all Lyrixa phases. Returns number of successful initializations."""
        print("🚀 INITIALIZING ALL LYRIXA PHASES")
        print("=" * 50)

        # Initialize each phase
        phase_results = []
        phase_results.append(self.initialize_phase_1())
        phase_results.append(self.initialize_phase_2())
        phase_results.append(self.initialize_phase_3())
        phase_results.append(self.initialize_phase_4())

        # Show results
        successful_phases = sum(phase_results)
        print(f"\n📊 PHASE INITIALIZATION SUMMARY:")
        print(f"   Successful: {successful_phases}/4 phases")

        for phase, status in self.phases_initialized.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {phase}")

        return successful_phases

    def launch_gui_mode(self) -> int:
        """Launch Lyrixa with the full GUI interface."""
        try:
            print("\n🌙 LAUNCHING LYRIXA MODERN GUI MODE")
            print("=" * 40)

            # Check for GUI framework
            from PySide6.QtWidgets import QApplication

            # Use Enhanced Lyrixa GUI (more stable)
            print("🚀 Creating Modern Dark Mode Lyrixa GUI...")

            try:
                from modern_lyrixa_gui import ModernLyrixaGUI

                # Create QApplication
                app = QApplication.instance() or QApplication(sys.argv)
                app.setApplicationName("Lyrixa AI Assistant")
                app.setApplicationVersion("2.0")

                # Create main window
                main_window = ModernLyrixaGUI()
                main_window.show()

                print("✅ Modern Lyrixa GUI launched successfully!")
                print("🌙 Beautiful dark mode interface ready!")
                print("🧠 Knowledge Responder integrated!")
                print("💬 Ready for intelligent conversations!")

                # Run the application
                return app.exec()

            except ImportError as e:
                print(f"⚠️ Modern Lyrixa GUI import failed: {e}")
                # Try unified GUI as fallback
                print("🔄 Trying Enhanced GUI as fallback...")

                try:
                    from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

                    app = QApplication.instance() or QApplication(sys.argv)
                    main_window = EnhancedLyrixaWindow()
                    main_window.show()

                    print("✅ Enhanced GUI launched as fallback!")
                    return app.exec()

                except Exception as e:
                    print(f"❌ Enhanced GUI also failed: {e}")
                    # Final fallback
                    print("🔄 Trying Unified GUI as final fallback...")

                    try:
                        from unified_aetherra_lyrixa_gui import UnifiedAetherraLyrixaGUI

                        app = QApplication.instance() or QApplication(sys.argv)
                        main_window = UnifiedAetherraLyrixaGUI()
                        main_window.show()

                        print("✅ Unified GUI launched as final fallback!")
                        return app.exec()

                    except Exception as e:
                        print(f"❌ All GUI options exhausted: {e}")
                        return 1

        except ImportError as e:
            print(f"❌ GUI mode not available: {e}")
            print("🔄 Falling back to console mode...")
            return self.launch_console_mode()

    def launch_console_mode(self) -> int:
        """Launch Lyrixa in console mode."""
        print("\n💻 LAUNCHING LYRIXA CONSOLE MODE")
        print("=" * 40)

        try:
            # Use the modularized launcher if available
            from lyrixa.launcher import main as lyrixa_main

            print("🎙️ Starting Lyrixa AI Assistant (Console Mode)...")
            asyncio.run(lyrixa_main())
            return 0

        except ImportError:
            print("❌ Console mode components not available")
            print("ℹ️ Please check the lyrixa/ directory structure")
            return 1

    def run_system_tests(self) -> int:
        """Run comprehensive system tests."""
        print("\n🧪 RUNNING LYRIXA SYSTEM TESTS")
        print("=" * 40)

        try:
            # Run the comprehensive test suite
            import subprocess

            test_files = [
                "test_advanced_gui_comprehensive.py",
                "phase_integration_plan.py",
            ]

            for test_file in test_files:
                if Path(test_file).exists():
                    print(f"🔬 Running {test_file}...")
                    result = subprocess.run(
                        [sys.executable, test_file], capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        print(f"   ✅ {test_file} passed")
                    else:
                        print(f"   ❌ {test_file} failed")
                        print(f"   Error: {result.stderr}")
                else:
                    print(f"   ⚠️ {test_file} not found")

            print("\n✅ System tests completed!")
            return 0

        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return 1

    def show_status(self):
        """Show current Lyrixa system status."""
        print("\n📊 LYRIXA SYSTEM STATUS")
        print("=" * 30)

        initialized_count = sum(self.phases_initialized.values())
        print(f"Initialized Phases: {initialized_count}/4")

        for phase, status in self.phases_initialized.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {phase}")

        if initialized_count == 4:
            print("\n🚀 All phases ready - Lyrixa fully operational!")
        else:
            print(f"\n⚠️ {4 - initialized_count} phase(s) need attention")


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Lyrixa AI Assistant - Unified Launcher"
    )
    parser.add_argument("--gui", action="store_true", help="Launch with GUI (default)")
    parser.add_argument("--console", action="store_true", help="Launch in console mode")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--status", action="store_true", help="Show system status only")

    args = parser.parse_args()

    # Create launcher
    launcher = LyrixaUnifiedLauncher()

    # Welcome message
    print("🚀 LYRIXA AI ASSISTANT - UNIFIED LAUNCHER")
    print("=" * 50)
    print("THE SINGLE LAUNCHER FOR ALL PHASE 1-4 FEATURES")
    print()

    # Check dependencies
    if not launcher.check_dependencies():
        print("❌ Critical dependencies missing. Cannot launch Lyrixa.")
        return 1

    # Initialize all phases
    successful_phases = launcher.initialize_all_phases()

    if successful_phases == 0:
        print("❌ No phases could be initialized. Check installation.")
        return 1

    # Show status if requested
    if args.status:
        launcher.show_status()
        return 0

    # Run tests if requested
    if args.test:
        return launcher.run_system_tests()

    # Launch in appropriate mode
    if args.console:
        return launcher.launch_console_mode()
    else:
        # Default to GUI mode
        return launcher.launch_gui_mode()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Lyrixa AI Assistant shutdown requested")
        print("Thank you for using Lyrixa!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue to the development team.")
        sys.exit(1)
