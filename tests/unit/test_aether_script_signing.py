# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from Aetherra.security.script_signing import embed_signature, verify_embedded_signature


def test_embed_and_verify_signature_roundtrip():
    body = """
# sample aether script (body only)
goal "Protect Aether Script"
remember "signed" as "integrity"
""".strip()

    signed = embed_signature(body)
    ok, reason = verify_embedded_signature(signed)
    assert ok, reason

    # Tamper with body should fail
    tampered = signed + "\n# extra"
    ok2, reason2 = verify_embedded_signature(tampered)
    assert not ok2
    assert reason2 in {"signature mismatch"}
