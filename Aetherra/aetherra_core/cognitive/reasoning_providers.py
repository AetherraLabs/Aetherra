"""Reasoning provider adapter interfaces (Wave A bootstrap).

Lightweight abstraction layer to allow plugging different LLM/tool routing backends
behind a consistent async interface without immediately disturbing existing
`ReasoningEngine` and `AetherraEngine` call sites.

Design goals (initial):
 - Zero hard dependencies: all provider imports are optional/best‑effort.
 - Fast failure + graceful fallback to placeholder reasoning text.
 - Simple metrics hooks (function attributes) so the hub metrics exporter can
   discover counters later without tight coupling.
 - Safe for test/profile environments with deterministic output when
   AETHERRA_PROFILE=test.

Environment variables (primary + plain aliases):
 - AETHERRA_INTELLIGENCE_PROVIDER (primary) = openai | anthropic | ollama | mock
 - AETHERRA_PROVIDER (alias; preferred simpler name) same accepted values
 - AETHERRA_MAX_TOKENS (optional, int) soft limit hint passed to providers.

Future (not implemented yet but reserved):
 - Tool injection (planner -> tool execution -> synthesis)
 - Cost / token usage accounting (prompt_tokens, completion_tokens)
 - Streaming callbacks (chunk/thought/tool) — align with engine callbacks
"""

from __future__ import annotations

# Standard library imports
import abc
import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:  # Optional prometheus_client instrumentation (best‑effort)
    from prometheus_client import Counter, Histogram  # type: ignore

    _PROVIDER_LATENCY = Histogram(
        "aetherra_reasoning_provider_latency_seconds",
        "Latency of provider reasoning calls",
        ["provider"],
        buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
    )
    _PROVIDER_CALLS = Counter(
        "aetherra_reasoning_provider_calls_total",
        "Total reasoning provider calls",
        ["provider", "status"],
    )
    _PROVIDER_EVIDENCE = Histogram(
        "aetherra_reasoning_evidence_items",
        "Evidence items surfaced per reasoning call",
        buckets=(0, 1, 2, 3, 5, 8, 13),
    )
except Exception:  # pragma: no cover - metrics optional
    _PROVIDER_LATENCY = None
    _PROVIDER_CALLS = None
    _PROVIDER_EVIDENCE = None


