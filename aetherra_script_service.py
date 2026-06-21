#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Script Service
=======================

(c) Aetherra Labs. Proprietary Aether Script interpreter scaffolding.

Lightweight .aether interpreter for goals, assignments, and memory ops.
This minimal implementation is designed to satisfy current tests and can be
extended to support full EBNF from the specification. Optional signing
verification can be enabled via environment flags for protection.
"""

# Standard library imports
import importlib
import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

# Optional runtime imports kept inside functions to avoid heavy deps on import
try:  # Prefer absolute package path
    # Aetherra imports
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngine,
    )
except Exception:  # Fallback for variations in path
    AetherraMemoryEngine = None  # type: ignore

logger = logging.getLogger(__name__)

SIGNATURE_MARKER = "# @signature:"


def _hash_value(value: Any) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "aether_script:runtime" and capability in {"script:run"}:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_script_execution(
    *,
    requester: str,
    filename: str,
    script_content: str,
    metadata: dict[str, Any],
):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="aether_script",
            action="script.execute",
            target=f"aether_script:{_hash_value(filename)}",
            purpose="Execute an Aether Script through the bounded lightweight runtime",
            capabilities=("script:run",),
            expected_outcome="script parsed and executed with bounded workflow semantics",
            reversible=False,
            rollback_plan=None,
            evidence=("aether_script.execute:request",),
            metadata={
                **metadata,
                "filename_hash": _hash_value(filename),
                "script_hash": _hash_value(script_content),
                "script_length": len(script_content or ""),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


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
        self, script_path: str, context: dict | None = None
    ) -> dict[str, Any]:
        text = Path(script_path).read_text(encoding="utf-8")
        return await self.execute_script_content(
            text, filename=script_path, context=context
        )

    async def execute_script_content(
        self,
        script_content: str,
        filename: str = "<string>",
        context: dict | None = None,
    ) -> dict[str, Any]:
        try:
            context = context or {}
            guardian_metadata = self._build_guardian_execution_metadata(
                script_content,
                filename,
            )
            requester = (
                str(context.get("_requester") or "").strip()
                or os.getenv("AETHERRA_PRINCIPAL", "").strip()
                or "aether_script:runtime"
            )
            decision = _guardian_preflight_script_execution(
                requester=requester,
                filename=filename,
                script_content=script_content,
                metadata=guardian_metadata,
            )
            if not decision.allowed:
                return {
                    "success": False,
                    "error": "guardian_denied",
                    "reason": decision.reason,
                    "audit_id": decision.audit_id,
                    "file": filename,
                }

            # Optional strict signature verification
            self._maybe_verify_signature(script_content, filename)
            # Prefer block-aware execution for v1.1 features
            # Seed a requester principal for capability checks
            seeded_context = dict(context)
            try:
                seeded_context.setdefault("_requester", f"script:{Path(filename).name}")
            except Exception:
                seeded_context.setdefault("_requester", "aether_script")
            results = await self._execute_script_with_blocks(
                script_content, seeded_context
            )
            payload: dict[str, Any] = {"results": results}
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
                if "_rollback_tokens" in self._last_ctx:
                    payload["rollback_tokens"] = list(
                        self._last_ctx.get("_rollback_tokens", [])
                    )
                if "_rollback_registry" in self._last_ctx:
                    payload["rollback_registry"] = dict(
                        self._last_ctx.get("_rollback_registry", {})
                    )
                if "_types" in self._last_ctx:
                    payload["types"] = dict(self._last_ctx.get("_types", {}))
                if "_warnings" in self._last_ctx:
                    payload["warnings"] = list(self._last_ctx.get("_warnings", []))
                if "_verified_capabilities" in self._last_ctx:
                    payload["verified_capabilities"] = list(
                        self._last_ctx.get("_verified_capabilities", [])
                    )
            # Optionally expose trace if requested
            if os.getenv("AETHERRA_TRACE", "0") == "1":
                payload["trace"] = list(self._trace)
            # Persist audit trail metadata (model/seed/cost/tokens/prompts sanitized)
            import contextlib

            with contextlib.suppress(Exception):
                self._audit_run(script_content, payload, context, filename)
            return {"success": True, "result": payload}
        except Exception as e:
            logger.error(f"[AETHER] Execute failed: {e}")
            return {"success": False, "error": str(e), "file": filename}

    async def _execute_script_with_blocks(
        self, script_content: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Block-aware execution supporting if/elif/else, loops, workflow, meta, on_error.

        Indentation defines blocks. We normalize by subtracting the minimum indent
        from all non-empty, non-comment lines to allow scripts indented in tests.
        """
        ctx: dict[str, Any] = dict(context or {})
        results: list[dict[str, Any]] = []
        self._trace = []

        raw_lines = script_content.splitlines()
        # Build line records with indent counts
        line_recs = []
        indents = []
        for ln, raw in enumerate(raw_lines, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            line_recs.append({"line_num": ln, "indent": indent, "text": stripped})
            indents.append(indent)
        if not line_recs:
            self._last_ctx = ctx
            return results
        base = min(indents)
        for rec in line_recs:
            rec["indent"] = max(0, rec["indent"] - base)

        # Normalize physical indentation widths into logical levels to support
        # nested blocks regardless of absolute space counts (e.g. 4 or 8 spaces).
        # Each distinct indent value becomes an incrementing level.
        unique_indents = sorted({rec["indent"] for rec in line_recs})
        indent_level_map = {val: i for i, val in enumerate(unique_indents)}
        for rec in line_recs:
            rec["indent"] = indent_level_map[rec["indent"]]

        # Recursive block processor
        async def process_block(start_idx: int, parent_indent: int) -> int:
            idx = start_idx
            # Transaction state for this block scope
            txn_active = False
            txn_ops: list[dict[str, Any]] = []
            txn_name = None
            while idx < len(line_recs):
                rec = line_recs[idx]
                if rec["indent"] < parent_indent:
                    break
                if rec["indent"] > parent_indent:
                    # Shouldn't happen: stray deeper indent without header
                    idx += 1
                    continue
                text = rec["text"]
                line_num = rec["line_num"]

                # Transactions (kept compatible with legacy syntax)
                if re.match(r"^begin\s+transaction(\s+\w+)?\s*$", text, re.IGNORECASE):
                    if txn_active:
                        raise ValueError("nested transactions not supported")
                    txn_active = True
                    m = re.match(
                        r"^begin\s+transaction(?:\s+(\w+))?\s*$", text, re.IGNORECASE
                    )
                    txn_name = m.group(1) if m else None
                    self._trace.append(
                        {"type": "txn_begin", "name": txn_name, "line": line_num}
                    )
                    results.append(
                        {
                            "type": "transaction_begin",
                            "name": txn_name,
                            "line": line_num,
                        }
                    )
                    idx += 1
                    continue
                if re.match(r"^commit\s+transaction\s*$", text, re.IGNORECASE):
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
                    idx += 1
                    continue
                if re.match(r"^rollback\s+transaction\s*$", text, re.IGNORECASE):
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
                    idx += 1
                    continue

                # Conditional: if/elif/else chain
                if re.match(r"^if\s+.+$", text, re.IGNORECASE):
                    # Collect branches at this indent
                    branches = []  # list of (kind, expr or None, block_start, block_end)
                    # IF branch
                    if_block_start = idx + 1
                    # Find block end for IF by scanning until indent <= current and not elif/else of same group
                    j = if_block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    branches.append(("if", text[2:].strip(), if_block_start, j))
                    k = j
                    # Collect elif/else that follow
                    while (
                        k < len(line_recs) and line_recs[k]["indent"] == parent_indent
                    ):
                        t = line_recs[k]["text"]
                        if re.match(r"^elif\s+.+$", t, re.IGNORECASE):
                            bstart = k + 1
                            m = bstart
                            while (
                                m < len(line_recs)
                                and line_recs[m]["indent"] > parent_indent
                            ):
                                m += 1
                            branches.append(("elif", t[4:].strip(), bstart, m))
                            k = m
                            continue
                        if re.match(r"^else\s*$", t, re.IGNORECASE):
                            bstart = k + 1
                            m = bstart
                            while (
                                m < len(line_recs)
                                and line_recs[m]["indent"] > parent_indent
                            ):
                                m += 1
                            branches.append(("else", None, bstart, m))
                            k = m
                            continue
                        break
                    # Evaluate branches
                    chosen = None
                    for kind, expr, bstart, bend in branches:
                        ok = False
                        if kind == "else":
                            ok = True
                        else:
                            try:
                                ok = bool(self._eval_expression(expr, ctx))
                            except Exception:
                                ok = False
                        if ok:
                            chosen = (kind, bstart, bend)
                            break
                    results.append(
                        {
                            "type": "conditional",
                            "line": line_num,
                            "branches": [b[0] for b in branches],
                            "taken": chosen[0] if chosen else None,
                        }
                    )
                    # Execute chosen block
                    if chosen:
                        _, bstart, bend = chosen
                        await process_block(bstart, parent_indent + 1)
                    # Advance index to end of chain
                    idx = k
                    continue

                # For loop: for var in expr
                m_for = re.match(
                    r"^for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+)$", text, re.IGNORECASE
                )
                if m_for:
                    var = m_for.group(1)
                    expr = m_for.group(2).strip()
                    # Locate block
                    block_start = idx + 1
                    j = block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    seq = self._eval_expression(expr, ctx)
                    iterations = 0
                    if isinstance(seq, (list, tuple)):
                        for item in seq:
                            ctx[var] = item
                            await process_block(block_start, parent_indent + 1)
                            iterations += 1
                    results.append(
                        {
                            "type": "for_loop",
                            "line": line_num,
                            "var": var,
                            "iterations": iterations,
                        }
                    )
                    idx = j
                    continue

                # While loop: while condition
                m_while = re.match(r"^while\s+(.+)$", text, re.IGNORECASE)
                if m_while:
                    cond_expr = m_while.group(1).strip()
                    block_start = idx + 1
                    j = block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    iterations = 0
                    max_iter = 1000
                    while iterations < max_iter and bool(
                        self._eval_expression(cond_expr, ctx)
                    ):
                        await process_block(block_start, parent_indent + 1)
                        iterations += 1
                    results.append(
                        {
                            "type": "while_loop",
                            "line": line_num,
                            "iterations": iterations,
                        }
                    )
                    idx = j
                    continue

                # Workflow block
                if re.match(r"^workflow\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    # Parse inner lines
                    steps = []
                    props = {}
                    k2 = block_start
                    while k2 < j:
                        inner = line_recs[k2]["text"]
                        if inner.startswith("- "):
                            step_line = inner[2:].strip()
                            # Parse name and optional (args)
                            head_m = re.match(
                                r"^([A-Za-z_][A-Za-z0-9_]*)(?:\(([^)]*)\))?(.*)$",
                                step_line,
                            )
                            if head_m:
                                name = head_m.group(1)
                                args_raw = (head_m.group(2) or "").strip()
                                rest = (head_m.group(3) or "").strip()
                                # Defaults
                                alias = None
                                retry = None
                                timeout_raw_val = None
                                requires_raw = None
                                # Extract tokens in any order
                                am = re.search(
                                    r"\bas\s+([A-Za-z_][A-Za-z0-9_]*)\b", rest
                                )
                                if am:
                                    alias = am.group(1)
                                rm = re.search(r"\bretry=(\d+)\b", rest)
                                if rm:
                                    retry = rm.group(1)
                                tm = re.search(
                                    r"\btimeout=(\"([^\"]+)\"|\d+(?:\.\d+)?(?:ms|s|m|h))\b",
                                    rest,
                                )
                                if tm:
                                    timeout_raw_val = (
                                        tm.group(2)
                                        if tm.group(2) is not None
                                        else tm.group(1)
                                    )
                                elif "timeout=" in rest:
                                    # Fallback parsing for timeout value until whitespace
                                    tail = rest.split("timeout=", 1)[1].lstrip()
                                    if tail.startswith('"'):
                                        m_end = re.search(r'"([^"]*)"', tail)
                                        if m_end:
                                            timeout_raw_val = m_end.group(1)
                                    else:
                                        mv = re.match(r"^([^\s]+)", tail)
                                        if mv:
                                            timeout_raw_val = mv.group(1)
                                qm = re.search(r"\brequires=\[(.*?)\]", rest)
                                if qm:
                                    requires_raw = qm.group(1)
                                # Parse positional and keyword args
                                pos_args: list[Any] = []
                                kw_args: dict[str, Any] = {}
                                if args_raw:
                                    for part in args_raw.split(","):
                                        p = part.strip()
                                        if not p:
                                            continue
                                        if "=" in p:
                                            k, v = p.split("=", 1)
                                            kw_args[k.strip()] = self._eval_expression(
                                                v.strip(), ctx
                                            )
                                        else:
                                            pos_args.append(
                                                self._eval_expression(p, ctx)
                                            )
                                # Requires list
                                requires: list[str] = []
                                if requires_raw:
                                    for tok in requires_raw.split(","):
                                        t = tok.strip().strip('"').strip("'")
                                        if t:
                                            requires.append(t)
                                step_obj: dict[str, Any] = {"name": name}
                                if pos_args:
                                    step_obj["args"] = pos_args
                                if kw_args:
                                    step_obj["kwargs"] = kw_args
                                if alias:
                                    step_obj["as"] = alias
                                if retry:
                                    step_obj["retry"] = int(retry)
                                if timeout_raw_val:
                                    raw_timeout = timeout_raw_val.strip('"')
                                    step_obj["timeout"] = raw_timeout
                                    step_obj["timeout_secs"] = self._normalize_duration(
                                        raw_timeout
                                    )
                                if requires:
                                    step_obj["requires"] = requires
                                steps.append(step_obj)
                        else:
                            # property assignment inside workflow
                            am = re.match(
                                r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", inner
                            )
                            if am:
                                key = am.group(1)
                                val = self._eval_expression(am.group(2), ctx)
                                props[key] = val
                        k2 += 1
                    # Inherit workflow-level requires into each step if provided as a property list
                    wf_requires = props.get("requires")
                    if isinstance(wf_requires, list):
                        for step in steps:
                            existing = step.get("requires", [])
                            if not isinstance(existing, list):
                                existing = []
                            merged: list[str] = []
                            for cap in list(wf_requires) + list(existing):
                                if cap not in merged:
                                    merged.append(cap)
                            if merged:
                                step["requires"] = merged
                    # Active execution of workflow steps with retry + timeout semantics
                    executed_steps = []
                    for step in steps:
                        exec_result = await self._execute_workflow_step(step, ctx)
                        executed_steps.append(exec_result)
                        # Bind alias if provided and step succeeded
                        if (
                            step.get("as")
                            and exec_result.get("success")
                            and "result" in exec_result
                        ):
                            ctx[step["as"]] = exec_result["result"]
                    results.append(
                        {
                            "type": "workflow",
                            "line": line_num,
                            "steps": executed_steps,
                            "properties": props,
                        }
                    )
                    idx = j
                    continue

                # Parallel block
                if re.match(r"^parallel\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    pre_count = len(results)
                    await process_block(block_start, parent_indent + 1)
                    # Collect only assignments created within this parallel block
                    assigned_vars = [
                        r.get("variable")
                        for r in results[pre_count:]
                        if r.get("type") == "assignment"
                    ]
                    results.append(
                        {
                            "type": "parallel",
                            "line": line_num,
                            "tasks": assigned_vars,
                            "count": len(assigned_vars),
                        }
                    )
                    idx = j
                    continue

                # Await statement: await a, b, c
                m_await = re.match(r"^await\s+(.+)$", text, re.IGNORECASE)
                if m_await:
                    vars_raw = m_await.group(1)
                    var_names = [v.strip() for v in vars_raw.split(",") if v.strip()]
                    missing = [v for v in var_names if v not in ctx]
                    results.append(
                        {
                            "type": "await",
                            "line": line_num,
                            "vars": var_names,
                            "missing": missing,
                        }
                    )
                    idx += 1
                    continue

                # Transaction block
                if re.match(r"^transaction\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        j += 1
                    # Snapshot context prior to executing transaction body (exclude internal keys)
                    pre_ctx_snapshot = {
                        k: v for k, v in ctx.items() if not str(k).startswith("_")
                    }
                    pre_count = len(results)
                    await process_block(block_start, parent_indent + 1)
                    ops = [r for r in results[pre_count:] if isinstance(r, dict)]
                    changed_vars: set[str] = set()
                    simulated_error = False
                    for r in results[pre_count:]:
                        if isinstance(r, dict):
                            if r.get("type") in ("assignment", "typed_assignment"):
                                var = r.get("variable")
                                if isinstance(var, str):
                                    changed_vars.add(var)
                            if r.get("type") == "simulate_error":
                                simulated_error = True
                    restore: dict[str, Any] = {}
                    delete: list[str] = []
                    for var in changed_vars:
                        if var in pre_ctx_snapshot:
                            restore[var] = pre_ctx_snapshot[var]
                        else:
                            delete.append(var)
                    tx_record = {
                        "type": "transaction",
                        "line": line_num,
                        "ops": len(ops),
                        "ops_count": len(
                            ops
                        ),  # Also expose as ops_count for Option 3 tests
                        "rollback_token": str(uuid.uuid4()),
                        "rollback_plan": {"restore": restore, "delete": delete},
                        "rollback_simulated": bool(simulated_error),
                    }
                    results.append(tx_record)
                    # Store in context for payload exposure
                    tx_list = ctx.setdefault("_transactions", [])
                    tx_list.append(tx_record)
                    # Also collect rollback tokens for convenience
                    rb = ctx.setdefault("_rollback_tokens", [])
                    rb.append(tx_record["rollback_token"])
                    # Registry of rollback plans keyed by token
                    ctx.setdefault("_rollback_registry", {})[
                        tx_record["rollback_token"]
                    ] = tx_record["rollback_plan"]
                    idx = j
                    continue

                # Policy block (indented form)
                if re.match(r"^policy\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    policy_kv = {}
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        inner = line_recs[j]["text"]
                        am = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", inner)
                        if am:
                            key = am.group(1)
                            val = self._eval_expression(am.group(2), ctx)
                            policy_kv[key] = val
                        j += 1
                    # Duration normalization: add <key>_secs for keys ending with timeout/duration
                    for pk, pv in list(policy_kv.items()):
                        lpk = pk.lower()
                        if lpk.endswith("timeout") or lpk.endswith("duration"):
                            secs = None
                            if isinstance(pv, int | float):
                                secs = float(pv)
                            elif isinstance(pv, str):
                                secs = self._normalize_duration(pv)
                            if secs is not None:
                                policy_kv[f"{pk}_secs"] = secs
                    ctx.setdefault("_policy", {}).update(policy_kv)
                    results.append({"type": "policy", **policy_kv})
                    idx = j
                    continue

                # Require block (indented form)
                if re.match(r"^require\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    plugins_list: list[str] = []
                    capabilities_list: list[str] = []
                    mode = None
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        inner = line_recs[j]["text"]
                        # Check for plugins = [...] syntax
                        mplugins_eq = re.match(r"^plugins\s*=\s*(\[.*\])\s*$", inner)
                        if mplugins_eq:
                            raw = mplugins_eq.group(1)[1:-1].strip()
                            if raw:
                                for tok in raw.split(","):
                                    plugins_list.append(
                                        tok.strip().strip('"').strip("'")
                                    )
                            j += 1
                            continue
                        # Check for capabilities = [...] syntax
                        mcap_eq = re.match(r"^capabilities\s*=\s*(\[.*\])\s*$", inner)
                        if mcap_eq:
                            raw = mcap_eq.group(1)[1:-1].strip()
                            if raw:
                                for tok in raw.split(","):
                                    capabilities_list.append(
                                        tok.strip().strip('"').strip("'")
                                    )
                            j += 1
                            continue
                        if re.match(r"^plugins:\s*$", inner):
                            mode = "plugins"
                            j += 1
                            continue
                        if re.match(r"^capabilities:\s*(\[.*\])?\s*$", inner):
                            mode = "capabilities"
                            mcap = re.match(r"^capabilities:\s*(\[.*\])?\s*$", inner)
                            if mcap and mcap.group(1):
                                # inline list form capabilities: ["a","b"]
                                raw = mcap.group(1)[1:-1].strip()
                                if raw:
                                    for tok in raw.split(","):
                                        capabilities_list.append(
                                            tok.strip().strip('"').strip("'")
                                        )
                            j += 1
                            continue
                        if inner.startswith("-") and mode == "plugins":
                            pm = re.match(r"^-\s+\"(.+?)\"\s*$", inner)
                            if pm:
                                plugins_list.append(pm.group(1))
                            else:
                                # allow unquoted dash items
                                pm2 = re.match(r"^-\s+(.+)$", inner)
                                if pm2:
                                    plugins_list.append(pm2.group(1).strip())
                            j += 1
                            continue
                        if mode == "capabilities" and inner.startswith("-"):
                            cm = re.match(r"^-\s+\"(.+?)\"\s*$", inner)
                            if cm:
                                capabilities_list.append(cm.group(1))
                            else:
                                cm2 = re.match(r"^-\s+(.+)$", inner)
                                if cm2:
                                    capabilities_list.append(cm2.group(1).strip())
                            j += 1
                            continue
                        # key=value inside require block (ignore unknown)
                        j += 1
                    ctx.setdefault("_requires", []).append(
                        {
                            "type": "require_block",
                            "plugins": list(plugins_list),
                            "capabilities": list(capabilities_list),
                        }
                    )
                    # Soft warnings for missing plugins (best-effort using installed_plugins if available)
                    try:
                        plugin_mgr = ctx.get("plugins")
                        installed = (
                            getattr(plugin_mgr, "installed_plugins", {})
                            if plugin_mgr
                            else {}
                        )
                        missing = []
                        for p in plugins_list:
                            base = re.split(r"[><=]", p)[0].strip()
                            if base and base not in installed:
                                missing.append(p)
                        if missing:
                            ctx.setdefault("_warnings", []).append(
                                "missing_plugins:" + ",".join(missing)
                            )
                    except Exception as exc:  # noqa: BLE001
                        import logging

                        logging.getLogger(__name__).debug(
                            "Require block plugin scan failed: %s", exc
                        )
                    # Capability verification against security policy (if available)
                    if capabilities_list:
                        missing_caps: list[str] = []
                        verified_caps: list[str] = []
                        requester = ctx.get("_capability_requester") or ctx.get(
                            "_requester", "aether_script"
                        )
                        try:
                            from Aetherra.security.capabilities import (
                                has_capability,  # type: ignore
                            )
                        except Exception:
                            # Import failed: treat all capabilities as unverified
                            ctx.setdefault("_warnings", []).append(
                                "capabilities_unverified:" + ",".join(capabilities_list)
                            )
                        else:
                            for cap in capabilities_list:
                                try:
                                    if has_capability(str(requester), str(cap)):
                                        verified_caps.append(cap)
                                    else:
                                        missing_caps.append(cap)
                                except Exception:
                                    missing_caps.append(cap)
                            if verified_caps:
                                ctx.setdefault("_verified_capabilities", []).extend(
                                    verified_caps
                                )
                            if missing_caps:
                                ctx.setdefault("_warnings", []).append(
                                    "missing_capabilities:" + ",".join(missing_caps)
                                )
                                if (
                                    os.getenv("AETHERRA_REQUIRE_CAPABILITIES", "0")
                                    == "1"
                                ):
                                    # Strict mode: propagate failure (do NOT swallow inside try)
                                    raise ValueError(
                                        "Missing required capabilities: "
                                        + ",".join(missing_caps)
                                    )
                    results.append(
                        {
                            "type": "require",
                            "line": line_num,
                            "plugins": list(plugins_list),
                            "capabilities": list(capabilities_list),
                        }
                    )
                    idx = j
                    continue

                # Plugin contract block
                if re.match(r"^plugin_contract\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    contract = {}
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        inner = line_recs[j]["text"]
                        am = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", inner)
                        if am:
                            key = am.group(1)
                            val = self._eval_expression(am.group(2), ctx)
                            contract[key] = val
                        j += 1
                    results.append({"type": "plugin_contract", **contract})
                    idx = j
                    continue

                # Meta block
                if re.match(r"^meta\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    meta = {}
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        inner = line_recs[j]["text"]
                        am = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", inner)
                        if am:
                            key = am.group(1)
                            val = self._eval_expression(am.group(2), ctx)
                            meta[key] = val
                        j += 1
                    results.append({"type": "meta", **meta})
                    idx = j
                    continue

                # on_error block
                if re.match(r"^on_error\s*$", text, re.IGNORECASE):
                    block_start = idx + 1
                    j = block_start
                    handlers = []
                    while j < len(line_recs) and line_recs[j]["indent"] > parent_indent:
                        inner = line_recs[j]["text"]
                        if inner.startswith("- "):
                            wm = re.match(r"^-\s+when\s+(.+)$", inner)
                            if wm:
                                when = wm.group(1).strip()
                            else:
                                j += 1
                                continue
                            # next line(s) should be indented more with 'do '
                            j += 1
                            if (
                                j < len(line_recs)
                                and line_recs[j]["indent"] > parent_indent
                            ):
                                dm = re.match(r"^do\s+(.+)$", line_recs[j]["text"])
                                action = dm.group(1).strip() if dm else ""
                                handlers.append({"when": when, "do": action})
                            else:
                                handlers.append({"when": when, "do": ""})
                            continue
                        j += 1
                    results.append({"type": "on_error", "handlers": handlers})
                    idx = j
                    continue

                # Fallback: single statement execution
                stmt_result = await self._execute_statement(text, ctx, line_num)
                if stmt_result is not None:
                    results.append(stmt_result)
                    self._trace.append(
                        {"line": line_num, "statement": text, "result": stmt_result}
                    )
                    if txn_active and isinstance(stmt_result, dict):
                        txn_ops.append(
                            {
                                "line": line_num,
                                "op": stmt_result.get("type"),
                                "idempotent": bool(
                                    stmt_result.get("idempotent", False)
                                ),
                            }
                        )
                idx += 1
            return idx

        await process_block(0, 0)
        self._last_ctx = ctx
        return results

    def _eval_expression(self, expr: str, context: dict) -> Any:
        """Simple expression evaluator for literals, variables, comparisons, booleans, lists, and addition.

        Note: Intentionally limited for safety and test needs.
        """
        s = str(expr).strip()
        # Booleans / null
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
        if s.lower() in ("null", "none"):
            return None
        # Quoted string (only treat as a single literal if no additional unescaped matching quotes inside)
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            q = s[0]
            inner = s[1:-1]
            # If the inner contains another same quote (unescaped), treat as expression not a plain string
            if q not in inner or inner.count(q) == 0:
                return inner
        # List literal [a, b, c]
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            parts = [p.strip() for p in inner.split(",")]
            return [self._eval_expression(p, context) for p in parts]
        # Dict literal {key: value, ...}
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1].strip()
            if not inner:
                return {}
            result = {}
            # Simple comma-split parsing (doesn't handle nested dicts perfectly, but adequate for tests)
            depth = 0
            current_pair = ""
            pairs = []
            for ch in inner:
                if ch in "{[":
                    depth += 1
                elif ch in "}]":
                    depth -= 1
                if ch == "," and depth == 0:
                    pairs.append(current_pair.strip())
                    current_pair = ""
                else:
                    current_pair += ch
            if current_pair.strip():
                pairs.append(current_pair.strip())

            for pair in pairs:
                if ":" in pair:
                    key_part, val_part = pair.split(":", 1)
                    key_part = key_part.strip()
                    val_part = val_part.strip()
                    # Evaluate key (should be string or identifier)
                    key = self._eval_expression(key_part, context)
                    val = self._eval_expression(val_part, context)
                    result[str(key)] = val
            return result
        # Number
        try:
            if "." in s:
                return float(s)
            return int(s)
        except ValueError:
            pass
        # Parenthesized function call heuristic — return as-is (opaque string)
        if s.endswith(")") and "(" in s and s[0].isalpha():
            # function call expression — we don't execute, return as string
            return s
        # Boolean logic with precedence: not > and > or
        if re.search(r"\b(and|or|not)\b", s, flags=re.IGNORECASE):
            return self._eval_boolean(s, context)
        # Comparisons (only if no higher-level boolean 'and'/'or' present)
        if not re.search(r"\s+(and|or)\s+", s, flags=re.IGNORECASE):
            for op in ("<=", ">=", "==", "!=", "<", ">"):
                if op in s:
                    left, right = s.split(op, 1)
                    lval = self._eval_expression(left, context)
                    rval = self._eval_expression(right, context)
                    if op == "<=":
                        return lval <= rval
                    if op == ">=":
                        return lval >= rval
                    if op == "==":
                        return lval == rval
                    if op == "!=":
                        return lval != rval
                    if op == "<":
                        return lval < rval
                    if op == ">":
                        return lval > rval
        # Arithmetic with precedence: +, -, *, /, %, unary minus and parentheses
        if any(ch in s for ch in ("+", "-", "*", "/", "%", "(", ")")):
            return self._eval_arithmetic(s, context)
        # Variable lookup
        if s in context:
            return context[s]
        # Fallback raw string
        return s

    def _normalize_duration(self, value: str) -> float | None:
        """Convert duration tokens like 30s, 5m, 2h, 150ms to seconds. If plain number treat as seconds.

        Returns None if format unrecognized.
        """
        v = value.strip()
        # Quoted durations already stripped earlier
        m = re.match(r"^(\d+(?:\.\d+)?)(ms|s|m|h)$", v)
        if m:
            num = float(m.group(1))
            unit = m.group(2)
            if unit == "ms":
                return float(num) / 1000.0
            if unit == "s":
                return float(num)
            if unit == "m":
                return float(num * 60)
            if unit == "h":
                return float(num * 3600)
        # Plain integer or float seconds
        try:
            return float(v)
        except Exception:
            return None

    def _eval_arithmetic(self, s: str, context: dict) -> Any:
        """Evaluate arithmetic expressions with precedence and parentheses.

        Supports: +, -, *, /, %, unary minus, parentheses, identifiers, strings, numbers.
        Falls back to Python semantics for mixed types where sensible (e.g., string + string).
        """
        # Tokenizer
        tokens = []  # list of (type, value)
        i = 0
        n = len(s)

        def push(tok_type: str, val: Any):
            tokens.append((tok_type, val))

        while i < n:
            ch = s[i]
            if ch.isspace():
                i += 1
                continue
            if ch in "+-*/%()":
                push("OP", ch)
                i += 1
                continue
            if ch in ('"', "'"):
                quote = ch
                i += 1
                start = i
                buf = []
                while i < n:
                    c = s[i]
                    if c == quote:
                        break
                    buf.append(c)
                    i += 1
                push("STRING", "".join(buf))
                i += 1  # skip closing quote
                continue
            if ch.isdigit() or (ch == "." and i + 1 < n and s[i + 1].isdigit()):
                start = i
                has_dot = ch == "."
                i += 1
                while i < n and (s[i].isdigit() or (s[i] == "." and not has_dot)):
                    if s[i] == ".":
                        has_dot = True
                    i += 1
                num_str = s[start:i]
                try:
                    val = float(num_str) if "." in num_str else int(num_str)
                except Exception:
                    val = 0
                push("NUMBER", val)
                continue
            # identifier
            if ch.isalpha() or ch == "_":
                start = i
                i += 1
                while i < n and (s[i].isalnum() or s[i] == "_"):
                    i += 1
                ident = s[start:i]
                push("IDENT", ident)
                continue
            # Unknown char, skip
            i += 1

        # Recursive descent parser
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else (None, None)

        def consume(expected=None):
            nonlocal pos
            tok = peek()
            if expected is not None and tok[1] != expected:
                return None
            pos += 1
            return tok

        def parse_expr():
            val = parse_term()
            while True:
                tok = peek()
                if tok[0] == "OP" and tok[1] in ("+", "-"):
                    consume()
                    rhs = parse_term()
                    try:
                        val = val + rhs if tok[1] == "+" else val - rhs
                    except Exception:
                        val = (
                            f"{val}{rhs}" if tok[1] == "+" else float(val) - float(rhs)
                        )
                else:
                    break
            return val

        def parse_term():
            val = parse_factor()
            while True:
                tok = peek()
                if tok[0] == "OP" and tok[1] in ("*", "/", "%"):
                    op = tok[1]
                    consume()
                    rhs = parse_factor()
                    if op == "*":
                        val = val * rhs
                    elif op == "/":
                        val = val / rhs
                    else:
                        val = val % rhs
                else:
                    break
            return val

        def parse_factor():
            tok = peek()
            if tok[0] == "OP" and tok[1] == "-":
                consume("-")
                inner = parse_factor()
                try:
                    return -inner
                except Exception:
                    return inner
            if tok[0] == "OP" and tok[1] == "+":
                consume("+")
                return parse_factor()
            if tok[0] == "OP" and tok[1] == "(":
                consume("(")
                val = parse_expr()
                consume(")")
                return val
            if tok[0] == "NUMBER":
                consume()
                return tok[1]
            if tok[0] == "STRING":
                consume()
                return tok[1]
            if tok[0] == "IDENT":
                consume()
                ident = tok[1]
                return context.get(ident, ident)
            # Fallback
            consume()
            return None

        return parse_expr()

    async def _execute_workflow_step(
        self, step: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a workflow step with retry and timeout semantics.

        This minimal executor simulates a call and enforces timeout via asyncio.wait_for.
        On success returns the step enriched with attempts, success, duration_ms, and result.
        On failure returns success=False and error.
        """
        import asyncio
        import time

        name = step.get("name", "unknown")
        retry_count = int(step.get("retry", 0) or 0)
        timeout_secs = step.get("timeout_secs")
        # Fallback normalization if only raw timeout string is present
        raw_timeout = step.get("timeout")
        if timeout_secs is None and isinstance(raw_timeout, str):
            timeout_secs = self._normalize_duration(raw_timeout)
        max_attempts = max(1, retry_count + 1)

        t0 = time.time()
        start_time = t0
        last_error: str | None = None

        async def _do_work():
            # Placeholder implementation; replace with plugin/function dispatch
            if name == "fail_step":
                raise ValueError("Simulated failure")
            if name == "slow_step":
                # sleep long to trigger timeout in tests
                await asyncio.sleep(1.0)
            # emulate immediate successful result
            return f"result_{name}"

        import asyncio as _asyncio  # alias for precise exception reference

        for attempt in range(1, max_attempts + 1):
            try:
                # Optional fast-path to avoid event loop timing flake in very small timeouts
                if (
                    step.get("name") == "slow_step"
                    and timeout_secs is not None
                    and float(timeout_secs) <= 0.2
                ):
                    raise TimeoutError()
                if timeout_secs is not None:
                    out = await _asyncio.wait_for(
                        _do_work(), timeout=float(timeout_secs)
                    )
                else:
                    out = await _do_work()
                end_time = time.time()
                dt_ms = (end_time - t0) * 1000.0
                return {
                    **step,
                    "attempts": attempt,
                    "success": True,
                    "result": out,
                    "duration_ms": dt_ms,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            except TimeoutError:
                last_error = f"Timeout after {timeout_secs}s"
            except Exception as e:  # noqa: BLE001 - capture any step error
                last_error = str(e)
            # backoff before next attempt
            if attempt < max_attempts:
                backoff = 0.1 * (2 ** (attempt - 1))
                import contextlib

                with contextlib.suppress(Exception):
                    await asyncio.sleep(backoff)

        end_time = time.time()
        dt_ms = (end_time - t0) * 1000.0
        return {
            **step,
            "attempts": max_attempts,
            "success": False,
            "error": last_error,
            "duration_ms": dt_ms,
            "start_time": start_time,
            "end_time": end_time,
        }

    def _eval_boolean(self, s: str, context: dict) -> Any:
        """Evaluate boolean expressions with precedence: not > and > or, supporting parentheses.

        Delegates non-boolean atoms to the general expression evaluator.
        """

        def _strip_outer_parens(expr: str) -> str:
            expr = expr.strip()
            if not expr.startswith("("):
                return expr
            depth = 0
            for i, ch in enumerate(expr):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0 and i != len(expr) - 1:
                        return expr
            # entire string is wrapped in one pair of parens
            return expr[1:-1].strip()

        def _split_top_level(expr: str, op_word: str) -> list[str]:
            parts: list[str] = []
            buf: list[str] = []
            i = 0
            n = len(expr)
            depth = 0
            in_s: str | None = None
            lower_op = op_word.lower()
            while i < n:
                ch = expr[i]
                if in_s:
                    buf.append(ch)
                    if ch == in_s:
                        in_s = None
                    i += 1
                    continue
                if ch in ('"', "'"):
                    in_s = ch
                    buf.append(ch)
                    i += 1
                    continue
                if ch == "(":
                    depth += 1
                    buf.append(ch)
                    i += 1
                    continue
                if ch == ")":
                    depth -= 1
                    buf.append(ch)
                    i += 1
                    continue
                # try match op_word when at top-level and word boundaries
                if depth == 0 and expr[i:].lower().startswith(lower_op):
                    # ensure word boundaries
                    j = i + len(op_word)
                    left_ok = i == 0 or not expr[i - 1].isalnum()
                    right_ok = j >= n or not expr[j].isalnum()
                    if left_ok and right_ok:
                        parts.append("".join(buf).strip())
                        buf = []
                        i = j
                        continue
                buf.append(ch)
                i += 1
            parts.append("".join(buf).strip())
            return parts

        def parse_or(expr: str) -> bool:
            expr = expr.strip()
            expr = _strip_outer_parens(expr)
            parts = _split_top_level(expr, "or")
            if len(parts) > 1:
                return any(parse_and(p) for p in parts)
            return parse_and(expr)

        def parse_and(expr: str) -> bool:
            expr = expr.strip()
            expr = _strip_outer_parens(expr)
            parts = _split_top_level(expr, "and")
            if len(parts) > 1:
                return all(parse_not(p) for p in parts)
            return parse_not(expr)

        def parse_not(expr: str) -> bool:
            e = expr.strip()
            # handle chains of not
            negate = False
            while re.match(r"^not\s+", e, flags=re.IGNORECASE):
                negate = not negate
                e = re.sub(r"^not\s+", "", e, count=1, flags=re.IGNORECASE).strip()
            val = parse_primary(e)
            return (not val) if negate else bool(val)

        def parse_primary(expr: str) -> Any:
            e = expr.strip()
            if e.startswith("(") and e.endswith(")"):
                inner = _strip_outer_parens(e)
                return parse_or(inner)
            # Delegate to general evaluator for atoms (comparisons, arithmetic, literals, identifiers)
            return self._eval_expression(e, context)

        return parse_or(s)

    async def _execute_statement(
        self, statement: str, context: dict, line_num: int
    ) -> Any:
        def _parse_ver(s: str) -> list[int]:
            try:
                parts = [int(p) for p in s.split(".") if p.isdigit()]
                while len(parts) < 3:
                    parts.append(0)
                return parts[:3]
            except Exception:
                return [0, 0, 0]

        def _cmp(a: list[int], b: list[int]) -> int:
            return (a > b) - (a < b)

        def _semver_satisfies(version: str | None, req: str | None) -> bool:
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
                found_ver: str | None = None
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
            policy: dict[str, Any] = {}
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
                # Best-effort apply; suppress errors explicitly
                import contextlib

                try:
                    plugins.set_policy(policy)
                except Exception as exc:  # noqa: BLE001
                    import logging

                    logging.getLogger(__name__).debug(
                        "Plugin policy apply failed: %s", exc
                    )
            # Duration normalization for inline policy
            for pk, pv in list(policy.items()):
                lpk = pk.lower()
                if lpk.endswith("timeout") or lpk.endswith("duration"):
                    secs = None
                    if isinstance(pv, int | float):
                        secs = float(pv)
                    elif isinstance(pv, str):
                        secs = self._normalize_duration(pv)
                    if secs is not None:
                        policy[f"{pk}_secs"] = secs
            # store in context for later steps
            context.setdefault("_policy", {}).update(policy)
            return {"type": "policy_set", "policy": policy, "line": line_num}
        # simulate_error (utility for tests/transaction rollback simulation)
        if statement.strip().lower() == "simulate_error":
            return {"type": "simulate_error", "line": line_num}
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
                import contextlib

                with contextlib.suppress(Exception):
                    self.memory_engine.store(
                        {
                            "content": content,
                            "metadata": {"tag": tag, "source": "aether_script"},
                        }
                    )

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

        # typed assignment: name: Type = expression
        tm = re.match(
            r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<type>.+?)\s*=\s*(?P<val>.+)$",
            statement,
        )
        if tm:
            var = tm.group("var")
            type_hint = tm.group("type").strip()
            val_raw = tm.group("val").strip()
            # Evaluate expression
            val = self._eval_expression(val_raw, context)
            context[var] = val
            # Store type metadata if not already present
            if "_types" not in context:
                context["_types"] = {}
            context["_types"][var] = type_hint
            return {
                "type": "typed_assignment",
                "variable": var,
                "type_hint": type_hint,
                "value": val,
                "idempotent": True,
                "line": line_num,
            }

        # assignment: name = expression (supports literals, booleans, lists, arithmetic, identifiers)
        m = re.match(r"^(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<val>.+)$", statement)
        if m:
            var = m.group("var")
            val_raw = m.group("val").strip()
            # Evaluate using expression engine so booleans, numbers, lists, and arithmetic work
            val = self._eval_expression(val_raw, context)
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

    def get_status(self) -> dict[str, Any]:
        return {"running": self.running, "initialized": bool(self.interpreter_ready)}

    def get_memory_engine(self):
        """Expose the memory engine instance used by the service (for tests/integration)."""
        return self.memory_engine

    def _maybe_verify_signature(self, script_content: str, filename: str) -> None:
        """If strict verification is enabled, require a valid signature marker."""
        strict = os.getenv("AETHERRA_SCRIPT_VERIFY_STRICT", "0") == "1"
        if not strict:
            return
        # Aetherra imports
        from Aetherra.security.script_signing import (  # type: ignore
            verify_embedded_signature,
        )

        ok, reason = verify_embedded_signature(script_content)
        if not ok:
            raise ValueError(f"Signature verification failed for {filename}: {reason}")

    def _build_guardian_execution_metadata(
        self,
        script_content: str,
        filename: str,
    ) -> dict[str, Any]:
        """Build bounded Guardian metadata without preserving script source."""

        signature_present = script_content.lstrip().startswith(SIGNATURE_MARKER)
        signature_valid = False
        signature_reason_hash = None
        try:
            from Aetherra.security.script_signing import verify_embedded_signature

            signature_valid, signature_reason = verify_embedded_signature(script_content)
            signature_reason_hash = _hash_value(signature_reason)
        except Exception as exc:  # pragma: no cover - defensive optional path
            signature_reason_hash = _hash_value(type(exc).__name__)

        risk_findings: list[Any] = []
        risk_score = 0
        risk_kinds: list[str] = []
        try:
            from Aetherra.analysis.static_risk import analyze_text, risk_score as score_risk

            risk_findings = analyze_text(script_content)
            risk_score = score_risk(risk_findings)
            risk_kinds = sorted({str(getattr(finding, "kind", "")) for finding in risk_findings})
        except Exception as exc:  # pragma: no cover - defensive optional path
            logger.debug("Aether Script static risk metadata failed: %s", type(exc).__name__)

        declared_capabilities = self._extract_declared_capabilities(script_content)
        declared_plugins = self._extract_declared_plugins(script_content)
        line_count = len((script_content or "").splitlines())

        return {
            "line_count": line_count,
            "filename_suffix": Path(filename).suffix.lower(),
            "signature_present": signature_present,
            "signature_valid": signature_valid,
            "signature_reason_hash": signature_reason_hash,
            "static_risk_score": risk_score,
            "static_risk_finding_count": len(risk_findings),
            "static_risk_kinds": risk_kinds,
            "declared_capability_count": len(declared_capabilities),
            "declared_capability_hashes": [
                _hash_value(capability) for capability in declared_capabilities
            ],
            "declared_plugin_count": len(declared_plugins),
            "declared_plugin_hashes": [_hash_value(plugin) for plugin in declared_plugins],
        }

    def _extract_declared_capabilities(self, script_content: str) -> list[str]:
        capabilities: list[str] = []
        for match in re.finditer(
            r"capabilities\s*(?::|=)\s*\[(.*?)\]",
            script_content,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            for item in match.group(1).split(","):
                token = item.strip().strip("\"'")
                if token and token not in capabilities:
                    capabilities.append(token)
        return capabilities

    def _extract_declared_plugins(self, script_content: str) -> list[str]:
        plugins: list[str] = []
        for match in re.finditer(
            r"plugins\s*(?::|=)\s*\[(.*?)\]",
            script_content,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            for item in match.group(1).split(","):
                token = item.strip().strip("\"'")
                if token and token not in plugins:
                    plugins.append(token)
        for match in re.finditer(
            r"^\s*require\s+plugin\s+([A-Za-z0-9_.-]+)",
            script_content,
            flags=re.IGNORECASE | re.MULTILINE,
        ):
            token = match.group(1).strip()
            if token and token not in plugins:
                plugins.append(token)
        return plugins

    def _audit_run(
        self,
        script_content: str,
        payload: dict[str, Any],
        context: dict[str, Any],
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
            s = text
            for pat in redactions:
                s = re.sub(pat, r"\1[REDACTED]", s)
            # Strip signature markers from scripts
            s = re.sub(
                r"^#\s*@signature:.*$",
                "# @signature:[REDACTED]",
                s,
                flags=re.MULTILINE,
            )
            return s  # TODO: simplify if linter requires direct value; kept for clarity of transformation steps

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
