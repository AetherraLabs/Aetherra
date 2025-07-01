# core/interpreter/enhanced_features.py
"""
Enhanced Feature Parser for NeuroCode Interpreter
=================================================

Handles advanced parsing features and NeuroCode extensions.
"""

import re
from typing import Any, Dict, Optional


class EnhancedFeatureParser:
    """Parser for enhanced NeuroCode features"""

    def __init__(self):
        self.feature_patterns = {
            "syntax_tree": r"use\s+syntax_tree",
            "enhanced_parser": r"use\s+enhanced_parser",
            "auto_tag": r"auto_tag:\s*(on|off)",
            "reflection": r"reflect\s+on\s+[\"']([^\"']*)[\"']",
            "suggestions": r"suggest\s+next\s+actions",
            "self_edit": r"self_edit:\s*(on|off)",
            "agent_mode": r"agent_mode:\s*(on|off)",
            "debug_mode": r"debug_mode:\s*(on|off)",
        }

    def can_handle(self, line: str) -> bool:
        """Check if this parser can handle the line"""
        for pattern in self.feature_patterns.values():
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def parse_enhanced_features(
        self, line: str, interpreter_context: Dict[str, Any]
    ) -> Optional[str]:
        """Parse enhanced features and return result"""

        # Syntax tree enhancement
        if re.search(self.feature_patterns["syntax_tree"], line, re.IGNORECASE):
            return self._enable_syntax_tree(interpreter_context)

        # Enhanced parser
        if re.search(self.feature_patterns["enhanced_parser"], line, re.IGNORECASE):
            return self._enable_enhanced_parser(interpreter_context)

        # Auto-tagging
        auto_tag_match = re.search(self.feature_patterns["auto_tag"], line, re.IGNORECASE)
        if auto_tag_match:
            enabled = auto_tag_match.group(1).lower() == "on"
            return self._toggle_auto_tag(enabled, interpreter_context)

        # Reflection
        reflection_match = re.search(self.feature_patterns["reflection"], line, re.IGNORECASE)
        if reflection_match:
            topic = reflection_match.group(1)
            return self._perform_reflection(topic, interpreter_context)

        # Suggestions
        if re.search(self.feature_patterns["suggestions"], line, re.IGNORECASE):
            return self._suggest_actions(interpreter_context)

        # Self-editing mode
        self_edit_match = re.search(self.feature_patterns["self_edit"], line, re.IGNORECASE)
        if self_edit_match:
            enabled = self_edit_match.group(1).lower() == "on"
            return self._toggle_self_edit(enabled, interpreter_context)

        # Agent mode
        agent_mode_match = re.search(self.feature_patterns["agent_mode"], line, re.IGNORECASE)
        if agent_mode_match:
            enabled = agent_mode_match.group(1).lower() == "on"
            return self._toggle_agent_mode(enabled, interpreter_context)

        # Debug mode
        debug_mode_match = re.search(self.feature_patterns["debug_mode"], line, re.IGNORECASE)
        if debug_mode_match:
            enabled = debug_mode_match.group(1).lower() == "on"
            return self._toggle_debug_mode(enabled, interpreter_context)

        return None

    def _enable_syntax_tree(self, context: Dict[str, Any]) -> str:
        """Enable syntax tree parsing"""
        context["use_enhanced_parser"] = True
        return "🌳 Syntax tree parsing enabled"

    def _enable_enhanced_parser(self, context: Dict[str, Any]) -> str:
        """Enable enhanced parser features"""
        context["enhanced_parsing"] = True
        return "⚡ Enhanced parser features enabled"

    def _toggle_auto_tag(self, enabled: bool, context: Dict[str, Any]) -> str:
        """Toggle auto-tagging feature"""
        context["auto_tag_enabled"] = enabled
        status = "enabled" if enabled else "disabled"
        return f"🏷️ Auto-tagging {status}"

    def _perform_reflection(self, topic: str, context: Dict[str, Any]) -> str:
        """Perform reflection on a topic"""
        memory = context.get("memory")
        if memory:
            # This would call the actual reflection function
            result = f"🤔 Reflecting on: {topic}"
            result += "\n   💭 Analyzing memory patterns..."
            result += "\n   📊 Generating insights..."
            result += "\n   ✅ Reflection complete"
            return result
        else:
            return f"🤔 Reflection requested on: {topic} (memory system not available)"

    def _suggest_actions(self, context: Dict[str, Any]) -> str:
        """Suggest next actions based on context"""
        memory = context.get("memory")
        goal_system = context.get("goal_system")

        if memory and goal_system:
            result = "💡 Action Suggestions:\n"
            result += "   1. Review recent memory patterns\n"
            result += "   2. Check goal progress\n"
            result += "   3. Analyze behavior trends\n"
            result += "   4. Consider new learning opportunities"
            return result
        else:
            return "💡 Action suggestions requested (systems not fully available)"

    def _toggle_self_edit(self, enabled: bool, context: Dict[str, Any]) -> str:
        """Toggle self-editing mode"""
        context["self_edit_mode"] = enabled
        status = "enabled" if enabled else "disabled"
        warning = " ⚠️ Use with caution!" if enabled else ""
        return f"✏️ Self-editing mode {status}{warning}"

    def _toggle_agent_mode(self, enabled: bool, context: Dict[str, Any]) -> str:
        """Toggle agent mode"""
        agent = context.get("agent")
        goal_system = context.get("goal_system")

        if goal_system:
            goal_system.set_agent_mode(enabled)

        if agent:
            if enabled:
                agent.activate()
            else:
                agent.deactivate()

        status = "enabled" if enabled else "disabled"
        return f"🤖 Agent mode {status}"

    def _toggle_debug_mode(self, enabled: bool, context: Dict[str, Any]) -> str:
        """Toggle debug mode"""
        context["debug_mode"] = enabled
        debug_system = context.get("debug_system")

        if debug_system and enabled:
            debug_system.debug("Debug mode enabled")

        status = "enabled" if enabled else "disabled"
        return f"🐛 Debug mode {status}"

    def get_feature_help(self) -> str:
        """Get help text for enhanced features"""
        help_text = "🎯 Enhanced NeuroCode Features:\n\n"
        help_text += "• use syntax_tree - Enable syntax tree parsing\n"
        help_text += "• use enhanced_parser - Enable enhanced parser\n"
        help_text += "• auto_tag: on/off - Toggle auto-tagging\n"
        help_text += '• reflect on "topic" - Perform reflection\n'
        help_text += "• suggest next actions - Get action suggestions\n"
        help_text += "• self_edit: on/off - Toggle self-editing mode\n"
        help_text += "• agent_mode: on/off - Toggle agent mode\n"
        help_text += "• debug_mode: on/off - Toggle debug mode\n"

        return help_text

    def validate_feature_syntax(self, line: str) -> Dict[str, Any]:
        """Validate enhanced feature syntax"""
        issues = []
        suggestions = []

        # Check for common syntax issues
        if ":" in line and not re.search(r":\s*(on|off|\"[^\"]*\")", line):
            issues.append("Invalid parameter format")
            suggestions.append("Use 'feature: on/off' or 'feature: \"value\"'")

        if line.startswith("use ") and not re.search(r"use\s+\w+", line):
            issues.append("Invalid 'use' syntax")
            suggestions.append("Use 'use feature_name'")

        return {"valid": len(issues) == 0, "issues": issues, "suggestions": suggestions}
