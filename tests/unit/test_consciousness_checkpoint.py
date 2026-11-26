"""Exact, bounded aggregate checkpoints; no replayed trust events or runtime health."""

# Standard library imports
import copy
import importlib
import json
import threading
from dataclasses import FrozenInstanceError, replace
from functools import partial

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.self_trust import SelfTrust, SubsystemTrust
from Aetherra.perception_bus.bus import PerceptionBus


def codec():
    assert importlib.util.find_spec("Aetherra.consciousness.checkpoint") is not None
    return importlib.import_module("Aetherra.consciousness.checkpoint")


def payload():
    return {
        "schema": 1,
        "checkpoint_id": "a" * 32,
        "owner": "consciousness:observer",
        "scope": "observer_continuity:v1",
        "captured_at": 1000.0,
        "qualia": {
            "valence": -0.4,
            "arousal": 0.2,
            "certainty": 0.3,
            "curiosity": 0.4,
            "care": 0.5,
            "fatigue": 0.6,
        },
        "trust": {
            "half_life_s": 3600.0,
            "subsystems": [
                {
                    "name": "memory",
                    "score": 40.0,
                    "last_event_ts": 1000.0,
                    "history": [65.0, 52.0, 40.0],
                },
                {
                    "name": "kernel",
                    "score": 88.0,
                    "last_event_ts": 999.0,
                    "history": [100.0, 88.0],
                },
            ],
        },
    }


def test_trust_restores_exact_values_without_observations():
    assert hasattr(SelfTrust, "restore_checkpoint"), "exact trust restore API missing"
    mod = codec()
    state = mod.decode_checkpoint(payload())
    now = [1000.0]
    trust = SelfTrust(clock=lambda: now[0])
    trust.observe("old", "failed")
    trust.restore_checkpoint(state.trust)
    assert set(trust.subsystems) == {"memory", "kernel"}
    assert trust.subsystems["memory"].score == 40.0
    assert trust.subsystems["memory"].last_event_ts == 1000.0
    assert trust.subsystems["memory"].history == [65.0, 52.0, 40.0]
    assert trust.get_subsystem_scores()["memory"] == 40.0
    now[0] = 4600.0
    assert trust.get_subsystem_scores()["memory"] == pytest.approx(65.0)
    assert trust.subsystems["memory"].history == [65.0, 52.0, 40.0]
    now[0] = 500.0
    assert trust.get_subsystem_scores()["memory"] == pytest.approx(65.0)


def test_checkpoint_roundtrip_is_detached_and_immutable():
    mod = codec()
    source = payload()
    state = mod.decode_checkpoint(source)
    assert mod.encode_checkpoint(state) == source
    source["trust"]["subsystems"][0]["score"] = 99
    assert mod.encode_checkpoint(state)["trust"]["subsystems"][0]["score"] == 40
    with pytest.raises(FrozenInstanceError):
        state.captured_at = 0
    encoded = mod.encode_checkpoint(state)
    encoded["trust"]["subsystems"][0]["history"].append(1)
    assert mod.load_checkpoint_json(mod.dump_checkpoint_json(state)) == state
    assert mod.encode_checkpoint(state)["trust"]["subsystems"][0]["history"] == [
        65,
        52,
        40,
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", 2),
        ("schema", True),
        ("schema", 1.0),
        ("checkpoint_id", "A" * 32),
        ("checkpoint_id", "../foreign"),
        ("owner", "consciousness:temporal"),
        ("scope", "conversation"),
        ("captured_at", -1),
        ("captured_at", True),
        ("captured_at", float("nan")),
    ],
)
def test_rejects_bad_envelope(field, value):
    mod = codec()
    data = payload()
    data[field] = value
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        mod.decode_checkpoint(data)


