# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Compatibility shim for tests importing 'lyrixa.*'.
Resolves to Aetherra.lyrixa.* modules.
"""

import sys as _sys
from importlib import import_module as _import_module

# When 'lyrixa' is imported, alias it to the actual package 'Aetherra.lyrixa'
_real_pkg = _import_module("Aetherra.lyrixa")
# Re-export attributes
for _k in getattr(_real_pkg, "__all__", ()):  # attribute may not exist
    globals()[_k] = getattr(_real_pkg, _k)
# Ensure submodule resolution goes through to Aetherra.lyrixa
_sys.modules.setdefault("lyrixa", _real_pkg)
