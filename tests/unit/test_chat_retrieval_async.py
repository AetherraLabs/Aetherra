"""Cold chat ranking must not stall the caller loop or outlive its Memory owner."""

# Standard library imports
import asyncio
import sqlite3
import threading
from types import SimpleNamespace

# Third party imports
import aiohttp
import numpy as np
import pytest
import pytest_asyncio
from flask import Flask

# Aetherra imports
from Aetherra.aetherra_core.memory import chat_retrieval
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from aetherra_hub.blueprints.health import bp as health_blueprint
from aetherra_hub.request_server import BoundedWSGIServer

FACT = "My aunt Leona taught me to mend a flat bike tire."
DISTRACTOR = "My uncle Mateo taught me how to swim."
QUERY = "Who showed me how to repair a puncture on my bicycle?"


class EncoderGate:
    """Replace only expensive model work; real rank/filtering/SQLite stay active."""

    def __init__(self, *, phase="load", timeout=2.0, loop=None):
        self.phase = phase
        self.timeout = timeout
        self.loop = loop
        self.started = asyncio.Event() if loop is not None else None
        self.entered = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()
        self.watchdog_fired = threading.Event()
        self.timer = None

    def _hold(self):
        def emergency_release():
            self.watchdog_fired.set()
            self.release.set()

        self.timer = threading.Timer(self.timeout, emergency_release)
        self.timer.daemon = True
        self.timer.start()
        self.entered.set()
        if self.started is not None:
            self.loop.call_soon_threadsafe(self.started.set)
        self.release.wait()

    def load(self):
        if self.phase == "load":
            self._hold()
        return self

    def encode(self, texts, *, normalize_embeddings, show_progress_bar):
        assert normalize_embeddings is True
        assert show_progress_bar is False
        try:
            if self.phase == "encode":
                self._hold()
            # Literal orthogonal evidence: the query/fact match, swimming does not.
            return np.array(
                [[1.0, 0.0] if text in {QUERY, FACT} else [0.0, 1.0] for text in texts]
            )
        finally:
            self.finished.set()

    def close(self):
        self.release.set()
        if self.timer is not None:
            self.timer.cancel()
            self.timer.join(timeout=2)
            assert not self.timer.is_alive()


@pytest_asyncio.fixture
async def stored_memory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory = LyrixaMemorySystem(str(tmp_path / "chat.db"))
    saved_id = await memory.store_memory({"role": "user", "content": FACT})
    await memory.store_memory({"role": "user", "content": DISTRACTOR})
    await memory.store_memory({"role": "assistant", "content": "An invented answer."})
    assert saved_id
    try:
        yield SimpleNamespace(memory=memory, saved_id=saved_id)
    finally:
        memory.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["load", "encode"])
async def test_slow_ranking_keeps_loop_responsive_and_sqlite_on_caller(
    stored_memory, monkeypatch, phase
):
    state = stored_memory
    caller = threading.get_ident()
    statements = []
    state.memory.conn.set_trace_callback(
        lambda sql: statements.append((threading.get_ident(), sql))
    )
    gate = EncoderGate(phase=phase, loop=asyncio.get_running_loop())
    monkeypatch.setattr(chat_retrieval, "_encoder", gate.load)
    task = asyncio.create_task(state.memory.recall_chat_memories(QUERY))
    try:
        await asyncio.wait_for(gate.started.wait(), 4)
        assert not gate.watchdog_fired.is_set(), "Ranking blocked the caller event loop"
        assert not task.done()
        gate.release.set()
        hits = await asyncio.wait_for(task, 3)
        assert [hit.id for hit in hits] == [state.saved_id]
        assert hits[0].content == {"role": "user", "content": FACT}
        assert hits[0].relevance == 1.0
        assert any(sql.startswith("SELECT") for _, sql in statements)
        assert any("UPDATE memories" in sql for _, sql in statements)
        assert {thread for thread, _ in statements} == {caller}
    finally:
        gate.close()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
