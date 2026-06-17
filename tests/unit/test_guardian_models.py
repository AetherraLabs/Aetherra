import pytest

from Aetherra.guardian import IntentDeclaration


def test_intent_declaration_requires_core_fields():
    with pytest.raises(ValueError, match="missing required fields"):
        IntentDeclaration(
            requester="",
            subsystem="plugin_manager",
            action="plugin.execute",
            target="demo",
            purpose="Execute plugin",
        )


def test_intent_declaration_serializes_for_audit():
    intent = IntentDeclaration(
        requester="plugin:demo",
        subsystem="plugin_manager",
        action="plugin.execute",
        target="demo",
        purpose="Execute plugin",
        capabilities=("execute",),
        evidence=("plugin:demo",),
    )

    audit = intent.to_audit_dict()

    assert audit["requester"] == "plugin:demo"
    assert audit["capabilities"] == ("execute",)
