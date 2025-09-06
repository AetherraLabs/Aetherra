#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Persistence restart test.

Ensures that when AETHERRA_KERNEL_PERSIST_TASKS=1 the kernel snapshots tasks
and a new kernel instance restores them on startup via _load_persisted_tasks.
"""

import json

import pytest

from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_persist_and_restore_tasks(tmp_path, monkeypatch):
    state_dir = tmp_path / ".aetherra"
    state_dir.mkdir()
    tasks_file = state_dir / "kernel_tasks.json"
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(state_dir))
    monkeypatch.setenv("AETHERRA_KERNEL_PERSIST_TASKS", "1")

    k1 = AetherraKernelLoop()

    # Enqueue a few tasks (loop not started so they remain pending)
    await k1.add_task(
        {"type": "plugin_invoke", "data": {"plugin_id": "x"}}, priority="normal"
    )
    await k1.add_task({"type": "memory_query", "data": {"q": "y"}}, priority="high")

    # Simulate normal shutdown path which triggers snapshot when persist_tasks enabled
    await k1.shutdown()

    assert tasks_file.exists(), "snapshot file not created"
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data.get("normal_priority", [])) == 1
    assert len(data.get("high_priority", [])) == 1

    # Re-instantiate kernel (env still set) and load persisted tasks (simulating restart)
    k2 = AetherraKernelLoop()
    await k2._load_persisted_tasks()  # type: ignore

    assert not tasks_file.exists(), "tasks file should be removed after restore"
    assert k2.high_priority_queue.qsize() == 1
    assert k2.normal_priority_queue.qsize() == 1
