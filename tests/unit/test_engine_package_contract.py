# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from Aetherra.aetherra_core.engine import (
    AETHERRA_ENGINE_AVAILABLE,
    AETHERRA_ENGINE_IMPORT_ERROR,
    AetherraEngine,
    get_engine_status,
)


def test_engine_package_exports_real_engine_when_available():
    assert AETHERRA_ENGINE_AVAILABLE is True
    assert AETHERRA_ENGINE_IMPORT_ERROR is None
    assert AetherraEngine.__module__ == "Aetherra.aetherra_core.engine.aetherra_engine"


def test_engine_package_status_reports_import_error_field():
    status = get_engine_status()

    assert status["aetherra"] is True
    assert status["engine_import_error"] is None
