#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
[AGENTS] OS-Level Agent Fabric
==============================

Implements the Agent Fabric layer shown in the architecture:
- Agent runtime registry
- Capability/Policy gate (least privilege)
- Observability hooks (status/metrics)
- Event Bus integration (publish/subscribe)

Agents are registered as individual services under the registry with names:
  agent.planner, agent.retriever, agent.memory_analyzer, agent.bughunter,
  agent.toolsmith, agent.ethics_guard, agent.summarizer, agent.ops

Each agent exposes a minimal handle_message and subscribes to a topic on the KEB.
"""

import asyncio
import logging
import os
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# -------------------- Capability / Policy Gate --------------------
@dataclass
class Policy:
    allowed_caps: Set[str] = field(default_factory=set)
    denied_caps: Set[str] = field(default_factory=set)

    def allows(self, cap: str) -> bool:
        c = (cap or "").strip()
        if not c:
            return False
        if c in self.denied_caps:
            return False
        if not self.allowed_caps:
            # If not explicitly set, default deny unless present in allowed
            return False
        return c in self.allowed_caps


class CapabilityGate:
    def __init__(self):
        self._policies: Dict[str, Policy] = {}

    def set_policy(self, agent_name: str, policy: Policy):
        self._policies[str(agent_name)] = policy

    def check(self, agent_name: str, capability: str) -> bool:
        pol = self._policies.get(str(agent_name))
        if pol is None:
            return False
        return pol.allows(capability)


# -------------------- Agent Base --------------------
class AgentBase:
    name: str = "agent.base"
    topic: str = "tasks.generic"
    capabilities: Set[str] = set()

    def __init__(self, registry, gate: CapabilityGate):
        self.registry = registry
        self.gate = gate
        self._hb: Optional[asyncio.Task] = None

    async def start(self):
        # Subscribe to topic for metrics visibility; fanout is broadcast-based
        try:
            # Only subscribe if the Event Bus service is present to avoid noise
            if getattr(
                self.registry, "get_service", None
            ) and self.registry.get_service("event_bus"):
                await self.registry.send_message(
                    "event_bus",
                    "keb.event.subscribe",
                    {"topic": self.topic, "service": self.name},
                )
        except Exception:
            pass
        # Simple heartbeat
        self._hb = asyncio.create_task(self._heartbeat())

    async def _heartbeat(self):
        try:
            while True:
                try:
                    await self.registry.update_heartbeat(self.name)
                except Exception:
                    pass
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            return

    async def shutdown(self):
        if self._hb:
            self._hb.cancel()

    async def handle_message(self, message_type: str, data: Any) -> Any:
        # Default dispatcher: react to KEB topic broadcast or agent.run
        mt = (message_type or "").lower()
        if mt.endswith(self.topic) or mt.endswith("agent.run"):
            return await self._handle(data or {})
        return {"ok": False, "error": "ignored"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        # To be implemented by subclasses
        return {"ok": True}


# -------------------- Concrete Agents --------------------
class PlannerAgent(AgentBase):
    name = "agent.planner"
    topic = "tasks.plan"
    capabilities = {"plan"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "plan"):
            return {"ok": False, "error": "forbidden"}
        goal = str(payload.get("goal") or payload.get("task") or "").strip()
        steps = []
        if goal:
            steps = [
                {"step": 1, "action": "analyze", "detail": goal},
                {"step": 2, "action": "retrieve", "detail": "gather context"},
                {"step": 3, "action": "execute", "detail": "perform actions"},
                {"step": 4, "action": "summarize", "detail": "report results"},
            ]
        return {"ok": True, "plan": steps}


class RetrieverAgent(AgentBase):
    name = "agent.retriever"
    topic = "tasks.retrieve"
    capabilities = {"retrieve"}
    _cache_max = 32

    def __init__(self, registry, gate: CapabilityGate):
        super().__init__(registry, gate)
        self._cache: "OrderedDict[str, Any]" = OrderedDict()

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "retrieve"):
            return {"ok": False, "error": "forbidden"}
        query = str(payload.get("query") or "").strip()
        limit = int(payload.get("limit") or 5)
        mtype = payload.get("memory_type")
        if not query:
            return {"ok": True, "items": [], "query": query}
        # Cache lookup
        key = f"{query}|{limit}|{mtype}"
        if key in self._cache:
            # move to end (recent)
            self._cache.move_to_end(key)
            return {
                "ok": True,
                "items": self._cache[key],
                "query": query,
                "cached": True,
            }
        # Try memory services if available; gracefully degrade to empty
        try:
            mem = None
            if getattr(self.registry, "get_service", None):
                mem = self.registry.get_service(
                    "memory_system"
                ) or self.registry.get_service("qfac_memory_system")
            if mem is None:
                return {"ok": True, "items": [], "query": query}
            # Prefer async Lyrixa-like API
            if hasattr(mem, "recall_memories"):
                try:
                    items = await mem.recall_memories(
                        query_text=query, limit=limit, memory_type=mtype
                    )  # type: ignore[attr-defined]
                    self._cache[key] = items
                    if len(self._cache) > self._cache_max:
                        self._cache.popitem(last=False)
                    return {"ok": True, "items": items, "query": query}
                except TypeError:
                    # Some impls might be sync
                    items = mem.recall_memories(
                        query_text=query, limit=limit, memory_type=mtype
                    )  # type: ignore[attr-defined]
                    self._cache[key] = items
                    if len(self._cache) > self._cache_max:
                        self._cache.popitem(last=False)
                    return {"ok": True, "items": items, "query": query}
            # Fallback to AetherraMemoryEngine-like API
            if hasattr(mem, "retrieve"):
                try:
                    items = mem.retrieve(query, {"limit": limit, "memory_type": mtype})
                except TypeError:
                    items = mem.retrieve(query)
                self._cache[key] = items
                if len(self._cache) > self._cache_max:
                    self._cache.popitem(last=False)
                return {"ok": True, "items": items, "query": query}
            # Unknown API; return empty gracefully
            return {"ok": True, "items": [], "query": query}
        except Exception as e:
            return {"ok": False, "error": str(e), "query": query, "items": []}


class MemoryAnalyzerAgent(AgentBase):
    name = "agent.memory_analyzer"
    topic = "tasks.memory.analyze"
    capabilities = {"analyze_memory"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "analyze_memory"):
            return {"ok": False, "error": "forbidden"}
        return {"ok": True, "analysis": {"summary": "no issues detected"}}


class BugHunterAgent(AgentBase):
    name = "agent.bughunter"
    topic = "tasks.bug"
    capabilities = {"scan_code"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "scan_code"):
            return {"ok": False, "error": "forbidden"}
        code = str(payload.get("code") or "")
        issues = []
        if "TODO" in code or "FIXME" in code:
            issues.append({"type": "todo", "message": "Found TODO/FIXME comments"})
        return {"ok": True, "issues": issues}


class ToolsmithAgent(AgentBase):
    name = "agent.toolsmith"
    topic = "tasks.tools"
    capabilities = {"generate_tool"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "generate_tool"):
            return {"ok": False, "error": "forbidden"}
        spec = str(payload.get("spec") or payload.get("description") or "").strip()
        code = payload.get("code")
        base_name = payload.get("name") or f"tool_{int(time.time())}"
        # Create toolshed directory
        try:
            root = Path(os.getcwd()) / "toolshed"
            root.mkdir(parents=True, exist_ok=True)
            file_py = root / f"{base_name}.py"
            if code and isinstance(code, str) and code.strip():
                content = code
            else:
                content = (
                    "# Auto-generated tool stub\n\n"
                    "def main(*args, **kwargs):\n"
                    f'    """Tool \'{base_name}\'\n\n'
                    f"    Spec: {spec}\n"
                    '    """\n'
                    "    # TODO: implement\n"
                    '    return {"status": "not_implemented"}\n'
                )
            file_py.write_text(content, encoding="utf-8")
            # Optional: write a tiny readme entry
            readme = root / "README.md"
            with readme.open("a", encoding="utf-8") as f:
                f.write(f"- {base_name}.py: {spec}\n")
            return {
                "ok": True,
                "tool": {"name": base_name, "path": str(file_py), "spec": spec},
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}


