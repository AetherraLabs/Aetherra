"""
🔗 PLUGIN CONFIDENCE SYSTEM INTEGRATION
=====================================

Integration layer that connects the Plugin Confidence & Safety System
with the existing Lyrixa plugin system and GUI components.

This module provides:
- Automatic confidence scoring for all plugin operations
- Real-time safety warnings in Lyrixa GUI
- Execution blocking for unsafe plugins
- Plugin recommendations and alternatives
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Import our confidence system
from .plugin_confidence_system import (
    PluginScorer,
    get_plugin_confidence_warning,
    should_block_plugin_execution,
)

# Import existing Lyrixa components
try:
    from .plugin_system import LyrixaPluginSystem

    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError:
    PLUGIN_SYSTEM_AVAILABLE = False
    logging.warning("Plugin system not available for confidence integration")

try:
    from lyrixa.plugins.plugin_analytics import PluginMetricsCollector

    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    logging.warning("Plugin analytics not available for confidence integration")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceEnhancedPluginSystem:
    """
    Enhanced plugin system with integrated confidence scoring and safety checks.

    This class wraps the existing plugin system and adds:
    - Automatic confidence analysis
    - Safety blocking
    - Real-time warnings
    - Plugin recommendations
    """

    def __init__(self, base_plugin_system=None, lyrixa_instance=None):
        """Initialize the confidence-enhanced plugin system."""

        self.lyrixa = lyrixa_instance
        self.base_system = base_plugin_system
        self.confidence_scorer = PluginScorer()

        # Callbacks for Lyrixa GUI integration
        self.warning_callback: Optional[Callable] = None
        self.block_callback: Optional[Callable] = None
        self.recommendation_callback: Optional[Callable] = None

        # Configuration
        self.auto_analyze_on_load = True
        self.block_unsafe_plugins = True
        self.show_confidence_warnings = True

        logger.info("🛡️ Confidence-Enhanced Plugin System initialized")

    def set_callbacks(
        self,
        warning_callback: Optional[Callable] = None,
        block_callback: Optional[Callable] = None,
        recommendation_callback: Optional[Callable] = None,
    ):
        """Set callback functions for GUI integration."""
        self.warning_callback = warning_callback
        self.block_callback = block_callback
        self.recommendation_callback = recommendation_callback

    def analyze_plugin_safely(
        self, plugin_name: str, plugin_path: Path
    ) -> Dict[str, Any]:
        """
        Safely analyze a plugin with comprehensive error handling.

        Args:
            plugin_name: Name of the plugin to analyze
            plugin_path: Path to the plugin directory or file

        Returns:
            Dict containing analysis results or error information
        """

        try:
            # Read plugin code
            main_file = plugin_path / "main.py" if plugin_path.is_dir() else plugin_path

            if not main_file.exists():
                return {
                    "success": False,
                    "error": f"Plugin main file not found: {main_file}",
                    "confidence_score": 0.0,
                    "risk_level": "CRITICAL",
                }

            with open(main_file, "r", encoding="utf-8") as f:
                plugin_code = f.read()

            # Perform confidence analysis
            analysis = self.confidence_scorer.analyze_plugin(
                plugin_name, plugin_code, plugin_path
            )

            # Add success flag
            analysis["success"] = True

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze plugin {plugin_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "plugin_name": plugin_name,
                "confidence_score": 0.0,
                "risk_level": "CRITICAL",
            }

    def load_plugin_with_confidence_check(
        self, plugin_name: str, plugin_path: Path, user_override: bool = False
    ) -> Dict[str, Any]:
        """
        Load a plugin with confidence and safety checks.

        Args:
            plugin_name: Name of the plugin
            plugin_path: Path to plugin
            user_override: Whether user has overridden safety warnings

        Returns:
            Dict with load result and confidence information
        """

        # Analyze plugin confidence
        analysis = self.analyze_plugin_safely(plugin_name, plugin_path)

        if not analysis["success"]:
            return {"loaded": False, "error": analysis["error"], "analysis": analysis}

        confidence_score = analysis["confidence_score"]
        risk_level = analysis["safety_analysis"]["risk_level"]

        # Check if plugin should be blocked
        should_block = should_block_plugin_execution(
            risk_level, confidence_score, user_override
        )

        if should_block:
            block_message = f"Plugin '{plugin_name}' blocked due to safety concerns"
            logger.warning(block_message)

            # Notify GUI if callback is set
            if self.block_callback:
                self.block_callback(plugin_name, risk_level, confidence_score, analysis)

            return {
                "loaded": False,
                "blocked": True,
                "reason": block_message,
                "analysis": analysis,
            }

        # Generate warnings if needed
        warning = get_plugin_confidence_warning(
            plugin_name, confidence_score, risk_level
        )
        if warning and self.show_confidence_warnings:
            logger.warning(warning)

            # Notify GUI if callback is set
            if self.warning_callback:
                self.warning_callback(plugin_name, warning, analysis)

        # Load the plugin using base system (if available)
        load_result = {"loaded": True, "analysis": analysis}

        if self.base_system and hasattr(self.base_system, "load_plugin"):
            try:
                base_result = self.base_system.load_plugin(plugin_name, plugin_path)
                load_result.update(base_result)
            except Exception as e:
                logger.error(f"Base system failed to load plugin: {str(e)}")
                load_result["loaded"] = False
                load_result["error"] = str(e)

        return load_result

    def execute_plugin_with_monitoring(
        self, plugin_name: str, command: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a plugin with confidence monitoring and metrics collection.

        Args:
            plugin_name: Name of the plugin to execute
            command: Command to execute
            **kwargs: Additional arguments for plugin

        Returns:
            Dict with execution result and updated confidence metrics
        """

        start_time = datetime.now()
        success = False
        error_info = None
        result = None

        try:
            # Get current confidence score
            current_confidence = self.confidence_scorer.get_plugin_confidence(
                plugin_name
            )

            # Check if plugin should be blocked
            if current_confidence:
                should_block = should_block_plugin_execution(
                    current_confidence["risk_level"],
                    current_confidence["confidence_score"],
                )

                if should_block:
                    return {
                        "success": False,
                        "blocked": True,
                        "error": f"Plugin '{plugin_name}' execution blocked due to low confidence",
                        "confidence_info": current_confidence,
                    }

            # Execute plugin using base system
            if self.base_system and hasattr(self.base_system, "execute_plugin"):
                result = self.base_system.execute_plugin(plugin_name, command, **kwargs)
                success = (
                    result.get("success", True) if isinstance(result, dict) else True
                )
            else:
                # Fallback execution
                result = {"message": f"Executed {command} on {plugin_name}"}
                success = True

        except Exception as e:
            error_info = {"type": type(e).__name__, "message": str(e)}
            result = {"error": str(e)}
            success = False
            logger.error(f"Plugin {plugin_name} execution failed: {str(e)}")

        finally:
            # Record execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.confidence_scorer.record_plugin_execution(
                plugin_name, execution_time, success, error_info
            )

        return {
            "success": success,
            "result": result,
            "execution_time": execution_time,
            "confidence_updated": True,
        }

    def get_plugin_recommendations(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Get recommendations for improving a specific plugin."""

        # Get stored confidence data
        confidence_data = self.confidence_scorer.get_plugin_confidence(plugin_name)

        if not confidence_data:
            return [
                {
                    "type": "NO_DATA",
                    "message": "No confidence data available for this plugin",
                    "priority": "LOW",
                }
            ]

        recommendations = []

        # Low confidence recommendations
        if confidence_data["confidence_score"] < 0.5:
            recommendations.append(
                {
                    "type": "LOW_CONFIDENCE",
                    "message": f"Plugin has low confidence score ({confidence_data['confidence_score']:.1%})",
                    "priority": "HIGH",
                    "actions": [
                        "Review plugin code for safety issues",
                        "Improve error handling",
                        "Add input validation",
                        "Consider rewriting plugin",
                    ],
                }
            )

        # Performance recommendations
        if confidence_data["avg_execution_time"] > 3.0:
            recommendations.append(
                {
                    "type": "PERFORMANCE",
                    "message": f"Plugin is slow (avg: {confidence_data['avg_execution_time']:.2f}s)",
                    "priority": "MEDIUM",
                    "actions": [
                        "Profile code for bottlenecks",
                        "Optimize algorithms",
                        "Add caching",
                        "Use async operations",
                    ],
                }
            )

        # Reliability recommendations
        if confidence_data["error_frequency"] > 0.2:
            recommendations.append(
                {
                    "type": "RELIABILITY",
                    "message": f"Plugin fails frequently ({confidence_data['error_frequency']:.1%} error rate)",
                    "priority": "HIGH",
                    "actions": [
                        "Add comprehensive error handling",
                        "Improve input validation",
                        "Add logging and debugging",
                        "Write unit tests",
                    ],
                }
            )

        # Safety recommendations based on risk level
        if confidence_data["risk_level"] in ["HIGH", "CRITICAL"]:
            recommendations.append(
                {
                    "type": "SAFETY",
                    "message": f"Plugin has {confidence_data['risk_level'].lower()} safety risk",
                    "priority": "CRITICAL",
                    "actions": [
                        "Remove unsafe imports",
                        "Eliminate dynamic code execution",
                        "Add input sanitization",
                        "Review security implications",
                    ],
                }
            )

        return recommendations

    def get_confidence_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive confidence data for dashboard display."""

        all_scores = self.confidence_scorer.get_all_plugin_scores()

        if not all_scores:
            return {
                "total_plugins": 0,
                "avg_confidence": 0.0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0,
                "blocked_plugins": 0,
                "plugins": [],
            }

        # Calculate statistics
        total_plugins = len(all_scores)
        avg_confidence = sum(p["confidence_score"] for p in all_scores) / total_plugins

        high_confidence = len([p for p in all_scores if p["confidence_score"] >= 0.8])
        medium_confidence = len(
            [p for p in all_scores if 0.5 <= p["confidence_score"] < 0.8]
        )
        low_confidence = len([p for p in all_scores if p["confidence_score"] < 0.5])
        blocked_plugins = len(
            [p for p in all_scores if p["risk_level"] in ["HIGH", "CRITICAL"]]
        )

        return {
            "total_plugins": total_plugins,
            "avg_confidence": avg_confidence,
            "high_confidence_count": high_confidence,
            "medium_confidence_count": medium_confidence,
            "low_confidence_count": low_confidence,
            "blocked_plugins": blocked_plugins,
            "plugins": all_scores,
            "last_updated": datetime.now().isoformat(),
        }

    def suggest_plugin_alternatives(
        self, plugin_name: str, required_capabilities: Optional[List[str]] = None
    ) -> List[Dict]:
        """Suggest alternative plugins with higher confidence scores."""

        all_scores = self.confidence_scorer.get_all_plugin_scores()
        current_plugin = next(
            (p for p in all_scores if p["plugin_name"] == plugin_name), None
        )

        if not current_plugin:
            return []

        current_confidence = current_plugin["confidence_score"]

        # Find plugins with higher confidence
        alternatives = [
            p
            for p in all_scores
            if p["plugin_name"] != plugin_name
            and p["confidence_score"] > current_confidence
            and p["risk_level"] not in ["HIGH", "CRITICAL"]
        ]

        # Sort by confidence score
        alternatives.sort(key=lambda x: x["confidence_score"], reverse=True)

        return alternatives[:5]  # Return top 5 alternatives


class LyrixaConfidenceIntegration:
    """
    Integration helper for connecting confidence system with Lyrixa GUI and core.
    """

    def __init__(self, lyrixa_instance):
        self.lyrixa = lyrixa_instance
        self.enhanced_system = ConfidenceEnhancedPluginSystem(
            lyrixa_instance=lyrixa_instance
        )

        # Set up callbacks for GUI integration
        self.enhanced_system.set_callbacks(
            warning_callback=self.handle_confidence_warning,
            block_callback=self.handle_plugin_block,
            recommendation_callback=self.handle_recommendations,
        )

    def handle_confidence_warning(self, plugin_name: str, warning: str, analysis: Dict):
        """Handle confidence warnings for display in Lyrixa GUI."""

        if hasattr(self.lyrixa, "show_warning"):
            self.lyrixa.show_warning("Plugin Confidence Warning", warning)
        else:
            logger.warning(f"CONFIDENCE WARNING: {warning}")

        # Store warning in memory if available
        if hasattr(self.lyrixa, "memory_system"):
            self.lyrixa.memory_system.store_plugin_warning(
                plugin_name, warning, analysis
            )

    def handle_plugin_block(
        self, plugin_name: str, risk_level: str, confidence_score: float, analysis: Dict
    ):
        """Handle blocked plugin execution."""

        block_message = f"Plugin '{plugin_name}' blocked due to {risk_level.lower()} risk (confidence: {confidence_score:.1%})"

        if hasattr(self.lyrixa, "show_error"):
            self.lyrixa.show_error("Plugin Blocked", block_message)
        else:
            logger.error(f"PLUGIN BLOCKED: {block_message}")

        # Suggest alternatives
        alternatives = self.enhanced_system.suggest_plugin_alternatives(plugin_name)
        if alternatives and hasattr(self.lyrixa, "suggest_alternatives"):
            self.lyrixa.suggest_alternatives(plugin_name, alternatives)

    def handle_recommendations(self, plugin_name: str, recommendations: List[Dict]):
        """Handle plugin improvement recommendations."""

        if hasattr(self.lyrixa, "show_recommendations"):
            self.lyrixa.show_recommendations(plugin_name, recommendations)
        else:
            logger.info(
                f"RECOMMENDATIONS for {plugin_name}: {len(recommendations)} suggestions available"
            )

    def get_confidence_system(self) -> ConfidenceEnhancedPluginSystem:
        """Get the enhanced plugin system for direct use."""
        return self.enhanced_system


# Utility functions for easy integration


def initialize_confidence_system(lyrixa_instance) -> LyrixaConfidenceIntegration:
    """
    Initialize the confidence system integration for Lyrixa.

    This is the main entry point for integrating confidence scoring
    into an existing Lyrixa instance.
    """

    return LyrixaConfidenceIntegration(lyrixa_instance)


def quick_confidence_check(plugin_name: str, plugin_path: Path) -> Dict[str, Any]:
    """
    Quick confidence check for a plugin without full system integration.

    Useful for one-off analysis or testing.
    """

    scorer = PluginScorer()

    try:
        with open(plugin_path, "r", encoding="utf-8") as f:
            code = f.read()

        return scorer.analyze_plugin(plugin_name, code, plugin_path.parent)

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "confidence_score": 0.0,
            "risk_level": "CRITICAL",
        }


# Example usage
if __name__ == "__main__":
    # Test integration
    print("🛡️ Testing Plugin Confidence Integration...")

    # Test quick confidence check
    test_code = """
def execute(command, **kwargs):
    return {"result": f"Safe execution: {command}"}

def get_info():
    return {"name": "Test Plugin", "version": "1.0.0"}
"""

    # Create temporary file for testing
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        temp_path = Path(f.name)

    try:
        result = quick_confidence_check("test_plugin", temp_path)
        print(f"Test Result: {result['confidence_score']:.1%} confidence")
        print(
            f"Risk Level: {result.get('safety_analysis', {}).get('risk_level', 'UNKNOWN')}"
        )
    finally:
        temp_path.unlink()  # Clean up

    print("✅ Integration test completed!")