@pytest.mark.parametrize(
    ("dim", "value"),
    [
        ("valence", -1.1),
        ("valence", 1.1),
        ("arousal", -0.1),
        ("care", 1.1),
        ("fatigue", True),
        ("certainty", float("inf")),
        ("curiosity", "0.5"),
    ],
)
def test_rejects_invalid_qualia(dim, value):
    data = payload()
    data["qualia"][dim] = value
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        codec().decode_checkpoint(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "private path/name"),
        ("name", "x" * 65),
        ("score", -1),
        ("score", 101),
        ("score", True),
        ("last_event_ts", -1),
        ("last_event_ts", float("inf")),
        ("history", [1] * 65),
        ("history", [False]),
        ("history", [101]),
    ],
)
def test_rejects_invalid_trust(field, value):
    data = payload()
    data["trust"]["subsystems"][0][field] = value
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        codec().decode_checkpoint(data)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda p: p.update(private_text="do not persist"),
        lambda p: p["qualia"].update(other=0),
        lambda p: p["trust"].update(unexpected=1),
        lambda p: p["trust"]["subsystems"][0].update(event="invented"),
        lambda p: p["trust"].update(half_life_s=0),
        lambda p: p["trust"].update(half_life_s=True),
        lambda p: p["trust"]["subsystems"].append(
            copy.deepcopy(p["trust"]["subsystems"][0])
        ),
        lambda p: p["trust"].update(
            subsystems=[
                {"name": f"s{i}", "score": 40, "last_event_ts": 1, "history": []}
                for i in range(65)
            ]
        ),
    ],
)
def test_rejects_unknown_fields_and_ambiguous_trust(mutate):
    data = payload()
    mutate(data)
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        codec().decode_checkpoint(data)


@pytest.mark.parametrize(
    "data",
    [
        b'{"schema":1,"schema":1}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b"[" * 9 + b"0" + b"]" * 9,
        b"x" * 65537,
        b"\xff",
        b"{}",
        b"[]",
        b"null",
    ],
    ids=[
        "duplicate",
        "nan",
        "infinity",
        "depth",
        "size",
        "encoding",
        "empty",
        "array",
        "null",
    ],
)
def test_json_boundary_rejects_untrusted_input(data):
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        codec().load_checkpoint_json(data)


def test_valid_bounds_and_nested_duplicate_keys():
    mod = codec()
    data = payload()
    data["qualia"]["valence"] = -1
    data["qualia"]["care"] = 1
    data["trust"]["subsystems"][0]["history"] = [0, 100] * 32
    assert mod.encode_checkpoint(mod.decode_checkpoint(data)) == data
    raw = json.dumps(data).replace('"score": 40.0', '"score": 40.0, "score": 41.0')
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        mod.load_checkpoint_json(raw)


def test_core_restore_does_not_restore_lifecycle_or_shared_state():
    mod = codec()
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    core.restore_observer_checkpoint(mod.decode_checkpoint(payload()))
    assert core.qualia.valence == -0.4
    assert core.qualia.fatigue == 0.6
    assert core.self_trust.subsystems["memory"].score == 40.0
    assert core.tick_count == core.total_events_perceived == 0
    assert core.working_memory == core.active_intents == core.narrative_thread == []
    assert core.continuity.path is None
    assert core.continuity.buffer == []
    assert core.consolidator is core.safety_envelope is None
    exported = core.export_observer_checkpoint("b" * 32)
    assert exported.checkpoint_id == "b" * 32
    assert mod.encode_checkpoint(exported)["trust"]["subsystems"][0]["name"] == "kernel"
    assert core.self_trust.subsystems["memory"].score == 40.0


def test_invalid_restore_leaves_all_state_untouched():
    mod = codec()
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    good = mod.decode_checkpoint(payload())
    core.restore_observer_checkpoint(good)
    before = (core.qualia, core.self_trust.subsystems)
    bad = replace(good, qualia=(("valence", 9.0),))
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        core.restore_observer_checkpoint(bad)
    assert (core.qualia, core.self_trust.subsystems) == before
    assert core.qualia is before[0]
    assert core.self_trust.subsystems is before[1]
    core.tick_count = 1
    with pytest.raises(RuntimeError, match="checkpoint_restore_after_tick"):
        core.restore_observer_checkpoint(good)


def test_checkpoint_methods_require_the_core_owner_thread():
    mod = codec()
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    errors = []

    def other_thread():
        for operation in (
            lambda: core.export_observer_checkpoint("b" * 32),
            lambda: core.restore_observer_checkpoint(mod.decode_checkpoint(payload())),
        ):
            try:
                operation()
            except RuntimeError as exc:
                errors.append(str(exc))

    thread = threading.Thread(target=other_thread)
    thread.start()
    thread.join(timeout=2)
    assert not thread.is_alive()
    assert errors == ["checkpoint_wrong_thread", "checkpoint_wrong_thread"]
    assert core.tick_count == 0
    assert core.self_trust.subsystems == {}


def test_export_bounds_history_without_mutating_live_trust():
    mod = codec()
    trust = SelfTrust(clock=lambda: 1000)
    trust.subsystems["memory"] = SubsystemTrust("memory", 40, 1000, list(range(100)))
    state = trust.export_checkpoint()
    assert len(state.subsystems[0].history) == 64
    assert state.subsystems[0].history[0] == 36
    assert len(trust.subsystems["memory"].history) == 100
    assert mod.decode_checkpoint(payload()).trust.subsystems[0].score == 40


