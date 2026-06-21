from Aetherra.maintenance import (
    classify_report_destination_for_root,
    classify_report_destination,
    normalize_project_relative_path,
    require_allowed_report_destination,
)


def test_normalize_project_relative_path():
    assert normalize_project_relative_path(".\\reports\\maintenance\\x.md") == (
        "reports/maintenance/x.md"
    )
    assert normalize_project_relative_path("./docs/reports/maintenance.md") == (
        "docs/reports/maintenance.md"
    )


def test_generated_report_output_paths_are_allowed():
    result = classify_report_destination("data/artifacts/maintenance/status.json")

    assert result.allowed is True
    assert result.category == "generated_output"
    assert result.reason == "approved_generated_report_directory"


def test_durable_docs_report_paths_are_allowed():
    result = classify_report_destination("docs/reports/maintenance/summary.md")

    assert result.allowed is True
    assert result.category == "durable_docs_record"


def test_durable_stub_inventory_path_is_allowed():
    result = classify_report_destination("docs/STUB_INVENTORY.json")

    assert result.allowed is True
    assert result.category == "durable_docs_record"
    assert result.reason == "approved_durable_docs_report_file"


def test_absolute_path_can_be_classified_relative_to_project_root(tmp_path):
    path = tmp_path / "artifacts" / "maintenance" / "status.json"

    result = classify_report_destination_for_root(path, tmp_path)

    assert result.allowed is True
    assert result.normalized_path == "artifacts/maintenance/status.json"


def test_require_allowed_report_destination_raises_for_blocked_path(tmp_path):
    path = tmp_path / "MAINTENANCE_REPORT.md"

    try:
        require_allowed_report_destination(path, tmp_path)
    except ValueError as exc:
        assert "root_level_generated_reports_are_not_allowed" in str(exc)
    else:
        raise AssertionError("Expected blocked report path to raise ValueError")


def test_root_level_generated_report_is_blocked():
    result = classify_report_destination("MAINTENANCE_REPORT.md")

    assert result.allowed is False
    assert result.category == "root_generated_report"
    assert result.reason == "root_level_generated_reports_are_not_allowed"


def test_unapproved_nested_report_path_is_blocked():
    result = classify_report_destination("tmp/manual/MAINTENANCE_REPORT.md")

    assert result.allowed is False
    assert result.category == "unapproved_destination"
