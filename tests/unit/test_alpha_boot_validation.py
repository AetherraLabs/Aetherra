# Standard library imports
import os

# Third party imports
import pytest

# Aetherra imports
from Aetherra import alpha_boot_validation
from Aetherra.alpha_boot_validation import run_alpha_boot_validation


def test_alpha_boot_validation_passes_in_isolated_workspace(tmp_path):
    report = run_alpha_boot_validation(workspace_root=tmp_path)
    data = report.to_dict()

    assert report.passed is True
    assert data["check_count"] == 4
    assert {check.name for check in report.checks} == {
        "core_imports",
        "kernel_readiness_contract",
        "hub_readiness_contract",
        "self_incorporation_health_contract",
    }
    assert all(check.passed for check in report.checks)


def test_alpha_boot_validation_restores_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", "preexisting-root")
    monkeypatch.setenv("AETHERRA_PROFILE", "preexisting-profile")

    report = run_alpha_boot_validation(workspace_root=tmp_path)

    assert report.passed is True
    assert os.environ["AETHERRA_WORKSPACE_ROOT"] == "preexisting-root"
    assert os.environ["AETHERRA_PROFILE"] == "preexisting-profile"


def test_kernel_contract_reports_synthetic_evidence_and_rejects_inferred_sources():
    check = alpha_boot_validation._check_kernel_readiness_contract()
    assert check.passed is True
    assert check.details["evidence_type"] == "synthetic_contract_fixture"
    assert check.details["live_runtime_verified"] is False
    for result in check.details["inferred_sources"].values():
        assert result["safe_to_schedule"] is False
        assert "kernel_status_inferred" in result["reasons"]


@pytest.mark.parametrize("untrusted_source", ["registry_daemon", "file_fallback"])
def test_kernel_contract_detects_assessor_accepting_inferred_state(
    monkeypatch, untrusted_source
):
    # Aetherra imports
    from Aetherra.aetherra_core import os_kernel

    assessor = os_kernel.assess_kernel_readiness

    def incorrectly_accept_inferred(status):
        if status.get("_source") == untrusted_source:
            status = {**status, "_source": "live_kernel"}
        return assessor(status)

    monkeypatch.setattr(
        os_kernel, "assess_kernel_readiness", incorrectly_accept_inferred
    )
    check = alpha_boot_validation._check_kernel_readiness_contract()
    assert check.passed is False
    assert (
        check.details["inferred_sources"][untrusted_source]["safe_to_schedule"] is True
    )
