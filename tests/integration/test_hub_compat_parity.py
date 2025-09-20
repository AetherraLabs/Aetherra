# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compat parity test ensuring deprecated shim still re-exports expected API.

Remains temporary; remove alongside shim removal (see CHANGELOG deprecation).
"""

# Standard library imports
import importlib
import warnings


def test_legacy_shim_emits_deprecation_and_exports():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        mod = importlib.import_module("aetherra_hub_server")
    # Expect at least one DeprecationWarning
    assert any(
        isinstance(x.message, DeprecationWarning) for x in w
    ), "No DeprecationWarning from shim import"
    assert hasattr(mod, "AetherraHubServer")
    assert hasattr(mod, "start_hub_server")
    # Start/stop quickly to ensure surface still functional
    server = mod.AetherraHubServer(0)
    assert server.start_server() is True
    server.stop_server()
