# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import pytest


@pytest.mark.asyncio
async def test_create_aether_from_task_custom_template(monkeypatch, tmp_path):
    # Arrange: custom template dir with a simple template
    tpl_dir = tmp_path / "tpl"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "template.aether").write_text(
        '# @meta: {"created": "{created}", "task": "{task}"}\n'
        'policy profile="test"\n'
        "{requires}\n"
        'narrate "Begin: {task}"\n',
        encoding="utf-8",
    )

    out_file = tmp_path / "out.aether"
    monkeypatch.setenv("AETHERRA_TEMPLATE_DIR", str(tpl_dir))
    monkeypatch.setenv("AETHERRA_REQUIRE_STRICT", "0")

    # Act: run generator main with --out
    # Aetherra imports
    from tools import create_aether_from_task as gen

    monkeypatch.chdir(tmp_path)
    # emulate CLI args
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")
    # Call main via function to avoid subprocess
    # Standard library imports
    import sys

    argv_bak = sys.argv[:]
    try:
        sys.argv = [
            "create_aether_from_task.py",
            "Build a memory smoke test",
            "--out",
            str(out_file),
        ]
        rc = gen.main()
        assert rc == 0
    finally:
        sys.argv = argv_bak

    # Assert: file exists and contains replaced fields and lenient requires
    assert out_file.exists()
    text = out_file.read_text(encoding="utf-8")
    assert "@meta:" in text and "Build a memory smoke test" in text
    # lenient requires contains no version pin
    assert "require module requests" in text
    assert 'version="^2"' not in text