class ExecutorAgent(AgentBase):
    name = "agent.executor"
    topic = "tasks.execute"
    capabilities = {"execute"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "execute"):
            return {"ok": False, "error": "forbidden"}
        action = payload.get("action") or "generic"
        params = payload.get("params") or {}
        # Try plugin manager for execution
        try:
            pm = None
            if getattr(self.registry, "get_service", None):
                pm = self.registry.get_service("plugin_manager")
            if pm and hasattr(pm, "execute_plugin"):
                try:
                    result = pm.execute_plugin("executor", action, **params)
                except TypeError:
                    result = pm.execute_plugin("executor")
                return {
                    "ok": True,
                    "executed": True,
                    "action": action,
                    "result": result,
                }
        except Exception as e:
            return {"ok": False, "error": str(e), "executed": False, "action": action}
        # Fallback: report simulated execution
        return {
            "ok": True,
            "executed": False,
            "action": action,
            "note": "no executor available",
        }


class EthicsGuardAgent(AgentBase):
    name = "agent.ethics_guard"
    topic = "tasks.ethics"
    capabilities = {"policy_check"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "policy_check"):
            return {"ok": False, "error": "forbidden"}
        text = str(payload.get("text") or "")
        flagged = any(k in text.lower() for k in ["api_key", "password"])
        return {"ok": True, "compliant": not flagged, "flagged": flagged}


