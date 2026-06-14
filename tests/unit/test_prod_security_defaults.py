# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import importlib


def test_plugin_signatures_are_required_in_production_profile(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    monkeypatch.delenv("AETHERRA_SIGNING_STRICT", raising=False)
    monkeypatch.delenv("AETHERRA_PROD_UNSAFE_ALLOW", raising=False)

    import Aetherra.security.plugin_signing as plugin_signing

    importlib.reload(plugin_signing)

    # Production should fail closed when no signature/pubkey is present.
    assert (
        plugin_signing.verify_plugin_signature({"name": "demo", "version": "1.0"})
        is False
    )
