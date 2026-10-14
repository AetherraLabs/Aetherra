"""In-process scrape contracts with fail-closed construction/import sentinels."""

# Standard library imports
import builtins
import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

# Third party imports
import pytest
from flask import Flask


class ForbiddenMetricsWorkError(BaseException):
    """Escape production best-effort catches when a scrape attempts unsafe work."""


@pytest.fixture
def offline(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_SKIP_DOTENV", "1")
    monkeypatch.setenv("AETHERRA_LYRIXA_FORCE_OFFLINE", "1")
    monkeypatch.setenv("AETHERRA_QFAC_VALIDATOR_FAKE", "0")
    monkeypatch.setenv("AETHERRA_QFAC_SHADOW_FAKE", "0")
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_THRESHOLD", "0")
    monkeypatch.setenv("AETHERRA_QFAC_RETRIEVAL_PARITY", "1")
    registry = importlib.import_module("aetherra_hub.services.registry_client")
    metrics = importlib.import_module("aetherra_hub.services.metrics_accum")
    services = {}
    lookups = []
    blocked = []

    class Registry:
        def get_service_info(self, name):
            lookups.append(name)
            instance = services.get(name)
            return SimpleNamespace(instance=instance) if instance is not None else None

    async def get_registry():
        return Registry()

    def forbidden_fallback():
        blocked.append("quantum-fallback")
        raise ForbiddenMetricsWorkError("Scrape attempted fallback construction")

    monkeypatch.setattr(registry, "_get_registry_async", get_registry)
    monkeypatch.setattr(registry, "_get_fallback_quantum_engine", forbidden_fallback)
    for name in (
        "get_kernel_status",
        "get_hmr_config_metrics",
        "get_hmr_audit_counters",
        "get_klm_metrics",
        "get_keb_metrics",
        "get_orchestrator_status",
        "get_storm_metrics",
        "get_engine_session_metrics",
        "get_engine_status",
        "get_registry_status",
    ):
        monkeypatch.setattr(registry, name, lambda: {})
    monkeypatch.setattr(metrics, "trainer_service", None)
    monkeypatch.setattr(metrics, "chat_metrics", metrics.ChatMetrics())
    monkeypatch.setattr(metrics, "kernel_hist", metrics.KernelHist())
    monkeypatch.setattr(metrics, "orchestrator_hist", metrics.OrchestratorHist())
    # Route key-status probes to empty scratch; never inspect the user's key files.
    monkeypatch.setattr(
        metrics.os.path, "expanduser", lambda path: str(tmp_path / "absent-key-file")
    )
    engine_module = ModuleType("Aetherra.aetherra_core.engine.aetherra_engine")
    engine_module.aetherra_engine = SimpleNamespace(
        get_engine_metrics_snapshot=lambda: {}
    )
    monkeypatch.setitem(sys.modules, engine_module.__name__, engine_module)
    plugin_module = ModuleType("aetherra_hub.services.plugin_metrics")
    plugin_module.as_prometheus_lines = lambda: []
    monkeypatch.setitem(sys.modules, plugin_module.__name__, plugin_module)
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("Aetherra.aetherra_core.memory") or name.split(".")[0] in (
            "qiskit",
            "qiskit_aer",
            "cirq",
            "pennylane",
            "openai",
            "anthropic",
        ):
            blocked.append("prohibited-import")
            raise ForbiddenMetricsWorkError("Scrape attempted QFAC/SDK import")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    return SimpleNamespace(
        registry=registry,
        metrics=metrics,
        services=services,
        lookups=lookups,
        blocked=blocked,
    )


def register_memory(offline):
    status = {"coherence": 0.625, "branches": 3, "fragments": 11}
    audit = {"nodes": ["a", "b"], "edges": [("a", "b")]}

    async def quantum_status():
        return dict(status)

    memory = SimpleNamespace(
        get_quantum_status=quantum_status,
        engine=SimpleNamespace(audit_branch_dag=lambda: audit),
    )
    offline.services["aetherra_engine"] = SimpleNamespace(memory_system=memory)
    return status, audit


def register_qfac(offline):
    calls = []

    def snapshot(name, value):
        def get():
            calls.append(name)
            return dict(value)

        return get

    qfac = SimpleNamespace(
        get_policy_decision=snapshot(
            "policy",
            {
                "mode": "hybrid",
                "allowed": True,
                "reason": "registered",
                "policy": "synthetic",
            },
        ),
        get_metrics_snapshot=snapshot(
            "metrics",
            {
                "nodes_total": 7,
                "nodes_compressed": 4,
                "degraded_nodes_total": 2,
                "overall_compression_ratio": 2.5,
                "compression_ratio_avg": 3.0,
            },
        ),
        get_retrieval_parity_metrics_snapshot=snapshot(
            "parity",
            {
                "total": 8,
                "top1_match": 4,
                "any_rank_mismatch": 3,
                "threshold_dropped": 2,
                "parity_by_k": {1: 4, 3: 6, 5: 8, 10: 8},
            },
        ),
    )
    offline.services["qfac_memory_system"] = qfac
    return qfac, calls


@pytest.mark.parametrize("getter", ["get_memory_quantum_status", "get_memory_audit"])
@pytest.mark.parametrize(
    "state", ["absent", "no-memory", "method-error", "registry-error"]
)
def test_read_only_getter_returns_minimal_without_fallback(
    offline, monkeypatch, getter, state
):
    def unavailable():
        raise RuntimeError("Synthetic snapshot unavailable")

    async def status_unavailable():
        unavailable()

    if state == "no-memory":
        offline.services["aetherra_engine"] = SimpleNamespace()
    elif state == "method-error":
        offline.services["aetherra_engine"] = SimpleNamespace(
            memory_system=SimpleNamespace(
                get_quantum_status=status_unavailable, audit_branch_dag=unavailable
            )
        )
    elif state == "registry-error":

        async def registry_unavailable():
            unavailable()

        monkeypatch.setattr(
            offline.registry, "_get_registry_async", registry_unavailable
        )
    assert getattr(offline.registry, getter)(allow_fallback=False) == {"enabled": False}
    assert offline.blocked == []


@pytest.mark.parametrize("getter", ["get_memory_quantum_status", "get_memory_audit"])
def test_read_only_getter_uses_registered_memory(offline, getter):
    status, audit = register_memory(offline)
    expected = (
        {"enabled": True, **status}
        if getter == "get_memory_quantum_status"
        else {"enabled": True, "audit": audit}
    )
    assert getattr(offline.registry, getter)(allow_fallback=False) == expected
    assert offline.blocked == []


@pytest.mark.parametrize("getter", ["get_memory_quantum_status", "get_memory_audit"])
@pytest.mark.parametrize("explicit", [False, True])
def test_default_getter_keeps_synthetic_fallback_contract(
    offline, monkeypatch, getter, explicit
):
    calls = []
    fallback = SimpleNamespace(
        get_status=lambda: {"coherence": 0.5}, audit_branch_dag=lambda: {"nodes": []}
    )
    monkeypatch.setattr(
        offline.registry,
        "_get_fallback_quantum_engine",
        lambda: calls.append(True) or fallback,
    )
    kwargs = {"allow_fallback": True} if explicit else {}
    result = getattr(offline.registry, getter)(**kwargs)
    assert result["enabled"] is False
    assert result["ephemeral"] is True
    assert calls == [True]
    assert offline.blocked == []


REGISTERED_LINES = [
    "aetherra_memory_coherence_score 0.625",
    "aetherra_memory_branches_total 3.0",
    "aetherra_memory_fragments_total 11.0",
    "aetherra_memory_branch_nodes_total 2.0",
    "aetherra_memory_branch_edges_total 1.0",
    "aetherra_qfac_policy_mode_current 1",
    "aetherra_qfac_policy_allowed 1",
    'aetherra_qfac_policy_info{key="reason",value="registered"} 1',
    'aetherra_qfac_policy_info{key="policy",value="synthetic"} 1',
    "aetherra_qfac_nodes_total 7.0",
    "aetherra_qfac_nodes_compressed 4.0",
    "aetherra_qfac_degraded_nodes_total 2.0",
    "aetherra_qfac_compression_ratio 2.5",
    "aetherra_qfac_compression_ratio_avg 3.0",
    "aetherra_qfac_retrieval_parity_total 8.0",
    "aetherra_qfac_retrieval_parity_top1_match_total 4.0",
    "aetherra_qfac_retrieval_parity_any_rank_mismatch_total 3.0",
    "aetherra_qfac_retrieval_threshold_dropped_results_total 2.0",
    "aetherra_qfac_retrieval_parity_ratio 0.5",
    "aetherra_qfac_retrieval_parity_top3_match_total 6.0",
    "aetherra_qfac_retrieval_parity_top3_ratio 0.75",
]


def test_registered_builder_never_imports_qfac_or_sdk(offline):
    register_memory(offline)
    register_qfac(offline)
    lines = offline.metrics.build_all_metrics_lines()
    assert "aetherra_qfac_nodes_total 7.0" in lines
    assert offline.blocked == []


@pytest.mark.parametrize("blueprint", [False, True])
def test_registered_scrape_has_exact_metrics_without_imports(
    offline, monkeypatch, blueprint
):
    register_memory(offline)
    _, calls = register_qfac(offline)
    observed = []
    for name in ("get_memory_quantum_status", "get_memory_audit"):
        original = getattr(offline.registry, name)

        def observed_getter(*, allow_fallback=True, original=original, name=name):
            observed.append((name, allow_fallback))
            return original(allow_fallback=allow_fallback)

        monkeypatch.setattr(offline.registry, name, observed_getter)
    if blueprint:
        # Load only this real blueprint, bypassing the package's eager imports.
        source = (
            Path(__file__).parents[2] / "aetherra_hub" / "blueprints" / "metrics.py"
        )
        spec = importlib.util.spec_from_file_location(
            "aetherra_hub.blueprints.metrics", source
        )
        assert spec is not None
        assert spec.loader is not None
        metrics_blueprint = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, metrics_blueprint)
        spec.loader.exec_module(metrics_blueprint)
        app = Flask(__name__)
        app.register_blueprint(metrics_blueprint.bp)
        response = app.test_client().get("/metrics")
        assert response.status_code == 200
        assert response.mimetype == "text/plain"
        lines = response.get_data(as_text=True).splitlines()
    else:
        lines = offline.metrics.build_all_metrics_lines()
    for line in REGISTERED_LINES:
        # Preserve existing top-1 duplication from the legacy by-k renderer.
        expected = (
            2 if line == "aetherra_qfac_retrieval_parity_top1_match_total 4.0" else 1
        )
        assert lines.count(line) == expected
    assert calls == ["policy", "metrics", "parity"]
    assert observed == [
        ("get_memory_quantum_status", False),
        ("get_memory_audit", False),
    ]
    assert offline.lookups.count("qfac_memory_system") == 1
    assert offline.blocked == []


