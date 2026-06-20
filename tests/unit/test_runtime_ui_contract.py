from Aetherra.runtime_ui import (
    ObservatoryMode,
    build_observatory_scene,
    build_observatory_state,
    validate_runtime_ui_payload,
)


def _valid_payload():
    state = build_observatory_state(
        mode=ObservatoryMode.FIRST_LAUNCH,
        events=[
            {
                "source": "guardian",
                "event_type": "decision",
                "summary": "Allowed read-only status request",
                "severity": "notice",
            }
        ],
    )
    scene = build_observatory_scene(state)
    return {
        "ok": True,
        "read_only": True,
        "manifest": {
            "read_only": True,
            "controls_enabled": False,
            "supported_activity_channels": [
                "containment",
                "evolution",
                "governance",
                "regulation",
                "system",
            ],
            "endpoints": {
                "activity": "/api/runtime-ui/activity",
                "bootstrap": "/api/runtime-ui/bootstrap",
                "manifest": "/api/runtime-ui/manifest",
                "observatory": "/api/runtime-ui/observatory",
                "openapi": "/api/openapi.json",
                "scene": "/api/runtime-ui/scene",
                "status": "/api/runtime-ui/status",
                "subsystem": "/api/runtime-ui/subsystems/{subsystem_name}",
            },
            "authority": {
                "observe": "runtime_ui",
                "approve": "guardian",
                "enforce": "security",
                "execute": "self_incorporation",
                "verify": "homeostasis",
            },
        },
        "observatory": state.to_dict(),
        "scene": scene.to_dict(),
        "activity": {
            "events": [event.to_dict() for event in state.events],
            "total": len(state.events),
            "limit": 25,
        },
    }


def test_runtime_ui_contract_validation_accepts_valid_bootstrap_payload():
    validation = validate_runtime_ui_payload(_valid_payload())

    assert validation.ok is True
    assert validation.errors == ()
    assert "manifest" in validation.checked
    assert "scene" in validation.checked


def test_runtime_ui_contract_validation_rejects_mutating_or_mismatched_payload():
    payload = _valid_payload()
    payload["manifest"]["controls_enabled"] = True
    payload["scene"]["nodes"] = payload["scene"]["nodes"][:-1]

    validation = validate_runtime_ui_payload(payload)

    assert validation.ok is False
    assert "manifest.controls_enabled must be false" in validation.errors
    assert "scene.nodes must match observatory.subsystems" in validation.errors
