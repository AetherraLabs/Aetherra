#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Corrupted persistence file resilience test.

Creates an intentionally malformed kernel_tasks.json then attempts restore.
Expected behavior (current alpha): loader should not raise unhandled exceptions
and should remove (or ignore) the corrupted file leaving queues empty.

If future implementation adds explicit logging / metrics, adapt assertions.
"""

import pytest

from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_corrupted_persist_file_graceful(tmp_path, monkeypatch):
    state_dir = tmp_path / ".aetherra"
    state_dir.mkdir()
    tasks_file = state_dir / "kernel_tasks.json"
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(state_dir))
    monkeypatch.setenv("AETHERRA_KERNEL_PERSIST_TASKS", "1")

    # Write junk / truncated JSON
    tasks_file.write_text(
        '{"high_priority": [{"type": "memory_query" }', encoding="utf-8"
    )

    k = AetherraKernelLoop()
    # Attempt load (ignore internal warnings). Should not raise.
    try:
        await k._load_persisted_tasks()  # type: ignore
    except Exception as e:  # pragma: no cover - failure path
        pytest.fail(f"_load_persisted_tasks raised on corrupted file: {e}")

    # Corrupted file should be removed or still present but ignored (allow both, just assert no queued tasks)
    assert k.high_priority_queue.qsize() == 0
    assert k.normal_priority_queue.qsize() == 0
