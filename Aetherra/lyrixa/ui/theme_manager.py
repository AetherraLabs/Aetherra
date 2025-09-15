#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lyrixa UI Theme Manager

Centralized theming system for Lyrixa & plugin GUIs.
Loads JSON theme definitions and renders a composite QSS stylesheet.

Phase 1 features:
- Load a primary theme JSON (cyber default)
- Provide palette + font accessors
- Variable substitution inside QSS templates
- Simple API: ThemeManager.load(); theme_manager.apply(app)

Later phases can add:
- Runtime theme switching
- Per-component overrides
- Persisted user selection
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

THEME_ENV_VAR = "LYRIXA_THEME"
DEFAULT_THEME_NAME = "cyber"


@dataclass
class Theme:
    name: str
    palette: dict[str, str]
    fonts: dict[str, str] = field(default_factory=dict)
    effects: dict[str, Any] = field(default_factory=dict)
    qss_fragments: dict[str, str] = field(default_factory=dict)

    def resolve(self, text: str) -> str:
        # Simple ${var} substitution
        for k, v in self.palette.items():
            text = text.replace(f"${{{k}}}", v)
        for k, v in self.fonts.items():
            text = text.replace(f"${{font_{k}}}", v)
        return text

    def color(self, key: str, default: str | None = None) -> str | None:
        return self.palette.get(key, default)

    def font(self, key: str, default: str | None = None) -> str | None:
        return self.fonts.get(key, default)


class ThemeManager:
    def __init__(self, themes_dir: Path | None = None):
        self.themes_dir = themes_dir or Path(__file__).parent / "themes"
        self.active: Theme | None = None

    def load(self, name: str | None = None) -> Theme:
        name = name or DEFAULT_THEME_NAME
        path = self.themes_dir / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Theme '{name}' not found: {path}")
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        theme = Theme(
            name=name,
            palette=raw.get("palette", {}),
            fonts=raw.get("fonts", {}),
            effects=raw.get("effects", {}),
            qss_fragments=raw.get("qss", {}),
        )
        self.active = theme
        return theme

    def build_stylesheet(self) -> str:
        if not self.active:
            return ""
        t = self.active
        parts = []
        # Base variables (exposed as comments for readability)
        parts.append(f"/* Lyrixa Theme: {t.name} */")
        # Core QSS fragments
        for key, frag in t.qss_fragments.items():
            try:
                parts.append(t.resolve(frag))
            except Exception as exc:
                logger.debug("[THEME] Failed fragment %s: %s", key, exc)
        return "\n\n".join(parts)

    def apply(self, app) -> None:
        try:
            qss = self.build_stylesheet()
            app.setStyleSheet(qss)
        except Exception as exc:
            logger.warning("[THEME] Failed applying theme: %s", exc)

    # Convenience passthroughs
    def color(self, key: str, default: str | None = None) -> str | None:
        return self.active.color(key, default) if self.active else default

    def font(self, key: str, default: str | None = None) -> str | None:
        return self.active.font(key, default) if self.active else default


# Convenience singleton
_theme_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_active_theme() -> Theme | None:
    tm = get_theme_manager()
    return tm.active


if __name__ == "__main__":
    tm = get_theme_manager()
    tm.load()
    print(tm.build_stylesheet()[:500])
