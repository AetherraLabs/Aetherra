"""Minimal Sphinx configuration for Aetherra documentation builds."""

from __future__ import annotations

project = "Aetherra"
author = "Aetherra Labs and Contributors"
extensions: list[str] = []
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "alabaster"
master_doc = "index"
