"""Fresh profile working directories must retain shipped observation thresholds."""

# Standard library imports
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis import audit_trace_layer, homeostasis_integration
from Aetherra.homeostasis.stability_metrics import StabilityMetrics
from Aetherra.homeostasis.system_supervisor import SystemSupervisor


@pytest.mark.parametrize("component", [StabilityMetrics, SystemSupervisor])
def test_default_thresholds_resolve_from_empty_profile(
    monkeypatch, tmp_path, component
):
    monkeypatch.chdir(tmp_path)
    instance = component()
    assert Path(instance.config_path).is_file()
    assert Path(instance.config_path).is_absolute()
    assert (
        instance.setpoints
        if isinstance(instance, StabilityMetrics)
        else instance.config
    )["core_metrics"]["memory_rtt"]["target"] > 0
    assert not (tmp_path / "Aetherra").exists()


@pytest.mark.parametrize("component", [StabilityMetrics, SystemSupervisor])
def test_explicit_threshold_file_is_preserved(monkeypatch, tmp_path, component):
    monkeypatch.chdir(tmp_path)
    custom = tmp_path / "custom.yaml"
    custom.write_text(
        "core_metrics:\n  memory_rtt:\n    target: 17\n", encoding="utf-8"
    )
    instance = component(str(custom))
    assert instance.config_path == str(custom)
    assert (
        instance.setpoints
        if isinstance(instance, StabilityMetrics)
        else instance.config
    )["core_metrics"]["memory_rtt"]["target"] == 17


def test_orchestrator_default_and_explicit_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setattr(audit_trace_layer, "_audit_layer_instance", None)
    default = homeostasis_integration.HomeostasisOrchestrator()
    assert Path(default.config_dir).is_absolute()
    assert (Path(default.config_dir) / "setpoints.yaml").is_file()
    assert (Path(default.config_dir) / "homeostasis_policy.yaml").is_file()
    custom = homeostasis_integration.HomeostasisOrchestrator(str(tmp_path / "custom"))
    assert custom.config_dir == str(tmp_path / "custom")
