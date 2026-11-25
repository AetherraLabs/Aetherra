"""Process-level transaction, fencing and clock witnesses on disposable full launches."""

from __future__ import annotations

# Standard library imports
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def auto():
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "tools"))
        # Third party imports
        import alpha_consciousness_automatic_smoke

        yield alpha_consciousness_automatic_smoke


def tick(status):
    return status["runtime_state"] == "running" and status["ticks_completed"] > 0


@pytest.mark.parametrize(
    "cut", ["before_insert", "after_insert", "after_cas", "after_commit"]
)
def test_kill_at_real_transaction_boundary(auto, tmp_path, cut):
    stream = uuid.uuid4().hex
    profile = tmp_path / "profile"
    database = profile / "lyrixa_memory.db"
    auto.configure(profile, stream, "create")
    with auto.launched(profile, tmp_path / "baseline", "a") as baseline:
        baseline.until(tick, 15)
    old = auto.inventory(database, stream)
    assert len(old["rows"]) == 1
    old_row = old["rows"][0]
    auto.acknowledged(
        baseline.provider["final_observer"]["continuity"],
        old_row,
        "orderly_stop",
        profile,
    )
    auto.configure(profile, stream, "resume")
    with auto.launched(
        profile, tmp_path / "cut", "b", cut=cut, stream_id=stream, epoch=2, generation=2
    ) as child:
        auto.restored(child, old_row)
        child.until(tick, 15)
        before = auto.inventory(database, stream)
        (child.artifacts / "stop-runtime").touch()
        witness = child.kill_at_cut()
    assert not (child.artifacts / "provider.json").exists()
    attempt = witness["attempt"]
    assert attempt["token"] == {
        "key": {"owner": auto.OWNER, "scope": auto.SCOPE, "stream_id": stream},
        "writer_epoch": 2,
    }
    assert attempt["expected_head"] == {k: before["head"][k] for k in auto.IDENTITY}
    assert witness["boundary"] == cut
    committed = cut == "after_commit"
    assert witness["in_transaction"] is not committed
    after = auto.inventory(database, stream, candidate=witness)
    assert after["candidate_ids"] == ([witness["record_id"]] if committed else [])
    if committed:
        assert len(after["rows"]) == 2
        assert after["rows"][0] == old_row
        new = after["rows"][1]
        assert new["generation"] == 2
        assert new["writer_epoch"] == 2
        assert new["record_id"] == witness["record_id"]
        assert new["audit_id"] == witness["audit_id"]
        assert new["metadata"]["save_trigger"] == "orderly_stop"
        assert all(
            new[k] == attempt[k]
            for k in (
                "operation_id",
                "checkpoint_id",
                "payload_digest",
                "metadata_digest",
            )
        )
    else:
        assert after == before
    assert any(
        r["audit_id"] == witness["audit_id"]
        and r["action"] == "consciousness.continuity_advance"
        for r in auto.smoke.audit_summary(profile)
    )
    auto.configure(profile, stream, "resume", recovery=attempt)
    with auto.launched(profile, tmp_path / "inspection", "b") as inspected:
        status = auto.restored(
            inspected,
            after["rows"][-1],
            outcome="committed_current" if committed else "not_committed",
        )
        assert status["observed_writer_epoch"] == 3
        assert status["matched_record_id"] == (
            witness["record_id"] if committed else None
        )
        checked = auto.inventory(database, stream, candidate=witness)
        assert checked["rows"] == after["rows"]
        assert checked["candidate_ids"] == after["candidate_ids"]
        assert checked["head"]["writer_epoch"] == 3
        assert checked["head"]["restore_pin_generation"] == after["head"]["generation"]
        inspected.until(tick, 15)
    final = auto.inventory(database, stream)
    assert final["rows"][:-1] == after["rows"]
    assert final["rows"][-1]["operation_id"] != attempt["operation_id"]
    auto.acknowledged(
        inspected.provider["final_observer"]["continuity"],
        final["rows"][-1],
        "orderly_stop",
        profile,
    )


