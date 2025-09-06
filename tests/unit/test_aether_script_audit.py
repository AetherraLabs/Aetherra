# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import json

import pytest

from aetherra_script_service import AetherScriptService


@pytest.mark.asyncio
async def test_audit_ledger_writes_and_redacts(monkeypatch, tmp_path):
    svc = AetherScriptService()
    await svc.initialize()

    audit_path = tmp_path / "audit" / "runs.jsonl"
    monkeypatch.setenv("AETHERRA_AUDIT", "1")
    monkeypatch.setenv("AETHERRA_AUDIT_PATH", str(audit_path))
    monkeypatch.setenv("AETHERRA_TRACE", "1")

    # Script contains a signature marker and an inline api_key that should be redacted
    script = "\n".join(
        [
            "# @signature: abc123",
            'remember "api_key=sk-TEST-123" as "k"',
            'narrate "done"',
        ]
    )

    context = {
        "model": "dummy-model-1",
        "tokens": {"input": 10, "output": 5},
        "cost": 0.001,
        "prompts": [
            "password=supersecret",
            "token: X123",
        ],
    }

    res = await svc.execute_script_content(script, filename="<test>", context=context)
    assert res["success"] is True

    # Read last JSONL record
    assert audit_path.exists(), "audit file not created"
    last = None
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            last = json.loads(line)
    assert last is not None

    # Basic fields captured
    assert last["file"] == "<test>"
    assert last["model"] == "dummy-model-1"
    assert last["tokens"] == {"input": 10, "output": 5}
    assert last["cost_usd"] == 0.001

    # Script sanitized: signature redacted and api_key value redacted
    script_s = last["script"]
    assert "# @signature:[REDACTED]" in script_s
    assert "api_key=[REDACTED]" in script_s
    assert "sk-TEST-123" not in script_s

    # Prompts sanitized
    prompts = last.get("prompts")
    assert prompts is not None and isinstance(prompts, list)
    assert any("password=[REDACTED]" in p for p in prompts)
    assert any("token: [REDACTED]" in p for p in prompts)
    assert all("supersecret" not in p for p in prompts)

    # Disabling audit should not append more lines
    before = audit_path.read_text(encoding="utf-8")
    monkeypatch.setenv("AETHERRA_AUDIT", "0")
    res2 = await svc.execute_script_content('narrate "again"', filename="<test>")
    assert res2["success"] is True
    after = audit_path.read_text(encoding="utf-8")
    assert after == before, "audit log changed despite AETHERRA_AUDIT=0"
