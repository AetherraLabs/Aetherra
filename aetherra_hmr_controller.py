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

import asyncio
import importlib
import importlib.util
import logging
import os
import time
from typing import Any, Dict, Optional

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
        self.state: Dict[str, Any] = {"status": "idle"}
        # Allowed sources (module names or approved paths). Comma-separated env, optional.
        self.allowed_sources = set(
            s.strip()
            for s in os.getenv("AETHERRA_HMR_ALLOWED_SOURCES", "").split(",")
            if s.strip()
        )
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
        self.audit_counters: Dict[str, int] = {}

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
    async def handle_kernel_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        t = (payload or {}).get("type")
        data = (payload or {}).get("data") or {}
        if t == "hmr_reload":
            target = data.get("target")
            source = data.get("source")
            if not target or not source:
                return {"ok": False, "error": "missing_target_or_source"}
            mode = data.get("mode", "safe")
            return await self._reload_target(str(target), str(source), mode=str(mode))
        if t == "hmr_status":
            return {"ok": True, "state": self.state}
        return {"ok": False, "error": "unsupported_hmr_task"}

    # ---------------- Core flow ----------------
    async def _reload_target(
        self, target: str, source: str, mode: str = "safe"
    ) -> Dict[str, Any]:
        """Prepare → Verify → Quiesce → Swap → Resume | Rollback"""
        start = time.time()
        self.state = {
            "status": "pending",
            "target": target,
            "source": source,
            "mode": mode,
        }

        # Strict gating: ensure source is allowed when configured
        if self.allowed_sources:
            if source not in self.allowed_sources and not any(
                source.startswith(p.rstrip("/*")) for p in self.allowed_sources
            ):
                self._audit(
                    "gated", target, source, ok=False, reason="source_not_allowed"
                )
                return {"ok": False, "error": "source_not_allowed"}

        # Metrics attempt
        try:
            if hasattr(self.kernel, "record_hmr_attempt"):
                self.kernel.record_hmr_attempt(str(target))
        except Exception:
            pass

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
                except Exception:
                    pass
                self._audit("post_swap_failed", target, source, ok=False)
                return {"ok": False, "error": "post_swap_failed"}

            # Resume
            try:
                if hasattr(self.kernel, "resume_target"):
                    self.kernel.resume_target(str(target))
            except Exception:
                pass

            swap_ms = int((time.time() - start) * 1000)
            try:
                if hasattr(self.kernel, "record_hmr_success"):
                    self.kernel.record_hmr_success(str(target), swap_ms)
            except Exception:
                pass

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
        except Exception:
            pass
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
        except Exception:
            pass

    async def _post_swap_health(self, target: str) -> bool:
        try:
            # Kernel get_status is synchronous in current codebase
            if hasattr(self.kernel, "get_status"):
                status = self.kernel.get_status()
                return bool(status)
        except Exception:
            pass
        return True

    def _resolve_current_target(self, target: str) -> Optional[Any]:
        if target in ("engine", "aetherra_engine"):
            return getattr(self.kernel, "aetherra_engine", None)
        if target in ("adapter:memory", "memory"):
            return getattr(self.kernel, "memory_system", None)
        if target in ("adapter:plugin", "plugin_manager"):
            return getattr(self.kernel, "plugin_manager", None)
        if target in ("adapter:lyrixa_chat", "lyrixa_chat"):
            return getattr(self.kernel, "lyrixa_chat", None)
        return None

    async def _broadcast(self, message_type: str, data: Dict[str, Any]):
        try:
            if hasattr(self.registry, "broadcast_message"):
                await self.registry.broadcast_message(message_type, data)
        except Exception:
            pass

    def _audit(
        self,
        event: str,
        target: str,
        source: str,
        ok: bool,
        reason: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
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
                import json

                f.write(json.dumps(record) + "\n")
            # increment in-memory counters
            try:
                self.audit_counters[event] = int(self.audit_counters.get(event, 0)) + 1
            except Exception:
                pass
        except Exception:
            pass

    def get_audit_counters(self) -> Dict[str, int]:
        try:
            return dict(self.audit_counters)
        except Exception:
            return {}

    def get_config_metrics(self) -> Dict[str, Any]:
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
                import shutil

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
                    try:
                        os.remove(candidates[i][1])
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass


async def get_hmr_controller(registry, kernel, strict: bool = False) -> HMRController:
    ctrl = HMRController(registry, kernel, strict=strict)
    await ctrl.start()
    return ctrl