@pytest.fixture(scope="module")
def takeover(auto, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("takeover")
    stream = uuid.uuid4().hex
    database = tmp_path / "shared-core.db"
    left, right = tmp_path / "left", tmp_path / "right"
    auto.configure(left, stream, "create", interval=30)
    auto.configure(right, stream, "resume", interval=30)
    with auto.launched(left, tmp_path / "old", "a", shared_core=str(database)) as old:
        auto.smoke.chat(old.base, auto.smoke.FACT)
        prior = old.until(
            lambda s: s["continuity"]["last_save_acceptance"] == "acknowledged", 45
        )
        old_row = auto.inventory(database, stream)["rows"][-1]
        auto.acknowledged(prior["status"]["continuity"], old_row, "periodic", left)
        with auto.launched(
            right, tmp_path / "new", "b", shared_core=str(database)
        ) as new:
            assert new.port != old.port
            assert new.process.pid != old.process.pid
            auto.restored(new, old_row)
            assert (
                "Leona"
                in auto.smoke.chat(new.base, auto.smoke.QUESTION)["body"]["result"][
                    "response"
                ]
            )
            lost = old.until(lambda s: s["continuity"]["ownership_state"] == "lost", 45)
            status = lost["status"]
            assert tick(status)
            assert status["think_stream_available"]
            assert status["continuity"]["last_error_code"] == "writer_fenced"
            assert status["continuity"]["saved_record_id"] == old_row["record_id"]
            assert [s["operation"] for s in lost["submissions"]] == [
                "acquire",
                "advance",
                "advance",
            ]
            assert (
                "Leona"
                in auto.smoke.chat(old.base, auto.smoke.QUESTION)["body"]["result"][
                    "response"
                ]
            )
            public = [auto.smoke.snapshot(old.base) for _ in range(3)]
            auto.write_json(old.artifacts / "fenced-public.json", public)
            time.sleep(31)
            sample = old.sample()
            assert sample["submissions"] == lost["submissions"]
            assert sample["status"]["ticks_completed"] > status["ticks_completed"]
            assert sample["status"]["continuity"]["ownership_state"] == "lost"
            accepted = new.until(
                lambda s: s["continuity"]["last_save_acceptance"] == "acknowledged", 15
            )
            rows = auto.inventory(database, stream)["rows"]
            assert rows[0] == old_row
            assert all(r["writer_epoch"] == 2 for r in rows[1:])
            auto.acknowledged(
                accepted["status"]["continuity"], rows[-1], "periodic", right
            )
        after_new = auto.inventory(database, stream)
        auto.acknowledged(
            new.provider["final_observer"]["continuity"],
            after_new["rows"][-1],
            "orderly_stop",
            right,
        )
    assert old.provider["submissions"] == lost["submissions"]
    assert old.provider["final_observer"]["continuity"]["ownership_state"] == "lost"
    assert auto.inventory(database, stream) == after_new
    return old, public


def test_two_live_launchers_fence_old_writer_while_ticks_and_chat_continue(takeover):
    old, _ = takeover
    assert (
        old.provider["final_observer"]["continuity"]["last_error_code"]
        == "writer_fenced"
    )


def test_fenced_public_projection_preserves_live_thinkstream(takeover):
    _, responses = takeover
    for response in responses:
        assert response["think"]["status"] == 200
        assert response["think"]["body"]["tick_id"] > 0
        assert response["ui"]["status"] == 200
        metrics = response["ui"]["body"]["subsystem"]["metrics"]
        assert metrics["continuity_ownership_state"] == "lost"
        assert metrics["continuity_health"] == "degraded"
        assert metrics["ticks_completed"] > 0


def test_synthetic_monday_friday_restores_only_verified_observations(auto, tmp_path):
    profile = tmp_path / "calendar"
    stream = uuid.uuid4().hex
    monday = datetime(2026, 11, 23, 12, tzinfo=UTC).timestamp()
    friday = monday + 4 * 86400
    auto.configure(profile, stream, "create")
    with auto.launched(
        profile, tmp_path / "monday", "a", synthetic_wall=monday
    ) as first:
        first.until(tick, 15)
    row = auto.inventory(profile / "lyrixa_memory.db", stream)["rows"][0]
    observed = row["metadata"]["last_verified_observation_at_unix_s"]
    assert monday <= observed < monday + 300
    auto.configure(profile, stream, "resume")
    with auto.launched(
        profile, tmp_path / "friday", "b", synthetic_wall=friday
    ) as second:
        status = auto.restored(second, row)
        assert friday <= status["session_started_at_unix_s"] < friday + 300
        assert status["observation_gap_state"] == "host_wall_clock_estimate"
        assert (
            status["observation_gap_seconds"]
            == status["session_started_at_unix_s"] - observed
        )
        assert status["offline_duration_state"] == "unknown"
        assert status["offline_duration_seconds"] is None
        assert second.selection["status"]["ticks_completed"] == 0


def test_automatic_retention_without_one_use_approval_latches(auto, tmp_path):
    stream = uuid.uuid4().hex
    profile = tmp_path / "no-approval"
    database = profile / "lyrixa_memory.db"
    auto.configure(profile, stream, "create", interval=30, retain=2)
    with auto.launched(profile, tmp_path / "writer", "a") as writer:
        blocked = writer.until(
            lambda s: s["continuity"]["state"] == "retention_blocked", 110
        )
        snapshot = auto.inventory(database, stream)
        assert [r["generation"] for r in snapshot["rows"]] == [1, 2, 3]
        assert snapshot["head"]["pruned_through"] == 0
        assert snapshot["head"]["retain_checkpoints"] == 2
        receipt = blocked["status"]["continuity"]
        assert receipt["retention_needed"]
        assert receipt["last_error_code"] == "denied"
        auto.acknowledged(receipt, snapshot["rows"][-1], "periodic", profile)
        assert [s["operation"] for s in blocked["submissions"]] == [
            "acquire",
            "advance",
            "advance",
            "advance",
            "prune",
        ]
        assert tick(blocked["status"])
        time.sleep(31)
        later = writer.sample()
        assert later["status"]["ticks_completed"] > blocked["status"]["ticks_completed"]
        assert later["submissions"] == blocked["submissions"]
    assert writer.provider["submissions"] == blocked["submissions"]
    assert (
        writer.provider["final_observer"]["continuity"]["state"] == "retention_blocked"
    )
    assert auto.inventory(database, stream) == snapshot
