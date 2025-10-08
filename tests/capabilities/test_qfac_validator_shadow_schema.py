import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines


def test_qfac_validator_and_shadow_metrics_schema_defaults_present():
    """
    Ensure validator/shadow metrics schema lines exist even when services are absent.
    We only assert the presence of metric names (not values), to lock interface.
    """
    lines = build_all_metrics_lines()
    body = "\n".join(lines)

    # Validator default metrics
    assert re.search(
        r"^# HELP aetherra_qfac_validator_green_total ", body, flags=re.MULTILINE
    )
    assert re.search(
        r"^# TYPE aetherra_qfac_validator_green_total counter$",
        body,
        flags=re.MULTILINE,
    )
    assert re.search(r"^aetherra_qfac_validator_green_total ", body, flags=re.MULTILINE)

    assert re.search(
        r"^# HELP aetherra_qfac_validator_blocked_total ", body, flags=re.MULTILINE
    )
    assert re.search(
        r"^# TYPE aetherra_qfac_validator_blocked_total counter$",
        body,
        flags=re.MULTILINE,
    )
    assert re.search(
        r"^aetherra_qfac_validator_blocked_total ", body, flags=re.MULTILINE
    )

    # Shadow logs default metrics
    assert re.search(
        r"^# HELP aetherra_qfac_shadow_logs_total ", body, flags=re.MULTILINE
    )
    assert re.search(
        r"^# TYPE aetherra_qfac_shadow_logs_total counter$", body, flags=re.MULTILINE
    )
    assert re.search(r"^aetherra_qfac_shadow_logs_total ", body, flags=re.MULTILINE)

    assert re.search(
        r"^# HELP aetherra_qfac_shadow_logs_recent ", body, flags=re.MULTILINE
    )
    assert re.search(
        r"^# TYPE aetherra_qfac_shadow_logs_recent gauge$", body, flags=re.MULTILINE
    )
    assert re.search(r"^aetherra_qfac_shadow_logs_recent ", body, flags=re.MULTILINE)
