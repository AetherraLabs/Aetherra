"""Perform one explicitly approved retention transaction on a stopped checkpoint stream."""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
import signal
import threading
import time
from pathlib import Path

# Aetherra imports
from Aetherra.aetherra_core.memory.checkpoint_stream import (
    AcquiredStream,
    InspectionResult,
    PruneResult,
    StreamKey,
)
from Aetherra.aetherra_core.memory.lifecycle_checkpoint import (
    CheckpointError,
    CheckpointJobControl,
    LifecycleCheckpointWorker,
    _stream_intent,
)
from Aetherra.consciousness.checkpoint import OWNER, SCOPE
from Aetherra.consciousness.checkpoint_session import recovery_descriptor
from Aetherra.guardian.approval import (
    approval_status,
    create_approval_request,
    intent_fingerprint,
    validate_approval,
)
from Aetherra.guardian.paths import workspace_root
from Aetherra.guardian.risk import assess_risk

_APPROVAL_ENV = "AETHERRA_GUARDIAN_APPROVAL_ID"


def _print_event(event):
    print(json.dumps(event), flush=True)


def _inputs(args):
    profile = args.profile.resolve(strict=True)
    database = (profile / args.database).resolve(strict=True)
    if (
        profile != workspace_root()
        or not profile.is_dir()
        or not database.is_relative_to(profile)
        or not database.is_file()
        or not 2 <= args.retain <= 100
    ):
        raise CheckpointError("invalid_profile_or_settings")
    key = StreamKey(OWNER, SCOPE, args.stream_id)
    attempt = None
    if args.prior_attempt is not None:
        with args.prior_attempt.open("rb") as source:
            data = source.read(8193)
        if len(data) > 8192:
            raise CheckpointError("invalid_descriptor")
        attempt = recovery_descriptor(
            json.loads(data), {"start_mode": "resume", "stream_id": key.stream_id}
        )
    return database, key, attempt


def _submit(worker, cancelled, operation, **inputs):
    if cancelled.is_set():
        raise CheckpointError("cancelled")
    wake = threading.Event()
    control = CheckpointJobControl(
        cancelled=cancelled,
        deadline=time.monotonic() + 1.0,
        still_owned=lambda: not cancelled.is_set(),
        wake_event=wake,
    )
    job = worker.submit_stream(operation=operation, control=control, **inputs)
    # A positive poll follows an observed worker handoff and a fresh ownership sample.
    while job.outstanding:
        remaining = control.deadline - time.monotonic()
        if cancelled.is_set() or remaining <= 0:
            job.cancel()
            raise CheckpointError("uncertain")
        wake.wait(min(0.05, remaining))
    completion = job.poll(local_owned=not cancelled.is_set())
    if completion is None:
        raise CheckpointError("uncertain")
    if completion.error_code is not None:
        raise CheckpointError(completion.error_code)
    if not job.admitted:
        raise CheckpointError("uncertain")
    return completion.value


def _await_decision(request_id, intent, cancelled):
    deadline = time.monotonic() + 900
    while True:
        validation = validate_approval(request_id, intent)
        if cancelled.is_set():
            raise CheckpointError("cancelled")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise CheckpointError("decision_timeout")
        if validation.valid:
            return
        if validation.reason != "approval_pending":
            raise CheckpointError(validation.reason)
        cancelled.wait(min(0.25, remaining))


def _maintain(worker, key, retain, attempt, emit, cancelled):
    acquired = _submit(
        worker,
        cancelled,
        "acquire",
        key=key,
        start_mode="resume",
        retain_checkpoints=retain,
    )
    if type(acquired) is not AcquiredStream or acquired.token.key != key:
        raise CheckpointError("corrupt")
    token, head = acquired.token, acquired.head
    if attempt is not None:
        inspection = _submit(worker, cancelled, "inspect", token=token, attempt=attempt)
        if type(inspection) is not InspectionResult or inspection.head != head:
            raise CheckpointError("corrupt")
        emit(
            {
                "status": "inspected",
                "outcome": inspection.outcome,
                "matched_record_id": inspection.matched_record_id,
            }
        )
    if not acquired.retention_needed:
        return {
            "status": "no_victim",
            "writer_epoch": token.writer_epoch,
            "generation": head.generation,
        }

    intent = _stream_intent("prune", (token, head, retain))
    request = create_approval_request(intent, assess_risk(intent))
    binding = {
        "request_id": request.request_id,
        "stream_id": key.stream_id,
        "writer_epoch": token.writer_epoch,
        "generation": head.generation,
        "head_digest": head.digest(),
        "retain_checkpoints": retain,
        "intent_fingerprint": intent_fingerprint(intent),
    }
    emit({"status": "approval_requested", **binding})
    _await_decision(request.request_id, intent, cancelled)
    os.environ[_APPROVAL_ENV] = request.request_id
    receipt = _submit(
        worker,
        cancelled,
        "prune",
        token=token,
        expected_head=head,
        retain_checkpoints=retain,
    )
    if (
        type(receipt) is not PruneResult
        or receipt.head != head
        or receipt.deleted_count < 1
        or receipt.retained_count < head.generation - receipt.pruned_through
        or receipt.retained_count > min(retain, head.generation)
        or approval_status(request.request_id)["state"] != "consumed"
    ):
        raise CheckpointError("uncertain")
    return {
        "status": "pruned",
        **binding,
        "deleted_count": receipt.deleted_count,
        "pruned_through": receipt.pruned_through,
        "retained_count": receipt.retained_count,
    }


def main(argv=None, *, emit=_print_event, cancelled=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--retain", type=int, required=True)
    parser.add_argument("--prior-attempt", type=Path)
    args = parser.parse_args(argv)
    cancelled = threading.Event() if cancelled is None else cancelled
    try:
        database, key, attempt = _inputs(args)
    except (OSError, ValueError, RuntimeError, CheckpointError):
        emit({"status": "blocked", "reason": "invalid_inputs"})
        return 1

    worker = LifecycleCheckpointWorker(str(database))
    previous = os.environ.get(_APPROVAL_ENV)
    try:
        event = _maintain(worker, key, args.retain, attempt, emit, cancelled)
    except CheckpointError as exc:
        event = {"status": "blocked", "reason": exc.code}
    except Exception:
        event = {"status": "blocked", "reason": "unavailable"}
    finally:
        try:
            closed_in_budget = worker.shutdown(timeout=2.0)
            if not closed_in_budget:
                try:
                    emit({"status": "close_pending", "closed": False})
                finally:
                    # Keep the foreground owner alive until the daemon closes its connection.
                    while not worker.shutdown(timeout=1.0):
                        pass
        finally:
            if previous is None:
                os.environ.pop(_APPROVAL_ENV, None)
            else:
                os.environ[_APPROVAL_ENV] = previous
    if not closed_in_budget and event["status"] != "blocked":
        event = {"status": "blocked", "reason": "close_timeout"}
    emit({**event, "closed": True, "closed_in_budget": closed_in_budget})
    return int(event["status"] == "blocked")


if __name__ == "__main__":
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    raise SystemExit(main(cancelled=stop))
