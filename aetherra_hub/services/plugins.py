"""Plugin manifest validation, signing checks, and in-memory registry.

This is a minimal extraction from the monolithic hub server. It keeps behavior
compatible while isolating logic for easier testing.
"""

from __future__ import annotations

# Standard library imports
import base64
import importlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)

try:  # optional
    # Aetherra imports
    from Aetherra.plugins.manifest_schema import (  # type: ignore
        compute_trust_zone,
        validate_manifest,
    )
except Exception:  # pragma: no cover - unavailable path

    def validate_manifest(data: Dict[str, Any]):  # type: ignore
        return False, ["validator_unavailable"], data

    def compute_trust_zone(strict: bool, verified: bool):  # type: ignore
        return "unsigned"


@dataclass
class PluginStore:
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    active_registrations: int = 0

    def list(self) -> Dict[str, Any]:
        return {
            "plugins": list(self.plugins.values()),
            "total": len(self.plugins),
            "timestamp": datetime.now().isoformat(),
        }

    def get(self, plugin_id: str) -> Dict[str, Any] | None:
        return self.plugins.get(plugin_id)

    def register(self, manifest: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        strict_env = (
            os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
            or os.environ.get("AETHERRA_HUB_STRICT", "0") == "1"
            or os.environ.get("AETHERRA_STRICT", "0") == "1"
        )
        strict = bool(strict_env)
        has_sig = bool(manifest.get("signature")) and bool(manifest.get("pubkey"))

        schema_errors = []
        normalized = dict(manifest)
        try:
            ok, errs, norm = validate_manifest(manifest)
            schema_errors = errs
            normalized = norm
        except Exception:
            ok = not strict
        if not ok:
            missing_entry_only = (
                isinstance(schema_errors, list)
                and len(schema_errors) == 1
                and (
                    "entry_point" in str(schema_errors[0])
                    and "required" in str(schema_errors[0])
                )
            )
            soft_entry_only = (not strict) and missing_entry_only
            strict_signed_entry_only = False
            if strict and missing_entry_only and has_sig:
                verifier, lib_ok = _load_verifier()
                if verifier and lib_ok:
                    try:
                        strict_signed_entry_only = bool(verifier(manifest))
                    except Exception:
                        strict_signed_entry_only = False
            if soft_entry_only or strict_signed_entry_only:
                normalized.setdefault("entry_point", "main.py")
                ok = True
            else:
                return False, {"error": "manifest_invalid", "details": schema_errors}

        verified = False
        if strict:
            if not has_sig:
                return False, {"error": "invalid signature"}
            if not _base64_ok(manifest.get("signature")) or not _base64_ok(
                manifest.get("pubkey")
            ):
                return False, {"error": "invalid signature"}
            verifier, lib_ok = _load_verifier()
            if not verifier or not lib_ok:
                return False, {"error": "signature verification unavailable"}
            try:
                verified = bool(verifier(manifest))
            except Exception:
                return False, {"error": "invalid signature"}
            if not verified:
                return False, {"error": "invalid signature"}
        else:
            if has_sig:
                verifier, lib_ok = _load_verifier()
                if verifier and lib_ok:
                    try:
                        verified = bool(verifier(manifest))
                    except Exception:
                        verified = False

        trust_zone = "unsigned"
        try:
            trust_zone = compute_trust_zone(strict, bool(verified))
        except Exception:
            trust_zone = "unsigned"

        plugin_id = (
            normalized.get("name")
            or manifest.get("name")
            or f"plugin_{len(self.plugins) + 1}"
        )
        normalized["registered_at"] = datetime.now().isoformat()
        normalized["status"] = "registered"
        normalized["signature_verified"] = bool(verified)
        normalized["trust_zone"] = trust_zone

        self.plugins[plugin_id] = normalized
        self.active_registrations += 1
        logger.info("[OK] Plugin registered: %s", plugin_id)
        return True, {"status": "success", "plugin_id": plugin_id}


def _base64_ok(val: Any) -> bool:
    try:
        if not val:
            return False
        base64.b64decode(str(val), validate=True)
        return True
    except Exception:
        return False


_verifier_cache: Dict[str, Any] | None = None


def _load_verifier():  # returns (callable|None, has_lib: bool)
    global _verifier_cache
    if _verifier_cache is not None:
        return _verifier_cache.get("fn"), bool(_verifier_cache.get("lib_ok"))
    try:  # pragma: no cover - dynamic import path
        ps = importlib.import_module("Aetherra.security.plugin_signing")
        fn = getattr(ps, "verify_plugin_signature", None)
        lib_ok = bool(getattr(ps, "NACL", False))
        _verifier_cache = {"fn": fn, "lib_ok": lib_ok}
        return fn, lib_ok
    except Exception:
        _verifier_cache = {"fn": None, "lib_ok": False}
        return None, False


store = PluginStore()
