# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Aetherra imports
from Aetherra.plugins.manifest_schema import compute_trust_zone, validate_manifest


def test_validate_manifest_minimal_ok():
    ok, errs, norm = validate_manifest(
        {"name": "plugin_x", "version": "1.0.0", "entry_point": "main.py"}
    )
    assert ok, errs
    assert norm["permissions"] == []
    assert norm["data_classification"] == "public"


def test_validate_manifest_invalid_permission():
    ok, errs, norm = validate_manifest(
        {
            "name": "p",
            "version": "1.0.0",
            "entry_point": "main.py",
            "permissions": ["invalid_perm"],
        }
    )
    assert not ok
    assert any("permissions:" in e for e in errs)


def test_compute_trust_zone():
    assert compute_trust_zone(strict=True, signature_verified=True) == "strict_signed"
    assert compute_trust_zone(strict=False, signature_verified=True) == "lenient_signed"
    assert compute_trust_zone(strict=False, signature_verified=False) == "unsigned"


def test_plugin_policy_enforcement(tmp_path, monkeypatch):
    # Create a simple plugin with side effects
    pdir = tmp_path / "lyrixa_plugins" / "io_plugin"
    pdir.mkdir(parents=True)
    (pdir / "manifest.json").write_text(
        """
        {
            "name": "io_plugin",
            "version": "1.0.0",
            "entry_point": "main.py",
            "side_effects": "filesystem",
            "permissions": [],
            "timeout_ms": 500
        }
        """.strip()
    )
    (pdir / "main.py").write_text(
        """
        def execute(command, **kwargs):
            return {"ok": True}
        """.strip()
    )

    # Point system to temp dir
    # Aetherra imports
    import Aetherra.plugins.core.plugin_system as ps

    ps.Path = lambda p="": tmp_path / (p or "")  # monkeypatch Path used in ctor

    system = ps.LyrixaPluginSystem()
    # Rediscover from tmp dir
    system._discover_plugins()

    # Activate
    result = system.activate_plugin("io_plugin")
    assert result.get("success"), result

    # Execute should fail due to missing permission for filesystem
    out = system.execute_plugin("io_plugin", "any")
    assert out.get("success") is False
    assert out.get("error") == "missing_permissions"

    # Update manifest to include permission and try again
    (pdir / "manifest.json").write_text(
        """
        {
            "name": "io_plugin",
            "version": "1.0.0",
            "entry_point": "main.py",
            "side_effects": "filesystem",
            "permissions": ["filesystem"],
            "timeout_ms": 500
        }
        """.strip()
    )

    # Force reload plugin manifest
    system.installed_plugins.clear()
    system._discover_plugins()
    system.activate_plugin("io_plugin")

    out2 = system.execute_plugin("io_plugin", "any")
    assert out2.get("success") is True