@pytest.mark.parametrize(
    "service",
    [None, SimpleNamespace(), SimpleNamespace(get_policy_decision=lambda: {})],
)
def test_unavailable_qfac_keeps_existing_schema_defaults(offline, service):
    offline.services["qfac_memory_system"] = service
    lines = offline.metrics.build_all_metrics_lines()
    for line in (
        "aetherra_qfac_policy_mode_current 0",
        "aetherra_qfac_policy_allowed 0",
        'aetherra_qfac_policy_info{key="reason",value="unavailable"} 1',
        "aetherra_qfac_nodes_total 0",
        "aetherra_qfac_nodes_compressed 0",
        "aetherra_qfac_degraded_nodes_total 0",
        "aetherra_qfac_compression_ratio 1",
        "aetherra_qfac_compression_ratio_avg 1",
        "aetherra_qfac_retrieval_parity_total 0",
        "aetherra_qfac_retrieval_parity_ratio 0",
    ):
        assert lines.count(line) == 1
    assert offline.blocked == []


def test_absent_memory_keeps_core_metrics_schema_without_construction(offline):
    lines = offline.metrics.build_all_metrics_lines()
    for line in (
        "aetherra_memory_coherence_score 0.0",
        "aetherra_memory_branches_total 0.0",
        "aetherra_memory_fragments_total 0.0",
    ):
        assert lines.count(line) == 1
    assert offline.blocked == []


