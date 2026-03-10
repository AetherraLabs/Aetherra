#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Adaptive Intelligence Orchestrator
==================================

Full orchestrator that:
- Classifies query intent
- Selects provider ensemble based on capability matrix
- Runs providers in parallel (where possible)
- Synthesizes final response with confidence breakdown and basic evidence

This integrates with the existing Lyrixa intelligence instance if provided,
and augments it by probing configured providers exposed on that instance.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import difflib
import logging
import statistics
from typing import Any, cast


class AdaptiveIntelligenceOrchestrator:
    def __init__(self, intelligence: Any = None):
        # intelligence: a LyrixaIntelligenceCore with .providers and .process_message
        self.intelligence: Any = intelligence
        # Simple capability matrix by intent
        self.capabilities = {
            "analytical": ["openai", "anthropic"],
            "creative": ["anthropic", "openai"],
            "coding": ["openai"],
            "scientific": ["openai", "anthropic"],
            "general": ["openai", "anthropic"],
        }

    async def orchestrate(
        self, message: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        if not self.intelligence or not getattr(self.intelligence, "providers", None):
            return None

        ctx: dict[str, Any] = context or {}
        intent = self._classify_intent(message)
        provider_names = self._select_providers(intent)
        if not provider_names:
            return None

        # Fire providers in parallel and gather results
        results: list[tuple[str, dict[str, Any]]] = []
        tasks = [self._run_provider(name, message, ctx) for name in provider_names]
        done = await asyncio.gather(*tasks, return_exceptions=True)
        for name, res in zip(provider_names, done, strict=True):
            if isinstance(res, Exception) or not isinstance(res, dict):
                continue
            if res.get("response") and not self._looks_errorish(str(res.get("response"))):
                results.append((name, res))

        if not results:
            return None

        text, cb, evidence = self._synthesize(results, message, ctx)
        return {"text": text, "confidence_breakdown": cb, "evidence": evidence}

    def _looks_errorish(self, t: str) -> bool:
        t = t.lower()
        return any(
            k in t
            for k in [
                "technical difficulties",
                "encountered an error",
                "not properly connected",
                "experiencing some",
                "model_not_found",
                "don't have a specific handler",
                "routing this as a question",
            ]
        )

    def _classify_intent(self, message: str) -> str:
        m = message.lower()
        if any(k in m for k in ["code", "bug", "refactor", "function", "class"]):
            return "coding"
        if any(k in m for k in ["prove", "theorem", "equation", "data", "statistical"]):
            return "scientific"
        if any(k in m for k in ["story", "poem", "creative", "lyrics"]):
            return "creative"
        if any(k in m for k in ["why", "how", "analyze", "explain", "compare"]):
            return "analytical"
        return "general"

    def _select_providers(self, intent: str) -> list[str]:
        # If intelligence is missing, no providers
        if not self.intelligence:
            return []
        providers: list[str] = []
        wanted = self.capabilities.get(intent, [])
        providers_map = cast(dict[str, Any], getattr(self.intelligence, "providers", {}))
        for name in wanted:
            p = providers_map.get(name)
            if p and p.get("available"):
                providers.append(name)
        # fallback to any available if none matched
        if not providers:
            for name, p in providers_map.items():
                if p.get("available"):
                    providers.append(name)
        return providers[:2]  # cap ensemble size

    async def _run_provider(self, name: str, message: str, ctx: dict[str, Any]) -> dict[str, Any]:
        # Use the intelligence pipeline but bias to provider by temporarily switching active_provider
        if not self.intelligence:
            return {}
        active_before = getattr(self.intelligence, "active_provider", None)
        try:
            self.intelligence.active_provider = name
            return await self.intelligence.process_message(message, ctx)
        finally:
            self.intelligence.active_provider = active_before

    def _synthesize(
        self,
        results: list[tuple[str, dict[str, Any]]],
        message: str,
        ctx: dict[str, Any],
    ) -> tuple[str, dict[str, float], list[dict[str, Any]]]:
        # Rank by length as a baseline
        ranked = sorted(results, key=lambda kv: len(str(kv[1].get("response", ""))), reverse=True)
        best_name, best_res = ranked[0]
        best_text = str(best_res.get("response", "")).strip()

        # Compute simple consensus across provider responses
        texts = [str(r[1].get("response", "")) for r in results]
        consensus_scores: list[float] = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                consensus_scores.append(difflib.SequenceMatcher(None, texts[i], texts[j]).ratio())
        consensus = statistics.mean(consensus_scores) if consensus_scores else 0.0

        # Pull coherence signal if present in context awareness
        coherence = 0.7
        try:
            awareness = ctx.get("workspace_awareness", {}) or {}
            conc = awareness.get("consciousness", {}) or {}
            coherence = float(conc.get("coherence", coherence))
        except Exception:
            logging.exception("Exception extracting coherence from context")

        # Provider reliability (static defaults, allow override from intelligence providers)
        provider_reliability_defaults = {"openai": 0.9, "anthropic": 0.86, "local": 0.6}
        reliability = provider_reliability_defaults.get(best_name, 0.7)
        try:
            prov = None
            if hasattr(self.intelligence, "providers"):
                prov = getattr(self.intelligence, "providers", {}).get(best_name)
            if isinstance(prov, dict):
                # optional explicit reliability on provider config
                reliability = float(prov.get("reliability", reliability))
                # slightly boost if higher priority (lower number means preferred)
                prio = prov.get("priority")
                if isinstance(prio, int):
                    reliability = float(
                        max(0.0, min(1.0, reliability + (0.02 if prio == 1 else 0.0)))
                    )
        except Exception:
            logging.exception("Exception extracting provider reliability")

        # Memory match strength based on memories used (intelligence returns count)
        memories_used = int(best_res.get("memories_used", 0) or 0)
        # map count -> [0.3, 0.95] logarithmically with diminishing returns
        mem_match = 0.3
        try:
            if memories_used > 0:
                mem_match = float(min(0.95, 0.3 + 0.25 * (1 + (memories_used**0.5))))
        except Exception:
            logging.exception("Exception calculating memory match strength")

        # Confidence breakdown with richer signals (preserve existing keys)
        model_signal = 0.82 if best_name == "openai" else 0.76
        cb = {
            "model": model_signal,
            "grounding": float(min(0.95, 0.5 + 0.07 * memories_used)),
            "coherence": float(max(0.0, min(1.0, coherence))),
            "consensus": float(round(consensus, 3)),
            "safety": 0.92,
            # new detailed signals
            "provider_reliability": float(round(reliability, 3)),
            "memory_match": float(round(mem_match, 3)),
        }

        # Compute an overall score (additive weights normalized), without removing existing fields
        try:
            overall = (
                0.25 * cb["model"]
                + 0.2 * cb["provider_reliability"]
                + 0.2 * cb["grounding"]
                + 0.15 * cb["memory_match"]
                + 0.1 * cb["coherence"]
                + 0.1 * cb["consensus"]
            )
            cb["overall"] = float(round(max(0.0, min(1.0, overall)), 3))
        except Exception:
            logging.exception("Exception calculating overall confidence score")

        # Evidence payload: top provider picks + memory usage
        evidence: list[dict[str, Any]] = []
        if memories_used:
            evidence.append({"type": "memory_usage", "count": memories_used})
        # Include brief provider attribution
        evidence.append(
            {
                "type": "provider_selection",
                "chosen": best_name,
                "alternates": [name for name, _ in ranked[1:3]],
            }
        )

        # Add weighting evidence for transparency
        evidence.append(
            {
                "type": "weighting",
                "provider_reliability": float(round(reliability, 3)),
                "memory_match": float(round(mem_match, 3)),
                "consensus": float(round(consensus, 3)),
                "coherence": float(round(coherence, 3)),
                "model_signal": float(round(model_signal, 3)),
            }
        )

        return best_text, cb, evidence
