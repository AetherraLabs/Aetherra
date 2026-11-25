"""Child-side witnesses for the disposable automatic-stream launcher harness."""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import os
import sqlite3
import threading
import time
from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import patch

# Third party imports
from alpha_integration_smoke import write_json

CUTS = ("before_insert", "after_insert", "after_cas", "after_commit")


class StreamProbe:
    def __init__(self, artifacts):
        self.artifacts = artifacts
        self.options = json.loads(
            (artifacts / "harness.json").read_text(encoding="utf-8")
        )
        self.submissions = []
        self.last_periodic = None
        self.next_sample = 1

    def sample(self, observer):
        status = observer.get_runtime_status()
        receipt = status["continuity"]
        if (
            receipt["last_save_acceptance"] == "acknowledged"
            and receipt["last_save_trigger"] == "periodic"
            and self.last_periodic != receipt["saved_operation_id"]
        ):
            self.last_periodic = receipt["saved_operation_id"]
            write_json(self.artifacts / f"periodic-{self.last_periodic}.json", receipt)
        if (self.artifacts / f"request-{self.next_sample}").exists():
            write_json(
                self.artifacts / f"sample-{self.next_sample}.json",
                {
                    "status": status,
                    "submissions": self.submissions[:],
                    "sample_monotonic": time.monotonic(),
                },
            )
            self.next_sample += 1

    def install(self, stack, launcher):
        # Aetherra imports
        from Aetherra.consciousness import runtime_observer
        from Aetherra.consciousness.checkpoint_session import ObserverCheckpointSession

        adapter = launcher.MemoryAdapter
        submit = adapter._submit_checkpoint_stream

        def observed_submit(instance, **job):
            request = job.get("request")
            self.submissions.append(
                {
                    "operation": job["operation"],
                    "operation_id": request.attempt.operation_id if request else None,
                    "monotonic": time.monotonic(),
                    "deadline": job["control"].deadline,
                }
            )
            return submit(instance, **job)

        stack.enter_context(
            patch.object(adapter, "_submit_checkpoint_stream", observed_submit)
        )
        schedule = ObserverCheckpointSession._schedule_write
        consume = ObserverCheckpointSession._consume_write

        def timed_schedule(session):
            count = len(self.submissions)
            due = session._next_due
            result = schedule(session)
            if len(self.submissions) > count:
                self.submissions[-1]["periodic_due_monotonic"] = due
            return result

        def timed_consume(session, *args, **kwargs):
            old_id = session._status["saved_operation_id"]
            consume_start = time.monotonic()
            result = consume(session, *args, **kwargs)
            consume_end = time.monotonic()
            accepted = session._status["saved_operation_id"]
            if accepted and accepted != old_id:
                submission = self.submissions[-1]
                assert submission["operation_id"] == accepted
                submission["consume_started_monotonic"] = consume_start
                submission["acknowledged_monotonic"] = consume_end
            return result

        stack.enter_context(
            patch.object(ObserverCheckpointSession, "_schedule_write", timed_schedule)
        )
        stack.enter_context(
            patch.object(ObserverCheckpointSession, "_consume_write", timed_consume)
        )
        observer = runtime_observer.ConsciousnessObserver
        restore = observer._restore_checkpoint

        def observed_restore(instance, core):
            result = restore(instance, core)
            write_json(
                self.artifacts / "selection.json",
                {
                    "status": instance.get_runtime_status(),
                    "session_clock": {
                        "session_started_monotonic": instance._session.started_monotonic,
                        "save_interval_seconds": instance._session._config[
                            "save_interval_seconds"
                        ],
                        "retain_checkpoints": instance._session._config[
                            "retain_checkpoints"
                        ],
                    },
                    "submissions": self.submissions[:],
                    "core_ticks": core.tick_count,
                    "core_events": core.total_events_perceived,
                },
            )
            return result

        stack.enter_context(
            patch.object(observer, "_restore_checkpoint", observed_restore)
        )
        if "synthetic_wall" in self.options:
            # Aetherra imports
            from Aetherra.consciousness.core import consciousness_core

            # Only these two modules see the fixture wall clock. Monotonic
            # eligibility, acceptance deadlines, SQLite and the OS clock are real.
            start = time.monotonic()
            wall = self.options["synthetic_wall"]
            clock = SimpleNamespace(
                time=lambda: wall + (time.monotonic() - start),
                monotonic=time.monotonic,
                sleep=time.sleep,
            )
            for module in (runtime_observer, consciousness_core):
                stack.enter_context(patch.object(module, "time", clock))
        if "shared_core" in self.options:
            # Aetherra imports
            from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
                AetherraMemoryEngineAdvanced,
                MemorySystemConfig,
            )

            init = AetherraMemoryEngineAdvanced.__init__

            def shared_init(engine, config=None):
                assert config is None
                init(
                    engine, MemorySystemConfig(core_db_path=self.options["shared_core"])
                )

            stack.enter_context(
                patch.object(AetherraMemoryEngineAdvanced, "__init__", shared_init)
            )
        if "cut" in self.options:
            self.install_cut(stack)

    def install_cut(self, stack):
        # Aetherra imports
        from Aetherra.aetherra_core.memory import (
            checkpoint_stream,
            lifecycle_checkpoint,
        )

        target = self.options["cut"]
        assert target in CUTS
        active = {}
        advance = checkpoint_stream._advance
        insert = checkpoint_stream._insert_checkpoint

        def barrier(db, boundary):
            if target != boundary:
                return
            assert db is active["db"]
            assert db.in_transaction == (boundary != "after_commit")
            write_json(
                self.artifacts / "cut.json",
                {
                    "pid": os.getpid(),
                    "boundary": boundary,
                    "in_transaction": db.in_transaction,
                    "attempt": active["attempt"],
                    "record_id": active["row"],
                    "audit_id": active["audit"],
                },
            )
            # Only the parent owning this process may complete a cut, by killing it.
            threading.Event().wait()

        class CutConnection(sqlite3.Connection):
            def commit(self):
                result = super().commit()
                if active.get("db") is self and active.get("cas"):
                    barrier(self, "after_commit")
                return result

        def connect(*args, **kwargs):
            return sqlite3.connect(*args, factory=CutConnection, **kwargs)

        def observed_insert(db, record_id, checkpoint_id, data):
            if db is not active.get("db"):
                return insert(db, record_id, checkpoint_id, data)
            assert checkpoint_id == active["attempt"]["checkpoint_id"]
            assert (
                hashlib.sha256(data).hexdigest() == active["attempt"]["payload_digest"]
            )
            active["row"] = record_id
            barrier(db, "before_insert")
            inserted = insert(db, record_id, checkpoint_id, data)
            assert inserted == 1
            barrier(db, "after_insert")
            return inserted

        def observed_advance(db, request, audit):
            attempt = request.attempt
            if (
                attempt.token.key.stream_id,
                attempt.token.writer_epoch,
                attempt.proposed_generation,
            ) != (
                self.options["stream_id"],
                self.options["epoch"],
                self.options["generation"],
            ):
                return advance(db, request, audit)
            assert not active
            assert json.loads(request.metadata_bytes)["save_trigger"] == "orderly_stop"
            active.update(db=db, attempt=asdict(attempt), audit=audit)
            receipt = advance(db, request, audit)
            assert receipt.head.record_id == active["row"]
            active["cas"] = True
            barrier(db, "after_cas")
            return receipt

        stack.enter_context(
            patch.object(
                lifecycle_checkpoint, "sqlite3", SimpleNamespace(connect=connect)
            )
        )
        stack.enter_context(
            patch.object(checkpoint_stream, "_advance", observed_advance)
        )
        stack.enter_context(
            patch.object(checkpoint_stream, "_insert_checkpoint", observed_insert)
        )