@pytest.mark.parametrize("case", ["history", "subsystems", "live_map"])
def test_typed_invalid_containers_reject_before_unbounded_allocation(case):
    # Standard library imports
    import tracemalloc

    mod = codec()
    base = mod.decode_checkpoint(payload()).trust
    if case == "history":
        bad = replace(
            base, subsystems=(replace(base.subsystems[0], history=(1.0,) * 100000),)
        )
        operation = partial(mod.validate_trust_checkpoint, bad)
    elif case == "subsystems":
        bad = replace(base, subsystems=(base.subsystems[0],) * 10000)
        operation = partial(mod.validate_trust_checkpoint, bad)
    else:
        trust = SelfTrust()
        trust.subsystems = {
            f"s{i}": SubsystemTrust(f"s{i}", 40, 1000, [40]) for i in range(10000)
        }
        operation = trust.export_checkpoint
    tracemalloc.start()
    try:
        with pytest.raises(ValueError, match="checkpoint_invalid"):
            operation()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 128 * 1024


def test_invalid_typed_trust_restore_preserves_scores_and_half_life():
    mod = codec()
    good = mod.decode_checkpoint(payload()).trust
    trust = SelfTrust(clock=lambda: 1000)
    trust.restore_checkpoint(good)
    before = trust.subsystems
    bad = replace(good, half_life_s=0)
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        trust.restore_checkpoint(bad)
    assert trust.subsystems is before
    assert trust.half_life == 3600
    assert trust.subsystems["memory"].score == 40


def test_full_subsystem_boundary_and_serialized_size_are_enforced():
    mod = codec()
    data = payload()
    data["trust"]["subsystems"] = [
        {"name": f"s{i}", "score": 40, "last_event_ts": 1000, "history": [40]}
        for i in range(64)
    ]
    state = mod.decode_checkpoint(data)
    assert len(state.trust.subsystems) == 64
    for item in data["trust"]["subsystems"]:
        item["history"] = [0.12345678901234567] * 64
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        mod.decode_checkpoint(data)
    with pytest.raises(ValueError, match="checkpoint_invalid"):
        mod.load_checkpoint_json('"' + "\u00e9" * 32768 + '"')


@pytest.mark.parametrize("section", ["root", "qualia", "trust", "record"])
def test_oversized_dictionary_rejected_before_key_copy(section):
    # Standard library imports
    import tracemalloc

    # Aetherra imports
    from Aetherra.consciousness.checkpoint import decode_checkpoint

    value = {
        "schema": 1,
        "checkpoint_id": "a" * 32,
        "owner": "consciousness:observer",
        "scope": "observer_continuity:v1",
        "captured_at": 123.0,
        "qualia": {
            "valence": -0.2,
            "arousal": 0.2,
            "certainty": 0.3,
            "curiosity": 0.4,
            "care": 0.5,
            "fatigue": 0.6,
        },
        "trust": {
            "half_life_s": 3600.0,
            "subsystems": [
                {
                    "name": "memory",
                    "score": 40.0,
                    "last_event_ts": 120.0,
                    "history": [40.0],
                }
            ],
        },
    }
    oversized = {str(i): i for i in range(100000)}
    if section == "root":
        value = oversized
    elif section == "qualia":
        value["qualia"] = oversized
    elif section == "trust":
        value["trust"] = oversized
    else:
        value["trust"]["subsystems"][0] = oversized
    tracemalloc.start()
    try:
        with pytest.raises(ValueError, match="checkpoint_invalid"):
            decode_checkpoint(value)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 200000


@pytest.mark.parametrize("boundary", ["other_thread", "after_tick"])
def test_prepared_restore_still_requires_unticked_owner_at_application(boundary):
    # Standard library imports
    from concurrent.futures import ThreadPoolExecutor

    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    original = core.qualia, core.self_trust.subsystems
    apply = core.prepare_observer_checkpoint_restore(
        codec().decode_checkpoint(payload())
    )
    if boundary == "other_thread":
        with (
            ThreadPoolExecutor(max_workers=1) as pool,
            pytest.raises(RuntimeError, match="checkpoint_wrong_thread"),
        ):
            pool.submit(apply).result(timeout=2)
    else:
        core.tick_count = 1
        with pytest.raises(RuntimeError, match="checkpoint_restore_after_tick"):
            apply()
    assert core.qualia is original[0]
    assert core.self_trust.subsystems is original[1]
