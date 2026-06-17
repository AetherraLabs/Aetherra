import json

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.guardian.policy import evaluate_guardian_policy, load_guardian_policy


def _intent(**overrides):
    values = {
        "requester": "plugin:demo",
        "subsystem": "plugin_manager",
        "action": "plugin.execute",
        "target": "demo",
        "purpose": "Execute plugin",
        "capabilities": ("execute",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_guardian_policy_explicit_deny_wins(monkeypatch, tmp_path):
    policy_path = tmp_path / "guardian_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "allow",
                "deny": [{"requester": "plugin:*", "action": "plugin.execute"}],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AETHERRA_GUARDIAN_POLICY", str(policy_path))

    result = evaluate_guardian_policy(_intent())

    assert result.allowed is False
    assert result.reason == "guardian_policy_denied"


def test_guardian_policy_allow_list_requires_match(monkeypatch, tmp_path):
    policy_path = tmp_path / "guardian_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": [{"requester": "plugin:trusted", "action": "plugin.execute"}],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AETHERRA_GUARDIAN_POLICY", str(policy_path))

    trusted = evaluate_guardian_policy(_intent(requester="plugin:trusted"))
    untrusted = evaluate_guardian_policy(_intent(requester="plugin:demo"))

    assert trusted.allowed is True
    assert untrusted.allowed is False
    assert untrusted.reason == "guardian_policy_no_allow_match"


def test_guardian_require_policy_denies_without_policy(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_REQUIRE_POLICY", "1")

    decision = evaluate_intent(
        _intent(),
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.DENY
    assert decision.reason == "guardian_policy_default_deny"


def test_guardian_policy_loads_metadata(tmp_path):
    policy_path = tmp_path / "guardian_policy.json"
    policy_path.write_text(
        json.dumps({"version": 1, "metadata": {"owner": "security"}}),
        encoding="utf-8",
    )

    policy = load_guardian_policy(policy_path)

    assert policy.metadata == {"owner": "security"}
