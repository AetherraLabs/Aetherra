#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Acceptance tests for autonomous error correction - Golden Paths.

Tests all 6 error correction categories to ensure end-to-end functionality:
1. Service registration API mismatch
2. Deprecated module imports
3. Missing modules
4. Missing capabilities (methods)
5. Plugin load failures
6. Expected data missing

Golden path criteria:
- Error appears in logs
- Error corrector detects pattern
- Cooldown respected (after successful fix)
- Fix handler applies correction (where enabled)
- Metrics increment correctly
- Statistics reflect detection and fix status
"""

import asyncio
import logging

import pytest

from Aetherra.homeostasis.autonomous_error_corrector import (
    AutonomousErrorCorrector,
)

# Create a test logger to inject errors
test_logger = logging.getLogger("test_error_injection")

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


# Shared corrector instance for simpler lifecycle control
_corrector_instance = None


async def setup_corrector():
    """Setup the error corrector (async)."""
    global _corrector_instance
    _corrector_instance = AutonomousErrorCorrector()
    await _corrector_instance.start()
    return _corrector_instance


async def teardown_corrector():
    """Teardown the error corrector (async)."""
    global _corrector_instance
    if _corrector_instance:
        await _corrector_instance.stop()
        _corrector_instance = None


@pytest.mark.acceptance
async def test_service_registration_api_mismatch_golden_path():
    """
    Test: Service registration API mismatch error is detected and handled.

    Golden path:
    1. Error appears in logs (unexpected keyword argument)
    2. Error corrector detects pattern
    3. Fix handler is called
    4. Cooldown only applies after successful fix (may be False in test env)
    5. Metrics increment correctly

    Note: In test environment, fix may fail due to missing service registry,
    but detection and metrics tracking should still work correctly.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        test_logger.warning(
            "register_service() got an unexpected keyword argument 'instance'"
        )
        await asyncio.sleep(0.7)

        # Verify detection and attempt
        assert error_corrector.stats["errors_detected"] > initial_detected
        assert error_corrector.stats["fixes_attempted"] >= initial_attempted

        # Verify error recorded with correct pattern name
        service_reg_errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "service_registration_api_mismatch"
        ]
        assert len(service_reg_errors) > 0
        assert service_reg_errors[0].fix_attempted
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_deprecated_import_golden_path():
    """
    Test: Deprecated import warning is detected and logged.

    Cooldown should prevent immediate second fix attempt after a successful fix.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        # Inject deprecation warning
        test_logger.warning(
            "aetherra_old_module is deprecated; use aetherra_new_module. Temporarily aliasing"
        )
        await asyncio.sleep(0.6)

        # Verify detection and fix attempt
        assert error_corrector.stats["errors_detected"] > initial_detected
        assert error_corrector.stats["fixes_attempted"] > initial_attempted

        # Capture current fixes_attempted after success
        after_first_fix = error_corrector.stats["fixes_attempted"]

        # Inject again immediately; cooldown should block second fix
        test_logger.warning(
            "aetherra_old_module is deprecated; use aetherra_new_module. Temporarily aliasing"
        )
        await asyncio.sleep(0.4)

        assert error_corrector.stats["fixes_attempted"] == after_first_fix

        # Recorded errors contain the right pattern
        errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "deprecated_module_import"
        ]
        assert len(errors) > 0
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_missing_module_golden_path():
    """
    Test: Missing module error is detected and fix attempted, with cooldown.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        test_logger.error("No module named 'missing_test_module'")
        await asyncio.sleep(0.6)

        assert error_corrector.stats["errors_detected"] > initial_detected
        assert error_corrector.stats["fixes_attempted"] > initial_attempted

        after_first_fix = error_corrector.stats["fixes_attempted"]

        # Second injection should be blocked by cooldown
        test_logger.error("No module named 'missing_test_module'")
        await asyncio.sleep(0.4)
        assert error_corrector.stats["fixes_attempted"] == after_first_fix

        errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "missing_module"
        ]
        assert len(errors) > 0
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_missing_capability_golden_path():
    """
    Test: Missing capability error is detected and fix attempted, with cooldown.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        test_logger.error(
            "AttributeError: 'scheduler' object has no attribute 'add_persistent_task'"
        )
        await asyncio.sleep(0.6)

        assert error_corrector.stats["errors_detected"] > initial_detected
        assert error_corrector.stats["fixes_attempted"] > initial_attempted

        after_first_fix = error_corrector.stats["fixes_attempted"]

        # Second injection should be blocked by cooldown
        test_logger.error(
            "AttributeError: 'scheduler' object has no attribute 'add_persistent_task'"
        )
        await asyncio.sleep(0.4)
        assert error_corrector.stats["fixes_attempted"] == after_first_fix

        errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "missing_capability"
        ]
        assert len(errors) > 0
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_plugin_load_failure_golden_path():
    """
    Test: Plugin load failure is detected (informational only).
    Auto-fix is disabled, so no fix attempt should be recorded.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        test_logger.warning("[SKIP] GUI plugin test_plugin.py not loaded")
        await asyncio.sleep(0.5)

        assert error_corrector.stats["errors_detected"] > initial_detected
        # No auto-fix for plugin_load_failure
        assert error_corrector.stats["fixes_attempted"] == initial_attempted

        errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "plugin_load_failure"
        ]
        assert len(errors) > 0
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_expected_data_missing_golden_path():
    """
    Test: Expected data missing is detected (informational only).
    Auto-fix is disabled, so no fix attempt should be recorded.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        initial_detected = error_corrector.stats["errors_detected"]
        initial_attempted = error_corrector.stats["fixes_attempted"]

        test_logger.warning(
            "Expected configuration data for module test_module but found none"
        )
        await asyncio.sleep(0.5)

        assert error_corrector.stats["errors_detected"] > initial_detected
        # No auto-fix for expected_data_missing
        assert error_corrector.stats["fixes_attempted"] == initial_attempted

        errors = [
            e
            for e in error_corrector.detected_errors
            if e.pattern_name == "expected_data_missing"
        ]
        assert len(errors) > 0
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_cooldown_enforcement_across_patterns():
    """
    Cooldown is per-pattern; different patterns should not block each other.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        base_attempted = error_corrector.stats["fixes_attempted"]

        # Trigger two different patterns quickly
        test_logger.warning(
            "aetherra_old_module is deprecated; use aetherra_new_module. Temporarily aliasing"
        )
        test_logger.error("No module named 'missing_test_module'")
        await asyncio.sleep(0.8)

        # Both should have been attempted once
        assert error_corrector.stats["fixes_attempted"] >= base_attempted + 2
    finally:
        await teardown_corrector()


@pytest.mark.acceptance
async def test_statistics_consistency():
    """
    Validate stats counters remain internally consistent after activity.
    """
    error_corrector = await setup_corrector()
    try:
        await asyncio.sleep(0.1)

        # Trigger a handful of patterns
        test_logger.warning(
            "aetherra_old_module is deprecated; use aetherra_new_module. Temporarily aliasing"
        )
        test_logger.error("No module named 'missing_test_module'")
        test_logger.error(
            "AttributeError: 'scheduler' object has no attribute 'add_persistent_task'"
        )
        await asyncio.sleep(1.0)

        stats = error_corrector.stats
        assert stats["errors_detected"] >= len(error_corrector.detected_errors)
        assert stats["fixes_successful"] <= stats["fixes_attempted"]
    finally:
        await teardown_corrector()
