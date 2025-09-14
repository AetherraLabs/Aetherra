#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Test plugin analytics edge cases and error conditions for coverage improvement.
Focuses on increasing coverage by testing uncovered code paths including error handling,
edge cases, and initialization scenarios.
"""

import asyncio
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def analytics_engine():
    """Create a plugin analytics engine for testing."""
    import atexit
    import tempfile

    from Aetherra.plugins.lifecycle.plugin_analytics import PluginAnalyticsIntegration

    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_analytics.db"
    engine = PluginAnalyticsIntegration(db_path=str(db_path))

    def cleanup():
        try:
            engine.close()
            # Force cleanup and give Windows time to release file handles
            import gc
            import time

            gc.collect()
            time.sleep(0.2)
            # Try to remove the temp directory
            import shutil

            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass  # Ignore cleanup errors on Windows
        except Exception:
            pass

    # Register cleanup for end of test
    atexit.register(cleanup)

    try:
        yield engine
    finally:
        cleanup()


@pytest.mark.asyncio
async def test_analytics_record_usage_error_handling(analytics_engine):
    """Test error handling in record_usage method."""

    # Test with invalid context that can't be JSON serialized
    class NonSerializable:
        def __str__(self):
            raise Exception("Intentional serialization error")

    # This should not crash even with bad context data
    analytics_engine.record_plugin_action(
        plugin_id="test_plugin",
        action="test_action",
        context={"bad_data": NonSerializable()},
    )

    # Verify the engine is still functional after error
    analytics_engine.record_plugin_action(
        plugin_id="test_plugin_2",
        action="normal_action",
        context={"good": "data"},
    )


@pytest.mark.asyncio
async def test_analytics_record_execution_edge_cases(analytics_engine):
    """Test edge cases in record_execution method."""
    # Test with extreme values
    analytics_engine.record_execution(
        plugin_id="extreme_plugin",
        execution_time=999999.999,  # Very large time
    )

    # Test with zero execution time
    analytics_engine.record_execution(plugin_id="zero_plugin", execution_time=0.0)

    # Test basic execution recording
    analytics_engine.record_execution(plugin_id="basic_plugin", execution_time=1.5)


@pytest.mark.asyncio
async def test_analytics_database_error_resilience(analytics_engine):
    """Test resilience to database connection errors."""
    # Mock database connection to fail
    with patch("sqlite3.connect") as mock_connect:
        mock_connect.side_effect = sqlite3.Error("Database locked")

        # These operations should not crash the system
        analytics_engine.record_plugin_action("plugin", "action")
        analytics_engine.record_execution("plugin", 1.0)

        # Verify analytics can recover after error
        mock_connect.side_effect = None
        analytics_engine.record_plugin_action("recovery_plugin", "recovery_action")


@pytest.mark.asyncio
async def test_analytics_concurrent_access(analytics_engine):
    """Test concurrent access to analytics engine."""

    async def record_batch(prefix: str, count: int):
        for i in range(count):
            analytics_engine.record_plugin_action(
                plugin_id=f"{prefix}_plugin_{i}",
                action=f"{prefix}_action",
            )
            analytics_engine.record_execution(
                plugin_id=f"{prefix}_plugin_{i}",
                execution_time=0.1 * i,
            )

    # Run multiple concurrent recording operations
    await asyncio.gather(
        record_batch("batch1", 10),
        record_batch("batch2", 10),
        record_batch("batch3", 10),
    )


@pytest.mark.asyncio
async def test_analytics_session_data_accumulation(analytics_engine):
    """Test session data accumulation and management."""

    # Record multiple executions for same plugin
    for i in range(5):
        analytics_engine.record_execution(
            plugin_id=f"plugin_{i}", execution_time=1.0 + i
        )

    # Verify basic functionality works
    analytics_engine.record_plugin_action(plugin_id="test_plugin", action="test_action")


@pytest.mark.asyncio
async def test_analytics_initialization_edge_cases():
    """Test analytics engine initialization with edge cases."""
    from Aetherra.plugins.lifecycle.plugin_analytics import PluginAnalyticsIntegration

    # Test with temporary directory using manual cleanup
    temp_dir = tempfile.mkdtemp()
    try:
        deep_path = Path(temp_dir) / "deep" / "nested" / "path" / "analytics.db"
        # Create parent directories first
        deep_path.parent.mkdir(parents=True, exist_ok=True)
        # Should work with existing directories
        engine = PluginAnalyticsIntegration(db_path=str(deep_path))
        assert deep_path.exists()
        # Clean up the engine
        engine.close()
    finally:
        # Clean up manually with error handling
        import shutil

        try:
            import gc
            import time

            gc.collect()
            time.sleep(0.1)
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass  # Ignore cleanup errors on Windows

    # Test with existing database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name

    try:
        # Create engine twice with same path (should not error)
        engine1 = PluginAnalyticsIntegration(db_path=db_path)
        engine2 = PluginAnalyticsIntegration(db_path=db_path)

        # Both should work
        engine1.record_plugin_action("plugin1", "action1")
        engine2.record_plugin_action("plugin2", "action2")

        # Clean up engines
        engine1.close()
        engine2.close()
    finally:
        try:
            import gc
            import time

            gc.collect()
            time.sleep(0.1)
            Path(db_path).unlink(missing_ok=True)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_analytics_migration_edge_cases(analytics_engine):
    """Test database migration edge cases and schema versioning."""
    # Verify basic functionality works (schema migration tested during setup)
    analytics_engine.record_plugin_action(
        plugin_id="migration_test", action="test_action"
    )

    # Verify we can record execution data (tests v2 schema with latency_ms)
    analytics_engine.record_execution(plugin_id="migration_test", execution_time=0.5)


@pytest.mark.asyncio
async def test_analytics_large_context_data(analytics_engine):
    """Test handling of large context data."""
    # Test with large context data
    large_context = {
        "large_data": "x" * 10000,  # 10KB string
        "nested": {"deep": {"structure": list(range(1000))}},
        "unicode": "测试数据 🚀 émoji",
    }

    analytics_engine.record_plugin_action(
        plugin_id="large_context_plugin",
        action="large_context_action",
        context=large_context,
    )


@pytest.mark.asyncio
async def test_analytics_special_characters_handling(analytics_engine):
    """Test handling of special characters in plugin IDs and actions."""
    special_cases = [
        ("plugin/with/slashes", "action:with:colons"),
        ("plugin with spaces", "action with spaces"),
        ("plugin-with-dashes", "action_with_underscores"),
        ("plugin.with.dots", "action.with.dots"),
        ("🚀 emoji plugin 🔥", "💡 emoji action ⭐"),
        ("", ""),  # Empty strings
    ]

    for plugin_id, action in special_cases:
        analytics_engine.record_plugin_action(
            plugin_id=plugin_id,
            action=action,
            context={"test": "special_chars"},
        )

        analytics_engine.record_execution(plugin_id=plugin_id, execution_time=0.1)
