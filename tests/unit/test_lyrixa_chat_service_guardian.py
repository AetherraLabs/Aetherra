import json

import pytest

from Aetherra.lyrixa.chat.lyrixa_chat_service import LyrixaChatService


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(tmp_path):
    return (tmp_path / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _last_audit_entry(tmp_path):
    entries = [
        json.loads(line)
        for line in _audit_text(tmp_path).splitlines()
        if line.strip()
    ]
    return entries[-1]


@pytest.mark.asyncio
async def test_lyrixa_safe_edit_is_guardian_audited_without_file_content(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    target = tmp_path / "setup_dev.py"
    target.write_text("banner = 'hello\\ world'\n", encoding="utf-8")
    service = LyrixaChatService(workspace_root=tmp_path)

    ok, change = await service.apply_fix(
        {
            "title": "Fix setup_dev.py",
            "file": str(target),
            "action": "escape_backslashes",
        },
        edit_root=tmp_path,
    )

    assert ok is True
    assert change["action"] == "escape_backslashes"
    ledger_text = _audit_text(tmp_path)
    assert "hello\\ world" not in ledger_text
    assert str(target) not in ledger_text
    assert _last_audit_entry(tmp_path)["details"]["intent"]["action"] == (
        "lyrixa.apply_safe_edit"
    )


@pytest.mark.asyncio
async def test_lyrixa_safe_edit_guardian_denial_leaves_file_unchanged(
    monkeypatch, tmp_path
):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-lyrixa-client",
        strict=True,
    )
    target = tmp_path / "setup_dev.py"
    original = "banner = 'hello\\ world'\n"
    target.write_text(original, encoding="utf-8")
    service = LyrixaChatService(workspace_root=tmp_path)

    ok, change = await service.apply_fix(
        {
            "title": "Fix setup_dev.py",
            "file": str(target),
            "action": "escape_backslashes",
        },
        edit_root=tmp_path,
    )

    assert ok is False
    assert change["error"] == "guardian_denied"
    assert target.read_text(encoding="utf-8") == original
