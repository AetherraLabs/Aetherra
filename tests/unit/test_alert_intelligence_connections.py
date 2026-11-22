"""Alert database operations release real SQLite handles before returning."""

# Standard library imports
import contextlib
import sqlite3

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis import intelligent_alert_manager
from Aetherra.homeostasis.alert_intelligence import AdaptiveThresholdEngine
from Aetherra.homeostasis.lyrixa_integration import LyrixaAlertIntegration


@pytest.fixture
def owned_connections(monkeypatch):
    connect = sqlite3.connect
    connections = []

    def tracked_connect(*args, **kwargs):
        connection = connect(*args, **kwargs)
        connections.append(connection)
        return connection

    monkeypatch.setattr(sqlite3, "connect", tracked_connect)
    try:
        yield connections
    finally:
        for connection in connections:
            connection.close()


@pytest.fixture(params=["engine", "manager"])
def database_owner(request, tmp_path, monkeypatch, owned_connections):
    engine = AdaptiveThresholdEngine(db_path=str(tmp_path / "thresholds.db"))
    if request.param == "engine":
        return engine

    monkeypatch.setattr(
        intelligent_alert_manager, "get_adaptive_threshold_engine", lambda: engine
    )
    monkeypatch.setattr(
        intelligent_alert_manager, "get_lyrixa_integration", LyrixaAlertIntegration
    )
    return intelligent_alert_manager.IntelligentAlertManager(
        db_path=str(tmp_path / "alerts.db")
    )


def assert_connections_closed(connections):
    assert connections
    for connection in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
            connection.execute("SELECT 1")


async def write_sample(owner):
    if isinstance(owner, AdaptiveThresholdEngine):
        await owner.add_metric_sample("cpu_usage", 42.0)
    else:
        await owner._record_alert_event("alert-1", "created", {})


def test_initialization_releases_database_handles(database_owner, owned_connections):
    assert_connections_closed(owned_connections)


@pytest.mark.asyncio
async def test_write_commits_and_releases_database_handles(
    database_owner, owned_connections
):
    await write_sample(database_owner)
    assert_connections_closed(owned_connections)

    with contextlib.closing(sqlite3.connect(database_owner.db_path)) as connection:
        if isinstance(database_owner, AdaptiveThresholdEngine):
            rows = connection.execute(
                "SELECT metric_name, value FROM metric_history"
            ).fetchall()
            assert rows == [("cpu_usage", 42.0)]
        else:
            rows = connection.execute(
                "SELECT alert_id, event_type FROM alert_events"
            ).fetchall()
            assert rows == [("alert-1", "created")]


@pytest.mark.asyncio
async def test_failed_write_releases_database_handles(
    database_owner, owned_connections, caplog
):
    table = (
        "metric_history"
        if isinstance(database_owner, AdaptiveThresholdEngine)
        else "alert_events"
    )
    with contextlib.closing(sqlite3.connect(database_owner.db_path)) as connection:
        connection.execute(f"DROP TABLE {table}")
        connection.commit()

    await write_sample(database_owner)

    assert "no such table" in caplog.text
    assert_connections_closed(owned_connections)


@pytest.mark.asyncio
async def test_insufficient_history_releases_database_handles(
    tmp_path, owned_connections
):
    engine = AdaptiveThresholdEngine(db_path=str(tmp_path / "thresholds.db"))

    await engine._update_pattern_for_metric("no_samples")
    await engine._rebuild_model_for_metric("no_samples")

    assert engine.metric_patterns == {}
    assert engine.anomaly_models == {}
    assert_connections_closed(owned_connections)
