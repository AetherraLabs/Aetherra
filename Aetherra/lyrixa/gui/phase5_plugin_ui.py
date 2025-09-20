#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔁 Phase 5: Plugin-Driven UI System
===================================
            # Create system object from state data
            class SystemObj:
                def __init__(self, state):
                    self.memory = type('obj', (object,), state.get('memory', {}))()
                    self.network = type('obj', (object,), state.get('network', {}))()
                    self.cpu = state.get('system', {}).get('cpu_usage', 0.2)
                    self.security_level = state.get('system', {}).get('security_level', 85)wers each .aetherplugin to define its own UI widgets through metadata schema.
Creates a truly extensible GUI where developers can ship intelligent UIs with their plugins.

Architecture:
- Extended plugin metadata schema with UI definitions
- Dynamic UI panel loading from plugin directories
- Conditional display based on plugin state
- Integration with existing Phase 3 auto-generation system
- Live plugin UI registration and management

Features:
- Plugin UI metadata parsing
- Dynamic HTML panel injection
- Conditional display evaluation
- Plugin UI lifecycle management
- Real-time plugin state monitoring
"""

# Standard library imports
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Prefer central sandbox for safe expression evaluation
    # Aetherra imports
    from Aetherra.security.sandbox import safe_eval as sandbox_safe_eval
except Exception:  # pragma: no cover - fallback stub if import path differs in some envs
    sandbox_safe_eval = None  # type: ignore

# Third party imports
from PySide6.QtCore import (
    QObject,  # noqa: F401 (optional runtime import)
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


@dataclass
class PluginUIDefinition:
    """Plugin UI panel definition from metadata"""

    plugin_id: str
    ui_panel: str  # HTML file path relative to plugin directory
    panel_title: str
    display_conditions: List[str]  # Conditional expressions for display
    panel_type: str = "widget"  # widget, overlay, modal, sidebar
    panel_size: str = "medium"  # small, medium, large, fullscreen
    update_frequency: int = 1000  # Update frequency in milliseconds
    dependencies: Optional[List[str]] = None  # Required services/plugins
    permissions: Optional[List[str]] = None  # Required permissions
    css_files: Optional[List[str]] = None  # Additional CSS files
    js_files: Optional[List[str]] = None  # Additional JavaScript files

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.permissions is None:
            self.permissions = []
        if self.css_files is None:
            self.css_files = []
        if self.js_files is None:
            self.js_files = []


@dataclass
class PluginUIState:
    """Current state of a plugin UI panel"""

    plugin_id: str
    is_visible: bool
    is_loaded: bool
    last_update: datetime
    error_count: int = 0
    last_error: Optional[str] = None
    web_view: Optional[QWebEngineView] = None
    container_widget: Optional[QWidget] = None


class PluginConditionEvaluator:
    """Evaluates plugin display conditions safely"""

    def __init__(self):
        self.plugin_states = {}
        self.system_state = {}

    def update_plugin_state(self, plugin_id: str, state: Dict[str, Any]):
        """Update plugin state for condition evaluation"""
        self.plugin_states[plugin_id] = state

    def update_system_state(self, state: Dict[str, Any]):
        """Update system state for condition evaluation"""
        self.system_state = state

    def evaluate_conditions(self, conditions: List[str], plugin_id: str) -> bool:
        """Safely evaluate display conditions"""
        if not conditions:
            return True

        try:
            # Create safe evaluation context with both dict and object access
            # For expressions like 'system.memory.usage > 0.5'

            # Create system object from state data
            class SystemObj:
                def __init__(self, state):
                    self.memory = type("obj", (object,), state.get("memory", {}))()
                    self.network = type("obj", (object,), state.get("network", {}))()
                    self.cpu = state.get("system", {}).get("cpu_usage", 0.2)
                    self.security_level = state.get("system", {}).get("security_level", 85)

            # Create memory object for direct access
            class MemoryObj:
                def __init__(self, state):
                    self.active = True
                    self.usage = state.get("memory", {}).get("usage", 0.3)
                    self.available = state.get("memory", {}).get("available", 1024 * 1024 * 1024)

            # Create network object for direct access
            class NetworkObj:
                def __init__(self, state):
                    self.connected = state.get("network", {}).get("connected", True)
                    self.speed = state.get("network", {}).get("speed", "high")

            context = {
                "plugin": self.plugin_states.get(plugin_id, {}),
                "system": SystemObj(self.system_state),
                "memory": MemoryObj(self.system_state),
                "network": NetworkObj(self.system_state),
                "cpu": self.system_state.get("system", {}).get("cpu_usage", 0.2),
                "True": True,
                "False": False,
                "true": True,
                "false": False,
            }

            # Evaluate all conditions (AND logic)
            return all(self._safe_eval(condition, context) for condition in conditions)

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Condition evaluation error for {plugin_id}: {e}")
            return False

    def _safe_eval(self, expression: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a single condition expression.
        Delegates to central sandbox.safe_eval with a strict allowlist by mapping
        dotted attributes into flat variable names (no attribute access allowed).
        """
        # Normalize common logical operators
        expr = (
            expression.replace("&&", " and ")
            .replace("||", " or ")
            .replace("==", " == ")
            .replace("!=", " != ")
        )

        # Build a flat variables dict from provided context for sandbox evaluation
        vars_map: Dict[str, Any] = {
            "True": True,
            "False": False,
            "true": True,
            "false": False,
        }

        # Helper to safely get nested attributes/keys
        def _get(d: Any, *path: str, default: Any = None) -> Any:
            cur = d
            for p in path:
                try:
                    cur = cur.get(p, default) if isinstance(cur, dict) else getattr(cur, p)
                except Exception:
                    return default
            return cur

        # Known mappings used in UI expressions
        mappings = {
            "system.memory.usage": "system_memory_usage",
            "system.memory.available": "system_memory_available",
            "system.network.connected": "system_network_connected",
            "system.network.speed": "system_network_speed",
            "system.cpu": "system_cpu",
            "memory.usage": "memory_usage",
            "memory.available": "memory_available",
            "network.connected": "network_connected",
            "network.speed": "network_speed",
            "cpu": "system_cpu",
        }

        # Populate values from context
        vars_map.update(
            {
                "system_memory_usage": _get(context, "system", "memory", "usage", default=0.3),
                "system_memory_available": _get(
                    context, "system", "memory", "available", default=1024 * 1024 * 1024
                ),
                "system_network_connected": _get(
                    context, "system", "network", "connected", default=True
                ),
                "system_network_speed": _get(context, "system", "network", "speed", default="high"),
                "system_cpu": _get(context, "system", "cpu", default=0.2),
                "memory_usage": _get(context, "memory", "usage", default=0.3),
                "memory_available": _get(
                    context, "memory", "available", default=1024 * 1024 * 1024
                ),
                "network_connected": _get(context, "network", "connected", default=True),
                "network_speed": _get(context, "network", "speed", default="high"),
            }
        )

        # Rewrite expression by replacing dotted names with flat variables
        rewritten = expr
        for dotted, flat in mappings.items():
            rewritten = rewritten.replace(dotted, flat)

        try:
            if sandbox_safe_eval is None:
                # Fallback: extremely restrictive eval with no builtins
                # nosec B307: eval used with no builtins for UI expression evaluation
                return bool(eval(rewritten, {"__builtins__": {}}, vars_map))
            value = sandbox_safe_eval(rewritten, variables=vars_map)
            return bool(value)
        except Exception as e:
            logger.warning(
                f"[PLUGIN-UI] Expression evaluation failed (sandbox): {expression} -> {rewritten} - {e}"
            )
            return False