@dataclass
class ProviderResult:
    """Normalized provider result returned to the engine.

    Fields intentionally small; richer structures can be hung off metadata.
    """

    text: str
    provider: str
    model: Optional[str] = None
    confidence: float = 0.75
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseProvider(abc.ABC):
    """Abstract provider interface."""

    name: str = "base"

    def __init__(self):  # pragma: no cover - trivial
        self.max_tokens_hint: Optional[int] = None
        try:
            if os.getenv("AETHERRA_MAX_TOKENS"):
                self.max_tokens_hint = int(os.getenv("AETHERRA_MAX_TOKENS", "0")) or None
        except Exception:
            self.max_tokens_hint = None

    @abc.abstractmethod
    async def reason(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # noqa: D401
        """Produce a reasoning/result text for the given prompt."""

    # Synchronous wrapper for call sites that are still sync
    def reason_blocking(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # pragma: no cover - thin wrapper
        return asyncio.run(self.reason(prompt, evidence=evidence))


# --- Provider Implementations (stubs / minimal) ---


class MockProvider(BaseProvider):  # pragma: no cover - deterministic path
    name = "mock"

    async def reason(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # noqa: D401
        parts: list[str] = []
        for e in evidence or []:
            try:
                if isinstance(e, dict):
                    c = e.get("content")
                    if isinstance(c, str) and c:
                        parts.append(c[:40])
            except Exception:
                continue
        ev_txt = " | ".join(parts)
        if ev_txt:
            msg = f"[mock] Based on evidence: {ev_txt} -> {prompt[:120]}"
        else:
            msg = f"[mock] {prompt[:160]}"
        return ProviderResult(text=msg, provider=self.name, model="mock.v1", confidence=0.6)


class OpenAIProvider(BaseProvider):  # pragma: no cover - network + optional
    name = "openai"

    def __init__(self):
        super().__init__()
        self._client = None
        try:
            import openai  # type: ignore

            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AETHERRA_OPENAI_KEY")
            if api_key:
                openai.api_key = api_key
                self._client = openai
        except Exception:
            self._client = None

    async def reason(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # noqa: D401
        if not self._client:
            return ProviderResult(
                text=f"[openai:unavailable] {prompt[:140]}",
                provider=self.name,
                model=None,
                confidence=0.4,
            )
        model = os.getenv("AETHERRA_OPENAI_MODEL", "gpt-4o-mini")
        # Merge evidence into a simple system preface
        sys_preface = (
            "You are Aetherra reasoning module. Provide concise grounded answer."  # keep short
        )
        if evidence:
            items: list[str] = []
            for e in evidence:
                try:
                    if isinstance(e, dict):
                        c = e.get("content")
                        if isinstance(c, str) and c:
                            items.append(f"- {c[:200]}")
                except Exception:
                    continue
            if items:
                joined = "\n".join(items)
                sys_preface += f"\nEvidence:\n{joined}"[:4000]
        try:
            # Minimal non-streaming call
            chat_api = getattr(self._client, "ChatCompletion", None)
            if chat_api is None:
                return ProviderResult(
                    text=f"[openai:unavailable] {prompt[:140]}",
                    provider=self.name,
                    model=model,
                    confidence=0.4,
                )
            resp = await asyncio.to_thread(
                chat_api.create,
                model=model,
                messages=[
                    {"role": "system", "content": sys_preface},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens_hint or 512,
                temperature=0.2,
            )
            try:
                txt = resp.choices[0].message["content"] if resp and resp.choices else "(empty)"
            except Exception:
                txt = str(resp)
            usage = getattr(resp, "usage", None)
            return ProviderResult(
                text=txt,
                provider=self.name,
                model=model,
                confidence=0.7,
                usage=dict(usage) if usage else None,
            )
        except Exception as e:  # degrade
            return ProviderResult(
                text=f"[openai:error:{type(e).__name__}] {prompt[:140]}",
                provider=self.name,
                model=model,
                confidence=0.4,
            )


class AnthropicProvider(BaseProvider):  # pragma: no cover - network + optional
    name = "anthropic"

    def __init__(self):
        super().__init__()
        self._client = None
        try:
            import anthropic  # type: ignore

            key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("AETHERRA_ANTHROPIC_KEY")
            if key:
                self._client = anthropic.Client(api_key=key)
        except Exception:
            self._client = None

    async def reason(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # noqa: D401
        if not self._client:
            return ProviderResult(
                text=f"[anthropic:unavailable] {prompt[:140]}", provider=self.name, confidence=0.4
            )
        model = os.getenv("AETHERRA_ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        # Simple evidence injection
        if evidence:
            items: list[str] = []
            for e in evidence:
                try:
                    if isinstance(e, dict):
                        c = e.get("content")
                        if isinstance(c, str) and c:
                            items.append(f"- {c[:200]}")
                except Exception:
                    continue
            if items:
                prompt = ("Evidence:\n" + "\n".join(items) + "\n\nUser: " + prompt)[:8000]
        try:
            resp = await asyncio.to_thread(
                self._client.messages.create,
                model=model,
                max_tokens=self.max_tokens_hint or 512,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )
            txt = (
                "".join(
                    p.text for m in getattr(resp, "content", []) for p in getattr(m, "text", [])
                )
                if hasattr(resp, "content")
                else str(resp)
            )
            return ProviderResult(text=txt[:8000], provider=self.name, model=model, confidence=0.72)
        except Exception as e:  # fallback path
            return ProviderResult(
                text=f"[anthropic:error:{type(e).__name__}] {prompt[:140]}",
                provider=self.name,
                model=model,
                confidence=0.4,
            )


class OllamaProvider(BaseProvider):  # pragma: no cover - local optional
    name = "ollama"

    def __init__(self):
        super().__init__()
        self._client = None
        try:
            import ollama  # type: ignore

            self._client = ollama
        except Exception:
            self._client = None

    async def reason(
        self, prompt: str, *, evidence: list[dict[str, Any]] | None = None
    ) -> ProviderResult:  # noqa: D401
        if not self._client:
            return ProviderResult(
                text=f"[ollama:unavailable] {prompt[:140]}", provider=self.name, confidence=0.4
            )
        model = os.getenv("AETHERRA_OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "llama3.1"))
        if evidence:
            items: list[str] = []
            for e in evidence:
                try:
                    if isinstance(e, dict):
                        c = e.get("content")
                        if isinstance(c, str) and c:
                            items.append(f"- {c[:120]}")
                except Exception:
                    continue
            if items:
                prompt = ("Evidence:\n" + "\n".join(items) + "\n\n" + prompt)[:6000]
        try:
            resp = await asyncio.to_thread(
                self._client.chat,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.2,
                    **({"num_predict": self.max_tokens_hint} if self.max_tokens_hint else {}),
                },
            )
            txt = (
                resp.get("message", {}).get("content", "(empty)")
                if isinstance(resp, dict)
                else str(resp)
            )
            return ProviderResult(text=txt[:8000], provider=self.name, model=model, confidence=0.7)
        except Exception as e:
            return ProviderResult(
                text=f"[ollama:error:{type(e).__name__}] {prompt[:140]}",
                provider=self.name,
                model=model,
                confidence=0.45,
            )


def build_provider(name: str | None) -> BaseProvider:
    # Accept both original and simplified env naming; caller passes explicit name or we fallback later.
    name = (name or "").strip().lower() or "mock"
    if name in {"openai", "oai"}:
        return OpenAIProvider()
    if name in {"anthropic", "claude"}:
        return AnthropicProvider()
    if name in {"ollama"}:
        return OllamaProvider()
    return MockProvider()


async def call_provider(
    prompt: str, *, evidence: list[dict[str, Any]] | None = None, provider_name: str | None = None
) -> ProviderResult:
    """Resolve provider by name/env and execute reasoning.

    Metrics (best‑effort) recorded if prometheus_client is available.
    """

    # Realistic alias acceptance: prefer explicit provider_name, else simpler alias, else legacy env.
    prov_name_env = (
        provider_name
        or os.getenv("AETHERRA_PROVIDER")
        or os.getenv("AETHERRA_INTELLIGENCE_PROVIDER")
    )
    provider = build_provider(prov_name_env)
    t0 = time.time()
    status = "ok"
    try:
        result = await provider.reason(prompt, evidence=evidence)
    except Exception as e:  # pragma: no cover - defensive
        status = "error"
        result = ProviderResult(
            text=f"[{provider.name}:exception:{type(e).__name__}] {prompt[:120]}",
            provider=provider.name,
            confidence=0.3,
            metadata={"error": str(e)},
        )
    dt = time.time() - t0
    try:  # metrics
        if _PROVIDER_LATENCY:
            _PROVIDER_LATENCY.labels(provider=provider.name).observe(dt)
        if _PROVIDER_CALLS:
            _PROVIDER_CALLS.labels(provider=provider.name, status=status).inc()
        if _PROVIDER_EVIDENCE and evidence is not None:
            _PROVIDER_EVIDENCE.observe(len(evidence))
    except Exception:
        pass
    return result


__all__ = [
    "ProviderResult",
    "BaseProvider",
    "MockProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "build_provider",
    "call_provider",
]
