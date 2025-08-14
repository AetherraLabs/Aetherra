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

import logging
import os
import re
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
            return {"success": True, "result": {"results": results}}
        except Exception as e:
            logger.error(f"[AETHER] Execute failed: {e}")
            return {"success": False, "error": str(e), "file": filename}

    async def _execute_script_content(
        self, script_content: str, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        ctx: Dict[str, Any] = dict(context or {})
        results: List[Dict[str, Any]] = []
        for line_num, raw in enumerate(script_content.splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            out = await self._execute_statement(line, ctx, line_num)
            if out is not None:
                results.append(out)
        return results

    async def _execute_statement(
        self, statement: str, context: Dict, line_num: int
    ) -> Any:
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


# Service factory function
async def get_aether_script_service(service_registry=None):
    """Factory function to create and initialize the Aether Script service."""
    service = AetherScriptService(service_registry)
    await service.initialize()
    return service
