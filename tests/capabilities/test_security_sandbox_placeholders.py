"""Security Sandbox Placeholder Capability Test

Ensures the lightweight sandbox utilities enforce basic constraints now,
establishing a test anchor for future hardening (process isolation, policy engine).

Checks:
1. safe_eval allows simple arithmetic logic.
2. safe_eval blocks attribute access and function definitions.
3. run_with_timeout enforces execution ceiling.
4. ensure_memory_budget no-ops (does not raise) when psutil missing or budget generous.
"""

from __future__ import annotations

# Standard library imports
import time

# Third party imports
import pytest

# Aetherra imports
from Aetherra.security.sandbox import (
    SandboxViolation,
    TimeBudgetExceeded,
    ensure_memory_budget,
    run_with_timeout,
    safe_eval,
)


def test_safe_eval_basic_arithmetic():
    assert safe_eval("1 + 2 * 3") == 7
    assert safe_eval("max(5, 2)") == 5  # allowed builtin


def test_safe_eval_forbidden_constructs():
    with pytest.raises(SandboxViolation):
        safe_eval("__import__('os').system('echo hi')")
    with pytest.raises(SandboxViolation):
        safe_eval("(lambda x: x)(5)")
    with pytest.raises(SandboxViolation):
        safe_eval("open('foo','w')")  # open not in SAFE_BUILTINS


def test_safe_eval_variable_injection():
    # Provide variables mapping and ensure they are usable
    result = safe_eval("a + b * 2", variables={"a": 2, "b": 5})
    assert result == 12


def test_run_with_timeout_enforced():
    start = time.time()
    with pytest.raises(TimeBudgetExceeded):
        run_with_timeout(time.sleep, args=(0.3,), timeout_sec=0.05)
    assert (time.time() - start) < 0.25  # Should abort early


def test_memory_budget_noop():
    # Provide unrealistic high budget so it should not raise
    ensure_memory_budget(10_000)  # 10GB effectively noop
