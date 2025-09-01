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
    from Aetherra.core.chat_router import (
        create_chat_router,
        example_command_handler,
        example_question_handler,
    )
except Exception:
    create_chat_router = None
    example_question_handler = None  # type: ignore
    example_command_handler = None  # type: ignore

try:
    from Aetherra.lyrixa.intelligence.lyrixa_full_intelligence import (
        get_lyrixa_intelligence,
    )
except Exception:
    get_lyrixa_intelligence = None

# Optional: service registry
try:
    from aetherra_service_registry import get_service_registry
except Exception:
    get_service_registry = None

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
        # If router is available, register basic helpful handlers so we don't fall back to generic messages
        try:
            if self.router and example_question_handler and example_command_handler:
                self.router.register_handler(
                    "question_handler", example_question_handler
                )  # type: ignore[arg-type]
                self.router.register_handler("command_handler", example_command_handler)  # type: ignore[arg-type]
        except Exception:
            pass

    async def initialize(self):
        # Try to connect to service registry
        if get_service_registry:
            try:
                self.registry = await get_service_registry()
            except Exception:
                self.registry = None
        # Warm up intelligence if available (allow forcing in quiet mode)
        try:
            force_intel = os.getenv("AETHERRA_LYRIXA_FORCE_INTELLIGENCE", "0") == "1"
            offline = os.getenv("AETHERRA_OFFLINE", "0") == "1"
            if get_lyrixa_intelligence and (force_intel or not offline):
                self._intelligence = await get_lyrixa_intelligence()
        except Exception:
            self._intelligence = None

        # Ensure the router has a friendly conversation handler fallback
        try:
            if self.router and "conversation_handler" not in getattr(
                self.router, "handlers", {}
            ):

                async def _conv_handler(message, routing_result):  # type: ignore[no-redef]
                    try:
                        content = getattr(message, "content", "")
                    except Exception:
                        content = ""
                    base = "I hear you."
                    if content:
                        base = f"You said: '{content}'."
                    return base + " How can I help you with the Aetherra project?"

                self.router.register_handler("conversation_handler", _conv_handler)  # type: ignore[arg-type]
        except Exception:
            pass

    async def chat(
        self, message: str, opts: Optional[ChatOptions] = None
    ) -> ChatResponse:
        opts = opts or ChatOptions()
        awareness = await self._workspace_awareness(summary_only=True)

        # If it's an identity/awareness query, answer deterministically
        if self._is_identity_or_awareness_query(message):
            reply = self._fallback_reply(message)
            return ChatResponse(
                text=reply, suggestions=[], applied_changes=[], awareness=awareness
            )

        # Prefer Lyrixa intelligence; fall back to router; then rules
        reply = None
        if self._intelligence:
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
            except Exception:
                reply = None

        if not reply:
            reply = self._fallback_reply(message)

        suggestions: List[Dict[str, Any]] = []
        applied: List[Dict[str, Any]] = []

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

    def _fallback_reply(self, message: str) -> str:
        m = message.lower().strip()
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
