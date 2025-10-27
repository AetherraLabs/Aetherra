# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio
import os
from pathlib import Path

import pytest

from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.mark.asyncio
async def test_selfinc_handles_scale_up_proposal(tmp_path: Path, monkeypatch):
    # Ensure state dir is in temp
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path))
    cfg = SelfIncorporationConfig()
    svc = SelfIncorporationService(cfg)

    # Start service
    await svc.start()

    # Capture old velocity
    old_v = svc._processing_velocity

    # Send proposal
    result = await svc.handle_message(
        "selfimprovement.proposal",
        {"type": "scale_up", "proposal_id": "p-1", "params": {"delta": 0.5}},
    )

    assert isinstance(result, dict)
    assert result.get("status") == "accepted"
    assert "plan_id" in result
    assert svc._processing_velocity > old_v


@pytest.mark.asyncio
async def test_selfinc_rejects_unknown_proposal(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path))
    cfg = SelfIncorporationConfig()
    svc = SelfIncorporationService(cfg)
    await svc.start()

    res = await svc.handle_message("selfimprovement.proposal", {"type": "unknown"})
    assert res.get("status") == "rejected"
    assert "unsupported_type" in res.get("reason", "")
