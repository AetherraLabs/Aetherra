#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧪 Import Test Suite for Contributors (pytest)
=============================================
Validates common import patterns under pytest to catch environment issues early.
"""

# Third party imports
import pytest

IMPORT_CASES = [
    (
        "Basic aetherra_core import",
        "from Aetherra.aetherra_core import get_system_status",
    ),
    (
        "Engine module import",
        "from Aetherra.aetherra_core.engine import get_engine_status",
    ),
    (
        "Memory module import",
        "from Aetherra.aetherra_core.memory import MEMORY_AVAILABLE",
    ),
    (
        "Config module import",
        "from Aetherra.aetherra_core.config import CONFIG_AVAILABLE",
    ),
    ("Core module import", "from Aetherra.core import get_package_status"),
    ("Plugins module import", "from Aetherra.plugins import get_package_status"),
    ("Runtime module import", "from Aetherra.runtime import get_package_status"),
    ("Kernel loop import", "from aetherra_kernel_loop import AetherraKernelLoop"),
    (
        "Service registry import",
        "from aetherra_service_registry import ServiceRegistry",
    ),
    ("OS launcher import", "import aetherra_os_launcher"),
    ("Startup script import", "import aetherra_startup"),
]


@pytest.mark.parametrize("description,import_statement", IMPORT_CASES)
def test_imports(description: str, import_statement: str):
    # Each case must import without raising.
    namespace = {}
    exec(import_statement, namespace)
    assert True
