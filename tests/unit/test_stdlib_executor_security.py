"""Security tests for the Aetherra standard executor."""

import json
import os

import pytest

from Aetherra.stdlib.executor import ExecutorPlugin


def test_python_command_uses_restricted_statement_language():
    executor = ExecutorPlugin()
    context = {"base": 3}
    try:
        result = executor._execute_python_code(
            "value = base * 2\nprint('result', value)", context
        )
    finally:
        executor.scheduler_running = False
        executor.thread_pool.shutdown(wait=True, cancel_futures=True)

    assert result == "result 6"
    assert context == {"base": 3, "value": 6}


def test_execute_now_writes_guardian_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    executor = ExecutorPlugin()
    try:
        result = executor.execute_now("aether:status", {})
        audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
        entries = [
            json.loads(line)
            for line in audit_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    finally:
        executor.scheduler_running = False
        executor.thread_pool.shutdown(wait=True, cancel_futures=True)

    assert result["status"] == "completed"
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "executor.execute"
    assert entries[-1]["details"]["intent"]["target"] == "executor:aether"


def test_execute_now_blocked_by_guardian_missing_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    executor = ExecutorPlugin()
    try:
        result = executor.execute_now("python:value = 1", {})
    finally:
        executor.scheduler_running = False
        executor.thread_pool.shutdown(wait=True, cancel_futures=True)

    assert result["status"] == "failed"
    assert "Executor command blocked by Guardian: missing_capability" in result["error"]


def test_guardian_audit_does_not_store_executor_command_text(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    secret_like_command = "python:token = 'secret-value'\nprint('ok')"
    executor = ExecutorPlugin()
    try:
        result = executor.execute_now(secret_like_command, {})
        audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
        ledger_text = audit_path.read_text(encoding="utf-8")
    finally:
        executor.scheduler_running = False
        executor.thread_pool.shutdown(wait=True, cancel_futures=True)

    assert result["status"] == "completed"
    assert "secret-value" not in ledger_text
    assert "executor:python" in ledger_text


def test_python_command_rejects_imports():
    executor = ExecutorPlugin()
    try:
        with pytest.raises(ValueError, match="Forbidden restricted statement"):
            executor._execute_python_code("import os", {})
    finally:
        executor.scheduler_running = False
        executor.thread_pool.shutdown(wait=True, cancel_futures=True)
