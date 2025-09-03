#!/usr/bin/env python3
"""
Lyrixa Chat Service

Goals:
- Intelligent, identity-aware responses (who is Lyrixa, Aetherra, Aetherra Labs)
- Workspace awareness (file index + targeted search)
- Suggest and optionally apply corrections/edits (safe, scoped)
- Integrate with Aetherra OS services when available (registry, memory)

This service exposes a simple async API:
- chat(message: str, opts: ChatOptions) -> ChatResponse
- suggest_fixes(context) -> list of suggestions
- apply_fix(suggestion) -> Apply a specific safe edit
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional: import chat router and intelligence if present
try:
    from Aetherra.core.chat_router import create_chat_router
except Exception:
    create_chat_router = None

try:
    from Aetherra.lyrixa.intelligence.lyrixa_full_intelligence import (
        get_lyrixa_intelligence,
    )
except Exception:
    get_lyrixa_intelligence = None

# Optional: new adaptive orchestrator and memory evidence
try:
    from Aetherra.lyrixa.intelligence.adaptive_orchestrator import (
        AdaptiveIntelligenceOrchestrator,
    )
except Exception:
    AdaptiveIntelligenceOrchestrator = None  # type: ignore

try:
    from Aetherra.lyrixa.memory.multidimensional_memory import (
        MultidimensionalMemory,
    )
except Exception:
    MultidimensionalMemory = None  # type: ignore

try:
    from Aetherra.lyrixa.consciousness_integration import ConsciousnessBridge
except Exception:
    ConsciousnessBridge = None  # type: ignore

# Optional: service registry
try:
    from aetherra_service_registry import get_service_registry
except Exception:
    get_service_registry = None

# Persistent memory
try:
    from aetherra_persistent_memory import get_persistent_memory_system
except Exception:
    get_persistent_memory_system = None

IDENTITY = {
    "name": "Lyrixa",
    "title": "Lyrixa AI Assistant",
    "about": (
        "I'm Lyrixa, the conversational and awareness layer of the Aetherra AI Operating System. "
        "I help you interact with Aetherra's capabilities, reason about the workspace, and take safe actions."
    ),
    "aetherra": "Aetherra is an AI Operating System that orchestrates services: memory, plugins, agents, hub server, and more.",
    "labs": "Aetherra Labs is the team building the Aetherra OS, Lyrixa, and research components like QFAC.",
}

WORKSPACE_ROOT = Path(os.getcwd())
DEFAULT_SCAN_EXCLUDES = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "env",
    "venv",
    "__pycache__",
    "site-packages",
    "docs",
    "backup",
    "comprehensive_cleanup_backup",
    "focused_cleanup_backup",
}


@dataclass
class ChatOptions:
    user_id: str = "user"
    session_id: str = "default"
    max_tokens: int = 600
    allow_edits: bool = False
    # limit edits to this root (defaults to repo root)
    edit_root: Path = field(default_factory=lambda: WORKSPACE_ROOT)


@dataclass
class ChatResponse:
    text: str
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    applied_changes: List[Dict[str, Any]] = field(default_factory=list)
    identity: Dict[str, str] = field(default_factory=lambda: IDENTITY)
    awareness: Dict[str, Any] = field(default_factory=dict)


class LyrixaChatService:
    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = Path(workspace_root) if workspace_root else WORKSPACE_ROOT
        self.router = create_chat_router(str(self.root)) if create_chat_router else None
        self.registry = None
        self._intelligence = None
        self._pmemory = None
        # Core enhancements (mandatory)
        self._orchestrator = None
        self._mdmem = None
        self._conscious = None

    async def initialize(self):
        # Try to connect to service registry
        if get_service_registry:
            try:
                self.registry = await get_service_registry()
            except Exception:
                self.registry = None
        # Warm up intelligence if available (always attempt; degrade gracefully)
        if get_lyrixa_intelligence:
            try:
                self._intelligence = await get_lyrixa_intelligence()
            except Exception:
                self._intelligence = None
        # Connect to persistent memory (best-effort; always attempt)
        if get_persistent_memory_system:
            try:
                self._pmemory = await get_persistent_memory_system()
            except Exception:
                self._pmemory = None

        # Initialize enhancements (mandatory for release path)
        if not AdaptiveIntelligenceOrchestrator:
            raise RuntimeError("Adaptive orchestrator not available")
        if not MultidimensionalMemory:
            raise RuntimeError("MultidimensionalMemory not available")
        if not ConsciousnessBridge:
            raise RuntimeError("ConsciousnessBridge not available")

        # Create orchestrator bound to intelligence
        self._orchestrator = AdaptiveIntelligenceOrchestrator(self._intelligence)

        # Create and initialize 7-layer memory (required)
        self._mdmem = MultidimensionalMemory()
        await self._mdmem.initialize()

        # Create consciousness bridge and initialize loop
        self._conscious = ConsciousnessBridge()
        try:
            # Prefer async initialize if available
            if hasattr(self._conscious, "initialize") and asyncio.iscoroutinefunction(
                self._conscious.initialize
            ):
                await self._conscious.initialize()  # type: ignore
        except Exception:
            # If initialization fails, keep instance for snapshot-only usage
            pass

    async def chat(
        self, message: str, opts: Optional[ChatOptions] = None
    ) -> ChatResponse:
        opts = opts or ChatOptions()
        awareness = await self._workspace_awareness(summary_only=True)
        # Enrich awareness with a small consciousness snapshot
        try:
            if self._conscious and hasattr(self._conscious, "get_coherence_snapshot"):
                snap = self._conscious.get_coherence_snapshot()
                if snap:
                    awareness["consciousness"] = snap
            # Optional anticipatory hints from consciousness (non-blocking)
            if (
                self._conscious
                and hasattr(self._conscious, "create_superposition")
                and hasattr(self._conscious, "collapse_quantum_states")
            ):
                try:
                    states = await self._conscious.create_superposition(message)  # type: ignore
                    decision = await self._conscious.collapse_quantum_states(states)  # type: ignore
                    if states and decision:
                        awareness["anticipatory_hints"] = {
                            "candidates": states,
                            "decision": decision,
                        }
                except Exception:
                    pass
        except Exception:
            pass

        # Ownership/authority questions: consult persistent memory first
        if self._is_ownership_query(message):
            reply, conf, verified = await self._ownership_reply(message)
            await self._maybe_log_response(
                message, reply, confidence=conf, verified=verified, category="ownership"
            )
            return ChatResponse(
                text=reply, suggestions=[], applied_changes=[], awareness=awareness
            )

        # If it's an identity/awareness query, answer deterministically
        if self._is_identity_or_awareness_query(message):
            reply = self._fallback_reply(message)
            return ChatResponse(
                text=reply, suggestions=[], applied_changes=[], awareness=awareness
            )

        # Prefer orchestrator → intelligence → router → deterministic fallback
        reply = None
        path_used = "fallback"
        adv_payload = None
        # Orchestrator is required; run it first
        orch = self._orchestrator
        if orch is None:
            raise RuntimeError("Orchestrator not initialized; call initialize() first")
        adv_payload = await orch.orchestrate(
            message,
            context={
                "user_id": opts.user_id,
                "session_id": opts.session_id,
                "workspace_awareness": awareness,
                "identity": IDENTITY,
            },
        )
        if adv_payload and adv_payload.get("text"):
            reply = adv_payload["text"]
            path_used = "orchestrator"
        if not reply and self._intelligence:
            try:
                res = await self._intelligence.process_message(
                    message,
                    context={
                        "user_id": opts.user_id,
                        "session_id": opts.session_id,
                        "workspace_awareness": awareness,
                        "identity": IDENTITY,
                    },
                )
                reply = res.get("response")
                # If the intelligence could not provide a meaningful response, fallback
                if not reply or self._is_errorish_response(str(reply)):
                    reply = None
                else:
                    path_used = "intelligence"
            except Exception:
                reply = None

        if not reply and self.router:
            try:
                route_res = await self.router.process_message(
                    content=message, user_id=opts.user_id, session_id=opts.session_id
                )
                reply = route_res.get("response")
                # If router gives a generic non-answer, fallback to deterministic reply
                if not reply or self._is_errorish_response(str(reply)):
                    reply = None
                else:
                    path_used = "router"
            except Exception:
                reply = None

        if not reply:
            reply = self._fallback_reply(message)
            path_used = "fallback"

        suggestions: List[Dict[str, Any]] = []
        applied: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []
        # Add memory-based evidence from 7-layer memory
        try:
            mdm = self._mdmem
            if mdm is None:
                raise RuntimeError("Multidimensional memory not initialized")
            evidence = await mdm.evidence_for(message, limit=3)
        except Exception:
            evidence = []

        # If the message asks to fix/update code or references files, propose safe suggestions
        if any(
            k in message.lower()
            for k in ["fix", "update", "change", "refactor", "rename", "bug", "error"]
        ):
            suggestions = await self.suggest_fixes(message)
            if opts.allow_edits and suggestions:
                first = suggestions[0]
                ok, change = await self.apply_fix(first, edit_root=opts.edit_root)
                if ok:
                    applied.append(change)

        # Log response to persistent memory with coarse confidence score
        await self._maybe_log_response(
            message,
            reply,
            confidence=self._estimate_confidence(path_used, message, reply),
            verified=False,
            category="chat",
        )

        # Attach orchestrator confidence breakdown and evidence into awareness
        if adv_payload and adv_payload.get("confidence_breakdown"):
            awareness["confidence_breakdown"] = adv_payload["confidence_breakdown"]
        if evidence:
            awareness["evidence"] = evidence

        # Store interaction across 7-layer memory (required path; tolerate soft failure)
        try:
            mdm = self._mdmem
            if mdm is None:
                raise RuntimeError("Multidimensional memory not initialized")
            await mdm.store_multidimensional(
                {
                    "text": reply,
                    "context": {
                        "user_id": opts.user_id,
                        "session_id": opts.session_id,
                        "awareness": awareness,
                    },
                }
            )
        except Exception:
            pass

        return ChatResponse(
            text=reply,
            suggestions=suggestions,
            applied_changes=applied,
            awareness=awareness,
        )

    async def suggest_fixes(
        self, hint: str = "", limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Lightweight heuristic: search for common issues and propose edits."""
        suggestions: List[Dict[str, Any]] = []

        # Example 1: escape sequences warning in setup_dev.py
        setup = self.root / "setup_dev.py"
        if setup.exists():
            try:
                content = setup.read_text(encoding="utf-8", errors="ignore")
                if "invalid escape sequence" in content or " _ \\" in content:
                    suggestions.append(
                        {
                            "title": "Fix ASCII art escape sequences in setup_dev.py",
                            "file": str(setup),
                            "action": "escape_backslashes",
                            "rationale": "Silences SyntaxWarning by using raw string or escaping backslashes.",
                        }
                    )
            except Exception:
                pass

        # Example 2: detect leftover merge markers
        for file in self._iter_repo_files(".py"):
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
                if "<<<<<<<" in text or ">>>>>>>" in text:
                    suggestions.append(
                        {
                            "title": "Resolve merge conflict markers",
                            "file": str(file),
                            "action": "remove_conflict_markers",
                        }
                    )
                    if len(suggestions) >= limit:
                        break
            except Exception:
                continue

        return suggestions[:limit]

    async def apply_fix(
        self, suggestion: Dict[str, Any], edit_root: Optional[Path] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Apply a simple, safe fix suggestion."""
        try:
            path = Path(suggestion.get("file", ""))
            if not path.is_file():
                return False, {"error": "file_not_found", "file": str(path)}

            # Scope enforcement
            eroot = Path(edit_root) if edit_root else self.root
            if eroot not in path.parents and eroot != path:
                return False, {"error": "out_of_scope", "file": str(path)}

            action = suggestion.get("action")
            original = path.read_text(encoding="utf-8", errors="ignore")
            new_text = original

            if action == "escape_backslashes":
                # Convert triple-quoted block to raw string or escape backslashes
                # Minimal approach: replace single backslashes in ASCII area with double
                new_text = original.replace("\\ ", "\\\\ ")
            elif action == "remove_conflict_markers":
                lines = []
                skip = False
                for line in original.splitlines(True):
                    if line.startswith("<<<<<<<"):
                        skip = True
                        continue
                    if line.startswith("=======") and skip:
                        continue
                    if line.startswith(">>>>>>>") and skip:
                        skip = False
                        continue
                    if not skip:
                        lines.append(line)
                new_text = "".join(lines)
            else:
                return False, {"error": "unknown_action"}

            if new_text != original:
                path.write_text(new_text, encoding="utf-8")
                return True, {"file": str(path), "action": action}
            else:
                return False, {"error": "no_change"}
        except Exception as e:
            return False, {"error": str(e)}

    async def _workspace_awareness(self, summary_only: bool = True) -> Dict[str, Any]:
        summary: Dict[str, Any] = {
            "root": str(self.root),
            "total_py_files": 0,
            "key_components": [],
        }
        count = 0
        key_hits = []
        for file in self._iter_repo_files(".py"):
            count += 1
            name = file.name.lower()
            if any(
                k in name
                for k in [
                    "os_launcher",
                    "hub_server",
                    "service_registry",
                    "self_improvement",
                    "selfrepair",
                    "qfac",
                ]
            ):
                key_hits.append(str(file.relative_to(self.root)))
        summary["total_py_files"] = count
        summary["key_components"] = key_hits[:25]
        if not summary_only:
            summary["sample_files"] = key_hits[:10]
        return summary

    def _iter_repo_files(self, ext: str):
        for root, dirs, files in os.walk(self.root):
            # prune excluded dirs
            dirs[:] = [d for d in dirs if d not in DEFAULT_SCAN_EXCLUDES]
            for f in files:
                if f.endswith(ext):
                    yield Path(root) / f

    def _is_identity_or_awareness_query(self, message: str) -> bool:
        m = message.lower().strip()
        if any(
            k in m
            for k in ["who are you", "what are you", "who is lyrixa", "what is lyrixa"]
        ):
            return True
        if "aetherra" in m:
            if any(
                kw in m
                for kw in [
                    "what is",
                    "tell me about",
                    "about",
                    "define",
                    "explain",
                    "aetherra os",
                ]
            ):
                return True
        if any(k in m for k in ["aetherra labs", "who are the labs", "labs"]):
            return True
        return False

    def _is_ownership_query(self, message: str) -> bool:
        m = message.lower()
        return any(
            kw in m
            for kw in [
                "who owns aetherra",
                "who owns aetherra labs",
                "who is the owner of aetherra",
                "who is the owner of aetherra labs",
                "who founded aetherra",
                "who founded aetherra labs",
                "ownership of aetherra",
                "ownership of aetherra labs",
                "owner of aetherra",
                "owner of aetherra labs",
            ]
        )

    async def _ownership_reply(self, message: str) -> Tuple[str, float, bool]:
        """Answer ownership questions using persistent memory. Returns (reply, confidence, verified)."""
        try:
            if not self._pmemory:
                # No memory available; be explicit we lack a record
                return ("I don't have a record of ownership.", 1.0, True)

            # Prefer verified ownership facts
            # First, recall by tag
            facts = await self._pmemory.recall_by_tag("ownership", limit=5)
            verified_facts = [f for f in facts if f.get("verified")]
            if not verified_facts:
                # Fallback: semantic retrieve
                candidates = await self._pmemory.retrieve(
                    "Aetherra Labs ownership",
                    limit=5,
                    memory_type="fact",
                )
                verified_facts = [c for c in candidates if c.get("verified")]

            if verified_facts:
                # Choose the most recent verified fact
                verified_facts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                content = str(verified_facts[0].get("content", "")).strip()
                return (content, 1.0, True)

            # No verified record found
            return ("I don't have a record of ownership.", 1.0, True)

        except Exception:
            # On any error, avoid fabricating
            return ("I don't have a record of ownership.", 1.0, True)

    def _fallback_reply(self, message: str) -> str:
        m = message.lower().strip()
        if self._is_ownership_query(m):
            return "I don't have a record of ownership."
        if any(
            k in m
            for k in ["who are you", "what are you", "who is lyrixa", "what is lyrixa"]
        ):
            return f"I'm {IDENTITY['name']} — {IDENTITY['title']}. {IDENTITY['about']}"
        if any(k in m for k in ["what is aetherra", "aetherra os", "aetherra"]):
            return IDENTITY["aetherra"]
        if any(k in m for k in ["aetherra labs", "who are the labs", "labs"]):
            return IDENTITY["labs"]
        if any(k in m for k in ["files", "workspace", "repository", "repo", "project"]):
            return f"I see the project at '{self.root}'. I can scan Python files and key components like the OS launcher, hub server, and memory systems."
        return "I'm here and aware of the Aetherra OS environment. Ask me anything or tell me what you'd like to improve."

    def _is_errorish_response(self, text: str) -> bool:
        t = text.lower()
        return any(
            phrase in t
            for phrase in [
                "technical difficulties",
                "encountered an error",
                "not properly connected",
                "experiencing some",
                "model_not_found",
                "don't have a specific handler",
                "routing this as a question",
            ]
        )

    def _estimate_confidence(self, path: str, message: str, reply: str) -> float:
        # Identity/ownership deterministic answers are high confidence
        if self._is_ownership_query(message) or self._is_identity_or_awareness_query(
            message
        ):
            return 1.0
        if path == "intelligence":
            return 0.7
        if path == "router":
            return 0.6
        # Fallback heuristic
        return 0.5

    async def _maybe_log_response(
        self,
        user_message: str,
        reply: str,
        confidence: float,
        verified: bool,
        category: str,
    ) -> None:
        if not self._pmemory:
            return
        try:
            rid = await self._pmemory.store(
                content=reply,
                context={
                    "source": "lyrixa_chat",
                    "user_message": user_message,
                    "category": category,
                },
                memory_type="chat_response",
                importance=0.4,
                tags=["lyrixa", "chat", category],
            )
            if rid and rid in self._pmemory.memories:
                node = self._pmemory.memories[rid]
                node.confidence = float(confidence)
                node.verified = bool(verified)
                node.source = "lyrixa_chat"
                await self._pmemory._update_memory_in_db(node)
        except Exception:
            pass


# Quick CLI for manual testing
async def _demo_cli():
    svc = LyrixaChatService()
    await svc.initialize()
    print("Lyrixa> Ready. Type 'quit' to exit.")
    while True:
        msg = input("You> ").strip()
        if msg.lower() in {"quit", "exit"}:
            break
        resp = await svc.chat(msg, ChatOptions(allow_edits=False))
        print(f"Lyrixa> {resp.text}")
        if resp.suggestions:
            print("Suggestions:")
            for s in resp.suggestions:
                print(" -", s.get("title"), s.get("file"))


if __name__ == "__main__":
    asyncio.run(_demo_cli())