async def test_first_http_headers_progress_while_cold_recall_is_running(
    stored_memory, monkeypatch
):
    # The production five-second per-socket timeout is deliberately unchanged.
    # Control only ordering: actual TCP connect, then real recall, then headers.
    app = Flask(__name__)
    app.register_blueprint(health_blueprint)
    server = BoundedWSGIServer("127.0.0.1", 0, app)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    gate = EncoderGate(timeout=6.5)
    monkeypatch.setattr(chat_retrieval, "_encoder", gate.load)
    recalls = []
    trace = aiohttp.TraceConfig()

    async def connected(_session, _context, _params):
        recalls.append(
            asyncio.create_task(stored_memory.memory.recall_chat_memories(QUERY))
        )
        # Queue the next client continuation behind the newly admitted recall.
        await asyncio.sleep(0)

    trace.on_connection_create_end.append(connected)
    try:
        # POST has no implicit aiohttp reconnect retry. The health route
        # rejects its method only after real HTTP headers reach the Hub.
        async with (
            aiohttp.ClientSession(
                trace_configs=[trace], timeout=aiohttp.ClientTimeout(total=12)
            ) as client,
            client.post(f"http://127.0.0.1:{server.server_port}/health") as reply,
        ):
            assert reply.status == 405
        assert not gate.watchdog_fired.is_set(), "Headers stalled behind ranking"
        gate.release.set()
        results = await asyncio.wait_for(asyncio.gather(*recalls), 3)
        assert [[hit.id for hit in hits] for hits in results] == [
            [stored_memory.saved_id]
        ]
    finally:
        gate.close()
        await asyncio.gather(*recalls, return_exceptions=True)
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
        assert not worker.is_alive()
        assert server.wait_for_idle(timeout=3)


@pytest.mark.asyncio
async def test_cancelled_ranking_cannot_update_or_reopen_closed_memory(
    stored_memory, monkeypatch
):
    state = stored_memory
    database = state.memory.db_path
    gate = EncoderGate(loop=asyncio.get_running_loop())
    monkeypatch.setattr(chat_retrieval, "_encoder", gate.load)
    task = asyncio.create_task(state.memory.recall_chat_memories(QUERY))
    try:
        await asyncio.wait_for(gate.started.wait(), 4)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert state.memory.close()
        gate.release.set()
        assert await asyncio.to_thread(gate.finished.wait, 3)
        assert state.memory.conn is None
        with sqlite3.connect(database) as connection:
            count = connection.execute(
                "SELECT access_count FROM memories WHERE id = ?", (state.saved_id,)
            ).fetchone()[0]
        assert count == 0
    finally:
        gate.close()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["close", "replace"])
async def test_rank_result_is_rejected_after_memory_connection_changes(
    stored_memory, monkeypatch, change
):
    state = stored_memory
    original = state.memory.conn
    replacement = sqlite3.connect(state.memory.db_path, check_same_thread=False)
    gate = EncoderGate()
    monkeypatch.setattr(chat_retrieval, "_encoder", gate.load)
    changed = threading.Event()
    errors = []

    def change_owner():
        try:
            assert gate.entered.wait(3)
            if change == "close":
                assert state.memory.close()
            else:
                state.memory.conn = replacement
            changed.set()
        except BaseException as exc:
            errors.append(exc)
        finally:
            gate.release.set()

    coordinator = threading.Thread(target=change_owner, daemon=True)
    coordinator.start()
    try:
        with pytest.raises(RuntimeError, match="^chat_recall_connection_changed$"):
            await state.memory.recall_chat_memories(QUERY)
        assert changed.is_set()
        assert not errors
        assert state.memory.conn is (None if change == "close" else replacement)
        assert (
            replacement.execute(
                "SELECT access_count FROM memories WHERE id = ?", (state.saved_id,)
            ).fetchone()[0]
            == 0
        )
    finally:
        gate.close()
        coordinator.join(timeout=3)
        assert not coordinator.is_alive()
        if change == "replace":
            state.memory.conn = original
        replacement.close()


@pytest.mark.asyncio
async def test_waiting_for_shared_rank_lock_keeps_loop_responsive(
    stored_memory, monkeypatch
):
    entered = threading.Event()
    release = threading.Event()
    watchdog_fired = threading.Event()
    callback_ran = asyncio.Event()
    encoder = EncoderGate(phase="none")
    monkeypatch.setattr(chat_retrieval, "_encoder", encoder.load)

    def hold_rank_lock():
        with chat_retrieval._lock:
            entered.set()
            if not release.wait(2):
                watchdog_fired.set()

    def next_loop_turn():
        callback_ran.set()
        release.set()

    holder = threading.Thread(target=hold_rank_lock, daemon=True)
    holder.start()
    task = None
    try:
        assert await asyncio.to_thread(entered.wait, 3)
        task = asyncio.create_task(stored_memory.memory.recall_chat_memories(QUERY))
        # The recall is admitted before this callback: lock contention may not
        # prevent the callback (or another HTTP request) from making progress.
        asyncio.get_running_loop().call_soon(next_loop_turn)
        hits = await asyncio.wait_for(task, 4)
        assert callback_ran.is_set()
        assert not watchdog_fired.is_set(), "Rank lock stalled the event loop"
        assert [hit.id for hit in hits] == [stored_memory.saved_id]
    finally:
        release.set()
        holder.join(timeout=3)
        assert not holder.is_alive()
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)
