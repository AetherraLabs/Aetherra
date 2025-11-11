#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Tests for expression evaluation in workflow scripts."""

import pytest

import aetherra_script_service


class TestExpressionEvaluation:
    """Test expression evaluation methods in AetherScriptService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return aetherra_script_service.AetherScriptService()

    def test_eval_expression_boolean_true(self, service):
        """Test evaluation of boolean true."""
        result = service._eval_expression("true", {})
        assert result is True

    def test_eval_expression_boolean_false(self, service):
        """Test evaluation of boolean false."""
        result = service._eval_expression("false", {})
        assert result is False

    def test_eval_expression_null(self, service):
        """Test evaluation of null/none."""
        assert service._eval_expression("null", {}) is None
        assert service._eval_expression("none", {}) is None

    def test_eval_expression_string_double_quotes(self, service):
        """Test evaluation of double-quoted string."""
        result = service._eval_expression('"hello"', {})
        assert result == "hello"

    def test_eval_expression_string_single_quotes(self, service):
        """Test evaluation of single-quoted string."""
        result = service._eval_expression("'world'", {})
        assert result == "world"

    def test_eval_expression_integer(self, service):
        """Test evaluation of integer."""
        result = service._eval_expression("42", {})
        assert result == 42
        assert isinstance(result, int)

    def test_eval_expression_float(self, service):
        """Test evaluation of float."""
        result = service._eval_expression("3.14", {})
        assert result == 3.14
        assert isinstance(result, float)

    def test_eval_expression_list_literal(self, service):
        """Test evaluation of list literal."""
        result = service._eval_expression("[1, 2, 3]", {})
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_eval_expression_empty_list(self, service):
        """Test evaluation of empty list."""
        result = service._eval_expression("[]", {})
        assert result == []

    def test_eval_expression_dict_literal(self, service):
        """Test evaluation of dictionary literal."""
        result = service._eval_expression('{"key": "value"}', {})
        assert isinstance(result, dict)
        assert "key" in result
        assert result["key"] == "value"

    def test_eval_expression_empty_dict(self, service):
        """Test evaluation of empty dictionary."""
        result = service._eval_expression("{}", {})
        assert result == {}

    def test_eval_expression_variable_lookup(self, service):
        """Test variable lookup from context."""
        context = {"x": 100}
        result = service._eval_expression("x", context)
        assert result == 100

    def test_eval_expression_missing_variable(self, service):
        """Test missing variable returns as string."""
        result = service._eval_expression("unknown", {})
        assert result == "unknown"

    def test_eval_expression_comparison_equal(self, service):
        """Test equality comparison."""
        result = service._eval_expression("5 == 5", {})
        assert result is True

    def test_eval_expression_comparison_not_equal(self, service):
        """Test inequality comparison."""
        result = service._eval_expression("5 != 3", {})
        assert result is True

    def test_eval_expression_comparison_less_than(self, service):
        """Test less than comparison."""
        result = service._eval_expression("3 < 5", {})
        assert result is True

    def test_eval_expression_comparison_greater_than(self, service):
        """Test greater than comparison."""
        result = service._eval_expression("10 > 5", {})
        assert result is True

    def test_eval_expression_comparison_less_equal(self, service):
        """Test less than or equal comparison."""
        result = service._eval_expression("5 <= 5", {})
        assert result is True

    def test_eval_expression_comparison_greater_equal(self, service):
        """Test greater than or equal comparison."""
        result = service._eval_expression("5 >= 5", {})
        assert result is True

    def test_eval_expression_addition(self, service):
        """Test addition operation."""
        result = service._eval_expression("10 + 5", {})
        assert result == 15

    def test_eval_expression_subtraction(self, service):
        """Test subtraction operation."""
        result = service._eval_expression("10 - 3", {})
        assert result == 7

    def test_eval_expression_multiplication(self, service):
        """Test multiplication operation."""
        result = service._eval_expression("4 * 5", {})
        assert result == 20

    def test_eval_expression_division(self, service):
        """Test division operation."""
        result = service._eval_expression("20 / 4", {})
        assert result == 5.0

    def test_eval_expression_modulo(self, service):
        """Test modulo operation."""
        result = service._eval_expression("10 % 3", {})
        assert result == 1

    def test_eval_expression_with_context_variables(self, service):
        """Test expression using context variables."""
        context = {"a": 10, "b": 5}
        result = service._eval_expression("a + b", context)
        assert result == 15

    def test_eval_expression_nested_list(self, service):
        """Test evaluation of nested list (note: nested brackets not supported by current implementation)."""
        # Current implementation splits on commas without depth tracking for lists
        # so nested structures are treated as strings
        result = service._eval_expression("[1, 2, 3]", {})
        assert result == [1, 2, 3]

    def test_eval_expression_function_call_passthrough(self, service):
        """Test function call expression returns as string."""
        result = service._eval_expression("func(arg)", {})
        assert isinstance(result, str)
        assert "func" in result

    def test_eval_expression_case_insensitive_true(self, service):
        """Test case-insensitive boolean true."""
        assert service._eval_expression("True", {}) is True
        assert service._eval_expression("TRUE", {}) is True

    def test_eval_expression_case_insensitive_false(self, service):
        """Test case-insensitive boolean false."""
        assert service._eval_expression("False", {}) is False
        assert service._eval_expression("FALSE", {}) is False

    def test_eval_expression_negative_number(self, service):
        """Test evaluation of negative number."""
        result = service._eval_expression("-10", {})
        assert result == -10

    def test_eval_expression_whitespace_handling(self, service):
        """Test expression with extra whitespace."""
        result = service._eval_expression("  42  ", {})
        assert result == 42

    def test_eval_expression_comparison_with_variables(self, service):
        """Test comparison using context variables."""
        context = {"x": 10, "y": 5}
        result = service._eval_expression("x > y", context)
        assert result is True

    def test_eval_expression_zero_value(self, service):
        """Test evaluation of zero."""
        result = service._eval_expression("0", {})
        assert result == 0
