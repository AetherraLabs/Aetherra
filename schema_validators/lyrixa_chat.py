# SPDX-License-Identifier: GPL-3.0-or-later
"""Lightweight validator for Lyrixa chat responses used by tests.
This is a minimal stub that performs structural checks only.
"""

from typing import Any


def validate_lyrixa_chat_response(payload: dict[str, Any]) -> bool:
    # Required top-level keys in tests
    required = ["message", "suggestions", "confidence"]
    for k in required:
        if k not in payload:
            return False
    # suggestions expected list, confidence numeric
    if not isinstance(payload.get("suggestions"), list):
        return False
    conf = payload.get("confidence")
    return isinstance(conf, int | float)
