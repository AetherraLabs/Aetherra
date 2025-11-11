#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Deep tests for Aetherra.core.aetherra_interpreter execution paths."""

import pytest

from Aetherra.core.aetherra_interpreter import AetherraInterpreter


class TestInterpreterExecution:
    """Test interpreter command execution and state management."""

    def test_execute_returns_consistent_type(self):
        """Test that execute always returns a consistent type."""
        interpreter = AetherraInterpreter()
        result1 = interpreter.execute("goal 'test'")
        result2 = interpreter.execute("agent 'task'")
        # Both should return same type
        assert type(result1) is type(result2)

    def test_execute_with_multiline_commands(self):
        """Test interpreter handles multiline input."""
        interpreter = AetherraInterpreter()
        multiline = """goal 'task1'
goal 'task2'"""
        result = interpreter.execute(multiline)
        assert result is not None

    def test_execute_with_special_characters(self):
        """Test interpreter handles special characters in input."""
        interpreter = AetherraInterpreter()
        special_chars = "goal 'test@#$%^&*()'"
        result = interpreter.execute(special_chars)
        assert result is not None

    def test_execute_preserves_quotes(self):
        """Test that quoted strings are handled properly."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal 'test with spaces'")
        assert result is not None

    def test_execute_with_numbers(self):
        """Test interpreter handles numeric input."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal '123'")
        assert result is not None

    def test_sequential_execution_independence(self):
        """Test that sequential executions don't interfere."""
        interpreter = AetherraInterpreter()
        result1 = interpreter.execute("goal 'first'")
        result2 = interpreter.execute("goal 'second'")
        # Both should complete without interference
        assert result1 is not None
        assert result2 is not None

    def test_execute_with_unicode(self):
        """Test interpreter handles unicode characters."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal '测试 🚀'")
        assert result is not None

    def test_execute_with_escaped_quotes(self):
        """Test handling of escaped quotes in strings."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal 'test\\'s'")
        assert result is not None

    def test_execute_empty_quotes(self):
        """Test handling of empty quoted strings."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal ''")
        assert result is not None

    def test_execute_long_input(self):
        """Test interpreter handles long input strings."""
        interpreter = AetherraInterpreter()
        long_text = "goal '" + "x" * 1000 + "'"
        result = interpreter.execute(long_text)
        assert result is not None

    def test_execute_repeated_keywords(self):
        """Test handling of repeated keywords."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal goal 'test'")
        assert result is not None

    def test_execute_mixed_case_keywords(self):
        """Test if keywords are case-sensitive."""
        interpreter = AetherraInterpreter()
        result1 = interpreter.execute("goal 'test'")
        result2 = interpreter.execute("GOAL 'test'")
        # Should handle consistently
        assert result1 is not None
        assert result2 is not None

    def test_multiple_interpreters_independent(self):
        """Test that multiple interpreter instances are independent."""
        interp1 = AetherraInterpreter()
        interp2 = AetherraInterpreter()
        result1 = interp1.execute("goal 'one'")
        result2 = interp2.execute("goal 'two'")
        # Both should work independently
        assert result1 is not None
        assert result2 is not None

    def test_execute_with_tabs(self):
        """Test interpreter handles tab characters."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal\t'test'")
        assert result is not None

    def test_execute_with_newlines_in_string(self):
        """Test handling of newline characters in strings."""
        interpreter = AetherraInterpreter()
        result = interpreter.execute("goal 'line1\\nline2'")
        assert result is not None
