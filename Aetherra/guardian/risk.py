"""Risk scoring for Guardian intent declarations."""

from __future__ import annotations

import os

from .models import IntentDeclaration, RiskAssessment, RiskLevel


def _is_production_profile() -> bool:
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    return profile in {"prod", "production"}


def assess_risk(intent: IntentDeclaration) -> RiskAssessment:
    """Score an intent using simple v0.1 deterministic risk factors."""

    score = 0
    factors: list[str] = []
    action = intent.action.lower()
    target = intent.target.lower()
    capabilities = {cap.lower() for cap in intent.capabilities}

    if action in {"read", "inspect", "list", "status", "plugin.execute"}:
        score += 10
        factors.append("bounded_action")
    if any(cap.endswith(":write") or cap in {"fs:write", "memory:write"} for cap in capabilities):
        score += 30
        factors.append("write_action")
    if action in {"delete", "remove"} or "fs:delete" in capabilities:
        score += 60
        factors.append("delete_action")
    if any(cap.startswith("network:") for cap in capabilities):
        score += 25
        factors.append("network_access")
    if "plugin:execute" in capabilities or action == "plugin.execute":
        score += 25
        factors.append("plugin_execution")
    if "plugin:load" in capabilities or action == "plugin.load":
        score += 35
        factors.append("plugin_loading")
    if "plugin:register" in capabilities or action == "plugin.register":
        score += 30
        factors.append("plugin_registration")
    if "plugin:install" in capabilities or action in {"plugin.install", "hub.plugin_install"}:
        score += 35
        factors.append("plugin_installation")
    if "plugin:create" in capabilities or action == "plugin.create_template":
        score += 25
        factors.append("plugin_creation")
    if "plugin:uninstall" in capabilities or action in {"plugin.uninstall", "hub.plugin_uninstall"}:
        score += 35
        factors.append("plugin_uninstallation")
    if "script:run" in capabilities or action == "script.execute":
        score += 25
        factors.append("script_execution")
    if "executor:execute" in capabilities or action == "executor.execute":
        score += 25
        factors.append("executor_command")
    if action == "optimization.apply":
        score += 30
        factors.append("optimization_application")
    if "agent:execute" in capabilities or action == "agent.execute_task":
        score += 25
        factors.append("agent_task_execution")
    if any(cap.startswith("homeostasis:") for cap in capabilities) or action.startswith(
        "homeostasis."
    ):
        score += 30
        factors.append("homeostasis_actuation")
    if action.startswith("maintenance.") or any(
        cap.startswith("maintenance:") for cap in capabilities
    ):
        score += 30
        factors.append("maintenance_operation")
    if action.startswith("kernel.") or any(cap.startswith("kernel:") for cap in capabilities):
        score += 20
        factors.append("kernel_control")
    if action.startswith("service_registry.") or any(
        cap.startswith("registry:") for cap in capabilities
    ):
        score += 20
        factors.append("service_registry_mutation")
    if action.startswith("event_bus.") or any(cap.startswith("event:") for cap in capabilities):
        score += 20
        factors.append("event_bus_mutation")
    if action.startswith("module_manager.") or any(
        cap.startswith("module:") for cap in capabilities
    ):
        score += 25
        factors.append("module_lifecycle")
    if action.startswith("hmr.") or "system:reload" in capabilities:
        score += 35
        factors.append("hot_reload")
    if "system:execute" in capabilities:
        score += 35
        factors.append("system_command")
    if "python:execute" in capabilities:
        score += 25
        factors.append("python_execution")
    if any(cap.startswith("secret") or "secret" in cap for cap in capabilities):
        score += 50
        factors.append("secret_access")
    if "memory:modify_identity" in capabilities or "identity" in target:
        score += 80
        factors.append("identity_modification")
    if "security:modify" in capabilities or "/security/" in target or "\\security\\" in target:
        score += 90
        factors.append("security_modification")
    if "self:modify" in capabilities or action.startswith("self."):
        score += 60
        factors.append("self_modification")
    if any(marker in target for marker in ("aetherra/core", "aetherra\\core", "kernel")):
        score += 40
        factors.append("core_modification")
    if _is_production_profile():
        score += 10
        factors.append("production_environment")
    mutating_action = any(
        factor in factors
        for factor in {
            "write_action",
            "delete_action",
            "identity_modification",
            "security_modification",
            "self_modification",
        }
    )
    if not intent.reversible and mutating_action:
        score += 25
        factors.append("missing_reversibility")

    if score >= 100:
        level = RiskLevel.CRITICAL
    elif score >= 70:
        level = RiskLevel.HIGH
    elif score >= 30:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return RiskAssessment(level=level, score=score, factors=tuple(factors))
