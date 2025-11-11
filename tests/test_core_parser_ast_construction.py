#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Tests for parser AST construction and tokenization flows."""

import pytest

from Aetherra.core.aetherra_parser import (
    AetherraLexer,
    AetherraParser,
    AgentNode,
    GoalNode,
    MemoryNode,
    Token,
    TokenType,
)


class TestParserASTConstruction:
    """Test parser tokenization flows and AST construction."""

    def test_lexer_tokenize_simple_goal(self):
        """Test tokenization of simple goal statement."""
        source = "goal: test objective"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        assert len(tokens) >= 3
        assert tokens[0].type == TokenType.GOAL
        assert tokens[1].type == TokenType.COLON
        assert any(t.value == "test" for t in tokens)

    def test_lexer_tokenize_with_newlines(self):
        """Test tokenization handles newlines correctly."""
        source = "goal: first\nagent: second"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        newline_tokens = [t for t in tokens if t.type == TokenType.NEWLINE]
        assert len(newline_tokens) >= 1

    def test_lexer_tokenize_with_comments(self):
        """Test tokenization skips comments."""
        source = "goal: test # this is a comment\nagent: on"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        # Comments should not appear in tokens
        for token in tokens:
            assert "comment" not in token.value

    def test_lexer_tokenize_string_literals(self):
        """Test tokenization of string literals."""
        source = 'remember: "test data"'
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        assert len(string_tokens) == 1
        assert "test data" in string_tokens[0].value

    def test_lexer_tokenize_numbers(self):
        """Test tokenization of numeric values."""
        source = "value: 42"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        assert len(number_tokens) == 1
        assert number_tokens[0].value == "42"

    def test_lexer_tokenize_operators(self):
        """Test tokenization of comparison operators."""
        source = "if x >= 5"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        operator_tokens = [t for t in tokens if t.type == TokenType.OPERATOR]
        assert len(operator_tokens) == 1
        assert operator_tokens[0].value == ">="

    def test_parser_parse_goal_basic(self):
        """Test parsing basic goal statement."""
        tokens = [
            Token(TokenType.GOAL, "goal", 1, 1),
            Token(TokenType.COLON, ":", 1, 5),
            Token(TokenType.IDENTIFIER, "test", 1, 7),
            Token(TokenType.IDENTIFIER, "objective", 1, 12),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_goal()

        assert isinstance(node, GoalNode)
        assert node.type == "goal"
        assert "test" in node.objective
        assert "objective" in node.objective

    def test_parser_parse_goal_with_priority(self):
        """Test parsing goal with priority."""
        tokens = [
            Token(TokenType.GOAL, "goal", 1, 1),
            Token(TokenType.COLON, ":", 1, 5),
            Token(TokenType.IDENTIFIER, "test", 1, 7),
            Token(TokenType.PRIORITY, "priority", 1, 12),
            Token(TokenType.COLON, ":", 1, 20),
            Token(TokenType.IDENTIFIER, "high", 1, 22),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_goal()

        assert isinstance(node, GoalNode)
        assert node.priority == "high"

    def test_parser_parse_agent_command(self):
        """Test parsing agent command."""
        tokens = [
            Token(TokenType.AGENT, "agent", 1, 1),
            Token(TokenType.COLON, ":", 1, 6),
            Token(TokenType.IDENTIFIER, "on", 1, 8),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_agent()

        assert isinstance(node, AgentNode)
        assert node.type == "agent"
        assert node.command == "on"

    def test_parser_parse_memory_remember(self):
        """Test parsing remember memory operation."""
        tokens = [
            Token(TokenType.REMEMBER, "remember", 1, 1),
            Token(TokenType.COLON, ":", 1, 9),
            Token(TokenType.STRING, "test data", 1, 11),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_memory()

        assert isinstance(node, MemoryNode)
        assert node.operation == "remember"
        assert node.data == "test data"

    def test_parser_expect_raises_on_wrong_token(self):
        """Test parser expect method raises SyntaxError."""
        tokens = [Token(TokenType.IDENTIFIER, "test", 1, 1)]
        parser = AetherraParser(tokens)

        with pytest.raises(SyntaxError):
            parser.expect(TokenType.GOAL)

    def test_parser_advance_updates_position(self):
        """Test parser advance method."""
        tokens = [
            Token(TokenType.GOAL, "goal", 1, 1),
            Token(TokenType.COLON, ":", 1, 5),
        ]
        parser = AetherraParser(tokens)

        assert parser.position == 0
        parser.advance()
        assert parser.position == 1
        assert parser.current_token.type == TokenType.COLON

    def test_parser_skip_newlines(self):
        """Test parser skips newline tokens."""
        tokens = [
            Token(TokenType.NEWLINE, "\n", 1, 1),
            Token(TokenType.NEWLINE, "\n", 2, 1),
            Token(TokenType.GOAL, "goal", 3, 1),
        ]
        parser = AetherraParser(tokens)

        parser.skip_newlines()
        assert parser.current_token.type == TokenType.GOAL

    def test_lexer_tokenize_empty_source(self):
        """Test tokenization of empty source."""
        lexer = AetherraLexer("")
        tokens = lexer.tokenize()

        assert isinstance(tokens, list)
        # Empty source may produce EOF token
        assert len(tokens) <= 1

    def test_lexer_tokenize_colon_token(self):
        """Test tokenization produces colon tokens."""
        source = "goal: test"
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        colon_tokens = [t for t in tokens if t.type == TokenType.COLON]
        assert len(colon_tokens) == 1

    def test_parser_parse_goal_without_priority(self):
        """Test parsing goal without priority defaults to None."""
        tokens = [
            Token(TokenType.GOAL, "goal", 1, 1),
            Token(TokenType.COLON, ":", 1, 5),
            Token(TokenType.IDENTIFIER, "test", 1, 7),
            Token(TokenType.NEWLINE, "\n", 1, 11),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_goal()

        assert node.priority is None

    def test_lexer_tokenize_multiple_operators(self):
        """Test tokenization of multiple operators."""
        source = ">= <= == !="
        lexer = AetherraLexer(source)
        tokens = lexer.tokenize()

        operator_tokens = [t for t in tokens if t.type == TokenType.OPERATOR]
        assert len(operator_tokens) == 4

    def test_parser_parse_agent_task_description(self):
        """Test parsing agent with task description."""
        tokens = [
            Token(TokenType.AGENT, "agent", 1, 1),
            Token(TokenType.COLON, ":", 1, 6),
            Token(TokenType.IDENTIFIER, "analyze", 1, 8),
            Token(TokenType.IDENTIFIER, "data", 1, 16),
        ]
        parser = AetherraParser(tokens)
        node = parser.parse_agent()

        assert "analyze" in node.command
        assert "data" in node.command

    def test_parser_raises_syntax_error_on_eof(self):
        """Test parser raises SyntaxError on unexpected EOF."""
        parser = AetherraParser([])

        with pytest.raises(SyntaxError, match="Unexpected end of input"):
            parser.parse_goal()
