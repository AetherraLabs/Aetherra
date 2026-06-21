"""Subsystem view profiles for the Cognitive Observatory."""

from __future__ import annotations

from typing import Any


def get_subsystem_profile(name: str) -> dict[str, Any]:
    """Return a safe view profile for one Runtime UI subsystem."""

    normalized_name = name.strip().lower().replace("-", "_")
    profile = SUBSYSTEM_PROFILES.get(normalized_name, _default_profile(normalized_name))
    return dict(profile)


def subsystem_guidance(name: str) -> str:
    """Return Lyrixa-style guidance for a subsystem view."""

    profile = get_subsystem_profile(name)
    title = str(profile.get("title") or name)
    purpose = str(profile.get("purpose") or "This view is read-only.")
    return f"You are viewing {title}. {purpose}"


def supported_subsystems() -> list[str]:
    """Return the sorted Runtime UI subsystem ids with explicit profiles."""

    return sorted(SUBSYSTEM_PROFILES)


def _default_profile(name: str) -> dict[str, Any]:
    return {
        "title": name.replace("_", " ").title(),
        "purpose": "Read-only subsystem observability.",
        "authority_owner": "System",
        "primary_view": "status",
        "panels": ["status", "health", "activity", "events"],
        "related_endpoints": [],
        "safety_rules": [
            "read_only",
            "no_direct_mutation",
            "privileged_actions_require_guardian_and_security",
        ],
    }


SUBSYSTEM_PROFILES: dict[str, dict[str, Any]] = {
    "security": {
        "title": "Security",
        "purpose": "Shows enforcement posture, sandbox boundaries, capability checks, and audit integrity.",
        "authority_owner": "Security",
        "primary_view": "enforcement",
        "panels": ["capabilities", "sandbox", "network_policy", "audit"],
        "related_endpoints": ["/api/security/status"],
        "safety_rules": ["observe_only", "redact_sensitive_values", "no_policy_mutation"],
    },
    "guardian": {
        "title": "Guardian",
        "purpose": "Shows decision state for allow, deny, approval, containment, and preauthorization flows.",
        "authority_owner": "Guardian",
        "primary_view": "decision_flow",
        "panels": ["mode", "approvals", "containment", "preauthorization", "audit_integrity"],
        "related_endpoints": ["/api/guardian/status", "/api/guardian/mode"],
        "safety_rules": ["observe_only", "approval_changes_require_control_auth", "redact_audit_details"],
    },
    "homeostasis": {
        "title": "Homeostasis",
        "purpose": "Shows observation, pressure, diagnosis, recommendation, and verification state.",
        "authority_owner": "Homeostasis",
        "primary_view": "health_regulation",
        "panels": ["health", "pressure", "diagnosis", "recommendations", "verification"],
        "related_endpoints": ["/api/homeostasis/status", "/homeostasis"],
        "safety_rules": ["observe_verify_only", "actions_require_guardian_review"],
    },
    "memory": {
        "title": "Memory",
        "purpose": "Shows safe memory health, continuity, pressure, and narrative summary metadata.",
        "authority_owner": "Memory",
        "primary_view": "continuity_landscape",
        "panels": ["health", "pressure", "continuity", "narrative_threads"],
        "related_endpoints": ["/api/memory/status"],
        "safety_rules": ["summary_only", "no_memory_write", "redact_private_content"],
    },
    "consciousness": {
        "title": "Consciousness",
        "purpose": "Shows bounded perception, attention, appraisal, deliberation, action, and reflection state.",
        "authority_owner": "Consciousness",
        "primary_view": "cognitive_loop",
        "panels": ["perception", "attention", "appraisal", "deliberation", "reflection"],
        "related_endpoints": ["/api/consciousness/status"],
        "safety_rules": ["trace_summary_only", "no_reasoning_fabrication"],
    },
    "agents": {
        "title": "Agents",
        "purpose": "Shows agent presence, task pressure, queue state, and governed execution activity.",
        "authority_owner": "Agent System",
        "primary_view": "agent_topology",
        "panels": ["agents", "tasks", "queues", "delegation", "guardian_checks"],
        "related_endpoints": ["/api/agents"],
        "safety_rules": ["observe_only", "agent_lifecycle_changes_require_guardian"],
    },
    "self_improvement": {
        "title": "Self-Improvement",
        "purpose": "Shows observations, hypotheses, simulations, and proposals without applying changes.",
        "authority_owner": "Self-Improvement",
        "primary_view": "proposal_stream",
        "panels": ["observations", "hypotheses", "simulations", "proposals", "risk"],
        "related_endpoints": ["/api/selfimprove/status"],
        "safety_rules": ["propose_only", "no_direct_execution", "guardian_review_required"],
    },
    "self_incorporation": {
        "title": "Self-Incorporation",
        "purpose": "Shows discovery, classification, dry-run plans, staged application, rollback, and verification.",
        "authority_owner": "Self-Incorporation",
        "primary_view": "incorporation_workshop",
        "panels": ["discovery", "classification", "plans", "approval", "rollback", "verification"],
        "related_endpoints": ["/api/selfinc/status"],
        "safety_rules": ["approved_execution_only", "rollback_required", "homeostasis_verification_required"],
    },
    "maintenance": {
        "title": "Maintenance",
        "purpose": "Shows the umbrella observe, diagnose, propose, review, apply, verify, and learn loop.",
        "authority_owner": "Maintenance",
        "primary_view": "maintenance_cycle",
        "panels": ["observation", "diagnosis", "proposal", "governance", "execution", "verification", "learning"],
        "related_endpoints": ["/api/maintenance/status"],
        "safety_rules": ["coordinate_only", "no_direct_bypass", "respect_system_authority_ownership"],
    },
    "aether_script": {
        "title": "Aether Script",
        "purpose": "Shows validation, signature state, static risk, workflow state, and execution-gate results.",
        "authority_owner": "Aether Script",
        "primary_view": "script_runtime",
        "panels": ["validation", "signatures", "risk", "workflow", "execution_gate"],
        "related_endpoints": ["/api/run", "/api/scripts"],
        "safety_rules": ["no_unsigned_execution", "guardian_preflight_required", "security_enforced"],
    },
    "kernel": {
        "title": "Kernel",
        "purpose": "Shows runtime core readiness, service state, event bus posture, and HMR readiness.",
        "authority_owner": "Kernel",
        "primary_view": "runtime_core",
        "panels": ["services", "events", "queues", "hmr", "readiness"],
        "related_endpoints": ["/api/kernel/status", "/api/kernel/metrics"],
        "safety_rules": ["observe_only", "kernel_mutation_requires_governed_path"],
    },
    "integration_validation": {
        "title": "Integration Validation",
        "purpose": "Shows readiness evidence across Security, Guardian, Maintenance, Aether Script, and runtime paths.",
        "authority_owner": "Integration Validation",
        "primary_view": "readiness_matrix",
        "panels": ["coverage", "checks", "evidence", "gaps"],
        "related_endpoints": [],
        "safety_rules": ["do_not_run_heavy_checks_per_request", "report_readiness_only"],
    },
}
