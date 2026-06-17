# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import os
import time
from types import SimpleNamespace

import pytest

import Aetherra.security.sandbox as sandbox_module
from Aetherra.security.sandbox import (
    IsolatedCallSpec,
    IsolatedExecutionError,
    MemoryBudgetExceeded,
    SandboxViolation,
    SecuritySandbox,
    TimeBudgetExceeded,
    execute_restricted_python,
    run_isolated,
)


def test_security_sandbox_blocks_risky_operations(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    sandbox = SecuritySandbox(
        {
            "timeout": 0.01,
            "memory_limit": 1_024,
            "max_operations": 1,
            "blocked_functions": ["subprocess.run"],
        }
    )

    assert sandbox.is_allowed("safe_operation") is True
    assert sandbox.is_allowed("subprocess.run") is False

    result = sandbox.run(lambda: "ok", timeout=0.001)
    assert result == "ok"


def test_safe_eval_rejects_callable_variable_shadowing():
    called = False

    def dangerous(*_args):
        nonlocal called
        called = True
        return 99

    with pytest.raises(SandboxViolation, match="shadows safe builtin"):
        sandbox_module.safe_eval("max(1, 2)", variables={"max": dangerous})

    assert called is False


def test_memory_budget_violation_is_not_suppressed(monkeypatch):
    class _MemoryInfo:
        rss = 200 * 1024 * 1024

    class _Process:
        @staticmethod
        def memory_info():
            return _MemoryInfo()

    fake_psutil = SimpleNamespace(Process=lambda: _Process())
    monkeypatch.setattr(sandbox_module, "psutil", fake_psutil)

    with pytest.raises(MemoryBudgetExceeded):
        sandbox_module.ensure_memory_budget(100)


def test_isolated_execution_returns_json_safe_result(tmp_path):
    module_path = tmp_path / "worker_plugin.py"
    module_path.write_text(
        "def execute(value):\n    return {'doubled': value * 2}\n",
        encoding="utf-8",
    )

    result = run_isolated(
        IsolatedCallSpec(
            module_name="test_worker_plugin_success",
            module_path=str(module_path),
            callable_name="execute",
        ),
        args=(21,),
        timeout_sec=2,
    )

    assert result == {"doubled": 42}


def test_isolated_timeout_terminates_worker(tmp_path):
    module_path = tmp_path / "slow_plugin.py"
    marker_path = tmp_path / "should_not_exist.txt"
    module_path.write_text(
        "from pathlib import Path\n"
        "import time\n"
        "def execute(marker):\n"
        "    time.sleep(0.5)\n"
        "    Path(marker).write_text('late', encoding='utf-8')\n",
        encoding="utf-8",
    )

    with pytest.raises(TimeBudgetExceeded):
        run_isolated(
            IsolatedCallSpec(
                module_name="test_worker_plugin_timeout",
                module_path=str(module_path),
                callable_name="execute",
            ),
            args=(str(marker_path),),
            timeout_sec=0.1,
        )

    time.sleep(0.6)
    assert not marker_path.exists()


def test_isolated_execution_rejects_non_json_result(tmp_path):
    module_path = tmp_path / "invalid_result_plugin.py"
    module_path.write_text(
        "def execute():\n    return object()\n",
        encoding="utf-8",
    )

    with pytest.raises(IsolatedExecutionError, match="JSON-serializable"):
        run_isolated(
            IsolatedCallSpec(
                module_name="test_worker_plugin_invalid_result",
                module_path=str(module_path),
                callable_name="execute",
            ),
            timeout_sec=2,
        )


def test_restricted_python_supports_assignments_and_print():
    result = execute_restricted_python(
        "x = base * 2\nprint('value', x)",
        {"base": 4},
    )

    assert result.variables == {"base": 4, "x": 8}
    assert result.output == ("value 8",)


@pytest.mark.parametrize(
    "code",
    [
        "import os",
        "while True:\n    pass",
        "open('file.txt', 'w')",
        "x = 'a' * 1000000000",
        "x = 2 ** 1000",
        "x = (danger := 1)",
    ],
)
def test_restricted_python_rejects_unsafe_or_unbounded_code(code):
    with pytest.raises(SandboxViolation):
        execute_restricted_python(code)
