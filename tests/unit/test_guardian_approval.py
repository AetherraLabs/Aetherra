# Standard library imports
import json
import multiprocessing
import threading

# Third party imports
import pytest

# Aetherra imports
from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.guardian.approval import (
    consume_approval,
    create_approval_request,
    list_approval_events,
    list_approval_statuses,
    resolve_approval,
    validate_approval,
)
from Aetherra.guardian.risk import assess_risk


def _intent(**overrides):
    values = {
        "requester": "self_improvement_engine",
        "subsystem": "self_improvement",
        "action": "self.apply_proposal",
        "target": "kernel",
        "purpose": "Apply proposal",
        "capabilities": ("self:modify", "code:modify", "system:reload"),
        "evidence": ("proposal:SI-APPROVAL",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_approval_must_be_resolved_before_consumption(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))

    result = validate_approval(approval.request_id, intent)

    assert result.valid is False
    assert result.reason == "approval_pending"


def test_approved_intent_can_be_consumed_once(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="user")

    first = consume_approval(approval.request_id, intent)
    second = consume_approval(approval.request_id, intent)

    assert first.valid is True
    assert second.valid is False
    assert second.reason == "approval_already_consumed"
    assert list_approval_events()[-1]["event"] == "consumed"


def test_approval_is_bound_to_original_intent(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent(target="kernel")
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="user")

    changed_intent = _intent(target="other-kernel")
    result = consume_approval(approval.request_id, changed_intent)

    assert result.valid is False
    assert result.reason == "approval_intent_mismatch"


def test_evaluate_intent_consumes_valid_approval(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    intent = _intent()
    first_decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )
    approval_id = first_decision.details["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="user")

    approved_decision = evaluate_intent(
        intent,
        approval_id=approval_id,
        capability_checker=lambda requester, capability: True,
    )
    replay_decision = evaluate_intent(
        intent,
        approval_id=approval_id,
        capability_checker=lambda requester, capability: True,
    )

    assert approved_decision.status == GuardianStatus.ALLOW_LIMITED
    assert approved_decision.reason == "approved_with_guardian_approval"
    assert replay_decision.status == GuardianStatus.REQUIRE_APPROVAL


def test_approval_expiration_blocks_resolution_and_consumption(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_TIMEOUT_SEC", "1")
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))

    created = list_approval_events()[0]
    created["expires_at"] = "2000-01-01T00:00:00Z"
    log_path = tmp_path / ".aetherra" / "guardian" / "approvals.jsonl"
    log_path.write_text(json.dumps(created) + "\n", encoding="utf-8")

    resolution = resolve_approval(approval.request_id, approved=True, approver="user")
    validation = validate_approval(approval.request_id, intent)
    statuses = list_approval_statuses()

    assert resolution["state"] == "expired"
    assert validation.valid is False
    assert validation.reason == "approval_expired"
    assert statuses[0]["state"] == "expired"


def test_claim_fails_closed_when_ledger_lock_is_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_GUARDIAN_STATE_DIR", str(tmp_path))
    (tmp_path / "approvals.jsonl.lock").mkdir()

    with pytest.raises((PermissionError, IsADirectoryError)):
        consume_approval("missing", _intent())
    assert not (tmp_path / "approvals.jsonl").exists()


def _claim_after_start(request_id, intent, start, results):
    start.wait()
    result = consume_approval(request_id, intent)
    results.put((result.valid, result.reason))


@pytest.mark.parametrize(
    "separate_process", [False, True], ids=["threads", "processes"]
)
def test_concurrent_consumers_share_one_approval(
    monkeypatch, tmp_path, separate_process
):
    monkeypatch.setenv("AETHERRA_GUARDIAN_STATE_DIR", str(tmp_path))
    intent = _intent(
        action="inspect", capabilities=(), purpose="Inspect synthetic fixture"
    )
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="fixture")

    context = multiprocessing.get_context("spawn")
    start = context.Barrier(2, timeout=15)
    results = context.Queue()
    worker_type = context.Process if separate_process else threading.Thread
    worker = worker_type(
        target=_claim_after_start,
        args=(approval.request_id, intent, start, results),
        daemon=True,
    )
    worker.start()
    try:
        start.wait()
        local = consume_approval(approval.request_id, intent)
        outcomes = [(local.valid, local.reason), results.get(timeout=15)]
    finally:
        worker.join(timeout=15)
        results.close()
    assert not worker.is_alive()
    if separate_process:
        with context.Pool(1) as restarted:
            replay = restarted.apply_async(
                consume_approval, (approval.request_id, intent)
            )
            assert replay.get(timeout=15).reason == "approval_already_consumed"
    assert sorted(outcomes) == [
        (False, "approval_already_consumed"),
        (True, "approval_valid"),
    ]
    assert [event["event"] for event in list_approval_events()] == [
        "created",
        "resolved",
        "consumed",
    ]


def test_claim_surfaces_durable_write_failure(monkeypatch, tmp_path):
    # Aetherra imports
    from Aetherra.guardian import state

    monkeypatch.setenv("AETHERRA_GUARDIAN_STATE_DIR", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="fixture")

    def unavailable(_fd):
        raise OSError("synthetic flush failure")

    monkeypatch.setattr(state.os, "fsync", unavailable)
    with pytest.raises(OSError, match="synthetic flush failure"):
        consume_approval(approval.request_id, intent)


@pytest.mark.parametrize(
    ("tail", "message"),
    [(b"{", "Expecting property name"), (b"[]", "must be a JSON object")],
)
def test_claim_refuses_unreadable_ledger(monkeypatch, tmp_path, tail, message):
    monkeypatch.setenv("AETHERRA_GUARDIAN_STATE_DIR", str(tmp_path))
    intent = _intent()
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="fixture")

    ledger = tmp_path / "approvals.jsonl"
    with ledger.open("ab") as handle:
        handle.write(tail)
    before = ledger.read_bytes()
    with pytest.raises(ValueError, match=message):
        consume_approval(approval.request_id, intent)
    assert ledger.read_bytes() == before


def test_busy_ledger_excludes_external_claim_and_resolution(monkeypatch, tmp_path):
    # Aetherra imports
    from Aetherra.guardian.state import locked_jsonl

    monkeypatch.setenv("AETHERRA_GUARDIAN_STATE_DIR", str(tmp_path))
    intent = _intent(action="inspect", capabilities=())
    approval = create_approval_request(intent, assess_risk(intent))
    resolve_approval(approval.request_id, approved=True, approver="fixture")

    with (
        multiprocessing.get_context("spawn").Pool(1) as worker,
        locked_jsonl(tmp_path / "approvals.jsonl"),
    ):
        claim = worker.apply_async(consume_approval, (approval.request_id, intent))
        with pytest.raises(TimeoutError, match="Guardian state log is busy"):
            claim.get(timeout=15)
        with pytest.raises(TimeoutError, match="Guardian state log is busy"):
            resolve_approval(approval.request_id, approved=False, approver="fixture")
    assert [event["event"] for event in list_approval_events()] == [
        "created",
        "resolved",
    ]
