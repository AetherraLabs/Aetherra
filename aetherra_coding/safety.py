"""Safety & Security integration (Phase 0 stub)

Provides wrapper to invoke .aether risk verifier.
Future: integrate full security pipeline and agent hooks.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run_aether_risk_verifier(strict: bool, diagnostics: list[str]) -> bool:
    script = Path("tools/verify_aether_scripts.py")
    if not script.exists():
        diagnostics.append(
            "[aether_risk] verifier script missing; treating as pass for Phase 0"
        )
        return True
    env = os.environ.copy()
    if strict:
        env["AETHERRA_SCRIPT_VERIFY_STRICT"] = "1"
    try:
        p = subprocess.Popen(
            [
                "python",
                str(script),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        out, _ = p.communicate()
        diagnostics.append("[aether_risk]\n" + out)
        return p.returncode == 0
    except FileNotFoundError:
        diagnostics.append("[aether_risk] python not found")
        return False
