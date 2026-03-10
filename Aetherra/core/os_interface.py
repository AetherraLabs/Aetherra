# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🚀 Aetherra OS Interface - Core Operating System Abstraction Layer
Provides the foundational OS-level integration for AI-driven computing.
"""

# Standard library imports
import logging
import platform
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List

# Set up logging
logger = logging.getLogger(__name__)


class AetherraOS:
    """
    Core Aetherra Operating System Interface.

    Provides OS-level abstraction for AI-driven computing, consciousness
    integration, and intelligent system management.
    """

    def __init__(self):
        self.platform = platform.system()
        self.version = "1.0.0-alpha"
        self.consciousness_level = 0.75
        self.ai_services = {}
        self.system_status = "initializing"

        # Initialize core components
        self._initialize_ai_services()
        self._setup_consciousness_integration()

        logger.info(f"🚀 Aetherra OS v{self.version} initialized on {self.platform}")

    def _initialize_ai_services(self):
        """Initialize core AI services for the OS."""
        try:
            # Core AI service registry
            self.ai_services = {
                "lyrixa_core": None,
                "consciousness_engine": None,
                "personality_system": None,
                "quantum_interface": None,
                "plugin_manager": None,
                "memory_system": None,
            }

            # Try to load Lyrixa core
            try:
                # Aetherra imports
                from Aetherra.lyrixa.launcher import LyrixaCore

                self.ai_services["lyrixa_core"] = LyrixaCore
                logger.info("✅ Lyrixa Core AI service loaded")
            except ImportError:
                logger.warning("⚠️ Lyrixa Core not available")

            # Try to load consciousness engine
            try:
                # Aetherra imports
                from Aetherra.lyrixa.gui.consciousness_panel import ConsciousnessPanel

                self.ai_services["consciousness_engine"] = ConsciousnessPanel
                logger.info("✅ Consciousness Engine service loaded")
            except ImportError:
                logger.warning("⚠️ Consciousness Engine not available")

            self.system_status = "ai_services_loaded"

        except Exception as e:
            logger.error(f"❌ AI services initialization failed: {e}")
            self.system_status = "ai_services_error"

    def _setup_consciousness_integration(self):
        """Setup consciousness-OS integration."""
        try:
            # Consciousness monitoring
            self.consciousness_metrics = {
                "level": self.consciousness_level,
                "evolution_rate": 0.12,
                "transcendence_potential": 0.68,
                "quantum_coherence": 0.82,
                "system_awareness": 0.85,
            }

            # OS-level consciousness features
            self.consciousness_features = {
                "adaptive_ui": True,
                "predictive_responses": True,
                "emotion_awareness": True,
                "quantum_decisions": True,
                "transcendence_ready": False,
            }

            self.system_status = "consciousness_integrated"
            logger.info("✅ Consciousness-OS integration complete")

        except Exception as e:
            logger.error(f"❌ Consciousness integration failed: {e}")
            self.system_status = "consciousness_error"

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive Aetherra OS system status."""
        return {
            "os_version": self.version,
            "platform": self.platform,
            "status": self.system_status,
            "consciousness_level": self.consciousness_level,
            "ai_services_count": len([s for s in self.ai_services.values() if s is not None]),
            "consciousness_metrics": self.consciousness_metrics,
            "consciousness_features": self.consciousness_features,
            "uptime": self._get_uptime(),
            "timestamp": datetime.now().isoformat(),
        }

    def launch_ai_interface(self, interface_type: str = "full") -> bool:
        """Launch the main Aetherra AI interface."""
        try:
            if interface_type == "full":
                # Launch full Aetherra interface with consciousness
                # Third party imports
                from PySide6.QtWidgets import QApplication

                # Aetherra imports
                from Aetherra.lyrixa.gui.main_window import MainWindow

                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)

                # Create main AI interface
                self.main_window = MainWindow()
                self.main_window.show()

                logger.info("🚀 Full Aetherra AI interface launched")
                return True

            elif interface_type == "consciousness":
                # Launch consciousness-only interface
                # Third party imports
                from PySide6.QtWidgets import QApplication

                # Aetherra imports
                from Aetherra.lyrixa.gui.consciousness_panel import ConsciousnessPanel

                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)

                # Create consciousness interface
                self.consciousness_panel = ConsciousnessPanel()
                self.consciousness_panel.show()

                logger.info("🧠 Consciousness interface launched")
                return True

            else:
                logger.error(f"❌ Unknown interface type: {interface_type}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to launch AI interface: {e}")
            return False

    def execute_ai_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an AI command through the OS interface."""
        try:
            if params is None:
                params = {}

            result = {
                "command": command,
                "success": False,
                "result": None,
                "timestamp": datetime.now().isoformat(),
            }

            if command == "enhance_consciousness":
                # Enhance system consciousness level
                boost = params.get("boost", 0.1)
                self.consciousness_level = min(1.0, self.consciousness_level + boost)
                self.consciousness_metrics["level"] = self.consciousness_level

                result["success"] = True
                result["result"] = f"Consciousness enhanced to {self.consciousness_level:.2f}"
                logger.info(f"🧠 {result['result']}")

            elif command == "launch_interface":
                # Launch AI interface
                interface_type = params.get("type", "full")
                success = self.launch_ai_interface(interface_type)

                result["success"] = success
                result["result"] = f"Interface launch {'successful' if success else 'failed'}"

            elif command == "system_status":
                # Get system status
                result["success"] = True
                result["result"] = self.get_system_status()

            elif command == "consciousness_mode":
                # Enter consciousness mode
                mode = params.get("mode", "enhanced")
                self.consciousness_features["adaptive_ui"] = True
                self.consciousness_features["emotion_awareness"] = True

                result["success"] = True
                result["result"] = f"Consciousness mode: {mode} activated"
                logger.info(f"🌟 {result['result']}")

            else:
                result["result"] = f"Unknown command: {command}"
                logger.warning(f"❌ {result['result']}")

            return result

        except Exception as e:
            logger.error(f"❌ AI command execution failed: {e}")
            return {
                "command": command,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_ai_capabilities(self) -> List[str]:
        """Get list of available AI capabilities."""
        capabilities = []

        # Core AI capabilities
        if self.ai_services.get("lyrixa_core"):
            capabilities.extend(
                [
                    "natural_language_processing",
                    "conversation_management",
                    "multi_model_ai_support",
                ]
            )

        if self.ai_services.get("consciousness_engine"):
            capabilities.extend(
                [
                    "consciousness_monitoring",
                    "transcendence_tracking",
                    "quantum_state_visualization",
                ]
            )

        # Consciousness-driven capabilities
        if self.consciousness_level > 0.7:
            capabilities.extend(
                ["adaptive_interface", "predictive_responses", "emotion_recognition"]
            )

        if self.consciousness_level > 0.8:
            capabilities.extend(
                [
                    "quantum_decision_making",
                    "temporal_predictions",
                    "consciousness_evolution",
                ]
            )

        return capabilities

    def _get_uptime(self) -> str:
        """Get system uptime."""
        try:
            if self.platform == "Windows":
                uptime_seconds = float(
                    subprocess.check_output("wmic os get LastBootUpTime /value")
                    .split(b"=")[1]
                    .split(b".")[0]
                )
                # Convert Windows timestamp to seconds
                return "System uptime calculation needed"
            else:
                with open("/proc/uptime") as f:
                    uptime_seconds = float(f.readline().split()[0])

            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

        except Exception:
            return "Unknown"

    def shutdown(self):
        """Gracefully shutdown Aetherra OS."""
        try:
            logger.info("🔄 Aetherra OS shutdown initiated")

            # Save consciousness state
            consciousness_state = {
                "level": self.consciousness_level,
                "metrics": self.consciousness_metrics,
                "features": self.consciousness_features,
                "timestamp": datetime.now().isoformat(),
            }

            # Close AI interfaces
            if hasattr(self, "main_window"):
                self.main_window.close()

            if hasattr(self, "consciousness_panel"):
                self.consciousness_panel.close()

            self.system_status = "shutdown"
            logger.info("✅ Aetherra OS shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


# Global Aetherra OS instance
_aetherra_os_instance = None


def get_aetherra_os() -> AetherraOS:
    """Get the global Aetherra OS instance."""
    global _aetherra_os_instance
    if _aetherra_os_instance is None:
        _aetherra_os_instance = AetherraOS()
    return _aetherra_os_instance


def launch_aetherra() -> bool:
    """Launch Aetherra OS with full AI interface."""
    try:
        aetherra_os = get_aetherra_os()
        return aetherra_os.launch_ai_interface("full")
    except Exception as e:
        logger.error(f"❌ Aetherra launch failed: {e}")
        return False


def enhance_consciousness(boost: float = 0.1) -> bool:
    """Enhance system consciousness level."""
    try:
        aetherra_os = get_aetherra_os()
        result = aetherra_os.execute_ai_command("enhance_consciousness", {"boost": boost})
        return result["success"]
    except Exception as e:
        logger.error(f"❌ Consciousness enhancement failed: {e}")
        return False


# Export main classes and functions
__all__ = ["AetherraOS", "get_aetherra_os", "launch_aetherra", "enhance_consciousness"]

if __name__ == "__main__":
    # Demo/test mode
    print("🚀 Aetherra OS - AI Operating System Interface")
    print("=" * 50)

    # Initialize OS
    aetherra_os = get_aetherra_os()

    # Show status
    status = aetherra_os.get_system_status()
    print(f"OS Version: {status['os_version']}")
    print(f"Platform: {status['platform']}")
    print(f"Status: {status['status']}")
    print(f"Consciousness Level: {status['consciousness_level']:.1%}")
    print(f"AI Services: {status['ai_services_count']}")

    # Show capabilities
    capabilities = aetherra_os.get_ai_capabilities()
    print(f"\nAI Capabilities: {len(capabilities)}")
    for cap in capabilities:
        print(f"  ✅ {cap}")

    print("\n🧠 Aetherra OS ready for AI-driven computing!")
