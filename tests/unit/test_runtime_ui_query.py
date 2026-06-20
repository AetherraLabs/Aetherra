from Aetherra.runtime_ui import (
    ObservatoryMode,
    allowed_observatory_modes,
    bounded_filter_value,
    bounded_user_name,
    parse_limit,
    parse_observatory_mode,
)


def test_runtime_ui_query_parses_modes_and_allowed_values():
    assert parse_observatory_mode(None) == ObservatoryMode.OVERVIEW
    assert parse_observatory_mode("ARCHITECT") == ObservatoryMode.ARCHITECT
    assert parse_observatory_mode("execute") is None
    assert allowed_observatory_modes() == [
        "first_launch",
        "overview",
        "architect",
        "subsystem",
    ]


def test_runtime_ui_query_bounds_user_and_filter_values():
    assert bounded_user_name("  Tim   Aetherra  ") == "Tim Aetherra"
    assert bounded_user_name("   ") is None
    assert bounded_filter_value("Self-Improvement") == "self_improvement"
    assert bounded_filter_value("   ") is None


def test_runtime_ui_query_parses_bounded_limits():
    assert parse_limit(None, default=25).value == 25
    assert parse_limit("0", default=25).value == 1
    assert parse_limit("250", default=25).value == 100

    invalid = parse_limit("many", default=25)
    assert invalid.ok is False
    assert invalid.error == "limit must be an integer"
