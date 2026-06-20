#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[HMR] Aetherra Hot Module Reload Controller
=========================================
Orchestrates hot-reload of selected services/adapters/engine without a full OS restart.

Phase 1 scope:
- Targets: engine, adapter:memory, adapter:plugin, lyrixa_chat
- Tasks: hmr_reload, hmr_status via kernel task queue
- Events: HMR_PREPARE, HMR_SWAP, HMR_ROLLBACK via Service Registry broadcast
- Best-effort quiesce and swap with optional state hand-off hooks
"""

# Standard library imports
import asyncio
import hashlib
import importlib
import importlib.util
import json
import logging
import os
import shutil
import time
from contextlib import suppress
from pathlib import PurePath
from typing import Any

logger = logging.getLogger(__name__)


class HMRController:
    """Hot Module Reload controller service.

    Registered in Service Registry as 'hmr_controller' by the launcher when enabled.
    """

    def __init__(self, registry, kernel, strict: bool = False):
        self.registry = registry
        self.kernel = kernel
        self.strict = bool(strict)
        self.running = False
        self.state: dict[str, Any] = {"status": "idle"}
        # Allowed sources (module names or approved paths). Comma-separated env, optional.
        self.allowed_sources = {
            s.strip()
            for s in os.getenv("AETHERRA_HMR_ALLOWED_SOURCES", "").split(",")
            if s.strip()
        }
        # Audit log path for HMR ops
        self.audit_path = os.getenv(
            "AETHERRA_HMR_AUDIT_PATH", ".aetherra/hmr_audit.jsonl"
        )
        # Audit rotation: max file size (bytes) and max backup files
        try:
            self.audit_max_bytes = int(
                os.getenv("AETHERRA_HMR_AUDIT_MAX_BYTES", str(5 * 1024 * 1024))
            )
        except Exception:
            self.audit_max_bytes = 5 * 1024 * 1024  # 5 MB default
        try:
            self.audit_max_backups = int(
                os.getenv("AETHERRA_HMR_AUDIT_MAX_BACKUPS", "3")
            )
        except Exception:
            self.audit_max_backups = 3
        # In-memory audit counters by event for Prometheus exposure
        self.audit_counters: dict[str, int] = {}
        self._rollback_tokens: dict[str, dict[str, Any]] = {}

    async def start(self):
        self.running = True
        try:
            # Best-effort registration; launcher may have already registered
            if hasattr(self.registry, "register_service"):
                await self.registry.register_service(
                    "hmr_controller",
                    self,
                    metadata={"type": "kernel_extension", "version": "1.0"},
                )
        except Exception:
            logger.debug("[HMR] Registry not ready for registration (best-effort)")

    async def stop(self):
        self.running = False

    # ---------------- Kernel task entry ----------------
    async def handle_kernel_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        t = (payload or {}).get("type")
        data = (payload or {}).get("data") or {}
        if t == "hmr_reload":
            target = data.get("target")
            source = data.get("source")
            if not target or not source:
                return {"ok": False, "error": "missing_target_or_source"}
            mode = data.get("mode", "safe")
            return await self._reload_target(
                str(target),
                str(source),
                mode=str(mode),
                requester=self._guardian_requester(data),
                approval_id=self._guardian_approval_id(data),
            )
        if t == "hmr_status":
            return {"ok": True, "state": self.state}
        return {"ok": False, "error": "unsupported_hmr_task"}

    def _guardian_requester(self, data: dict[str, Any] | None = None) -> str:
        data = data or {}
        requester = data.get("guardian_requester") or data.get("requester")
        return str(requester or "hmr_controller").strip() or "hmr_controller"

    def _guardian_approval_id(self, data: dict[str, Any] | None = None) -> str | None:
        data = data or {}
        value = data.get("guardian_approval_id") or data.get("approval_id")
        if value is None:
            return None
        approval_id = str(value).strip()
        return approval_id or None

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "hmr_controller" and capability == "system:reload":
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_source_metadata(self, source: str) -> dict[str, Any]:
        source_ref = str(source)
        source_hash = hashlib.sha256(source_ref.encode("utf-8")).hexdigest()
        suffix = PurePath(source_ref).suffix.lower() if source_ref.endswith(".py") else ""
        return {
            "source_kind": "file" if source_ref.endswith(".py") else "module",
            "source_sha256": source_hash,
            "source_suffix": suffix,
            "source_length": len(source_ref),
            "allowed_sources_configured": bool(self.allowed_sources),
        }

    def _token_hash(self, rollback_token: str) -> str:
        return hashlib.sha256(str(rollback_token).encode("utf-8")).hexdigest()[:16]

    def supports_rollback_action(self, action: str) -> bool:
        """Return whether this controller can truthfully roll back an action."""

        if action == "register_plugin":
            plugin_manager = self._resolve_plugin_manager()
            return bool(plugin_manager and hasattr(plugin_manager, "unload_plugin"))
        if action == "register_agent":
            agent_orchestrator = self._resolve_agent_orchestrator()
            return bool(
                agent_orchestrator
                and self._find_agent_unregister(agent_orchestrator) is not None
            )
        return False

    def register_rollback_token(
        self,
        rollback_token: str,
        action: str,
        result: dict[str, Any],
        target: dict[str, Any] | None = None,
        rollback_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Register rollback metadata for a completed HMR-backed action."""

        token = str(rollback_token or "").strip()
        action_name = str(action or "").strip()
        if not token.startswith("rb_"):
            return {"ok": False, "error": "invalid_rollback_token"}

        if action_name == "register_plugin":
            plugin_manager = None
            if isinstance(rollback_context, dict):
                plugin_manager = rollback_context.get("plugin_manager")
            if plugin_manager is None:
                plugin_manager = self._resolve_plugin_manager()
            if not plugin_manager or not hasattr(plugin_manager, "unload_plugin"):
                return {
                    "ok": False,
                    "error": "rollback_action_unsupported",
                    "action": action_name,
                }
            plugin_name = str((result or {}).get("name") or "").strip()
            if not plugin_name:
                return {
                    "ok": False,
                    "error": "rollback_target_missing",
                    "action": action_name,
                }
            self._rollback_tokens[token] = {
                "action": action_name,
                "plugin_name": plugin_name,
                "plugin_manager": plugin_manager,
                "registered_at": time.time(),
                "target_hash": hashlib.sha256(
                    json.dumps(target or {}, sort_keys=True, default=str).encode(
                        "utf-8"
                    )
                ).hexdigest()[:16],
            }
            self._audit(
                "rollback_token_registered",
                action_name,
                "self_incorporation",
                ok=True,
                extra={"rollback_token_hash": self._token_hash(token)},
            )
            return {"ok": True, "action": action_name}

        if action_name == "register_agent":
            agent_orchestrator = None
            if isinstance(rollback_context, dict):
                agent_orchestrator = rollback_context.get("agent_orchestrator")
            if agent_orchestrator is None:
                agent_orchestrator = self._resolve_agent_orchestrator()
            if (
                not agent_orchestrator
                or self._find_agent_unregister(agent_orchestrator) is None
            ):
                return {
                    "ok": False,
                    "error": "rollback_action_unsupported",
                    "action": action_name,
                }
            agent_id = str((result or {}).get("id") or "").strip()
            if not agent_id:
                return {
                    "ok": False,
                    "error": "rollback_target_missing",
                    "action": action_name,
                }
            self._rollback_tokens[token] = {
                "action": action_name,
                "agent_id": agent_id,
                "agent_orchestrator": agent_orchestrator,
                "registered_at": time.time(),
                "target_hash": hashlib.sha256(
                    json.dumps(target or {}, sort_keys=True, default=str).encode(
                        "utf-8"
                    )
                ).hexdigest()[:16],
            }
            self._audit(
                "rollback_token_registered",
                action_name,
                "self_incorporation",
                ok=True,
                extra={"rollback_token_hash": self._token_hash(token)},
            )
            return {"ok": True, "action": action_name}

        return {"ok": False, "error": "rollback_action_unsupported"}

    async def rollback_token(self, rollback_token: str) -> dict[str, Any]:
        """Roll back a previously registered token-bound HMR action."""

        token = str(rollback_token or "").strip()
        token_hash = self._token_hash(token)
        record = self._rollback_tokens.get(token)
        if not record:
            self._audit(
                "rollback_token_missing",
                "unknown",
                "self_incorporation",
                ok=False,
                reason="rollback_token_not_found",
                extra={"rollback_token_hash": token_hash},
            )
            return {"ok": False, "error": "rollback_token_not_found"}

        action = str(record.get("action") or "")
        if action == "register_plugin":
            plugin_name = str(record.get("plugin_name") or "")
            rollback_result = await self._rollback_registered_plugin_with_manager(
                plugin_name,
                record.get("plugin_manager"),
            )
            if rollback_result.get("ok"):
                self._rollback_tokens.pop(token, None)
                with suppress(Exception):
                    if hasattr(self.kernel, "record_hmr_rollback"):
                        self.kernel.record_hmr_rollback("register_plugin")
            self._audit(
                "rollback_token_consumed",
                action,
                "self_incorporation",
                ok=bool(rollback_result.get("ok")),
                reason=rollback_result.get("error"),
                extra={
                    "rollback_token_hash": token_hash,
                    "plugin_name_hash": hashlib.sha256(
                        plugin_name.encode("utf-8")
                    ).hexdigest()[:16],
                },
            )
            return {**rollback_result, "action": action}

        if action == "register_agent":
            agent_id = str(record.get("agent_id") or "")
            rollback_result = await self._rollback_registered_agent_with_orchestrator(
                agent_id,
                record.get("agent_orchestrator"),
            )
            if rollback_result.get("ok"):
                self._rollback_tokens.pop(token, None)
                with suppress(Exception):
                    if hasattr(self.kernel, "record_hmr_rollback"):
                        self.kernel.record_hmr_rollback("register_agent")
            self._audit(
                "rollback_token_consumed",
                action,
                "self_incorporation",
                ok=bool(rollback_result.get("ok")),
                reason=rollback_result.get("error"),
                extra={
                    "rollback_token_hash": token_hash,
                    "agent_id_hash": hashlib.sha256(agent_id.encode("utf-8")).hexdigest()[
                        :16
                    ],
                },
            )
            return {**rollback_result, "action": action}

        return {
            "ok": False,
            "error": "rollback_action_unsupported",
            "action": action or "unknown",
        }

    async def rollback_by_token(self, rollback_token: str) -> dict[str, Any]:
        """Compatibility alias for token-bound rollback."""

        return await self.rollback_token(rollback_token)

    async def rollback_integration(self, rollback_token: str) -> dict[str, Any]:
        """Compatibility alias for token-bound rollback."""

        return await self.rollback_token(rollback_token)

    def _guardian_preflight(
        self,
        *,
        requester: str,
        target: str,
        source: str,
        mode: str,
        approval_id: str | None,
    ) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="hmr_controller",
                action="hmr.reload",
                target=f"hmr_controller:{target}",
                purpose=f"Hot reload runtime target {target}",
                capabilities=("system:reload",),
                expected_outcome="Replace the runtime target with a validated shadow instance",
                reversible=True,
                rollback_plan="restore the previous runtime instance through kernel rollback_swap",
                evidence=(f"hmr_target:{target}",),
                metadata={
                    "target": target,
                    "mode": mode,
                    **self._guardian_source_metadata(source),
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied HMR reload for {target}: {decision.reason}"
            )

    # ---------------- Core flow ----------------
    async def _reload_target(
        self,
        target: str,
        source: str,
        mode: str = "safe",
        requester: str = "hmr_controller",
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        """Prepare → Verify → Quiesce → Swap → Resume | Rollback"""
        start = time.time()
        self.state = {
            "status": "pending",
            "target": target,
            "source": source,
            "mode": mode,
        }

        # Strict gating: ensure source is allowed when configured
        if self.allowed_sources and source not in self.allowed_sources and not any(
            source.startswith(p.rstrip("/*")) for p in self.allowed_sources
        ):
            self._audit("gated", target, source, ok=False, reason="source_not_allowed")
            return {"ok": False, "error": "source_not_allowed"}

        self._guardian_preflight(
            requester=requester,
            target=target,
            source=source,
            mode=mode,
            approval_id=approval_id,
        )

        # Metrics attempt
        try:
            if hasattr(self.kernel, "record_hmr_attempt"):
                self.kernel.record_hmr_attempt(str(target))
        except Exception as exc:
            logger.debug("[HMR] attempt metric failed for %s: %s", target, exc)

        try:
            # Prepare: load shadow under a fresh module namespace
            shadow = await self._load_shadow(target, source)
            if shadow is None:
                self._audit("load_failed", target, source, ok=False)
                return {"ok": False, "error": "load_failed"}

            # Verify: light health probe on shadow instance
            if not await self._health_probe(target, shadow):
                self._audit("probe_failed", target, source, ok=False)
                return {"ok": False, "error": "probe_failed"}

            # Notify prepare
            await self._broadcast("HMR_PREPARE", {"target": target})

            # Quiesce affected work
            drained = await self._quiesce(target, timeout_sec=30)
            if not drained and mode != "force":
                self._audit("quiesce_timeout", target, source, ok=False)
                return {"ok": False, "error": "quiesce_timeout"}

            # State hand-off (optional)
            old = self._resolve_current_target(target)
            exported = {}
            if old and hasattr(old, "export_state"):
                try:
                    if asyncio.iscoroutinefunction(old.export_state):
                        exported = await old.export_state()
                    else:
                        exported = old.export_state()
                except Exception:
                    logger.warning(
                        "[HMR] export_state failed; continuing without state"
                    )
                    exported = {}

            if exported and hasattr(shadow, "import_state"):
                try:
                    if asyncio.iscoroutinefunction(shadow.import_state):
                        await shadow.import_state(exported)
                    else:
                        shadow.import_state(exported)
                except Exception:
                    if self.strict:
                        return {"ok": False, "error": "state_import_failed"}
                    logger.warning("[HMR] import_state failed; continuing (non-strict)")

            # Swap
            swapped = await self._swap(target, shadow)
            await self._broadcast("HMR_SWAP", {"target": target, "ok": swapped})

            # Post-swap health and resume or rollback
            healthy = swapped and await self._post_swap_health(target)
            if not healthy:
                await self._rollback(target, old)
                await self._broadcast("HMR_ROLLBACK", {"target": target})
                try:
                    if hasattr(self.kernel, "record_hmr_rollback"):
                        self.kernel.record_hmr_rollback(str(target))
                except Exception as exc:
                    logger.debug("[HMR] rollback metric failed for %s: %s", target, exc)
                self._audit("post_swap_failed", target, source, ok=False)
                return {"ok": False, "error": "post_swap_failed"}

            # Resume
            try:
                if hasattr(self.kernel, "resume_target"):
                    self.kernel.resume_target(str(target))
            except Exception as exc:
                logger.debug("[HMR] resume failed for %s: %s", target, exc)

            swap_ms = int((time.time() - start) * 1000)
            try:
                if hasattr(self.kernel, "record_hmr_success"):
                    self.kernel.record_hmr_success(str(target), swap_ms)
            except Exception as exc:
                logger.debug("[HMR] success metric failed for %s: %s", target, exc)

            self.state = {"status": "swapped", "target": target, "swap_ms": swap_ms}
            self._audit("swapped", target, source, ok=True, extra={"swap_ms": swap_ms})
            return {"ok": True, "swap_ms": swap_ms}

        finally:
            # attempts already recorded at start; nothing to do here
            pass

    # ---------------- Helpers ----------------
    async def _load_shadow(self, target: str, source: str):
        """Load a shadow instance from module path or file path."""
        try:
            mod = None
            if isinstance(source, str) and source.endswith(".py"):
                spec = importlib.util.spec_from_file_location(
                    f"hmr_shadow_{int(time.time())}", source
                )
                if not spec or not spec.loader:
                    return None
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            else:
                mod = importlib.import_module(str(source))

            # Resolve a candidate instance
            if hasattr(mod, "build"):
                candidate = mod.build()  # type: ignore[attr-defined]
            elif hasattr(mod, "create"):
                candidate = mod.create()  # type: ignore[attr-defined]
            else:
                # Common aliases by convention
                candidate = (
                    getattr(mod, "EngineAdapter", None)
                    or getattr(mod, "AetherraEngine", None)
                    or getattr(mod, "Adapter", None)
                )

            return candidate
        except Exception as e:
            logger.error(f"[HMR] Failed loading shadow from {source}: {e}")
            return None

    async def _health_probe(self, target: str, instance: Any) -> bool:
        """Run a light probe on the shadow instance."""
        try:
            if hasattr(instance, "get_status"):
                status = instance.get_status()
                if asyncio.iscoroutine(status):
                    status = await status
                return bool(status)
            return True
        except Exception as e:
            logger.warning(f"[HMR] Probe failed for {target}: {e}")
            return False

    async def _quiesce(self, target: str, timeout_sec: int = 30) -> bool:
        try:
            if hasattr(self.kernel, "quiesce_for_target"):
                return await self.kernel.quiesce_for_target(str(target), timeout_sec)
        except Exception as exc:
            logger.debug("[HMR] quiesce failed for %s: %s", target, exc)
        # fallback: brief sleep as best-effort
        await asyncio.sleep(0.2)
        return True

    async def _swap(self, target: str, new_instance: Any) -> bool:
        try:
            if hasattr(self.kernel, "swap_system"):
                return await self.kernel.swap_system(str(target), new_instance)
        except Exception:
            return False
        return False

    async def _rollback(self, target: str, old_instance: Any):
        try:
            if hasattr(self.kernel, "rollback_swap"):
                await self.kernel.rollback_swap(str(target), old_instance)
        except Exception as exc:
            logger.debug("[HMR] rollback failed for %s: %s", target, exc)

    async def _post_swap_health(self, target: str) -> bool:
        try:
            # Kernel get_status is synchronous in current codebase
            if hasattr(self.kernel, "get_status"):
                status = self.kernel.get_status()
                return bool(status)
        except Exception as exc:
            logger.debug("[HMR] post-swap health failed for %s: %s", target, exc)
        return True

    def _resolve_current_target(self, target: str) -> Any | None:
        if target in ("engine", "aetherra_engine"):
            return getattr(self.kernel, "aetherra_engine", None)
        if target in ("adapter:memory", "memory"):
            return getattr(self.kernel, "memory_system", None)
        if target in ("adapter:plugin", "plugin_manager"):
            return getattr(self.kernel, "plugin_manager", None)
        if target in ("adapter:lyrixa_chat", "lyrixa_chat"):
            return getattr(self.kernel, "lyrixa_chat", None)
        return None

    def _resolve_plugin_manager(self) -> Any | None:
        plugin_manager = getattr(self.kernel, "plugin_manager", None)
        if plugin_manager is not None:
            return plugin_manager
        try:
            if hasattr(self.registry, "get_service"):
                return self.registry.get_service("plugin_manager")
        except Exception:
            return None
        return None

    def _resolve_agent_orchestrator(self) -> Any | None:
        agent_orchestrator = getattr(self.kernel, "agent_orchestrator", None)
        if agent_orchestrator is not None:
            return agent_orchestrator
        try:
            if hasattr(self.registry, "get_service"):
                return self.registry.get_service("agent_orchestrator")
        except Exception:
            return None
        return None

    def _find_agent_unregister(self, agent_orchestrator: Any) -> Any | None:
        for attr in ("unregister_agent", "remove_agent", "deregister_agent"):
            unregister = getattr(agent_orchestrator, attr, None)
            if callable(unregister):
                return unregister
        return None

    async def _rollback_registered_plugin(self, plugin_name: str) -> dict[str, Any]:
        return await self._rollback_registered_plugin_with_manager(plugin_name, None)

    async def _rollback_registered_plugin_with_manager(
        self,
        plugin_name: str,
        plugin_manager: Any | None,
    ) -> dict[str, Any]:
        if not plugin_name:
            return {"ok": False, "error": "rollback_target_missing"}
        plugin_manager = plugin_manager or self._resolve_plugin_manager()
        if not plugin_manager or not hasattr(plugin_manager, "unload_plugin"):
            return {"ok": False, "error": "plugin_manager_unavailable"}

        unload = plugin_manager.unload_plugin
        result = unload(plugin_name)
        if asyncio.iscoroutine(result):
            result = await result
        return {
            "ok": bool(result),
            "plugin_name_hash": hashlib.sha256(plugin_name.encode("utf-8")).hexdigest()[
                :16
            ],
        }

    async def _rollback_registered_agent_with_orchestrator(
        self,
        agent_id: str,
        agent_orchestrator: Any | None,
    ) -> dict[str, Any]:
        if not agent_id:
            return {"ok": False, "error": "rollback_target_missing"}
        agent_orchestrator = agent_orchestrator or self._resolve_agent_orchestrator()
        if not agent_orchestrator:
            return {"ok": False, "error": "agent_orchestrator_unavailable"}

        unregister = self._find_agent_unregister(agent_orchestrator)
        if not unregister:
            return {"ok": False, "error": "agent_unregister_unavailable"}

        result = unregister(agent_id)
        if asyncio.iscoroutine(result):
            result = await result
        return {
            "ok": bool(result),
            "agent_id_hash": hashlib.sha256(agent_id.encode("utf-8")).hexdigest()[:16],
        }

    async def _broadcast(self, message_type: str, data: dict[str, Any]):
        try:
            if hasattr(self.registry, "broadcast_message"):
                await self.registry.broadcast_message(message_type, data)
        except Exception as exc:
            logger.debug("[HMR] broadcast failed for %s: %s", message_type, exc)

    def _audit(
        self,
        event: str,
        target: str,
        source: str,
        ok: bool,
        reason: str | None = None,
        extra: dict[str, Any] | None = None,
    ):
        try:
            record = {
                "ts": time.time(),
                "event": event,
                "target": target,
                "source": source,
                "ok": ok,
            }
            if reason:
                record["reason"] = reason
            if extra:
                record.update(extra)
            path = self.audit_path
            # best-effort write
            _dir = os.path.dirname(path)
            if _dir:
                os.makedirs(_dir, exist_ok=True)
            # rotate if file too large before appending
            self._maybe_rotate_audit(path)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            # increment in-memory counters
            with suppress(Exception):
                self.audit_counters[event] = int(self.audit_counters.get(event, 0)) + 1
        except Exception as exc:
            logger.debug("[HMR] audit write failed for %s: %s", event, exc)

    def get_audit_counters(self) -> dict[str, int]:
        try:
            return dict(self.audit_counters)
        except Exception:
            return {}

    def get_config_metrics(self) -> dict[str, Any]:
        """Return a small set of HMR config metrics for observability surfaces.

        Keys:
          - enabled: bool (controller running)
          - strict: bool
          - allowed_sources_count: int
          - audit_max_bytes: int
          - audit_max_backups: int
        """
        try:
            return {
                "enabled": bool(self.running),
                "strict": bool(self.strict),
                "allowed_sources_count": int(len(self.allowed_sources or [])),
                "audit_max_bytes": int(self.audit_max_bytes or 0),
                "audit_max_backups": int(self.audit_max_backups or 0),
            }
        except Exception:
            return {
                "enabled": False,
                "strict": bool(self.strict),
                "allowed_sources_count": 0,
                "audit_max_bytes": 0,
                "audit_max_backups": 0,
            }

    # ---------------- Internal: audit rotation ----------------
    def _maybe_rotate_audit(self, path: str):
        """If the audit file exceeds the configured size, rotate it.

        Rotation scheme:
          - Rename current file to `<path>.<YYYYMMDD-HHMMSS>`
          - Keep up to `self.audit_max_backups` files (delete oldest beyond limit)
        Best-effort, silent on errors.
        """
        try:
            if self.audit_max_bytes is None or self.audit_max_bytes <= 0:
                return
            if not os.path.exists(path):
                return
            try:
                size = os.path.getsize(path)
            except Exception:
                size = 0
            if size < self.audit_max_bytes:
                return
            # Perform rotation
            ts = time.strftime("%Y%m%d-%H%M%S", time.localtime())
            rotated = f"{path}.{ts}"
            try:
                shutil.move(path, rotated)
            except Exception:
                # If move fails, attempt to copy+truncate
                try:
                    with open(path, "rb") as src, open(rotated, "wb") as dst:
                        dst.write(src.read())
                    # truncate original
                    open(path, "w").close()
                except Exception:
                    return
            # Enforce max backups
            try:
                base = os.path.basename(path)
                dirn = os.path.dirname(path) or "."
                candidates = []
                for name in os.listdir(dirn):
                    if name.startswith(base + "."):
                        full = os.path.join(dirn, name)
                        try:
                            mtime = os.path.getmtime(full)
                        except Exception:
                            mtime = 0
                        candidates.append((mtime, full))
                # Sort oldest first
                candidates.sort()
                # Keep newest self.audit_max_backups, delete the rest
                excess = max(0, len(candidates) - max(0, int(self.audit_max_backups)))
                for i in range(excess):
                    with suppress(Exception):
                        os.remove(candidates[i][1])
            except Exception as exc:
                logger.debug("[HMR] audit backup pruning failed for %s: %s", path, exc)
        except Exception as exc:
            logger.debug("[HMR] audit rotation failed for %s: %s", path, exc)


async def get_hmr_controller(registry, kernel, strict: bool = False) -> HMRController:
    ctrl = HMRController(registry, kernel, strict=strict)
    await ctrl.start()
    return ctrl
