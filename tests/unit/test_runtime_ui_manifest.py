from Aetherra.runtime_ui import (
    build_runtime_ui_manifest,
    get_subsystem_profile,
    subsystem_guidance,
    supported_subsystems,
)


def test_runtime_ui_manifest_declares_safe_foundation_contract():
    manifest = build_runtime_ui_manifest()

    assert manifest["contract_version"] == "1.0"
    assert manifest["read_only"] is True
    assert manifest["controls_enabled"] is False
    assert manifest["legacy_ui_enabled"] is False
    assert manifest["authority"]["approve"] == "guardian"
    assert manifest["authority"]["execute"] == "self_incorporation"
    assert manifest["endpoints"]["status"] == "/api/runtime-ui/status"
    assert "guardian" in manifest["supported_subsystems"]


def test_runtime_ui_profiles_are_normalized_and_safe_by_default():
    profile = get_subsystem_profile("self-improvement")
    fallback = get_subsystem_profile("future-system")

    assert profile["authority_owner"] == "Self-Improvement"
    assert profile["primary_view"] == "proposal_stream"
    assert "propose_only" in profile["safety_rules"]
    assert fallback["title"] == "Future System"
    assert fallback["safety_rules"][-1] == "privileged_actions_require_guardian_and_security"


def test_runtime_ui_profile_guidance_and_supported_subsystems():
    guidance = subsystem_guidance("guardian")
    subsystems = supported_subsystems()

    assert guidance.startswith("You are viewing Guardian.")
    assert subsystems == sorted(subsystems)
    assert {"guardian", "security", "homeostasis"} <= set(subsystems)
