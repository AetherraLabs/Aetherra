# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem


@pytest.mark.parametrize(
    "desired,backend,validated,expect_mode,expect_allowed,inject_coherence",
    [
        (
            "quantum",
            "simulator",
            False,
            "classical",
            0,
            False,
        ),  # denied w/out validation
        ("hybrid", "simulator", False, "classical", 0, False),
        # Even with validation, missing coherence metric in prod causes downgrade
        ("hybrid", "simulator", True, "classical", 0, False),
        # Provide coherence EMA -> allowed
        ("hybrid", "simulator", True, "hybrid", 1, True),
        # Non-simulator backend counts as validated but still needs coherence metric
        ("quantum", "qiskit", False, "classical", 0, False),
        ("quantum", "qiskit", False, "quantum", 1, True),
    ],
)
def test_qfac_policy_resolution_prod_enforced(
    monkeypatch,
    desired,
    backend,
    validated,
    expect_mode,
    expect_allowed,
    inject_coherence,
):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_MODE", desired)
    monkeypatch.setenv("AETHERRA_QFAC_BACKEND", backend)
    if validated:
        monkeypatch.setenv("AETHERRA_QFAC_VALIDATED", "1")
    else:
        monkeypatch.delenv("AETHERRA_QFAC_VALIDATED", raising=False)
    # Ensure policy enforcement
    monkeypatch.setenv("AETHERRA_QFAC_POLICY", "enforce")
    if inject_coherence:
        monkeypatch.setenv("AETHERRA_QFAC_COHERENCE_EMA", "0.9")
    else:
        monkeypatch.delenv("AETHERRA_QFAC_COHERENCE_EMA", raising=False)
    # Allow simulator in prod only when explicitly configured (not here unless validated flag true)
    monkeypatch.delenv("AETHERRA_QFAC_ALLOW_SIMULATOR_IN_PROD", raising=False)

    sys = QFACMemorySystem("_test_qfac_policy_sys")
    dec = sys.get_policy_decision()
    assert dec.get("mode") == expect_mode
    assert (1 if dec.get("allowed") else 0) == expect_allowed


def test_qfac_policy_metrics_export(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_QFAC_MODE", "quantum")
    monkeypatch.setenv("AETHERRA_QFAC_BACKEND", "qiskit")  # treated as validated
    monkeypatch.setenv("AETHERRA_QFAC_POLICY", "enforce")
    # Provide coherence EMA to satisfy gates
    monkeypatch.setenv("AETHERRA_QFAC_COHERENCE_EMA", "0.9")

    # Instantiate to produce decision
    QFACMemorySystem("_test_qfac_metrics")

    # Now build metrics lines
    # Aetherra imports
    from aetherra_hub.services.metrics_accum import build_all_metrics_lines

    lines = build_all_metrics_lines()
    # Find mode gauge line
    mode_line = next(
        (
            line
            for line in lines
            if line.startswith("aetherra_qfac_policy_mode_current")
        ),
        None,
    )
    assert mode_line is not None
    allowed_line = next(
        (line for line in lines if line.startswith("aetherra_qfac_policy_allowed")),
        None,
    )
    assert allowed_line is not None
    info_lines = [
        line for line in lines if line.startswith("aetherra_qfac_policy_info")
    ]
    assert any("reason" in line for line in info_lines)
    assert any("policy" in line for line in info_lines)
