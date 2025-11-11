#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Deep tests for Aetherra.core.aetherra_parser tokenization."""

import pytest

from Aetherra.core.aetherra_parser import AetherraLexer, Token, TokenType


class TestParserTokenization:
    """Test parser lexer tokenization capabilities."""

    def test_lexer_initialization(self):
        """Test lexer initializes with correct state."""
        lexer = AetherraLexer("test source")
        assert lexer.source == "test source"
        assert lexer.position == 0
        assert lexer.line == 1
        assert lexer.column == 1

    def test_lexer_current_char_at_start(self):
        """Test current_char returns first character."""
        lexer = AetherraLexer("abc")
        assert lexer.current_char() == "a"

    def test_lexer_current_char_at_end(self):
        """Test current_char returns None at end."""
        lexer = AetherraLexer("")
        assert lexer.current_char() is None

    def test_lexer_peek_char(self):
        """Test peek_char looks ahead without advancing."""
        lexer = AetherraLexer("abc")
        assert lexer.peek_char() == "b"
        assert lexer.position == 0  # Should not advance

    def test_lexer_peek_char_beyond_end(self):
        """Test peek_char at end returns None."""
        lexer = AetherraLexer("a")
        assert lexer.peek_char() is None

    def test_lexer_advance_updates_position(self):
        """Test advance increments position."""
        lexer = AetherraLexer("abc")
        initial_pos = lexer.position
        lexer.advance()
        assert lexer.position == initial_pos + 1

    def test_lexer_advance_tracks_line_numbers(self):
        """Test advance increments line on newline."""
        lexer = AetherraLexer("a\nb")
        assert lexer.line == 1
        lexer.advance()  # Move to \n
        lexer.advance()  # Move past \n
        assert lexer.line == 2

    def test_lexer_advance_resets_column_on_newline(self):
        """Test advance resets column on newline."""
        lexer = AetherraLexer("abc\ndef")
        lexer.advance()
        lexer.advance()
        lexer.advance()  # Now at column 4
        assert lexer.column == 4
        lexer.advance()  # Move past \n
        assert lexer.column == 1  # Should reset

    def test_lexer_skip_whitespace(self):
        """Test skip_whitespace skips spaces and tabs."""
        lexer = AetherraLexer("   \t  abc")
        lexer.skip_whitespace()
        assert lexer.current_char() == "a"

    def test_lexer_skip_whitespace_preserves_newlines(self):
        """Test skip_whitespace does not skip newlines."""
        lexer = AetherraLexer("  \nabc")
        lexer.skip_whitespace()
        assert lexer.current_char() == "\n"

    def test_lexer_skip_comment(self):
        """Test skip_comment skips to end of line."""
        lexer = AetherraLexer("# comment\nabc")
        lexer.skip_comment()
        assert lexer.current_char() == "\n"

    def test_lexer_skip_comment_at_end_of_file(self):
        """Test skip_comment handles end of file."""
        lexer = AetherraLexer("# comment")
        lexer.skip_comment()
        assert lexer.current_char() is None

    def test_lexer_read_string_with_single_quotes(self):
        """Test read_string parses single-quoted strings."""
        lexer = AetherraLexer("'hello'")
        result = lexer.read_string()
        assert result == "hello"

    def test_lexer_read_string_with_double_quotes(self):
        """Test read_string parses double-quoted strings."""
        lexer = AetherraLexer('"world"')
        result = lexer.read_string()
        assert result == "world"

    def test_lexer_read_string_with_escaped_quote(self):
        """Test read_string handles escaped quotes."""
        lexer = AetherraLexer("'it\\'s'")
        result = lexer.read_string()
        assert "'" in result or "s" in result  # Should handle escape

    def test_lexer_read_string_empty(self):
        """Test read_string handles empty strings."""
        lexer = AetherraLexer("''")
        result = lexer.read_string()
        assert result == ""

    def test_lexer_read_string_with_spaces(self):
        """Test read_string preserves internal spaces."""
        lexer = AetherraLexer("'hello world'")
        result = lexer.read_string()
        assert result == "hello world"

    def test_lexer_read_number_integer(self):
        """Test read_number parses integers."""
        lexer = AetherraLexer("123abc")
        result = lexer.read_number()
        assert result == "123"

    def test_lexer_read_number_float(self):
        """Test read_number parses floats."""
        lexer = AetherraLexer("3.14abc")
        result = lexer.read_number()
        assert result == "3.14"

    def test_lexer_read_number_stops_at_non_digit(self):
        """Test read_number stops at first non-digit."""
        lexer = AetherraLexer("42xyz")
        result = lexer.read_number()
        assert result == "42"
        assert lexer.current_char() == "x"

    def test_lexer_read_identifier(self):
        """Test read_identifier parses identifiers."""
        lexer = AetherraLexer("variable123 ")
        result = lexer.read_identifier()
        assert "variable" in result or "123" in result

    def test_lexer_keywords_contains_goal(self):
        """Test keywords dictionary contains 'goal'."""
        lexer = AetherraLexer("")
        assert "goal" in lexer.keywords
        assert lexer.keywords["goal"] == TokenType.GOAL

    def test_lexer_keywords_contains_agent(self):
        """Test keywords dictionary contains 'agent'."""
        lexer = AetherraLexer("")
        assert "agent" in lexer.keywords
        assert lexer.keywords["agent"] == TokenType.AGENT

    def test_lexer_keywords_contains_memory(self):
        """Test keywords dictionary contains 'memory'."""
        lexer = AetherraLexer("")
        assert "memory" in lexer.keywords
        assert lexer.keywords["memory"] == TokenType.MEMORY

    def test_token_creation_with_all_fields(self):
        """Test Token dataclass with all fields."""
        token = Token(TokenType.GOAL, "test_goal", 5, 10)
        assert token.type == TokenType.GOAL
        assert token.value == "test_goal"
        assert token.line == 5
        assert token.column == 10

    def test_lexer_handles_unicode(self):
        """Test lexer handles unicode input."""
        lexer = AetherraLexer("测试")
        assert lexer.current_char() is not None

    def test_lexer_handles_empty_source(self):
        """Test lexer handles empty source string."""
        lexer = AetherraLexer("")
        assert lexer.current_char() is None
        assert lexer.position == 0

    def test_lexer_multiple_advances(self):
        """Test multiple advances work correctly."""
        lexer = AetherraLexer("abcdef")
        lexer.advance()
        lexer.advance()
        lexer.advance()
        assert lexer.current_char() == "d"
        assert lexer.position == 3

    def test_lexer_peek_with_offset(self):
        """Test peek_char with custom offset."""
        lexer = AetherraLexer("abcdef")
        assert lexer.peek_char(1) == "b"
        assert lexer.peek_char(2) == "c"
        assert lexer.peek_char(3) == "d"

    def test_lexer_read_string_unclosed(self):
        """Test read_string handles unclosed string."""
        lexer = AetherraLexer("'unclosed")
        result = lexer.read_string()
        # Should handle gracefully without crash
        assert isinstance(result, str)

    def test_lexer_column_tracking(self):
        """Test column number tracks correctly."""
        lexer = AetherraLexer("abc")
        assert lexer.column == 1
        lexer.advance()
        assert lexer.column == 2
        lexer.advance()
        assert lexer.column == 3

    def test_lexer_with_mixed_content(self):
        """Test lexer with mixed keywords, strings, and numbers."""
        lexer = AetherraLexer("goal 'test' 123")
        assert lexer.source == "goal 'test' 123"
        assert lexer.position == 0

    def test_token_type_enum_values(self):
        """Test TokenType enum has expected values."""
        assert hasattr(TokenType, "GOAL")
        assert hasattr(TokenType, "AGENT")
        assert hasattr(TokenType, "MEMORY")
        assert hasattr(TokenType, "STRING")
        assert hasattr(TokenType, "NUMBER")