@pytest.mark.parametrize("operation", ["policy", "metrics", "parity"])
def test_qfac_snapshot_errors_preserve_partial_fallbacks(
    offline, monkeypatch, operation, caplog
):
    caplog.set_level("DEBUG", logger=offline.metrics.__name__)
    qfac, calls = register_qfac(offline)
    methods = {
        "policy": "get_policy_decision",
        "metrics": "get_metrics_snapshot",
        "parity": "get_retrieval_parity_metrics_snapshot",
    }

    def unavailable():
        calls.append(operation)
        message = (
            "private-policy-value C:/private/policy-state"
            if operation == "policy"
            else "Synthetic snapshot unavailable"
        )
        raise RuntimeError(message)

    monkeypatch.setattr(qfac, methods[operation], unavailable)
    lines = offline.metrics.build_all_metrics_lines()
    assert (
        "aetherra_qfac_policy_mode_current 0" in lines
        if operation == "policy"
        else "aetherra_qfac_policy_mode_current 1" in lines
    )
    assert (
        "aetherra_qfac_nodes_total 0" in lines
        if operation == "metrics"
        else "aetherra_qfac_nodes_total 7.0" in lines
    )
    if operation == "policy":
        assert 'aetherra_qfac_policy_info{key="reason",value="unavailable"} 1' in lines
        assert "aetherra_qfac_retrieval_parity_total 8.0" in lines
        assert "aetherra_qfac_retrieval_parity_ratio 0.5" in lines
        assert calls == ["policy", "metrics", "parity"]
        assert offline.lookups.count("qfac_memory_system") == 1
        assert_policy_failure_diagnostic(offline, caplog)
    else:
        assert "aetherra_qfac_retrieval_parity_total 0" in lines
    assert offline.blocked == []


