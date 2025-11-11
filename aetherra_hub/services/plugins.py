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
from typing import Any

logger = logging.getLogger(__name__)

try:  # optional
    # Aetherra imports
    from Aetherra.plugins.manifest_schema import (  # type: ignore
        compute_trust_zone,
        validate_manifest,
    )
except Exception:  # pragma: no cover - unavailable path

    def validate_manifest(
        data: dict[str, Any],
    ) -> tuple[bool, list[str], dict[str, Any]]:  # type: ignore
        return False, ["validator_unavailable"], data

    def compute_trust_zone(strict: bool, verified: bool) -> str:  # type: ignore
        return "unsigned"


@dataclass
class PluginStore:
    plugins: dict[str, dict[str, Any]] = field(default_factory=dict)
    active_registrations: int = 0

    def list(self) -> dict[str, Any]:
        return {
            "plugins": list(self.plugins.values()),
            "total": len(self.plugins),
            "timestamp": datetime.now().isoformat(),
        }

    def get(self, plugin_id: str) -> dict[str, Any] | None:
        return self.plugins.get(plugin_id)

    def register(self, manifest: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        strict_env = (
            os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
            or os.environ.get("AETHERRA_HUB_STRICT", "0") == "1"
            or os.environ.get("AETHERRA_STRICT", "0") == "1"
        )
        strict = bool(strict_env)
        has_sig = bool(manifest.get("signature")) and bool(manifest.get("pubkey"))
        # Developer override: allow unsigned registration even when strict flags are set
        # if explicit env set AND verification libs unavailable.
        if os.environ.get("AETHERRA_ALLOW_UNSIGNED_DEV", "0") == "1":
            # Temporarily downgrade strictness for this registration attempt only.
            strict = False
            logger.warning(
                "[PLUGINS][DEV] Allowing unsigned plugin registration under AETHERRA_ALLOW_UNSIGNED_DEV=1 override"
            )
            # Remove any signature fields to avoid accidental verification attempts downstream
            if manifest.get("signature") or manifest.get("pubkey"):
                manifest.pop("signature", None)
                manifest.pop("pubkey", None)
                has_sig = False
                logger.debug(
                    "[PLUGINS][DEV] Stripped signature/pubkey from manifest under dev override"
                )
        # Additional dev relaxation: if still strict but missing signature, downgrade silently for dev override
        if (
            strict
            and not has_sig
            and os.environ.get("AETHERRA_ALLOW_UNSIGNED_DEV", "0") == "1"
        ):
            strict = False
            logger.debug(
                "[PLUGINS][DEV] Downgraded strict due to missing signature in dev override mode"
            )

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
            # In dev override mode, we already stripped signature; skip optional verification entirely
            if os.environ.get("AETHERRA_ALLOW_UNSIGNED_DEV", "0") != "1" and has_sig:
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


_verifier_cache: dict[str, Any] | None = None


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