class PluginUIManager(QObject):
    """
    🔁 Phase 5: Plugin-Driven UI System Manager
    ===========================================

    Manages plugin UI definitions, loading, and lifecycle.
    Integrates with Phase 3 auto-generation for seamless plugin UI integration.
    """

    # Signals
    plugin_ui_loaded = Signal(str, str)  # plugin_id, panel_html
    plugin_ui_unloaded = Signal(str)  # plugin_id
    plugin_ui_updated = Signal(str, str)  # plugin_id, updated_data
    plugin_ui_error = Signal(str, str)  # plugin_id, error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugin_definitions: Dict[str, PluginUIDefinition] = {}
        self.plugin_states: Dict[str, PluginUIState] = {}
        self.condition_evaluator = PluginConditionEvaluator()
        self.plugin_directories: List[Path] = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plugin_states)
        self.update_timer.start(1000)  # Update every second

        # Initialize plugin scanning
        self.scan_for_plugins()

    def add_plugin_directory(self, directory: str):
        """Add a directory to scan for plugins"""
        plugin_dir = Path(directory)
        if plugin_dir.exists() and plugin_dir not in self.plugin_directories:
            self.plugin_directories.append(plugin_dir)
            logger.info(f"[PLUGIN-UI] Added plugin directory: {plugin_dir}")

    def scan_for_plugins(self):
        """Scan plugin directories for UI-enabled plugins"""
        # Default plugin directories
        default_dirs = [
            Path("plugins"),
            Path("Aetherra/plugins"),
            Path("lyrixa_plugins"),
            Path.cwd() / "plugins",
        ]

        for plugin_dir in default_dirs:
            if plugin_dir.exists():
                self.add_plugin_directory(str(plugin_dir))

        # Scan each directory
        for plugin_dir in self.plugin_directories:
            self._scan_directory(plugin_dir)

    def _scan_directory(self, directory: Path):
        """Scan a specific directory for plugin UI definitions"""
        try:
            for plugin_file in directory.glob("*.aetherplugin"):
                self._load_plugin_ui_definition(plugin_file)

            # Also scan subdirectories
            for subdir in directory.iterdir():
                if subdir.is_dir():
                    plugin_manifest = subdir / "plugin.json"
                    if plugin_manifest.exists():
                        self._load_plugin_ui_definition(plugin_manifest)

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error scanning directory {directory}: {e}")

    def _load_plugin_ui_definition(self, plugin_file: Path):
        """Load plugin UI definition from metadata"""
        try:
            with open(plugin_file, encoding="utf-8") as f:
                plugin_data = json.load(f)

            # Check if plugin has UI definition
            if "ui_panel" not in plugin_data:
                return  # No UI panel defined

            plugin_id = plugin_data.get("id", plugin_file.stem)

            # Create UI definition
            ui_def = PluginUIDefinition(
                plugin_id=plugin_id,
                ui_panel=plugin_data["ui_panel"],
                panel_title=plugin_data.get("panel_title", plugin_id),
                display_conditions=plugin_data.get("display_conditions", []),
                panel_type=plugin_data.get("panel_type", "widget"),
                panel_size=plugin_data.get("panel_size", "medium"),
                update_frequency=plugin_data.get("update_frequency", 1000),
                dependencies=plugin_data.get("dependencies", []),
                permissions=plugin_data.get("permissions", []),
                css_files=plugin_data.get("css_files", []),
                js_files=plugin_data.get("js_files", []),
            )

            # Validate UI panel file exists
            panel_path = plugin_file.parent / ui_def.ui_panel
            if not panel_path.exists():
                logger.warning(f"[PLUGIN-UI] UI panel not found: {panel_path}")
                return

            self.plugin_definitions[plugin_id] = ui_def
            self.plugin_states[plugin_id] = PluginUIState(
                plugin_id=plugin_id,
                is_visible=False,
                is_loaded=False,
                last_update=datetime.now(),
            )

            logger.info(f"[PLUGIN-UI] Loaded UI definition for plugin: {plugin_id}")
            self._load_plugin_ui_panel(plugin_id)

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error loading plugin UI from {plugin_file}: {e}")

    def _load_plugin_ui_panel(self, plugin_id: str):
        """Load the HTML panel for a plugin"""
        try:
            ui_def = self.plugin_definitions[plugin_id]
            plugin_state = self.plugin_states[plugin_id]

            # Find plugin directory
            plugin_dir = None
            for directory in self.plugin_directories:
                potential_file = directory / f"{plugin_id}.aetherplugin"
                potential_dir = directory / plugin_id

                if potential_file.exists():
                    plugin_dir = directory
                    break
                elif potential_dir.exists():
                    plugin_dir = potential_dir
                    break

            if not plugin_dir:
                logger.error(f"[PLUGIN-UI] Plugin directory not found for {plugin_id}")
                return

            # Load HTML panel
            panel_path = plugin_dir / ui_def.ui_panel
            with open(panel_path, encoding="utf-8") as f:
                panel_html = f.read()

            # Inject plugin-specific styling and scripts
            enhanced_html = self._enhance_plugin_html(panel_html, ui_def, plugin_dir)

            plugin_state.is_loaded = True
            plugin_state.last_update = datetime.now()

            # Emit signal with loaded HTML
            self.plugin_ui_loaded.emit(plugin_id, enhanced_html)

            logger.info(f"[PLUGIN-UI] Loaded UI panel for plugin: {plugin_id}")

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error loading UI panel for {plugin_id}: {e}")
            plugin_state = self.plugin_states.get(plugin_id)
            if plugin_state:
                plugin_state.error_count += 1
                plugin_state.last_error = str(e)

    def _enhance_plugin_html(self, html: str, ui_def: PluginUIDefinition, plugin_dir: Path) -> str:
        """Enhance plugin HTML with additional CSS/JS and metadata"""
        enhancements = []

        # Add plugin metadata
        enhancements.append(
            f"""
        <script>
            window.pluginMetadata = {{
                id: "{ui_def.plugin_id}",
                title: "{ui_def.panel_title}",
                type: "{ui_def.panel_type}",
                size: "{ui_def.panel_size}",
                updateFrequency: {ui_def.update_frequency}
            }};
        </script>"""
        )

        # Add CSS files
        for css_file in ui_def.css_files or []:
            css_path = plugin_dir / css_file
            if css_path.exists():
                enhancements.append(f'<link rel="stylesheet" href="file:///{css_path}">')

        # Add JavaScript files
        for js_file in ui_def.js_files or []:
            js_path = plugin_dir / js_file
            if js_path.exists():
                enhancements.append(f'<script src="file:///{js_path}"></script>')

        # Insert enhancements before closing head tag
        if "</head>" in html:
            enhanced_html = html.replace("</head>", "\n".join(enhancements) + "\n</head>")
        else:
            # Add to beginning if no head tag
            enhanced_html = "\n".join(enhancements) + "\n" + html

        return enhanced_html

    def update_plugin_states(self):
        """Update plugin states and visibility based on conditions"""
        try:
            # Update system state in condition evaluator using memory adapter
            try:
                # Aetherra imports
                from Aetherra.lyrixa.integrations.memory_adapter import (
                    create_system_object_for_plugins,
                )

                system_obj = create_system_object_for_plugins()

                # Convert SystemObject to dictionary format expected by evaluator
                system_data = {
                    "memory": {
                        "usage": getattr(system_obj.memory, "usage", 0.3),
                        "available": getattr(system_obj.memory, "available", 1024 * 1024 * 1024),
                        "total": getattr(system_obj.memory, "total", 8192),
                    },
                    "network": {
                        "connected": getattr(system_obj.network, "connected", True),
                        "speed": getattr(system_obj.network, "speed", "high"),
                        "latency": getattr(system_obj.network, "latency", 12),
                    },
                    "system": {
                        "cpu_usage": getattr(system_obj, "cpu", 0.2),
                        "load": "low",
                    },
                }

                self.condition_evaluator.update_system_state(system_data)
                logger.debug("[PLUGIN-UI] Using memory adapter system data")
            except (ImportError, AttributeError):
                # Fallback to static data if memory adapter unavailable
                fallback_data = {
                    "memory": {"usage": 0.3, "available": 1024 * 1024 * 1024},
                    "network": {"connected": True, "speed": "high"},
                    "system": {"cpu_usage": 0.2, "load": "low"},
                }
                self.condition_evaluator.update_system_state(fallback_data)
                logger.debug("[PLUGIN-UI] Using fallback system data")

            for plugin_id, ui_def in self.plugin_definitions.items():
                plugin_state = self.plugin_states[plugin_id]

                # Evaluate display conditions
                should_be_visible = self.condition_evaluator.evaluate_conditions(
                    ui_def.display_conditions, plugin_id
                )

                # Update visibility if changed
                if should_be_visible != plugin_state.is_visible:
                    plugin_state.is_visible = should_be_visible
                    plugin_state.last_update = datetime.now()

                    if should_be_visible:
                        logger.info(f"[PLUGIN-UI] Showing plugin UI: {plugin_id}")
                    else:
                        logger.info(f"[PLUGIN-UI] Hiding plugin UI: {plugin_id}")

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error updating plugin states: {e}")

    def get_visible_plugin_uis(self) -> List[PluginUIDefinition]:
        """Get list of currently visible plugin UIs"""
        visible_uis = []
        for plugin_id, ui_def in self.plugin_definitions.items():
            plugin_state = self.plugin_states.get(plugin_id)
            if plugin_state and plugin_state.is_visible and plugin_state.is_loaded:
                visible_uis.append(ui_def)
        return visible_uis

    def get_plugin_html(self, plugin_id: str) -> Optional[str]:
        """Get HTML content for a specific plugin"""
        try:
            if plugin_id not in self.plugin_definitions:
                return None

            ui_def = self.plugin_definitions[plugin_id]

            # Find and load HTML
            for directory in self.plugin_directories:
                panel_path = directory / ui_def.ui_panel
                if panel_path.exists():
                    with open(panel_path, encoding="utf-8") as f:
                        html = f.read()
                    return self._enhance_plugin_html(html, ui_def, directory)

            return None

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error getting HTML for plugin {plugin_id}: {e}")
            return None

    @Slot(str, str)
    def update_plugin_data(self, plugin_id: str, data: str):
        """Update plugin with new data"""
        try:
            plugin_data = json.loads(data)
            self.condition_evaluator.update_plugin_state(plugin_id, plugin_data)
            self.plugin_ui_updated.emit(plugin_id, data)

        except Exception as e:
            logger.error(f"[PLUGIN-UI] Error updating plugin data for {plugin_id}: {e}")

    @Slot(str)
    def reload_plugin_ui(self, plugin_id: str):
        """Reload a specific plugin UI"""
        if plugin_id in self.plugin_definitions:
            self._load_plugin_ui_panel(plugin_id)

    @Slot()
    def reload_all_plugins(self):
        """Reload all plugin UIs"""
        logger.info("[PLUGIN-UI] Reloading all plugin UIs")
        self.plugin_definitions.clear()
        self.plugin_states.clear()
        self.scan_for_plugins()

    def get_plugin_summary(self) -> Dict[str, Any]:
        """Get summary of all plugin UIs for debugging"""
        return {
            "total_plugins": len(self.plugin_definitions),
            "visible_plugins": len(self.get_visible_plugin_uis()),
            "loaded_plugins": sum(1 for state in self.plugin_states.values() if state.is_loaded),
            "plugin_directories": [str(d) for d in self.plugin_directories],
            "plugins": {
                plugin_id: {
                    "title": ui_def.panel_title,
                    "type": ui_def.panel_type,
                    "visible": self.plugin_states[plugin_id].is_visible,
                    "loaded": self.plugin_states[plugin_id].is_loaded,
                    "conditions": ui_def.display_conditions,
                }
                for plugin_id, ui_def in self.plugin_definitions.items()
            },
        }
