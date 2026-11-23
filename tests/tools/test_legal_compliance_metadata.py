"""The maintenance inventory must read installed metadata without pkg_resources."""

# Standard library imports
from importlib import metadata

# Third party imports
import pytest

# Aetherra imports
from tools.maintenance import verify_legal_compliance as checker


@pytest.mark.parametrize(
    ("license_header", "compatible"),
    [
        ("License: MIT", True),
        ("Classifier: License :: OSI Approved :: MIT License", True),
        ("License-Expression: MIT", True),
        ("License-Expression: MIT AND LicenseRef-Private", False),
        ("License-Expression: LicenseRef-PrivateMIT", False),
        ("License-Expression: LicenseRef-Private\nLicense: MIT", False),
        ("License: Proprietary", False),
    ],
)
def test_inventory_reads_real_distribution_metadata(
    tmp_path, monkeypatch, capsys, license_header, compatible
):
    info = tmp_path / "synthetic_inventory-1.2.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(
        "Metadata-Version: 2.4\nName: synthetic-inventory\nVersion: 1.2\n"
        f"{license_header}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        checker, "distributions", lambda: metadata.distributions(path=[str(tmp_path)])
    )
    assert checker.check_license_compatibility() is compatible
    output = capsys.readouterr().out
    assert "synthetic-inventory" in output
    assert "1.2" in output
    assert "Found 1 installed packages" in output
    assert "Unknown/Error packages: 0" in output
