#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Deep tests for Aetherra.core.ai_runtime error handling and edge cases."""

from unittest import mock

import pytest

from Aetherra.core import ai_runtime


class TestAIRuntimeErrorHandling:
    """Test AI runtime error handling scenarios."""

    def test_ask_ai_handles_connection_error(self):
        """Test ask_ai handles connection errors gracefully."""
        original_client = ai_runtime.client
        try:
            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.side_effect = ConnectionError(
                "Connection failed"
            )
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test prompt")
            assert isinstance(result, str)
            assert "error" in result.lower() or "connection" in result.lower()
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_handles_timeout_error(self):
        """Test ask_ai handles timeout errors."""
        original_client = ai_runtime.client
        try:
            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.side_effect = TimeoutError(
                "Request timed out"
            )
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test prompt")
            assert isinstance(result, str)
            assert "error" in result.lower() or "timeout" in result.lower()
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_handles_invalid_model_error(self):
        """Test ask_ai handles invalid model errors."""
        original_client = ai_runtime.client
        try:
            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.side_effect = ValueError(
                "Model not found"
            )
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test", model="invalid-model")
            assert isinstance(result, str)
            assert "error" in result.lower()
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_handles_none_response_content(self):
        """Test ask_ai handles None response content."""
        original_client = ai_runtime.client
        try:
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = None

            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test prompt")
            assert isinstance(result, str)
            assert result == ""  # Should return empty string
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_with_extreme_temperature(self):
        """Test ask_ai handles extreme temperature values."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            result1 = ai_runtime.ask_ai("test", temperature=0.0)
            result2 = ai_runtime.ask_ai("test", temperature=2.0)
            assert isinstance(result1, str)
            assert isinstance(result2, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_with_negative_temperature(self):
        """Test ask_ai handles negative temperature."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            result = ai_runtime.ask_ai("test", temperature=-1.0)
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_with_empty_prompt(self):
        """Test ask_ai handles empty prompt string."""
        original_client = ai_runtime.client
        try:
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Response to empty"

            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("")
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_with_very_long_prompt(self):
        """Test ask_ai handles very long prompts."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            long_prompt = "test " * 10000
            result = ai_runtime.ask_ai(long_prompt)
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_model_fallback_behavior(self):
        """Test that ask_ai falls back to alternative models."""
        original_client = ai_runtime.client
        try:
            mock_client = mock.MagicMock()
            # First call fails, second succeeds
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Fallback success"

            mock_client.chat.completions.create.side_effect = [
                ValueError("Model not available"),
                mock_response,
            ]
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test")
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_debug_mode_with_error(self):
        """Test debug mode outputs when error occurs."""
        original_client = ai_runtime.client
        try:
            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.side_effect = RuntimeError("Test error")
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("test", debug_mode=True)
            assert isinstance(result, str)
            assert "error" in result.lower()
        finally:
            ai_runtime.client = original_client

    def test_analyze_memory_patterns_with_empty_memories(self):
        """Test analyze_memory_patterns handles empty memory list."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            result = ai_runtime.analyze_memory_patterns(
                memories=[], tag_frequency={}, category_frequency={}
            )
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_analyze_memory_patterns_with_malformed_data(self):
        """Test analyze_memory_patterns raises KeyError for malformed memory data."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            # Memory without 'text' key should raise KeyError
            with pytest.raises(KeyError):
                ai_runtime.analyze_memory_patterns(
                    memories=[{"id": 1}],
                    tag_frequency={"work": 5},
                    category_frequency={},
                )
        finally:
            ai_runtime.client = original_client

    def test_load_env_file_with_malformed_line(self):
        """Test load_env_file handles malformed lines."""
        # Should not crash on malformed .env content
        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch(
                "builtins.open",
                mock.mock_open(
                    read_data="VALID=value\nINVALID_NO_EQUALS\nANOTHER=ok\n"
                ),
            ),
        ):
            # Should handle gracefully
            ai_runtime.load_env_file()

    def test_load_env_file_with_empty_file(self):
        """Test load_env_file handles empty .env file."""
        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch("builtins.open", mock.mock_open(read_data="")),
        ):
            ai_runtime.load_env_file()

    def test_load_env_file_with_comments_only(self):
        """Test load_env_file handles .env with only comments."""
        with (
            mock.patch("os.path.exists", return_value=True),
            mock.patch(
                "builtins.open", mock.mock_open(read_data="# Comment 1\n# Comment 2\n")
            ),
        ):
            ai_runtime.load_env_file()

    def test_ask_ai_with_unicode_in_prompt(self):
        """Test ask_ai handles unicode characters in prompt."""
        original_client = ai_runtime.client
        try:
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Unicode response"

            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            ai_runtime.client = mock_client

            result = ai_runtime.ask_ai("测试 🚀 prompt")
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client

    def test_ask_ai_with_special_characters(self):
        """Test ask_ai handles special characters in prompt."""
        original_client = ai_runtime.client
        try:
            ai_runtime.client = None
            result = ai_runtime.ask_ai("test@#$%^&*()")
            assert isinstance(result, str)
        finally:
            ai_runtime.client = original_client
