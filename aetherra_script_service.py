#!/usr/bin/env python3
"""
Aetherra Script Service
=======================

(c) Aetherra Labs. Proprietary Aether Script interpreter scaffolding.

Lightweight .aether interpreter for goals, assignments, and memory ops.
This minimal implementation is designed to satisfy current tests and can be
extended to support full EBNF from the specification. Optional signing
verification can be enabled via environment flags for protection.
"""

import importlib
import json
import logging
import os
import re
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional runtime imports kept inside functions to avoid heavy deps on import
try:  # Prefer absolute package path
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngine,
    )
except Exception:  # Fallback for variations in path
    AetherraMemoryEngine = None  # type: ignore

logger = logging.getLogger(__name__)

SIGNATURE_MARKER = "# @signature:"


class AetherScriptService:
    """Minimal .aether interpreter with async interface."""

    def __init__(self, service_registry=None):
        self.service_registry = service_registry
        self.interpreter_ready = False
        self.running = False
        self.memory_engine = None
        self._last_ctx = {}
        self._trace = []

    async def initialize(self):
        """Initialize the Aether Script service (no-op for now)."""
        # Try to attach to the memory system
        try:
            if self.service_registry is not None:
                mem = self.service_registry.get_service("memory_system")
                if mem is not None:
                    self.memory_engine = mem
            if self.memory_engine is None and AetherraMemoryEngine is not None:
                # Local memory engine as a fallback
                self.memory_engine = AetherraMemoryEngine()
        except Exception:
            # Keep service usable even if memory system is unavailable
            self.memory_engine = None
        self.interpreter_ready = True
        return True

    async def start(self):
        self.running = True
        return True

    async def stop(self):
        self.running = False
        return True

    async def execute_script_file(
        self, script_path: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        text = Path(script_path).read_text(encoding="utf-8")
        return await self.execute_script_content(
            text, filename=script_path, context=context
        )

    async def execute_script_content(
        self,
        script_content: str,
        filename: str = "<string>",
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        try:
            # Optional strict signature verification
            self._maybe_verify_signature(script_content, filename)
            results = await self._execute_script_content(script_content, context or {})
            payload: Dict[str, Any] = {"results": results}
            # Expose policy and requires for tooling/UX
            if isinstance(self._last_ctx, dict):
                if "_policy" in self._last_ctx:
                    payload["policy"] = dict(self._last_ctx.get("_policy", {}))
                if "_requires" in self._last_ctx:
                    payload["requires"] = list(self._last_ctx.get("_requires", []))
                if self._last_ctx.get("_transactions"):
                    payload["transactions"] = list(
                        self._last_ctx.get("_transactions", [])
                    )
            # Optionally expose trace if requested
            if os.getenv("AETHERRA_TRACE", "0") == "1":
                payload["trace"] = list(self._trace)
            # Persist audit trail metadata (model/seed/cost/tokens/prompts sanitized)
            try:
                self._audit_run(script_content, payload, context or {}, filename)
            except Exception:
                # Non-fatal: audit logging should never break execution
                pass
            return {"success": True, "result": payload}
        except Exception as e:
            logger.error(f"[AETHER] Execute failed: {e}")
            return {"success": False, "error": str(e), "file": filename}

    async def _execute_script_content(
        self, script_content: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        ctx: Dict[str, Any] = dict(context or {})
        results: List[Dict[str, Any]] = []
        self._trace = []
        # Transaction state
        txn_active = False
        txn_ops: List[Dict[str, Any]] = []
        txn_name = None
        for line_num, raw in enumerate(script_content.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # Handle transaction control lines directly
            if re.match(r"^begin\s+transaction(\s+\w+)?\s*$", line, re.IGNORECASE):
                if txn_active:
                    raise ValueError("nested transactions not supported")
                txn_active = True
                m = re.match(
                    r"^begin\s+transaction(?:\s+(\w+))?\s*$", line, re.IGNORECASE
                )
                txn_name = m.group(1) if m else None
                self._trace.append(
                    {"type": "txn_begin", "name": txn_name, "line": line_num}
                )
                results.append(
                    {"type": "transaction_begin", "name": txn_name, "line": line_num}
                )
                continue
            if re.match(r"^commit\s+transaction\s*$", line, re.IGNORECASE):
                if not txn_active:
                    raise ValueError("commit without active transaction")
                summary = {
                    "type": "transaction_commit",
                    "name": txn_name,
                    "ops": len(txn_ops),
                    "line": line_num,
                }
                results.append(summary)
                self._trace.append(
                    {
                        "type": "txn_commit",
                        "name": txn_name,
                        "ops": len(txn_ops),
                        "line": line_num,
                    }
                )
                ctx.setdefault("_transactions", []).append(
                    {"name": txn_name, "ops": list(txn_ops)}
                )
                txn_active = False
                txn_ops = []
                txn_name = None
                continue
            if re.match(r"^rollback\s+transaction\s*$", line, re.IGNORECASE):
                if not txn_active:
                    raise ValueError("rollback without active transaction")
                results.append(
                    {
                        "type": "transaction_rollback",
                        "name": txn_name,
                        "ops": len(txn_ops),
                        "line": line_num,
                    }
                )
                self._trace.append(
                    {
                        "type": "txn_rollback",
                        "name": txn_name,
                        "ops": len(txn_ops),
                        "line": line_num,
                    }
                )
                txn_active = False
                txn_ops = []
                txn_name = None
                continue

            out = await self._execute_statement(line, ctx, line_num)
            if out is not None:
                results.append(out)
                # Track trace
                self._trace.append({"line": line_num, "statement": line, "result": out})
                # Collect transactional ops
                if txn_active and isinstance(out, dict):
                    # Mark idempotent false by default unless result says otherwise
                    txn_ops.append(
                        {
                            "line": line_num,
                            "op": out.get("type"),
                            "idempotent": bool(out.get("idempotent", False)),
                        }
                    )
        # Save last context for callers
        self._last_ctx = ctx
        return results

    async def _execute_statement(
        self, statement: str, context: Dict, line_num: int
    ) -> Any:
        def _parse_ver(s: str) -> List[int]:
            try:
                parts = [int(p) for p in s.split(".") if p.isdigit()]
                while len(parts) < 3:
                    parts.append(0)
                return parts[:3]
            except Exception:
                return [0, 0, 0]

        def _cmp(a: List[int], b: List[int]) -> int:
            return (a > b) - (a < b)

        def _semver_satisfies(version: Optional[str], req: Optional[str]) -> bool:
            if not req:
                return True
            if not version:
                return False
            v = _parse_ver(str(version))
            r = str(req).strip()
            if r == "*":
                return True
            if r.startswith("^"):
                base = _parse_ver(r[1:])
                upper = [base[0] + 1, 0, 0]
                return _cmp(v, base) >= 0 and _cmp(v, upper) < 0
            if r.startswith("~"):
                base = _parse_ver(r[1:])
                upper = [base[0], base[1] + 1, 0]
                return _cmp(v, base) >= 0 and _cmp(v, upper) < 0
            # exact match
            return _parse_ver(str(version)) == _parse_ver(r)

        # require plugin <name> [version="x.y.z"] [signature="..."]
        m = re.match(
            r"^require\s+plugin\s+([A-Za-z0-9_\-\.]+)(?:\s+version=\"([^\"]+)\")?(?:\s+signature=\"([^\"]+)\")?\s*$",
            statement,
            re.IGNORECASE,
        )
        if m:
            name = m.group(1)
            ver_req = m.group(2)
            sig_req = m.group(3)
            ok = True
            reason = None
            plugins = context.get("plugins")
            # Check presence/version if a plugin manager is provided
            if plugins is not None:
                try:
                    inst = None
                    # prefer dict-like installed_plugins
                    if hasattr(plugins, "installed_plugins"):
                        inst = getattr(plugins, "installed_plugins", {}).get(name)
                    elif hasattr(plugins, name):
                        inst = getattr(plugins, name)
                    if inst is None:
                        ok = False
                        reason = "not_installed"
                    else:
                        # attempt to read manifest.version
                        pver = getattr(getattr(inst, "manifest", inst), "version", None)
                        if ver_req and not _semver_satisfies(
                            str(pver) if pver else None, ver_req
                        ):
                            ok = False
                            reason = f"version_unsatisfied:{pver}!~{ver_req}"
                except Exception:
                    ok = False
                    reason = "check_error"
            # Signature requirement is recorded but not verified here (hub verifies on register)
            result = {
                "type": "require",
                "kind": "plugin",
                "name": name,
                "version": ver_req,
                "signature": sig_req,
                "ok": bool(ok),
                "line": line_num,
            }
            context.setdefault("_requires", []).append(result)
            if not ok and os.getenv("AETHERRA_REQUIRE_STRICT", "0") == "1":
                raise ValueError(f"require plugin failed: {name} ({reason})")
            return result

        # require module <name> [version="x.y.z"|"^1.2"|"~1.2.3"]
        m = re.match(
            r"^require\s+module\s+([A-Za-z0-9_\-\.]+)(?:\s+version=\"([^\"]+)\")?\s*$",
            statement,
            re.IGNORECASE,
        )
        if m:
            mod_name = m.group(1)
            ver_req = m.group(2)
            ok = True
            reason = None
            try:
                importlib.import_module(mod_name)
                found_ver: Optional[str] = None
                try:
                    found_ver = importlib_metadata.version(mod_name)
                except Exception:
                    try:
                        found_ver = getattr(
                            importlib.import_module(mod_name), "__version__", None
                        )
                    except Exception:
                        found_ver = None
                if ver_req and not _semver_satisfies(found_ver, ver_req):
                    ok = False
                    reason = f"version_unsatisfied:{found_ver}!~{ver_req}"
            except Exception:
                ok = False
                reason = "not_importable"
            result = {
                "type": "require",
                "kind": "module",
                "name": mod_name,
                "version": ver_req,
                "ok": bool(ok),
                "line": line_num,
            }
            context.setdefault("_requires", []).append(result)
            if not ok and os.getenv("AETHERRA_REQUIRE_STRICT", "0") == "1":
                raise ValueError(f"require module failed: {mod_name} ({reason})")
            return result

        # policy key=value [key2=value2 ...]
        m = re.match(r"^policy\s+(.+)$", statement, re.IGNORECASE)
        if m:
            raw_items = m.group(1)
            policy: Dict[str, Any] = {}
            # split by spaces or commas, support key=value
            for token in re.split(r"[\s,]+", raw_items.strip()):
                if not token:
                    continue
                if "=" not in token:
                    continue
                k, v = token.split("=", 1)
                k = k.strip()
                v = v.strip()
                # parse booleans
                if v.lower() in ("true", "false"):
                    val: Any = v.lower() == "true"
                else:
                    # parse number if possible
                    try:
                        val = int(v)
                    except ValueError:
                        try:
                            val = float(v)
                        except ValueError:
                            # strip optional quotes
                            if (v.startswith('"') and v.endswith('"')) or (
                                v.startswith("'") and v.endswith("'")
                            ):
                                val = v[1:-1]
                            else:
                                val = v
                policy[k] = val
            # Apply to plugin system if available in context
            plugins = context.get("plugins")
            if plugins and hasattr(plugins, "set_policy"):
                try:
                    plugins.set_policy(policy)
                except Exception:
                    pass
            # store in context for later steps
            context.setdefault("_policy", {}).update(policy)
            return {"type": "policy_set", "policy": policy, "line": line_num}
        # goal "..."
        m = re.match(r'^goal\s+"(.+?)"\s*$', statement, re.IGNORECASE)
        if m:
            goal_text = m.group(1)
            return {"type": "goal", "text": goal_text, "line": line_num}

        # remember "..." as "tag"
        m = re.match(
            r'^remember\s+"(.+?)"\s+as\s+"(.+?)"\s*$', statement, re.IGNORECASE
        )
        if m:
            content, tag = m.group(1), m.group(2)
            # Persist to memory engine if available
            if self.memory_engine is not None:
                try:
                    self.memory_engine.store(
                        {
                            "content": content,
                            "metadata": {"tag": tag, "source": "aether_script"},
                        }
                    )
                except Exception:
                    # Non-fatal; continue processing
                    pass

            return {
                "type": "remember",
                "content": content,
                "tag": tag,
                "line": line_num,
            }

        # narrate "..." -> capture narration event (no side effects)
        m = re.match(r'^narrate\s+"(.+?)"\s*$', statement, re.IGNORECASE)
        if m:
            text = m.group(1)
            return {
                "type": "narrate",
                "text": text,
                "idempotent": True,
                "line": line_num,
            }

        # assignment: name = value (string or number)
        m = re.match(r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<val>.+)$", statement)
        if m:
            var = m.group("var")
            val_raw = m.group("val").strip()
            if (val_raw.startswith('"') and val_raw.endswith('"')) or (
                val_raw.startswith("'") and val_raw.endswith("'")
            ):
                val = val_raw[1:-1]
            else:
                try:
                    val = int(val_raw)
                except ValueError:
                    try:
                        val = float(val_raw)
                    except ValueError:
                        val = val_raw
            context[var] = val
            return {
                "type": "assignment",
                "variable": var,
                "value": val,
                "idempotent": True,
                "line": line_num,
            }

        # Unknown
        return {"type": "unknown", "raw": statement, "line": line_num}

    def get_status(self) -> Dict[str, Any]:
        return {"running": self.running, "initialized": bool(self.interpreter_ready)}

    def get_memory_engine(self):
        """Expose the memory engine instance used by the service (for tests/integration)."""
        return self.memory_engine

    def _maybe_verify_signature(self, script_content: str, filename: str) -> None:
        """If strict verification is enabled, require a valid signature marker."""
        strict = os.getenv("AETHERRA_SCRIPT_VERIFY_STRICT", "0") == "1"
        if not strict:
            return
        from Aetherra.security.script_signing import (
            verify_embedded_signature,  # type: ignore
        )

        ok, reason = verify_embedded_signature(script_content)
        if not ok:
            raise ValueError(f"Signature verification failed for {filename}: {reason}")

    def _audit_run(
        self,
        script_content: str,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        filename: str,
    ) -> None:
        """Append a sanitized audit record including model/seed/tokens/cost/prompts.

        Controlled via env:
        - AETHERRA_AUDIT=0 disables
        - AETHERRA_AUDIT_PATH sets output file (default audit/aetherra_runs.jsonl)
        """
        if os.getenv("AETHERRA_AUDIT", "1") == "0":
            return
        # Gather model info from env and context
        model = (
            context.get("model")
            or os.getenv("AETHERRA_MODEL")
            or os.getenv("OPENAI_MODEL")
            or os.getenv("OPENAI_API_MODEL")
        )
        # Token/cost info if provided by caller
        tokens = context.get("tokens") or {
            "input": context.get("input_tokens"),
            "output": context.get("output_tokens"),
        }
        cost = context.get("cost") or context.get("cost_usd")
        # Seed/profile metadata for reproducibility
        audit_env = {
            "AETHERRA_PROFILE": os.getenv("AETHERRA_PROFILE"),
            "AETHERRA_DETERMINISTIC": os.getenv("AETHERRA_DETERMINISTIC"),
            "PYTHONHASHSEED": os.getenv("PYTHONHASHSEED"),
        }

        # Sanitize prompts: we store script content and any provided prompts with redaction
        def _sanitize(text: str) -> str:
            # Redact likely secrets/keys/tokens inline
            redactions = [
                r"(?i)(api[_-]?key\s*[:=]\s*)([^\s\"']+)",
                r"(?i)(secret\s*[:=]\s*)([^\s\"']+)",
                r"(?i)(token\s*[:=]\s*)([^\s\"']+)",
                r"(?i)(password\s*[:=]\s*)([^\s\"']+)",
            ]
            out = text
            for pat in redactions:
                out = re.sub(pat, r"\1[REDACTED]", out)
            # Strip signature markers from scripts
            out = re.sub(
                r"^#\s*@signature:.*$",
                "# @signature:[REDACTED]",
                out,
                flags=re.MULTILINE,
            )
            return out

        prompts = None
        if "prompts" in context and isinstance(context["prompts"], list):
            try:
                prompts = [_sanitize(str(p)) for p in context["prompts"]]
            except Exception:
                prompts = None
        sanitized_script = _sanitize(script_content)

        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "file": filename,
            "model": model,
            "env": audit_env,
            "tokens": tokens,
            "cost_usd": cost,
            "trace_included": bool(payload.get("trace")),
            "transactions": payload.get("transactions"),
            "policy": payload.get("policy"),
            "requires": payload.get("requires"),
            "script": sanitized_script,
            "prompts": prompts,
        }
        out_path = os.getenv(
            "AETHERRA_AUDIT_PATH", os.path.join("audit", "aetherra_runs.jsonl")
        )
        # Ensure directory exists
        Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# Service factory function
async def get_aether_script_service(service_registry=None):
    """Factory function to create and initialize the Aether Script service."""
    service = AetherScriptService(service_registry)
    await service.initialize()
    return service