class SummarizerAgent(AgentBase):
    name = "agent.summarizer"
    topic = "tasks.summarize"
    capabilities = {"summarize"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "summarize"):
            return {"ok": False, "error": "forbidden"}
        text = str(payload.get("text") or "")
        if not text:
            return {"ok": True, "summary": ""}
        # Prefer engine or chat if available; gracefully fall back to heuristic
        try:
            # Try engine summarization if present
            eng = None
            if getattr(self.registry, "get_service", None):
                eng = self.registry.get_service("aetherra_engine")
            if eng is not None:
                for meth in ("summarize_text", "summarize", "generate_summary"):
                    if hasattr(eng, meth):
                        try:
                            fn = getattr(eng, meth)
                            res = (
                                fn(text)
                                if not asyncio.iscoroutinefunction(fn)
                                else await fn(text)
                            )
                            if isinstance(res, str) and res.strip():
                                return {"ok": True, "summary": res.strip()}
                            if isinstance(res, dict) and res.get("summary"):
                                return {
                                    "ok": True,
                                    "summary": str(res["summary"]).strip(),
                                }
                        except Exception:
                            pass
            # Try chat service for summarization prompt
            chat = None
            if getattr(self.registry, "get_service", None):
                chat = self.registry.get_service("lyrixa_chat")
            if chat is not None and hasattr(chat, "handle_message"):
                try:
                    resp = await chat.handle_message(
                        "lyrixa.chat",
                        {
                            "message": f"Summarize the following text succinctly:\n\n{text}"
                        },
                    )
                    msg = (resp or {}).get("summary") or (resp or {}).get("text")
                    if isinstance(msg, str) and msg.strip():
                        return {"ok": True, "summary": msg.strip()}
                except Exception:
                    pass
            # Try plugin manager optimizer
            pm = None
            if getattr(self.registry, "get_service", None):
                pm = self.registry.get_service("plugin_manager")
            if pm is not None and hasattr(pm, "execute_plugin"):
                try:
                    out = None
                    try:
                        out = pm.execute_plugin("optimizer", "summarize", text=text)
                    except TypeError:
                        out = pm.execute_plugin("optimizer")
                    if isinstance(out, str) and out.strip():
                        return {"ok": True, "summary": out.strip()}
                    if isinstance(out, dict) and out.get("summary"):
                        return {"ok": True, "summary": str(out["summary"]).strip()}
                except Exception:
                    pass
        except Exception:
            pass
        # Heuristic fallback: first sentence up to ~200 chars
        cut = text.find(".")
        if cut == -1 or cut > 200:
            cut = min(200, len(text))
        summary = text[:cut].strip()
        return {"ok": True, "summary": summary}


