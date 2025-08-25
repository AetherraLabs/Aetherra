import pytest

from aetherra_script_service import AetherScriptService


@pytest.mark.asyncio
async def test_transactions_and_trace(monkeypatch):
    svc = AetherScriptService()
    await svc.initialize()

    script = "\n".join(
        [
            "begin transaction t1",
            "x = 1",
            'narrate "hello"',
            "commit transaction",
        ]
    )

    monkeypatch.setenv("AETHERRA_TRACE", "1")
    result = await svc.execute_script_content(script, filename="<test>")
    assert result["success"] is True
    payload = result["result"]
    # Transactions summary present
    assert any(t.get("name") == "t1" for t in payload.get("transactions", []))
    # Results include assignment and narrate with idempotent True
    types = [r.get("type") for r in payload["results"]]
    assert "assignment" in types and "narrate" in types
    for r in payload["results"]:
        if r["type"] in ("assignment", "narrate"):
            assert r.get("idempotent") is True
    # Trace emitted when env flag set
    assert isinstance(payload.get("trace"), list)
