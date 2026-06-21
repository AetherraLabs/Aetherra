import os

from Aetherra.integration_validation import run_integration_validation


def test_cross_system_integration_validation_passes_in_isolated_workspace(tmp_path):
    report = run_integration_validation(workspace_root=tmp_path)
    data = report.to_dict()

    assert report.passed is True
    assert data["check_count"] == 4
    assert {check.name for check in report.checks} == {
        "guardian_security_chain",
        "homeostasis_observation_diagnosis",
        "maintenance_coordination_chain",
        "aether_script_runtime_gate",
    }
    assert all(check.passed for check in report.checks)


def test_cross_system_integration_validation_restores_environment(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "preexisting")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", "preexisting-root")

    report = run_integration_validation(workspace_root=tmp_path)

    assert report.passed is True
    assert os.environ["AETHERRA_REQUIRE_CAPABILITIES"] == "preexisting"
    assert os.environ["AETHERRA_WORKSPACE_ROOT"] == "preexisting-root"
