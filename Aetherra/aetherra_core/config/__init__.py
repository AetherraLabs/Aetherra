# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

from .config_loader import (  # noqa: F401
    AetherraConfigLoader,
    get_config,
    get_config_loader,
    load_config,
)

CONFIG_AVAILABLE = True

__all__ = [
    "CONFIG_AVAILABLE",
    "AetherraConfigLoader",
    "get_config_loader",
    "load_config",
    "get_config",
]
