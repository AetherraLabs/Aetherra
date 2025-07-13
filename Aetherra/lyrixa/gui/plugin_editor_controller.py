"""
🎯 Plugin Editor Controller
Bridges conversation manager with the actual Plugin Editor UI
Ensures intent routing triggers real UI actions, not just responses
"""

import logging
import os
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PluginEditorController:
    """
    🎯 Plugin Editor Controller

    Handles the bridge between Lyrixa's conversation understanding
    and actual Plugin Editor UI actions
    """

    _instance = None

    def __init__(self, gui_interface=None, plugin_dir="plugins"):
        self.gui_interface = gui_interface
        self.plugin_dir = plugin_dir
        self.current_plugin = None
        self.last_action_timestamp = None

        # Plugin templates for different types
        self.plugin_templates = {
            "assistant_trainer": self._get_assistant_trainer_template(),
            "data_processor": self._get_data_processor_template(),
            "automation": self._get_automation_template(),
            "utility": self._get_utility_template()
        }

    @classmethod
    def get_instance(cls, gui_interface=None, plugin_dir="plugins"):
        """Get singleton instance of controller"""
        if cls._instance is None:
            cls._instance = cls(gui_interface, plugin_dir)
        elif gui_interface and not cls._instance.gui_interface:
            cls._instance.gui_interface = gui_interface
        return cls._instance

    def handle_plugin_editor_intent(
        self,
        user_input: str,
        detected_intent: str,
        meta_reasoning_engine=None
    ) -> Tuple[bool, str, Dict]:
        """
        🎯 Main handler for plugin editor intents
        Returns: (success, response_message, action_data)
        """
        action_data = {
            "intent": detected_intent,
            "user_input": user_input,
            "timestamp": import_time().time(),
            "actions_taken": []
        }

        try:
            # Analyze the intent
            intent_analysis = self._analyze_plugin_intent(user_input)

            # Log intent routing with meta-reasoning
            if meta_reasoning_engine:
                routing_trace = meta_reasoning_engine.explain_intent_routing(
                    user_input=user_input,
                    detected_intent=detected_intent,
                    confidence=intent_analysis["confidence"],
                    routing_decision="plugin_editor_handler",
                    available_routes=["conversation_only", "plugin_editor_handler", "file_manager", "general_assistant"],
                    reasoning=f"Detected plugin editor keywords: {intent_analysis['keywords']}"
                )
                action_data["routing_trace_id"] = routing_trace.trace_id

            # Execute the appropriate action
            if intent_analysis["action"] == "load_plugin":
                return self._handle_load_plugin(intent_analysis, action_data, meta_reasoning_engine)

            elif intent_analysis["action"] == "create_plugin":
                return self._handle_create_plugin(intent_analysis, action_data, meta_reasoning_engine)

            elif intent_analysis["action"] == "inject_code":
                return self._handle_inject_code(intent_analysis, action_data, meta_reasoning_engine)

            elif intent_analysis["action"] == "open_editor":
                return self._handle_open_editor(intent_analysis, action_data, meta_reasoning_engine)

            else:
                return False, "I understand you want to work with the plugin editor, but I'm not sure exactly what action to take.", action_data

        except Exception as e:
            logger.error(f"Plugin editor intent handling failed: {e}")
            return False, f"Sorry, I encountered an error while trying to work with the plugin editor: {str(e)}", action_data

    def _analyze_plugin_intent(self, user_input: str) -> Dict:
        """Analyze user input to determine specific plugin editor action"""
        text = user_input.lower()

        # Extract potential plugin name
        plugin_name = self._extract_plugin_name(text)

        # Determine action based on keywords
        if any(word in text for word in ["load", "open", "show"]) and "plugin" in text:
            action = "load_plugin"
            confidence = 0.9 if plugin_name else 0.7

        elif any(word in text for word in ["create", "generate", "make", "build"]) and "plugin" in text:
            action = "create_plugin"
            confidence = 0.85 if plugin_name else 0.6

        elif any(word in text for word in ["inject", "populate", "fill", "add code"]):
            action = "inject_code"
            confidence = 0.8

        elif "editor" in text and any(word in text for word in ["open", "show", "switch"]):
            action = "open_editor"
            confidence = 0.75

        else:
            action = "general_plugin_request"
            confidence = 0.5

        keywords = [word for word in ["plugin", "editor", "load", "create", "inject", "code"] if word in text]

        return {
            "action": action,
            "plugin_name": plugin_name,
            "confidence": confidence,
            "keywords": keywords,
            "original_text": user_input
        }

    def _extract_plugin_name(self, text: str) -> Optional[str]:
        """Extract plugin name from user input"""
        # Look for patterns like "assistant trainer", "data processor", etc.
        patterns = [
            r"(\w+\s*trainer)",
            r"(\w+\s*processor)",
            r"(\w+\s*manager)",
            r"(\w+\s*plugin)",
            r"plugin\s+(\w+)",
            r"(\w+)\s+plugin"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().replace(" ", "_")
                return name.lower()

        return None

    def _handle_load_plugin(self, intent_analysis: Dict, action_data: Dict, meta_reasoning_engine=None) -> Tuple[bool, str, Dict]:
        """Handle loading an existing plugin"""
        plugin_name = intent_analysis.get("plugin_name", "unknown_plugin")

        # Try to find the plugin file
        plugin_file = self._find_plugin_file(plugin_name)

        if plugin_file:
            # Load existing plugin
            success = self.load_file(plugin_file)
            action_data["actions_taken"].append(f"loaded_file_{plugin_file}")

            if meta_reasoning_engine:
                ui_trace = meta_reasoning_engine.trace_ui_action(
                    action_type="load_plugin_file",
                    context={"plugin_name": plugin_name, "file_path": plugin_file},
                    target="plugin_editor",
                    confidence=0.9 if success else 0.3,
                    explanation=f"Successfully loaded {plugin_name} plugin from {plugin_file}" if success else f"Failed to load {plugin_name}",
                    success=success
                )
                action_data["ui_trace_id"] = ui_trace.trace_id

            if success:
                return True, f"✅ I've loaded the {plugin_name} plugin into the Plugin Editor! You can now review and edit it.", action_data
            else:
                return False, f"❌ I found the {plugin_name} plugin file but couldn't load it into the editor.", action_data
        else:
            # Plugin doesn't exist, offer to create it
            return self._handle_create_plugin(intent_analysis, action_data, meta_reasoning_engine)

    def _handle_create_plugin(self, intent_analysis: Dict, action_data: Dict, meta_reasoning_engine=None) -> Tuple[bool, str, Dict]:
        """Handle creating a new plugin"""
        plugin_name = intent_analysis.get("plugin_name", "new_plugin")

        # Get appropriate template
        plugin_type = self._classify_plugin_type(plugin_name)
        template_code = self.plugin_templates.get(plugin_type, self.plugin_templates["utility"])

        # Customize template with plugin name
        customized_code = template_code.replace("PLUGIN_NAME", plugin_name)
        filename = f"{plugin_name}.aether"

        # Inject into editor
        success = self.inject_plugin_code(customized_code, filename)
        action_data["actions_taken"].append(f"created_plugin_{plugin_name}")

        if meta_reasoning_engine:
            ui_trace = meta_reasoning_engine.trace_ui_action(
                action_type="create_new_plugin",
                context={"plugin_name": plugin_name, "plugin_type": plugin_type, "filename": filename},
                target="plugin_editor",
                confidence=0.9 if success else 0.3,
                explanation=f"Created new {plugin_type} plugin '{plugin_name}' and injected template code" if success else f"Failed to create {plugin_name} plugin",
                success=success,
                metadata={"template_used": plugin_type, "code_length": len(customized_code)}
            )
            action_data["ui_trace_id"] = ui_trace.trace_id

        if success:
            return True, f"✅ I've created a new {plugin_type} plugin called '{plugin_name}' and loaded it into the Plugin Editor! The template is ready for you to customize.", action_data
        else:
            return False, f"❌ I tried to create the {plugin_name} plugin but couldn't inject it into the editor.", action_data

    def _handle_inject_code(self, intent_analysis: Dict, action_data: Dict, meta_reasoning_engine=None) -> Tuple[bool, str, Dict]:
        """Handle injecting code into the editor"""
        # This would typically be called with specific code
        # For now, use a general template
        plugin_name = intent_analysis.get("plugin_name", "injected_plugin")
        code = self.plugin_templates["utility"].replace("PLUGIN_NAME", plugin_name)
        filename = f"{plugin_name}.aether"

        success = self.inject_plugin_code(code, filename)
        action_data["actions_taken"].append(f"injected_code_{filename}")

        if meta_reasoning_engine:
            ui_trace = meta_reasoning_engine.trace_ui_action(
                action_type="inject_plugin_code",
                context={"filename": filename, "code_length": len(code)},
                target="plugin_editor",
                confidence=0.8 if success else 0.2,
                explanation=f"Injected plugin code into editor as {filename}" if success else "Failed to inject code into editor",
                success=success
            )
            action_data["ui_trace_id"] = ui_trace.trace_id

        if success:
            return True, f"✅ I've injected the plugin code into the Editor as {filename}! You can now review and modify it.", action_data
        else:
            return False, f"❌ I couldn't inject the code into the Plugin Editor.", action_data

    def _handle_open_editor(self, intent_analysis: Dict, action_data: Dict, meta_reasoning_engine=None) -> Tuple[bool, str, Dict]:
        """Handle opening/focusing the plugin editor"""
        success = self.focus_editor()
        action_data["actions_taken"].append("focused_plugin_editor")

        if meta_reasoning_engine:
            ui_trace = meta_reasoning_engine.trace_ui_action(
                action_type="focus_plugin_editor",
                context={"user_request": intent_analysis["original_text"]},
                target="plugin_editor_tab",
                confidence=0.9 if success else 0.3,
                explanation="Switched to Plugin Editor tab and focused editor" if success else "Failed to focus Plugin Editor",
                success=success
            )
            action_data["ui_trace_id"] = ui_trace.trace_id

        if success:
            return True, "✅ I've opened the Plugin Editor for you! You can now create or edit plugins.", action_data
        else:
            return False, "❌ I couldn't open the Plugin Editor tab.", action_data

    # Core UI interaction methods

    def load_file(self, filename: str) -> bool:
        """Load a plugin file into the editor"""
        try:
            if self.gui_interface and hasattr(self.gui_interface, 'plugin_editor_tab'):
                # Try to load the file
                file_path = os.path.join(self.plugin_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    self.gui_interface.plugin_editor_tab.set_code_block(content, filename)
                    self.gui_interface.tab_widget.setCurrentWidget(self.gui_interface.plugin_editor_tab)
                    self.current_plugin = filename
                    logger.info(f"✅ Loaded plugin file: {filename}")
                    return True
                else:
                    logger.warning(f"⚠️ Plugin file not found: {file_path}")
                    return False
            else:
                logger.warning("⚠️ No GUI interface available for file loading")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to load file {filename}: {e}")
            return False

    def inject_plugin_code(self, code: str, filename: str = "generated_plugin.aether") -> bool:
        """Inject plugin code into the editor"""
        try:
            if self.gui_interface and hasattr(self.gui_interface, 'inject_plugin_code'):
                success = self.gui_interface.inject_plugin_code(code, filename)
                if success:
                    self.current_plugin = filename
                    logger.info(f"✅ Injected plugin code: {filename}")
                return success
            else:
                logger.warning("⚠️ No GUI interface available for code injection")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to inject code: {e}")
            return False

    def set_code(self, content: str) -> bool:
        """Set editor content directly"""
        try:
            if self.gui_interface and hasattr(self.gui_interface, 'plugin_editor_tab'):
                self.gui_interface.plugin_editor_tab.editor.setPlainText(content)
                logger.info("✅ Set editor content directly")
                return True
            else:
                logger.warning("⚠️ No GUI interface available for setting content")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to set content: {e}")
            return False

    def focus_editor(self) -> bool:
        """Focus the plugin editor tab"""
        try:
            if self.gui_interface and hasattr(self.gui_interface, 'plugin_editor_tab'):
                self.gui_interface.tab_widget.setCurrentWidget(self.gui_interface.plugin_editor_tab)
                self.gui_interface.plugin_editor_tab.focus_editor()
                logger.info("✅ Focused Plugin Editor")
                return True
            else:
                logger.warning("⚠️ No GUI interface available for focusing")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to focus editor: {e}")
            return False

    def activate_plugin(self) -> bool:
        """Activate/test the current plugin"""
        try:
            if self.gui_interface and hasattr(self.gui_interface, 'plugin_editor_tab'):
                # This would trigger the test plugin functionality
                self.gui_interface.plugin_editor_tab.test_plugin()
                logger.info("✅ Activated plugin for testing")
                return True
            else:
                logger.warning("⚠️ No GUI interface available for plugin activation")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to activate plugin: {e}")
            return False

    # Helper methods

    def _find_plugin_file(self, plugin_name: str) -> Optional[str]:
        """Find an existing plugin file"""
        possible_names = [
            f"{plugin_name}.aether",
            f"{plugin_name}.py",
            f"{plugin_name}_plugin.aether",
            f"{plugin_name}_plugin.py"
        ]

        for name in possible_names:
            file_path = os.path.join(self.plugin_dir, name)
            if os.path.exists(file_path):
                return name

        return None

    def _classify_plugin_type(self, plugin_name: str) -> str:
        """Classify plugin type based on name"""
        name = plugin_name.lower()

        if "trainer" in name or "assistant" in name:
            return "assistant_trainer"
        elif "process" in name or "data" in name:
            return "data_processor"
        elif "auto" in name or "schedule" in name:
            return "automation"
        else:
            return "utility"

    # Plugin templates

    def _get_assistant_trainer_template(self) -> str:
        return '''plugin PLUGIN_NAME {
    metadata {
        name: "PLUGIN_NAME"
        version: "1.0.0"
        description: "AI assistant training and enhancement plugin"
        author: "Aetherra System"
        capabilities: ["training", "learning", "assistance"]
    }

    function train_assistant(data, feedback) {
        // Implement assistant training logic
        log("Training assistant with new data")
        return {"status": "training_complete", "improvements": data.length}
    }

    function provide_assistance(query) {
        // Enhanced assistance with training data
        log("Providing trained assistance for: " + query)
        return {"response": "Enhanced response based on training", "confidence": 0.9}
    }

    function get_training_status() {
        return {"trained": true, "accuracy": 0.95, "sessions": 42}
    }
}'''

    def _get_data_processor_template(self) -> str:
        return '''plugin PLUGIN_NAME {
    metadata {
        name: "PLUGIN_NAME"
        version: "1.0.0"
        description: "Data processing and analysis plugin"
        author: "Aetherra System"
        capabilities: ["data_processing", "analysis", "transformation"]
    }

    function process_data(input_data, options) {
        // Process and transform data
        log("Processing data with options: " + JSON.stringify(options))

        let processed = input_data.map(item => {
            return {
                ...item,
                processed_at: new Date(),
                processed_by: "PLUGIN_NAME"
            }
        })

        return {"data": processed, "count": processed.length}
    }

    function analyze_patterns(data) {
        // Analyze data for patterns
        return {"patterns": ["trend_1", "trend_2"], "confidence": 0.85}
    }

    function export_results(data, format) {
        return {"exported": true, "format": format, "size": data.length}
    }
}'''

    def _get_automation_template(self) -> str:
        return '''plugin PLUGIN_NAME {
    metadata {
        name: "PLUGIN_NAME"
        version: "1.0.0"
        description: "Task automation and scheduling plugin"
        author: "Aetherra System"
        capabilities: ["automation", "scheduling", "task_management"]
    }

    function schedule_task(task, schedule) {
        // Schedule automated task
        log("Scheduling task: " + task.name + " for " + schedule)
        return {"task_id": generateId(), "scheduled": true, "next_run": schedule}
    }

    function execute_automation(task_id) {
        // Execute automated task
        log("Executing automation task: " + task_id)
        return {"executed": true, "result": "success", "duration": "2.3s"}
    }

    function get_automation_status() {
        return {"active_tasks": 3, "completed": 15, "success_rate": 0.94}
    }

    function generateId() {
        return "task_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9)
    }
}'''

    def _get_utility_template(self) -> str:
        return '''plugin PLUGIN_NAME {
    metadata {
        name: "PLUGIN_NAME"
        version: "1.0.0"
        description: "General utility plugin"
        author: "Aetherra System"
        capabilities: ["utility", "helper", "tools"]
    }

    function main(input, options) {
        // Main plugin functionality
        log("PLUGIN_NAME executing with input: " + JSON.stringify(input))

        return {
            "status": "success",
            "result": "Plugin executed successfully",
            "input_received": input,
            "timestamp": new Date().toISOString()
        }
    }

    function get_info() {
        return {
            "name": "PLUGIN_NAME",
            "status": "active",
            "version": "1.0.0",
            "last_used": new Date().toISOString()
        }
    }

    function test() {
        return {"test": "passed", "message": "PLUGIN_NAME is working correctly"}
    }
}'''


def import_time():
    """Helper to import time module"""
    import time
    return time
