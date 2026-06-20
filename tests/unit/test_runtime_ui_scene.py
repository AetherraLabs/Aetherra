from Aetherra.runtime_ui import (
    ObservatoryMode,
    SubsystemStatus,
    build_observatory_scene,
    build_observatory_state,
)


def test_observatory_scene_has_stable_layout_for_core_nodes():
    state = build_observatory_state(
        mode=ObservatoryMode.OVERVIEW,
        system_status={
            "guardian": {"status": "active", "activity": 0.7},
            "security": {"status": "active", "activity": 0.5},
            "memory": {"status": "stable", "activity": 0.2},
        },
    )

    scene = build_observatory_scene(state)
    payload = scene.to_dict()

    assert payload["core_label"] == "AETHERRA"
    assert payload["read_only"] is True
    assert payload["coordinate_space"] == "normalized_3d"

    nodes = {node["name"]: node for node in payload["nodes"]}
    assert nodes["guardian"]["group"] == "governance"
    assert nodes["security"]["x"] > nodes["guardian"]["x"]
    assert nodes["memory"]["group"] == "cognition"
    assert nodes["guardian"]["accessibility_label"] == "Guardian: active"


def test_observatory_scene_reflects_status_in_emphasis_and_connections():
    state = build_observatory_state(
        system_status={
            "guardian": {"status": "contained", "activity": 0.2},
            "security": {"status": "active", "activity": 0.3},
        }
    )

    scene = build_observatory_scene(state)
    nodes = {node.name: node for node in scene.nodes}
    connections = {
        (connection.source, connection.target): connection
        for connection in scene.connections
    }

    assert nodes["guardian"].status == SubsystemStatus.CONTAINED
    assert nodes["guardian"].emphasis == 1.0
    assert (
        connections[("guardian", "security")].status
        == SubsystemStatus.CONTAINED
    )
    assert connections[("guardian", "security")].thickness == 0.9
