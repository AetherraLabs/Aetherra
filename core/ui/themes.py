"""
🎨 Theme Management System
=========================

Advanced theming system for LyrixaUI with customizable color schemes,
typography, and visual styles.
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class UITheme(Enum):
    """Available UI themes for Lyrixa"""

    DARK = "dark"
    LIGHT = "light"
    NEON = "neon"
    CLASSIC = "classic"
    MATRIX = "matrix"
    CYBERPUNK = "cyberpunk"


@dataclass
class UIColors:
    """Color scheme for UI components"""

    # Primary colors
    primary: str = "#00ff88"
    secondary: str = "#0088ff"
    accent: str = "#ff8800"

    # Background colors
    background: str = "#000011"
    surface: str = "#001122"
    overlay: str = "#002233"

    # Text colors
    text: str = "#ffffff"
    text_secondary: str = "#cccccc"
    text_muted: str = "#888888"

    # Status colors
    error: str = "#ff0044"
    warning: str = "#ffaa00"
    success: str = "#00ff44"
    info: str = "#0088ff"

    # Interactive colors
    hover: str = "#004455"
    active: str = "#006677"
    disabled: str = "#333333"

    # Borders and separators
    border: str = "#444444"
    separator: str = "#222222"


@dataclass
class Typography:
    """Typography configuration"""

    font_family: str = "Fira Code"
    font_size: int = 14
    line_height: float = 1.5
    letter_spacing: float = 0.0

    # Font weights
    light: int = 300
    regular: int = 400
    medium: int = 500
    bold: int = 700


@dataclass
class Spacing:
    """Spacing and layout configuration"""

    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class ThemeConfig:
    """Complete theme configuration"""

    name: str
    colors: UIColors
    typography: Typography
    spacing: Spacing
    animations_enabled: bool = True
    shadow_enabled: bool = True


class ThemeManager:
    """Manages UI themes and customization"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.aethercode/themes")
        self.current_theme = UITheme.DARK
        self.custom_themes: Dict[str, ThemeConfig] = {}
        self._load_default_themes()
        self._load_custom_themes()

    def _load_default_themes(self):
        """Load built-in default themes"""
        self.default_themes = {
            UITheme.DARK: ThemeConfig(
                name="Dark",
                colors=UIColors(),
                typography=Typography(),
                spacing=Spacing(),
            ),
            UITheme.LIGHT: ThemeConfig(
                name="Light",
                colors=UIColors(
                    primary="#0066cc",
                    secondary="#6600cc",
                    accent="#cc6600",
                    background="#ffffff",
                    surface="#f8f9fa",
                    overlay="#e9ecef",
                    text="#212529",
                    text_secondary="#495057",
                    text_muted="#6c757d",
                    hover="#e9ecef",
                    active="#dee2e6",
                    border="#dee2e6",
                    separator="#e9ecef",
                ),
                typography=Typography(),
                spacing=Spacing(),
            ),
            UITheme.NEON: ThemeConfig(
                name="Neon",
                colors=UIColors(
                    primary="#00ffff",
                    secondary="#ff00ff",
                    accent="#ffff00",
                    background="#000000",
                    surface="#0a0a0a",
                    overlay="#1a1a1a",
                    text="#00ffff",
                    text_secondary="#ff00ff",
                    success="#00ff00",
                    error="#ff0066",
                    warning="#ffaa00",
                ),
                typography=Typography(font_family="Orbitron"),
                spacing=Spacing(),
                animations_enabled=True,
                shadow_enabled=True,
            ),
            UITheme.MATRIX: ThemeConfig(
                name="Matrix",
                colors=UIColors(
                    primary="#00ff41",
                    secondary="#008f11",
                    accent="#41ff00",
                    background="#000000",
                    surface="#001100",
                    overlay="#002200",
                    text="#00ff41",
                    text_secondary="#008f11",
                    success="#00ff41",
                    error="#ff4141",
                    warning="#ffff00",
                ),
                typography=Typography(font_family="Courier New"),
                spacing=Spacing(),
            ),
            UITheme.CYBERPUNK: ThemeConfig(
                name="Cyberpunk",
                colors=UIColors(
                    primary="#ff0080",
                    secondary="#0080ff",
                    accent="#ffff00",
                    background="#0d001a",
                    surface="#1a0033",
                    overlay="#26004d",
                    text="#ff0080",
                    text_secondary="#0080ff",
                    success="#00ff80",
                    error="#ff4040",
                    warning="#ff8000",
                ),
                typography=Typography(font_family="Share Tech Mono"),
                spacing=Spacing(),
            ),
        }

    def _load_custom_themes(self):
        """Load custom themes from config directory"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            return

        for filename in os.listdir(self.config_dir):
            if filename.endswith(".json"):
                try:
                    theme_path = os.path.join(self.config_dir, filename)
                    with open(theme_path) as f:
                        theme_data = json.load(f)

                    theme_name = theme_data.get("name", filename[:-5])
                    theme_config = self._dict_to_theme_config(theme_data)
                    self.custom_themes[theme_name] = theme_config

                except Exception as e:
                    print(f"Warning: Failed to load custom theme {filename}: {e}")

    def _dict_to_theme_config(self, data: Dict[str, Any]) -> ThemeConfig:
        """Convert dictionary to ThemeConfig object"""
        colors_data = data.get("colors", {})
        typography_data = data.get("typography", {})
        spacing_data = data.get("spacing", {})

        return ThemeConfig(
            name=data.get("name", "Custom"),
            colors=UIColors(**colors_data),
            typography=Typography(**typography_data),
            spacing=Spacing(**spacing_data),
            animations_enabled=data.get("animations_enabled", True),
            shadow_enabled=data.get("shadow_enabled", True),
        )

    def get_current_theme(self) -> ThemeConfig:
        """Get the currently active theme configuration"""
        if isinstance(self.current_theme, UITheme):
            return self.default_themes[self.current_theme]
        else:
            return self.custom_themes.get(
                self.current_theme, self.default_themes[UITheme.DARK]
            )

    def set_theme(self, theme: UITheme | str):
        """Set the current theme"""
        if isinstance(theme, UITheme) and theme in self.default_themes:
            self.current_theme = theme
        elif isinstance(theme, str) and theme in self.custom_themes:
            self.current_theme = theme
        else:
            raise ValueError(f"Unknown theme: {theme}")

    def list_themes(self) -> Dict[str, str]:
        """List all available themes"""
        themes = {}

        # Add default themes
        for theme in UITheme:
            themes[theme.value] = self.default_themes[theme].name

        # Add custom themes
        for name, config in self.custom_themes.items():
            themes[name] = config.name

        return themes

    def create_custom_theme(
        self,
        name: str,
        base_theme: UITheme = UITheme.DARK,
        color_overrides: Optional[Dict[str, str]] = None,
    ) -> ThemeConfig:
        """Create a new custom theme based on an existing theme"""
        base_config = self.default_themes[base_theme]

        # Create new colors with overrides
        colors_dict = base_config.colors.__dict__.copy()
        if color_overrides:
            colors_dict.update(color_overrides)

        new_theme = ThemeConfig(
            name=name,
            colors=UIColors(**colors_dict),
            typography=base_config.typography,
            spacing=base_config.spacing,
            animations_enabled=base_config.animations_enabled,
            shadow_enabled=base_config.shadow_enabled,
        )

        self.custom_themes[name] = new_theme
        return new_theme

    def save_custom_theme(self, name: str):
        """Save a custom theme to disk"""
        if name not in self.custom_themes:
            raise ValueError(f"Custom theme '{name}' not found")

        theme = self.custom_themes[name]
        theme_data = {
            "name": theme.name,
            "colors": theme.colors.__dict__,
            "typography": theme.typography.__dict__,
            "spacing": theme.spacing.__dict__,
            "animations_enabled": theme.animations_enabled,
            "shadow_enabled": theme.shadow_enabled,
        }

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

        theme_path = os.path.join(self.config_dir, f"{name}.json")
        with open(theme_path, "w") as f:
            json.dump(theme_data, f, indent=2)

    def delete_custom_theme(self, name: str):
        """Delete a custom theme"""
        if name in self.custom_themes:
            del self.custom_themes[name]

            theme_path = os.path.join(self.config_dir, f"{name}.json")
            if os.path.exists(theme_path):
                os.remove(theme_path)

    def export_theme(self, theme_name: str, export_path: str):
        """Export a theme to a file"""
        if theme_name in self.custom_themes:
            theme = self.custom_themes[theme_name]
        elif hasattr(UITheme, theme_name.upper()):
            theme = self.default_themes[UITheme[theme_name.upper()]]
        else:
            raise ValueError(f"Theme '{theme_name}' not found")

        theme_data = {
            "name": theme.name,
            "colors": theme.colors.__dict__,
            "typography": theme.typography.__dict__,
            "spacing": theme.spacing.__dict__,
            "animations_enabled": theme.animations_enabled,
            "shadow_enabled": theme.shadow_enabled,
        }

        with open(export_path, "w") as f:
            json.dump(theme_data, f, indent=2)

    def import_theme(self, import_path: str) -> str:
        """Import a theme from a file"""
        with open(import_path) as f:
            theme_data = json.load(f)

        theme_name = theme_data.get("name", "Imported Theme")
        theme_config = self._dict_to_theme_config(theme_data)

        self.custom_themes[theme_name] = theme_config
        return theme_name
