# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from Aetherra.analysis.static_risk import analyze_paths


def test_static_risk_flags_risky_lines(tmp_path):
    f = tmp_path / "bad.aether"
    f.write_text(
        """
# goal: test risk
run_plugin("curl http://malicious")
os.system('rm -rf /')
open('file.txt','w').write('x')
""",
        encoding="utf-8",
    )
    res = analyze_paths([f])
    assert res["files"][str(f)]["score"] >= 6  # shell (4) + network (2)
