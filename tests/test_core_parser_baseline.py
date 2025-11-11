#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Baseline tests for Aetherra.core.aetherra_parser to seed coverage."""

from Aetherra.core.aetherra_parser import (
    AetherraLexer,
    AetherraNode,
    GoalNode,
    Token,
    TokenType,
)


def test_token_type_enum():
    assert hasattr(TokenType, "GOAL")
    assert hasattr(TokenType, "AGENT")
    assert hasattr(TokenType, "MEMORY")
    assert isinstance(TokenType.GOAL, TokenType)


def test_token_creation():
    tok = Token(TokenType.GOAL, "my_goal", 1, 0)
    assert tok.type == TokenType.GOAL
    assert tok.value == "my_goal"
    assert tok.line == 1
    assert tok.column == 0


def test_node_base():
    node = AetherraNode(type="base", line=1)
    assert node.type == "base"
    assert node.line == 1


def test_goal_node_creation():
    goal = GoalNode(type="goal", line=1, objective="achieve_something", priority="high")
    assert goal.objective == "achieve_something"
    assert goal.priority == "high"
    assert goal.line == 1


def test_lexer_instantiation():
    lexer = AetherraLexer("goal 'test'")
    assert lexer is not None
    assert hasattr(lexer, "source")
    assert lexer.source == "goal 'test'"
    assert lexer.position == 0
    assert lexer.line == 1