def assert_policy_failure_diagnostic(offline, caplog):
    records = [
        record for record in caplog.records if record.name == offline.metrics.__name__
    ]
    assert len(records) == 1
    assert (
        records[0].getMessage()
        == "metrics: registered QFAC policy lookup failed (RuntimeError)"
    )
    assert records[0].exc_info is None
    assert records[0].stack_info is None
    clean = (
        "private-policy-value" not in caplog.text and "C:/private" not in caplog.text
    )
    assert clean, "policy diagnostic included private data"


def test_policy_attribute_failure_keeps_registered_independent_snapshots(
    offline, caplog
):
    caplog.set_level("DEBUG", logger=offline.metrics.__name__)
    qfac, calls = register_qfac(offline)

    class PolicyAttributeFailure:
        get_metrics_snapshot = staticmethod(qfac.get_metrics_snapshot)
        get_retrieval_parity_metrics_snapshot = staticmethod(
            qfac.get_retrieval_parity_metrics_snapshot
        )

        @property
        def get_policy_decision(self):
            calls.append("policy-attribute")
            raise RuntimeError("private-policy-value C:/private/policy-state")

    offline.services["qfac_memory_system"] = PolicyAttributeFailure()
    lines = offline.metrics.build_all_metrics_lines()
    assert "aetherra_qfac_policy_mode_current 0" in lines
    assert "aetherra_qfac_nodes_total 7.0" in lines
    assert "aetherra_qfac_retrieval_parity_total 8.0" in lines
    assert calls == ["policy-attribute", "metrics", "parity"]
    assert offline.lookups.count("qfac_memory_system") == 1
    assert offline.blocked == []
    assert_policy_failure_diagnostic(offline, caplog)


def test_registry_lookup_error_keeps_scrape_fallback(offline, monkeypatch):
    async def unavailable():
        raise RuntimeError("Synthetic registry unavailable")

    monkeypatch.setattr(offline.registry, "_get_registry_async", unavailable)
    lines = offline.metrics.build_all_metrics_lines()
    assert "aetherra_qfac_policy_mode_current 0" in lines
    assert "aetherra_qfac_nodes_total 0" in lines
    assert offline.blocked == []


def test_existing_qfac_schema_contract_under_safe_boundaries(offline):
    contract = importlib.import_module("tests.capabilities.test_qfac_metrics_schema")
    contract.test_qfac_metrics_schema_contains_required_series()
    assert offline.blocked == []
