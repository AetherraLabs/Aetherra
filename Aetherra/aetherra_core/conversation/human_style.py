"""
🗣️ Human Style Layer
====================

Lightweight, deterministic humanization layer for assistant responses.

Design goals:
- Deterministic by default (seeded by env) and safe for unit tests.
- No network calls; pure string transforms with small, tested rules.
- Env-driven persona, tone, and optional emoji/question toggles.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Tuple


def _get_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return str(v).strip() in {"1", "true", "yes", "on"}


def _get_str(name: str, default: str) -> str:
    v = os.environ.get(name)
    return default if v is None else str(v)


def _get_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


def _stable_choice(seed: int, bucket: int) -> bool:
    # Minimal deterministic pseudo-random using hashing on seed and bucket
    try:
        h = abs(hash((seed, bucket))) % 100
        return h % 3 == 0  # ~33% probability
    except Exception:
        return False


_CONTRACTIONS = (
    (r"\bI am\b", "I'm"),
    (r"\bwe are\b", "we're"),
    (r"\byou are\b", "you're"),
    (r"\bdo not\b", "don't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bcan not\b", "cannot"),  # better style than can't in technical contexts
    (r"\bcan\s*not\b", "cannot"),
    (r"\bit is\b", "it's"),
    (r"\bthat is\b", "that's"),
)


_EMPATHY_HINTS = (
    ("struggl", "I get how that can feel tricky."),
    ("confus", "Totally fair to be unsure here."),
    ("overwhelm", "Let's take it step by step."),
    ("error", "We can work through the error together."),
)


@dataclass
class HumanStyleMarkers:
    used_contractions: int = 0
    asked_question: bool = False
    used_empathy: bool = False


class HumanStyle:
    def __init__(self) -> None:
        self.enabled = _get_bool("AETHERRA_STYLE_ENABLED", True)
        self.persona = _get_str("AETHERRA_STYLE_PERSONA", "Lyrixa")
        self.tone = _get_str("AETHERRA_STYLE_TONE", "friendly").lower()
        self.use_emoji = _get_bool("AETHERRA_STYLE_EMOJI", False)
        self.ask_question = _get_bool("AETHERRA_STYLE_ASK_QUESTION", True)
        self.max_len = _get_int("AETHERRA_STYLE_MAX_LEN", 0)
        self.seed = _get_int("AETHERRA_STYLE_SEED", 13)

        # Optional safe emoji adapter
        try:
            from unicode_logger import safe_emoji_message  # type: ignore

            self._emoji_safe = safe_emoji_message
        except Exception:
            self._emoji_safe = lambda s: s

    def enhance(
        self,
        user_message: str,
        base_text: str,
        evidence_count: int = 0,
        bucket_index: int = 0,
    ) -> Tuple[str, HumanStyleMarkers]:
        """Return (styled_text, markers). If disabled, returns base_text unchanged."""
        if not self.enabled:
            return base_text, HumanStyleMarkers()

        text = base_text.strip()
        markers = HumanStyleMarkers()

        # 1) Tone and soft empathy opener (only when helpful)
        low = user_message.lower()
        empathy = None
        for hint, line in _EMPATHY_HINTS:
            if hint in low:
                empathy = line
                break
        if empathy and self.tone in ("friendly", "enthusiastic"):
            text = f"{empathy} {text}"
            markers.used_empathy = True

        # 2) Contractions pass (mild)
        before = text
        for pattern, repl in _CONTRACTIONS:
            try:
                text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
            except Exception:
                continue
        markers.used_contractions = 1 if text != before else 0

        # 3) Offer a concise follow-up question when appropriate
        if self.ask_question and _stable_choice(self.seed, bucket_index):
            if not text.rstrip().endswith("?"):
                # Short, open question varies with tone
                q = "What would you like to try next?"
                if self.tone == "friendly":
                    q = "What would you like to try next?"
                elif self.tone == "enthusiastic":
                    q = "What should we tackle next?"
                elif self.tone == "concise":
                    q = "Next step?"
                text = f"{text} {q}"
                markers.asked_question = True

        # 4) Optional, minimal emoji (1 symbol max) — safe-mapped
        if self.use_emoji:
            # add only if not a failure apology
            if ":" not in text and "sorry" not in text.lower():
                emoji = " 🙂" if self.tone in ("friendly", "enthusiastic") else ""
                if emoji:
                    text = self._emoji_safe(text + emoji)

        # 5) Max length clamp if configured
        if self.max_len and self.max_len > 20:
            if len(text) > self.max_len:
                text = text[: self.max_len - 1].rstrip() + "…"

        return text, markers
