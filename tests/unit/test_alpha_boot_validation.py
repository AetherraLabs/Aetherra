import os

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
