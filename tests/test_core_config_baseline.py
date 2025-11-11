#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Baseline tests for Aetherra.core.config to seed coverage."""

from pathlib import Path

from Aetherra.core.config import Config


def test_config_version_present():
    assert hasattr(Config, "VERSION")
    assert isinstance(Config.VERSION, str)
    assert len(Config.VERSION) > 0


def test_config_project_root_is_path():
    assert hasattr(Config, "PROJECT_ROOT")
    assert isinstance(Config.PROJECT_ROOT, Path)


def test_config_data_dir_defined():
    assert hasattr(Config, "DATA_DIR")
    assert isinstance(Config.DATA_DIR, Path)


def test_config_plugins_dir_defined():
    assert hasattr(Config, "PLUGINS_DIR")
    assert isinstance(Config.PLUGINS_DIR, Path)


def test_config_defaults():
    assert hasattr(Config, "DEFAULT_MODEL")
    assert isinstance(Config.DEFAULT_MODEL, str)
    assert hasattr(Config, "MAX_TOKENS")
    assert isinstance(Config.MAX_TOKENS, int)
    assert Config.MAX_TOKENS > 0
    assert hasattr(Config, "TEMPERATURE")
    assert isinstance(Config.TEMPERATURE, int | float)
