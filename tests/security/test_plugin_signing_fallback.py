# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import base64
from pathlib import Path

import pytest


def test_ed25519_cryptography_fallback_sign_and_verify(tmp_path: Path):
    """
    Force PyNaCl path off and exercise the cryptography-backed Ed25519 fallback.
    Verifies: keypair generation, signing, and verification succeed; optional code_hash check passes.
    """
    import Aetherra.security.plugin_signing as ps

    # Skip if cryptography backend is unavailable in the environment
    if not getattr(ps, "CRYPTO", False):
        pytest.skip("cryptography backend not available; cannot exercise fallback")

    # Ensure fallback path by disabling PyNaCl at runtime
    orig_nacl = getattr(ps, "NACL", False)
    try:
        ps.NACL = False

        # Generate keypair via cryptography fallback
        pub_b64, sec_b64 = ps.generate_keypair()
        assert isinstance(pub_b64, str) and isinstance(sec_b64, str)
        assert len(base64.b64decode(pub_b64)) == 32
        assert len(base64.b64decode(sec_b64)) == 32

        # Create a small file and include code hash verification
        fpath = tmp_path / "sample.txt"
        fpath.write_text("hello aetherra", encoding="utf-8")
        code_hash = ps.compute_files_hash([str(fpath)])

        manifest = {
            "name": "test_plugin",
            "version": "1.0.0",
            "code_files": [str(fpath)],
            "code_hash": code_hash,
        }

        signed = ps.sign_manifest(manifest, sec_b64)
        assert signed.get("signature"), "signature missing in fallback path"
        assert signed.get("pubkey") == pub_b64, "pubkey mismatch in signed manifest"

        assert ps.verify_plugin_signature(signed) is True

    finally:
        # Restore original NACL flag to avoid side effects
        try:
            ps.NACL = orig_nacl
        except Exception:
            pass
