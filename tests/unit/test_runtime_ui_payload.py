from Aetherra.runtime_ui import (
    ObservatoryMode,
    build_runtime_ui_activity_payload,
    build_runtime_ui_bootstrap_payload,
    build_runtime_ui_contract_validation_payload,
    build_runtime_ui_observatory_payload,
    build_runtime_ui_scene_payload,
    build_runtime_ui_status_payload,
    build_runtime_ui_subsystem_payload,
)


def test_runtime_ui_payload_builders_return_read_only_bootstrap_and_status():
    bootstrap = build_runtime_ui_bootstrap_payload(
        mode=ObservatoryMode.FIRST_LAUNCH,
        user_name="Tim",
        limit=2,
    )
    status = build_runtime_ui_status_payload()

    assert bootstrap["read_only"] is True
    assert bootstrap["observatory"]["mode"] == "first_launch"
    assert bootstrap["observatory"]["greeting"] == "Good morning, Tim."
    assert bootstrap["activity"]["limit"] == 2
    assert len(bootstrap["activity"]["events"]) == 2
    assert status["status"] == "healthy"
    assert status["validation"]["ok"] is True


def test_runtime_ui_payload_builders_return_scene_observatory_and_validation():
    observatory = build_runtime_ui_observatory_payload(ObservatoryMode.OVERVIEW)
    scene = build_runtime_ui_scene_payload(ObservatoryMode.OVERVIEW)
    validation = build_runtime_ui_contract_validation_payload(
        mode=ObservatoryMode.OVERVIEW,
        user_name=None,
        limit=25,
    )

    assert observatory["observatory"]["core_label"] == "AETHERRA"
    assert scene["scene"]["coordinate_space"] == "normalized_3d"
    assert validation["validation"]["ok"] is True


def test_runtime_ui_payload_builders_filter_activity_and_subsystems():
    activity = build_runtime_ui_activity_payload(
        channel="governance",
        source=None,
        limit=10,
    )
    subsystem = build_runtime_ui_subsystem_payload("self-improvement")
    missing = build_runtime_ui_subsystem_payload("desktop")

    assert activity["events"]
    assert all(event["visual_channel"] == "governance" for event in activity["events"])
    assert subsystem is not None
    assert subsystem["subsystem"]["name"] == "self_improvement"
    assert subsystem["profile"]["authority_owner"] == "Self-Improvement"
    assert missing is None
