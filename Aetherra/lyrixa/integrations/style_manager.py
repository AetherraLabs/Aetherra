#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
JavaScript Style Manager for Lyrixa Web Panels
Prevents style redeclaration errors and manages dynamic styling
"""

# Standard library imports
import logging
from typing import Optional, Set

logger = logging.getLogger(__name__)


class JavaScriptStyleManager:
    """
    Manages JavaScript styles to prevent redeclaration errors
    """

    def __init__(self):
        self.declared_styles: Set[str] = set()
        self.style_counter = 0

    def generate_unique_style_id(self, base_name: str = "style") -> str:
        """Generate a unique style variable name"""
        self.style_counter += 1
        unique_id = f"{base_name}_{self.style_counter}"
        self.declared_styles.add(unique_id)
        return unique_id

    def sanitize_css_for_qt(self, css_content: str) -> str:
        """Sanitize CSS content to be compatible with Qt's CSS subset"""
        # Remove or replace CSS3 properties that Qt doesn't support
        css_replacements = {
            "box-shadow": "/* box-shadow not supported in Qt */",
            "text-shadow": "/* text-shadow not supported in Qt */",
            "border-radius": "border-radius",  # This one usually works
            "rgba(": "rgb(",  # Convert rgba to rgb
            "hsla(": "hsl(",  # Convert hsla to hsl
        }

        sanitized_css = css_content
        for unsupported, replacement in css_replacements.items():
            if unsupported in sanitized_css:
                if unsupported.startswith("box-shadow") or unsupported.startswith(
                    "text-shadow"
                ):
                    # Remove entire property declarations
                    # Standard library imports
                    import re

                    pattern = rf"{unsupported}[^;]*;"
                    sanitized_css = re.sub(pattern, replacement, sanitized_css)
                else:
                    sanitized_css = sanitized_css.replace(unsupported, replacement)

        return sanitized_css

    def create_safe_style_injection(
        self,
        css_content: str,
        style_id: Optional[str] = None,
        sanitize_for_qt: bool = True,
    ) -> str:
        """Create safe JavaScript code for style injection without redeclaration"""
        if style_id is None:
            style_id = self.generate_unique_style_id()

        # Sanitize CSS if requested
        if sanitize_for_qt:
            css_content = self.sanitize_css_for_qt(css_content)

        # Use a safer approach that doesn't redeclare variables
        safe_js = f"""
(function() {{
    const styleId = '{style_id}';
    let existingStyle = document.getElementById(styleId);

    if (existingStyle) {{
        existingStyle.remove();
    }}

    const styleElement = document.createElement('style');
    styleElement.id = styleId;
    styleElement.textContent = `{css_content}`;
    document.head.appendChild(styleElement);
}})();
"""
        return safe_js

    def clear_declared_styles(self):
        """Clear the set of declared styles"""
        self.declared_styles.clear()
        self.style_counter = 0
        logger.debug("[STYLE] Cleared declared styles")


# Global style manager
style_manager = JavaScriptStyleManager()


def get_style_manager():
    """Get the global style manager instance"""
    return style_manager


def create_safe_css_injection(
    css_content: str, component_name: str = "component"
) -> str:
    """Create safe CSS injection JavaScript code"""
    manager = get_style_manager()
    style_id = f"lyrixa_{component_name}_{manager.style_counter}"
    return manager.create_safe_style_injection(css_content, style_id)


# Common CSS fixes for the personality system
PERSONALITY_CSS_FIX = """
/* Lyrixa Personality System CSS */
.personality-container {
    position: relative;
    z-index: 1000;
}

.personality-theme {
    transition: all 0.3s ease-in-out;
}

.neutral-theme {
    background: linear-gradient(135deg, #2c3e50, #3498db);
}

.excited-theme {
    background: linear-gradient(135deg, #f39c12, #e74c3c);
}

.focused-theme {
    background: linear-gradient(135deg, #27ae60, #2980b9);
}

.creative-theme {
    background: linear-gradient(135deg, #9b59b6, #e91e63);
}
"""


def get_personality_css_fix() -> str:
    """Get the safe CSS injection for personality themes"""
    return create_safe_css_injection(PERSONALITY_CSS_FIX, "personality_theme")


# Plugin UI CSS fixes
PLUGIN_UI_CSS_FIX = """
/* Plugin UI CSS Fixes */
.plugin-panel {
    border-radius: 8px;
    margin: 10px;
    padding: 15px;
    /* box-shadow removed for Qt compatibility */
}

.plugin-header {
    font-weight: bold;
    margin-bottom: 10px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 5px;
}

.plugin-content {
    line-height: 1.6;
}

.memory-status {
    color: #27ae60;
    font-family: monospace;
}

.network-status {
    color: #3498db;
    font-family: monospace;
}
"""


def get_plugin_ui_css_fix() -> str:
    """Get the safe CSS injection for plugin UI"""
    return create_safe_css_injection(PLUGIN_UI_CSS_FIX, "plugin_ui")


if __name__ == "__main__":
    # Test the style manager
    manager = get_style_manager()

    test_css = "body { background: blue; }"
    safe_js = manager.create_safe_style_injection(test_css)
    print("Safe JavaScript:")
    print(safe_js)

    print("\nPersonality CSS Fix:")
    print(get_personality_css_fix())
