#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Integration tests for Aetherra core components working together."""

import pytest

from Aetherra.core.aetherra_interpreter import AetherraInterpreter
from Aetherra.core.aetherra_parser import (
    AetherraLexer,
    AetherraParser,
    Token,
    TokenType,
)
from Aetherra.core.config import Config


class TestCoreIntegration:
    """Test integration between config, parser, and interpreter."""

    def test_config_version_accessible(self):
        """Test Config.VERSION is accessible."""
        assert hasattr(Config, "VERSION")
        assert isinstance(Config.VERSION, str)
        assert len(Config.VERSION) > 0

    def test_config_project_root_exists(self):
        """Test Config.PROJECT_ROOT is a valid path."""
        assert hasattr(Config, "PROJECT_ROOT")
        assert Config.PROJECT_ROOT is not None

    def test_config_paths_consistency(self):
        """Test that config paths are consistent."""
        assert (
            Config.DATA_DIR.parent == Config.PROJECT_ROOT
            or Config.DATA_DIR == Config.PROJECT_ROOT / "data"
        )
        assert (
            Config.PLUGINS_DIR.parent == Config.PROJECT_ROOT
            or Config.PLUGINS_DIR == Config.PROJECT_ROOT / "plugins"
        )

    def test_lexer_parser_integration_simple_goal(self):
        """Test lexer tokenization followed by parser goal parsing."""
        source = "goal: test objective"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        parser = AetherraParser(tokens)
        node = parser.parse_goal()

        assert node.type == "goal"
        assert "test" in node.objective
        assert "objective" in node.objective

    def test_lexer_parser_integration_with_priority(self):
        """Test full pipeline with priority parsing."""
        source = "goal: improve performance priority: high"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        parser = AetherraParser(tokens)
        node = parser.parse_goal()

        assert node.priority == "high"

    def test_interpreter_executes_parsed_content(self):
        """Test interpreter can execute content after parsing."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal: test")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_config_default_model_value(self):
        """Test Config default model is set."""
        assert hasattr(Config, "DEFAULT_MODEL")
        assert isinstance(Config.DEFAULT_MODEL, str)
        assert (
            "gpt" in Config.DEFAULT_MODEL.lower()
            or "turbo" in Config.DEFAULT_MODEL.lower()
        )

    def test_config_max_tokens_positive(self):
        """Test Config.MAX_TOKENS is positive."""
        assert Config.MAX_TOKENS > 0
        assert isinstance(Config.MAX_TOKENS, int)

    def test_config_temperature_in_range(self):
        """Test Config.TEMPERATURE is reasonable."""
        assert 0.0 <= Config.TEMPERATURE <= 2.0
        assert isinstance(Config.TEMPERATURE, int | float)

    def test_parser_handles_multiline_with_newlines(self):
        """Test parser with multiple newlines."""
        source = "goal: first\n\nagent: second"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        # Should have multiple NEWLINE tokens
        newline_count = sum(1 for t in tokens if t.type == TokenType.NEWLINE)
        assert newline_count >= 2

    def test_interpreter_handles_empty_after_whitespace(self):
        """Test interpreter with whitespace-only input."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("   ")

        assert isinstance(result, str)

    def test_lexer_preserves_line_column_info(self):
        """Test lexer maintains line and column information."""
        source = "goal: test\nagent: on"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        # Check that tokens have line info
        assert all(hasattr(t, "line") for t in tokens)
        assert all(hasattr(t, "column") for t in tokens)
        assert any(t.line == 2 for t in tokens)  # Second line exists

    def test_config_memory_settings_defined(self):
        """Test Config memory settings are defined."""
        assert hasattr(Config, "MAX_MEMORY_ENTRIES")
        assert hasattr(Config, "MEMORY_CLEANUP_THRESHOLD")
        assert Config.MAX_MEMORY_ENTRIES > 0
        assert 0.0 < Config.MEMORY_CLEANUP_THRESHOLD <= 1.0

    def test_config_plugin_settings_defined(self):
        """Test Config plugin settings are defined."""
        assert hasattr(Config, "PLUGIN_TIMEOUT")
        assert hasattr(Config, "MAX_PLUGINS")
        assert Config.PLUGIN_TIMEOUT > 0
        assert Config.MAX_PLUGINS > 0

    def test_parser_token_stream_consistency(self):
        """Test parser maintains consistent token stream."""
        tokens = [
            Token(TokenType.GOAL, "goal", 1, 1),
            Token(TokenType.COLON, ":", 1, 5),
            Token(TokenType.IDENTIFIER, "test", 1, 7),
        ]
        parser = AetherraParser(tokens)

        initial_position = parser.position
        parser.advance()
        assert parser.position == initial_position + 1

    def test_interpreter_returns_string_type(self):
        """Test interpreter always returns string type."""
        interpreter = AetherraInterpreter()
        results = [
            interpreter.execute("test"),
            interpreter.execute("goal: objective"),
            interpreter.execute(""),
        ]

        assert all(isinstance(r, str) for r in results)

    def test_lexer_parser_agent_command_integration(self):
        """Test full pipeline for agent command."""
        source = "agent: analyze data"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        parser = AetherraParser(tokens)
        node = parser.parse_agent()

        assert node.type == "agent"
        assert "analyze" in node.command
        assert "data" in node.command
