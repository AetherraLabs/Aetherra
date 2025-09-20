"""Token counting strategy service."""

from __future__ import annotations

# Standard library imports
import os
from typing import Callable

# Local imports
from ..config import settings

TokenCounter = Callable[[str], int]


def _heuristic(text: str) -> int:
    try:
        return int(max(1, round((len(text or "")) / 4)))
    except Exception:
        return 1


def _tiktoken_counter(model: str) -> TokenCounter:
    try:  # pragma: no cover - optional dependency
        # Third party imports
        import tiktoken  # type: ignore

        try:
            enc = tiktoken.get_encoding(model)
        except Exception:
            try:
                enc = tiktoken.encoding_for_model(model)
            except Exception:
                enc = tiktoken.get_encoding("cl100k_base")

        def _cnt(text: str) -> int:
            try:
                return int(len(enc.encode(text or "")))
            except Exception:
                return _heuristic(text)

        return _cnt
    except Exception:
        return _heuristic


def _engine_counter() -> TokenCounter:
    def _cnt(text: str) -> int:
        try:
            # Standard library imports
            import asyncio

            # Aetherra imports
            from aetherra_service_registry import get_service_registry  # type: ignore

            async def _run():
                reg = await get_service_registry()
                info = reg.get_service_info("aetherra_engine")
                if not info or not info.instance:
                    return _heuristic(text)
                eng = info.instance
                for name in ("estimate_tokens", "count_tokens", "token_count"):
                    fn = getattr(eng, name, None)
                    if fn is not None:
                        try:
                            return int(fn(text))
                        except Exception:
                            continue
                return _heuristic(text)

            try:
                return asyncio.run(_run())
            except RuntimeError:  # already running loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Fallback heuristic inside existing loop to avoid complexity
                    return _heuristic(text)
                return loop.run_until_complete(_run())
        except Exception:
            return _heuristic(text)

    return _cnt


def create_token_counter() -> TokenCounter:
    mode = (
        (settings.tokenizer_mode or os.environ.get("AETHERRA_TOKENIZER", "heuristic"))
        .strip()
        .lower()
    )
    if mode == "tiktoken":  # optional
        model = os.environ.get("AETHERRA_TOKENIZER_MODEL", "cl100k_base")
        return _tiktoken_counter(model)
    if mode == "engine":
        return _engine_counter()
    return _heuristic


# Export default counter singleton
count_tokens = create_token_counter()