class OpsBotAgent(AgentBase):
    name = "agent.ops"
    topic = "tasks.ops"
    capabilities = {"ops_status"}

    async def _handle(self, payload: Dict[str, Any]) -> Any:
        if not self.gate.check(self.name, "ops_status"):
            return {"ok": False, "error": "forbidden"}
        # Return lightweight system snapshot via registry
        try:
            status = self.registry.get_registry_status()
        except Exception:
            status = {"running": False}
        return {"ok": True, "registry": status}


# -------------------- Agent Fabric --------------------
class AgentFabric:
    def __init__(self, registry):
        self.registry = registry
        self.gate = CapabilityGate()
        self.agents: List[AgentBase] = []
        self._metrics = {
            "agent_messages_total": 0,
            "agent_errors_total": 0,
            "per_agent": {},  # name -> {calls, errors, latency_ms_sum}
        }
        # AAR modes and safety flags
        self.mode = os.getenv("AAR_MODE", "headless").lower()
        self.safe_mode = os.getenv("AAR_SAFE_MODE", "0") == "1" or self.mode == "safe"
        # Default read-only in headless/safe unless explicitly allowed
        allow_local_writes = os.getenv("AAR_ALLOW_LOCAL_WRITES", "0") == "1"
        self.read_only = (
            os.getenv("AAR_READ_ONLY", "0") == "1"
            or self.safe_mode
            or (self.mode == "headless" and not allow_local_writes)
        )
        # Capability profiles per mode
        self._profile_caps: Dict[str, Dict[str, Set[str]]] = {
            "full": {
                "agent.planner": {"plan"},
                "agent.retriever": {"retrieve"},
                "agent.memory_analyzer": {"analyze_memory"},
                "agent.bughunter": {"scan_code"},
                "agent.toolsmith": {"generate_tool"},
                "agent.ethics_guard": {"policy_check"},
                "agent.summarizer": {"summarize"},
                "agent.executor": {"execute"},
                "agent.ops": {"ops_status"},
            },
            "headless": {
                "agent.planner": {"plan"},
                "agent.retriever": {"retrieve"},
                "agent.memory_analyzer": {"analyze_memory"},
                "agent.bughunter": {"scan_code"},
                "agent.toolsmith": {"generate_tool"},
                "agent.ethics_guard": {"policy_check"},
                "agent.summarizer": {"summarize"},
                # executor disabled in headless (defer actions)
                "agent.executor": set(),
                "agent.ops": {"ops_status"},
            },
            "safe": {
                "agent.planner": {"plan"},
                "agent.retriever": set(),
                "agent.memory_analyzer": set(),
                "agent.bughunter": {"scan_code"},
                "agent.toolsmith": set(),
                "agent.ethics_guard": {"policy_check"},
                "agent.summarizer": {"summarize"},
                "agent.executor": set(),
                "agent.ops": {"ops_status"},
            },
        }
        # Optional outbox for deferred writes
        try:
            from aetherra_outbox import Outbox  # type: ignore

            self.outbox = Outbox()
        except Exception:
            self.outbox = None

    async def start(self):
        # Apply capability profile by mode
        profile = self._profile_caps.get("safe" if self.safe_mode else self.mode)
        if profile is None:
            profile = self._profile_caps["headless"]
        for agent_name, caps in profile.items():
            self.gate.set_policy(agent_name, Policy(set(caps)))

        # Create agent instances
        self.agents = [
            PlannerAgent(self.registry, self.gate),
            RetrieverAgent(self.registry, self.gate),
            MemoryAnalyzerAgent(self.registry, self.gate),
            BugHunterAgent(self.registry, self.gate),
            ToolsmithAgent(self.registry, self.gate),
            EthicsGuardAgent(self.registry, self.gate),
            SummarizerAgent(self.registry, self.gate),
            ExecutorAgent(self.registry, self.gate),
            OpsBotAgent(self.registry, self.gate),
        ]

        # Register agents as individual services and subscribe topics
        for a in self.agents:
            try:
                await self.registry.register_service(
                    a.name, a, metadata={"type": "agent"}
                )
                await a.start()
            except Exception as e:
                logger.warning(f"[AGENTS] Failed to start {a.name}: {e}")

        logger.info("[AGENTS] Agent Fabric ready with %d agents", len(self.agents))

    async def handle_message(self, message_type: str, data: Any) -> Any:
        mt = (message_type or "").lower()
        if mt.endswith("agents.status"):
            st = self.get_status()
            st["mode"] = "safe" if self.safe_mode else self.mode
            st["read_only"] = bool(self.read_only)
            ob = getattr(self, "outbox", None)
            st["outbox"] = bool(ob)
            try:
                st["outbox_size"] = sum(1 for _ in ob.iter_entries()) if ob else 0
            except Exception:
                st["outbox_size"] = None
            return st
        if mt.endswith("agents.outbox.list"):
            ob = getattr(self, "outbox", None)
            if not ob:
                return {"ok": False, "error": "no_outbox"}
            entries = []
            try:
                for obj in ob.iter_entries() or []:
                    p = (obj or {}).get("payload") or {}
                    entries.append(
                        {
                            "key": obj.get("key"),
                            "ts": obj.get("ts"),
                            "intent": p.get("intent"),
                            "agent": p.get("agent"),
                            "action": p.get("action"),
                            "goal": p.get("goal"),
                        }
                    )
            except Exception as e:
                return {"ok": False, "error": str(e)}
            return {"ok": True, "entries": entries, "count": len(entries)}
        if mt.endswith("agents.outbox.clear"):
            ob = getattr(self, "outbox", None)
            if not ob:
                return {"ok": False, "error": "no_outbox"}
            if self.read_only:
                return {"ok": False, "error": "read_only"}
            try:
                ob.clear()
                return {"ok": True, "cleared": True}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        if mt.endswith("agents.metrics"):
            return self.get_metrics()
        if mt.endswith("agent.pipeline"):
            # Simple pipeline: plan -> retrieve -> summarize
            payload = data or {}
            goal = str(
                payload.get("goal") or payload.get("text") or payload.get("query") or ""
            ).strip()
            if not goal:
                return {"ok": False, "error": "missing_goal"}
            res = {"ok": True, "goal": goal, "stages": {}}
            # Find agents
            planner = next((a for a in self.agents if a.name == "agent.planner"), None)
            retriever = next(
                (a for a in self.agents if a.name == "agent.retriever"), None
            )
            summarizer = next(
                (a for a in self.agents if a.name == "agent.summarizer"), None
            )
            executor = next(
                (a for a in self.agents if a.name == "agent.executor"), None
            )
            # Execute stages best-effort
            if planner:
                res["stages"]["plan"] = await self._dispatch_agent(
                    planner, {"goal": goal}
                )
            if retriever:
                res["stages"]["retrieve"] = await self._dispatch_agent(
                    retriever, {"query": goal, "limit": payload.get("limit", 5)}
                )
            if executor:
                if self.read_only:
                    payload = {
                        "intent": "execute",
                        "action": "pipeline_task",
                        "goal": goal,
                    }
                    ob = getattr(self, "outbox", None)
                    if ob:
                        try:
                            enq = ob.enqueue(payload)
                            res["stages"]["execute"] = {
                                "ok": True,
                                "queued": True,
                                "outbox_key": enq.key,
                            }
                        except Exception as e:
                            res["stages"]["execute"] = {"ok": False, "error": str(e)}
                    else:
                        res["stages"]["execute"] = {
                            "ok": False,
                            "error": "read_only_no_outbox",
                        }
                else:
                    res["stages"]["execute"] = await self._dispatch_agent(
                        executor, {"action": "pipeline_task", "params": {"goal": goal}}
                    )
            if summarizer:
                text = goal
                # Prefer summarizing retrieved content if available
                items = (res["stages"].get("retrieve") or {}).get("items") or []
                if isinstance(items, list) and items:
                    # stringify items conservatively
                    text = str(items)[:1000]
                res["stages"]["summarize"] = await self._dispatch_agent(
                    summarizer, {"text": text}
                )
            return res
        # direct run: dispatch to named agent
        if mt.endswith("agent.run"):
            payload = data or {}
            target = str(payload.get("agent") or "").strip()
            for a in self.agents:
                if a.name == target:
                    # Defer write-like actions in read-only modes
                    if self.read_only and a.name in {
                        "agent.executor",
                        "agent.toolsmith",
                    }:
                        intent = {
                            "intent": "agent.run",
                            "agent": a.name,
                            "payload": payload,
                        }
                        ob = getattr(self, "outbox", None)
                        if ob:
                            try:
                                enq = ob.enqueue(intent)
                                return {
                                    "ok": True,
                                    "queued": True,
                                    "outbox_key": enq.key,
                                }
                            except Exception as e:
                                return {"ok": False, "error": str(e)}
                        return {"ok": False, "error": "read_only_no_outbox"}
                    return await self._dispatch_agent(a, payload)
        return {"ok": False, "error": "unknown_message"}

    async def _dispatch_agent(self, agent: AgentBase, payload: Dict[str, Any]) -> Any:
        name = agent.name
        self._metrics["agent_messages_total"] += 1
        p = self._metrics.setdefault("per_agent", {}).setdefault(
            name, {"calls": 0, "errors": 0, "latency_ms_sum": 0.0}
        )
        p["calls"] += 1
        t0 = time.perf_counter()
        try:
            timeout_ms = 0
            try:
                import os

                timeout_ms = int(os.getenv("AETHERRA_AGENT_TIMEOUT_MS", "2000") or 2000)
            except Exception:
                timeout_ms = 2000
            res = await asyncio.wait_for(
                agent._handle(payload), timeout=timeout_ms / 1000.0
            )
            return res
        except Exception as e:
            self._metrics["agent_errors_total"] += 1
            p["errors"] += 1
            return {"ok": False, "error": str(e)}
        finally:
            dt_ms = (time.perf_counter() - t0) * 1000.0
            p["latency_ms_sum"] += dt_ms

    def get_status(self) -> Dict[str, Any]:
        return {
            "agents": [a.name for a in self.agents],
            "policies": {a.name: list(a.capabilities) for a in self.agents},
        }

    def get_metrics(self) -> Dict[str, Any]:
        # Include simple averages per agent
        out = {k: v for k, v in self._metrics.items() if k != "per_agent"}
        per_agent = {}
        for name, m in self._metrics.get("per_agent", {}).items():
            avg = (m["latency_ms_sum"] / m["calls"]) if m["calls"] else 0.0
            per_agent[name] = {
                "calls": m["calls"],
                "errors": m["errors"],
                "avg_latency_ms": round(avg, 2),
            }
        out["per_agent"] = per_agent
        return out

    async def shutdown(self):
        for a in self.agents:
            try:
                await a.shutdown()
            except Exception:
                pass


_fabric_instance: Optional[AgentFabric] = None


async def get_agent_fabric(service_registry) -> AgentFabric:
    global _fabric_instance
    if _fabric_instance is None:
        _fabric_instance = AgentFabric(service_registry)
    return _fabric_instance
