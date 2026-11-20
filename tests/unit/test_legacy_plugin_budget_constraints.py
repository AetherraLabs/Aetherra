"""Synthetic, offline source-to-sink contracts for legacy plugin budgets."""

# Standard library imports
import asyncio
import builtins
import importlib
import logging
import sys
from types import ModuleType, SimpleNamespace

# Third party imports
import pytest

PRIVATE = "private-constraint-payload"


@pytest.fixture
def runtime(monkeypatch, tmp_path, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0")
    monkeypatch.setenv("AETHERRA_CONSCIOUSNESS_PLUGIN_HOOK", "0")
    # Stub analytics before importing the module's global manager.
    analytics = ModuleType("Aetherra.plugins.core.plugin_analytics")
    analytics.PluginAnalyticsIntegration = lambda: None
    monkeypatch.setitem(sys.modules, analytics.__name__, analytics)
    module = importlib.import_module("Aetherra.plugins.core.plugin_manager")
    monkeypatch.setattr(
        module.PluginManager, "_initialize_analytics", lambda self: None
    )
    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir()
    manager = module.PluginManager(str(plugin_root))
    calls = []
    events = []

    def callback(*args, **kwargs):
        calls.append((args, kwargs))
        return "synthetic-result"

    manager.plugins["synthetic"] = SimpleNamespace(execute=callback)
    monkeypatch.setattr(
        manager,
        "track_plugin_event",
        lambda name, event, extra_context=None: events.append((event, extra_context)),
    )
    security = importlib.import_module("Aetherra.security")
    sandbox = importlib.import_module("Aetherra.security.sandbox")
    helper_calls = []

    def timed(func, args=None, kwargs=None, timeout_sec=5.0):
        helper_calls.append(("timeout", timeout_sec))
        return func(*(args or ()), **(kwargs or {}))

    def memory(max_mb):
        helper_calls.append(("memory", max_mb))

    helper = SimpleNamespace(
        run_with_timeout=timed,
        ensure_memory_budget=memory,
        TimeBudgetExceeded=sandbox.TimeBudgetExceeded,
        psutil=object(),
    )
    monkeypatch.setattr(security, "sandbox", helper)
    caplog.set_level(logging.DEBUG, logger=module.__name__)
    return SimpleNamespace(
        module=module,
        manager=manager,
        calls=calls,
        events=events,
        helper_calls=helper_calls,
        helper=helper,
        sandbox=sandbox,
        security=security,
        callback=callback,
    )


def assert_denied(runtime, caplog, capsys):
    assert len(runtime.calls) == 0, "denied request reached plugin callback"
    assert any(event == "execute_error" for event, _ in runtime.events)
    assert all(event != "execute_success" for event, _ in runtime.events)
    records = [
        record for record in caplog.records if record.name == runtime.module.__name__
    ]
    assert len(records) == 1
    assert records[0].exc_info is None
    assert records[0].stack_info is None
    output = capsys.readouterr()
    clean = PRIVATE not in (caplog.text + output.out + output.err + str(runtime.events))
    assert clean, "constraint diagnostic included private data"


INVALID = [
    None,
    "",
    "not-a-number",
    -1,
    -0.25,
    float("nan"),
    float("inf"),
    -float("inf"),
    "NaN",
    "Infinity",
    "-Infinity",
    "1e9999",
    "1e-9999",
    "-1e-9999",
    True,
    False,
    [],
    {},
    complex(1, 1),
]


@pytest.mark.parametrize("field", ["_timeout_sec", "_memory_mb"])
@pytest.mark.parametrize(
    "value", INVALID, ids=[f"invalid-{index}" for index in range(len(INVALID))]
)
def test_invalid_budget_never_invokes_plugin(runtime, caplog, capsys, field, value):
    assert (
        runtime.manager.execute_plugin("synthetic", PRIVATE, **{field: value}) is None
    )
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize(
    "budgets",
    [{"_timeout_sec": 1}, {"_memory_mb": 1}, {"_timeout_sec": 1, "_memory_mb": 1}],
)
def test_sandbox_import_failure_denies_budgeted_call(
    runtime, monkeypatch, caplog, capsys, budgets
):
    original_import = builtins.__import__

    def unavailable(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "Aetherra.security" and "sandbox" in fromlist:
            raise ImportError(PRIVATE)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", unavailable)
    assert runtime.manager.execute_plugin("synthetic", PRIVATE, **budgets) is None
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize(
    ("field", "attribute", "availability"),
    [
        ("_timeout_sec", "run_with_timeout", "absent"),
        ("_timeout_sec", "run_with_timeout", "none"),
        ("_timeout_sec", "run_with_timeout", "noncallable"),
        ("_memory_mb", "ensure_memory_budget", "absent"),
        ("_memory_mb", "ensure_memory_budget", "none"),
        ("_memory_mb", "ensure_memory_budget", "noncallable"),
        ("_memory_mb", "psutil", "absent"),
        ("_memory_mb", "psutil", "none"),
    ],
)
def test_required_helper_unavailable_denies(
    runtime, monkeypatch, caplog, capsys, field, attribute, availability
):
    if availability == "absent":
        monkeypatch.delattr(runtime.helper, attribute)
    else:
        monkeypatch.setattr(
            runtime.helper, attribute, None if availability == "none" else 42
        )
    assert runtime.manager.execute_plugin("synthetic", **{field: 1}) is None
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize("timeout", [0, 1])
def test_memory_failure_denies_even_without_timeout(
    runtime, monkeypatch, caplog, capsys, timeout
):
    def rejected(max_mb):
        raise runtime.sandbox.MemoryBudgetExceeded(PRIVATE)

    monkeypatch.setattr(runtime.helper, "ensure_memory_budget", rejected)
    assert (
        runtime.manager.execute_plugin(
            "synthetic", _timeout_sec=timeout, _memory_mb=0.25
        )
        is None
    )
    assert_denied(runtime, caplog, capsys)


def test_timeout_helper_failure_is_sanitized(runtime, monkeypatch, caplog, capsys):
    def rejected(func, *, timeout_sec):
        raise RuntimeError(PRIVATE)

    monkeypatch.setattr(runtime.helper, "run_with_timeout", rejected)
    assert runtime.manager.execute_plugin("synthetic", _timeout_sec=1) is None
    assert_denied(runtime, caplog, capsys)


def test_timeout_above_platform_join_limit_never_invokes(runtime, caplog, capsys):
    timeout = runtime.module.threading.TIMEOUT_MAX * 2
    assert runtime.manager.execute_plugin("synthetic", _timeout_sec=timeout) is None
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize(
    ("budgets", "expected"),
    [
        ({}, []),
        ({"_timeout_sec": 0, "_memory_mb": 0}, []),
        ({"_timeout_sec": "0", "_memory_mb": "0"}, []),
        ({"_timeout_sec": "1.25"}, [("timeout", 1.25)]),
        ({"_memory_mb": "0.25"}, [("memory", 0.25)]),
        ({"_timeout_sec": 1, "_memory_mb": 0.25}, [("memory", 0.25), ("timeout", 1.0)]),
    ],
)
@pytest.mark.parametrize("entrypoint", ["execute", "main"])
def test_success_invokes_exactly_once_and_consumes_constraints(
    runtime, budgets, expected, entrypoint
):
    runtime.manager.plugins["synthetic"] = SimpleNamespace(
        **{entrypoint: runtime.callback}
    )
    assert (
        runtime.manager.execute_plugin("synthetic", "input", option="value", **budgets)
        == "synthetic-result"
    )
    assert runtime.calls == [(("input",), {"option": "value"})]
    assert runtime.helper_calls == expected
    assert [event for event, _ in runtime.events] == [
        "execute_start",
        "execute_success",
    ]


def test_unbudgeted_execution_does_not_need_sandbox(runtime, monkeypatch):
    monkeypatch.setattr(runtime.security, "sandbox", None)
    assert runtime.manager.execute_plugin("synthetic") == "synthetic-result"
    assert len(runtime.calls) == 1


def test_invalid_budget_is_rejected_before_loading(
    runtime, monkeypatch, caplog, capsys
):
    loads = []
    monkeypatch.setattr(
        runtime.manager, "load_plugin", lambda name: loads.append(name) or False
    )
    assert runtime.manager.execute_plugin("unloaded", _timeout_sec="NaN") is None
    assert len(loads) == 0, "invalid constraint reached plugin loading"
    assert_denied(runtime, caplog, capsys)


def test_memory_failure_is_rejected_before_loading(
    runtime, monkeypatch, caplog, capsys
):
    loads = []

    def rejected(max_mb):
        raise runtime.sandbox.MemoryBudgetExceeded(PRIVATE)

    monkeypatch.setattr(runtime.helper, "ensure_memory_budget", rejected)
    monkeypatch.setattr(
        runtime.manager, "load_plugin", lambda name: loads.append(name) or False
    )
    assert runtime.manager.execute_plugin("unloaded", _memory_mb=1) is None
    assert len(loads) == 0, "failed memory preflight reached plugin loading"
    assert_denied(runtime, caplog, capsys)


def test_loading_rechecks_memory_before_callback(runtime, monkeypatch, caplog, capsys):
    checks = []

    def memory(max_mb):
        checks.append(max_mb)
        if len(checks) > 1:
            raise runtime.sandbox.MemoryBudgetExceeded(PRIVATE)

    def load(name):
        runtime.manager.plugins[name] = SimpleNamespace(execute=runtime.callback)
        return True

    monkeypatch.setattr(runtime.helper, "ensure_memory_budget", memory)
    monkeypatch.setattr(runtime.manager, "load_plugin", load)
    assert runtime.manager.execute_plugin("unloaded", _memory_mb=1) is None
    assert checks == [1.0, 1.0]
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize("available", [False, True])
def test_real_memory_helper_with_fake_process_boundary(
    runtime, monkeypatch, caplog, capsys, available
):
    fake_process = SimpleNamespace(
        memory_info=lambda: SimpleNamespace(rss=2 * 1024 * 1024)
    )
    monkeypatch.setattr(
        runtime.sandbox,
        "psutil",
        SimpleNamespace(Process=lambda: fake_process) if available else None,
    )
    monkeypatch.setattr(runtime.security, "sandbox", runtime.sandbox)
    assert runtime.manager.execute_plugin("synthetic", _memory_mb=1) is None
    assert_denied(runtime, caplog, capsys)


def test_real_timeout_helper_executes_only_synthetic_callback(runtime, monkeypatch):
    monkeypatch.setattr(runtime.security, "sandbox", runtime.sandbox)
    assert (
        runtime.manager.execute_plugin("synthetic", _timeout_sec=1)
        == "synthetic-result"
    )
    assert len(runtime.calls) == 1


def test_loading_disables_memory_backend_denies_before_callback(
    runtime, monkeypatch, caplog, capsys
):
    fake_process = SimpleNamespace(memory_info=lambda: SimpleNamespace(rss=1024 * 1024))
    monkeypatch.setattr(
        runtime.sandbox, "psutil", SimpleNamespace(Process=lambda: fake_process)
    )
    monkeypatch.setattr(runtime.security, "sandbox", runtime.sandbox)
    loaded = []

    def load(name):
        loaded.append(name)
        runtime.manager.plugins[name] = SimpleNamespace(execute=runtime.callback)
        monkeypatch.setattr(runtime.sandbox, "psutil", None)
        return True

    monkeypatch.setattr(runtime.manager, "load_plugin", load)
    result = runtime.manager.execute_plugin("unloaded", _memory_mb=2)
    assert loaded == ["unloaded"]
    assert_denied(runtime, caplog, capsys)
    assert result is None


@pytest.mark.parametrize("timeout", [0, 1])
def test_real_memory_helper_success_with_fake_process(runtime, monkeypatch, timeout):
    fake_process = SimpleNamespace(memory_info=lambda: SimpleNamespace(rss=1024 * 1024))
    monkeypatch.setattr(
        runtime.sandbox, "psutil", SimpleNamespace(Process=lambda: fake_process)
    )
    monkeypatch.setattr(runtime.security, "sandbox", runtime.sandbox)
    assert (
        runtime.manager.execute_plugin("synthetic", _memory_mb=2, _timeout_sec=timeout)
        == "synthetic-result"
    )
    assert len(runtime.calls) == 1


@pytest.mark.parametrize(
    "budgets",
    [
        {"_timeout_sec": "NaN", "_memory_mb": 1},
        {"_timeout_sec": 1, "_memory_mb": "NaN"},
    ],
)
def test_valid_peer_budget_does_not_hide_invalid_constraint(
    runtime, caplog, capsys, budgets
):
    assert runtime.manager.execute_plugin("synthetic", **budgets) is None
    assert runtime.helper_calls == []
    assert_denied(runtime, caplog, capsys)


@pytest.mark.parametrize(
    "exception", [KeyboardInterrupt, SystemExit, asyncio.CancelledError]
)
def test_memory_process_control_propagates_without_callback(
    runtime, monkeypatch, exception
):
    def interrupted(max_mb):
        raise exception

    monkeypatch.setattr(runtime.helper, "ensure_memory_budget", interrupted)
    with pytest.raises(exception):
        runtime.manager.execute_plugin("synthetic", _memory_mb=1)
    assert len(runtime.calls) == 0


def test_load_fallback_import_error_retains_original_cause(runtime, monkeypatch):
    errors = []

    class CapturedImportError(ImportError):
        def __init__(self, message):
            super().__init__(message)
            errors.append(self)

    original = CapturedImportError("Synthetic import unavailable")

    def unavailable(name):
        raise original

    monkeypatch.setattr(
        runtime.module, "ImportError", CapturedImportError, raising=False
    )
    monkeypatch.setattr(runtime.module.importlib, "import_module", unavailable)
    monkeypatch.setattr(
        runtime.module.importlib.util, "spec_from_file_location", lambda *args: None
    )
    assert runtime.manager.load_plugin("unloaded") is False
    assert runtime.manager.plugin_states["unloaded"] == runtime.module.PluginState.ERROR
    assert errors[-1].__cause__ is original


@pytest.mark.parametrize(
    ("responses", "expected", "expected_calls"),
    [
        ((None, ""), "No plugin could process the message.", [0, 1]),
        ((None, "second-result"), "second-result", [0, 1]),
        (("first-result", "second-result"), "first-result", [0]),
    ],
)
def test_execute_chain_keeps_synthetic_order_and_fallback(
    runtime, responses, expected, expected_calls
):
    calls = []

    def handler(index):
        def process(message):
            assert message == "synthetic-input"
            calls.append(index)
            return responses[index]

        return SimpleNamespace(process_message=process)

    runtime.manager.plugins = {"first": handler(0), "second": handler(1)}
    assert runtime.manager.execute_chain("synthetic-input") == expected
    assert calls == expected_calls
