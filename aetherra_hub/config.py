"""Centralized settings for hub server.

Reads environment once; other modules import Settings.from_env() once at app startup.
"""

from __future__ import annotations

# Standard library imports
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(slots=True)
class Settings:
    # Existing / legacy fields
    ai_api_enabled: bool = False
    ai_api_stream: bool = False
    ai_api_require_token: bool = False
    ai_api_token: str = ""
    ws_enabled: bool = False
    prod_profile: bool = False
    idem_ttl_sec: int = 120
    idem_enforce: bool = False
    chat_version_required: bool = False
    tokenizer_mode: str = "heuristic"  # heuristic|tiktoken|engine

    # New plugin + logging / policy fields (backward compatible defaults)
    log_requests: bool = True
    require_plugin_signature: bool = False
    max_description_len: int = 2000
    max_payload_kb: int = 256
    idempotency_ttl_seconds: int = 600

    # Newly implemented previously doc-only env flags (minimal semantics):
    coherence_gate_min: float = 0.0  # AETHERRA_COHERENCE_GATE_MIN
    coherence_hard_min: float = 0.0  # AETHERRA_COHERENCE_HARD_MIN
    drift_alert_min: float = 0.0  # AETHERRA_DRIFT_ALERT_MIN
    engine_wait_ms: int = 0  # AETHERRA_ENGINE_WAIT_MS (legacy pacing placeholder)
    hub_debug_metrics: bool = False  # AETHERRA_HUB_DEBUG_METRICS
    hub_reset_engine_on_start: bool = False  # AETHERRA_HUB_RESET_ENGINE_ON_START
    observer_aware_enabled: bool = False  # AETHERRA_OBSERVER_AWARE_ENABLED
    sse_replay_max_age_s: int = 0  # AETHERRA_SSE_REPLAY_MAX_AGE_S
    sse_replay_max_events: int = 0  # AETHERRA_SSE_REPLAY_MAX_EVENTS
    stream_soft_timeout_s: int = 0  # AETHERRA_STREAM_SOFT_TIMEOUT_S
    test_reset_engine: bool = False  # AETHERRA_TEST_RESET_ENGINE (test-only trigger)

    @staticmethod
    @lru_cache(maxsize=1)
    def from_env() -> Settings:  # type: ignore[name-defined]
        profile = (os.environ.get("AETHERRA_PROFILE", "") or "").strip().lower()
        prod = profile in ("prod", "production")
        default_require = "1" if prod else "0"
        return Settings(
            ai_api_enabled=os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1",
            ai_api_stream=os.environ.get("AETHERRA_AI_API_STREAM", "0") == "1",
            ai_api_require_token=os.environ.get(
                "AETHERRA_AI_API_REQUIRE_TOKEN", default_require
            )
            == "1",
            ai_api_token=(
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                or ""
            ).strip(),
            ws_enabled=os.environ.get("AETHERRA_AI_API_WS", "0") == "1",
            prod_profile=prod,
            idem_ttl_sec=int(
                os.environ.get("AETHERRA_IDEMPOTENCY_TTL_SEC", "120") or 120
            ),
            idem_enforce=os.environ.get("AETHERRA_IDEMPOTENCY_ENFORCE", "0") == "1",
            chat_version_required=os.environ.get("AETHERRA_CHAT_VERSION_REQUIRED", "0")
            == "1",
            tokenizer_mode=(
                os.environ.get("AETHERRA_TOKENIZER", "heuristic") or "heuristic"
            ).lower(),
            log_requests=(
                os.environ.get("AETH_LOG_REQUESTS", "1").lower()
                in {"1", "true", "yes", "on"}
            ),
            require_plugin_signature=(
                os.environ.get("AETH_REQUIRE_PLUGIN_SIGNATURE", "0").lower()
                in {"1", "true", "yes", "on"}
            ),
            max_description_len=int(
                os.environ.get("AETH_MAX_PLUGIN_DESC", "2000") or 2000
            ),
            max_payload_kb=int(os.environ.get("AETH_MAX_PAYLOAD_KB", "256") or 256),
            idempotency_ttl_seconds=int(
                os.environ.get("AETH_IDEMPOTENCY_TTL", "600") or 600
            ),
            coherence_gate_min=float(
                os.environ.get("AETHERRA_COHERENCE_GATE_MIN", "0") or 0
            ),
            coherence_hard_min=float(
                os.environ.get("AETHERRA_COHERENCE_HARD_MIN", "0") or 0
            ),
            drift_alert_min=float(os.environ.get("AETHERRA_DRIFT_ALERT_MIN", "0") or 0),
            engine_wait_ms=int(os.environ.get("AETHERRA_ENGINE_WAIT_MS", "0") or 0),
            hub_debug_metrics=(
                os.environ.get("AETHERRA_HUB_DEBUG_METRICS", "0").lower()
                in {"1", "true", "yes", "on"}
            ),
            hub_reset_engine_on_start=(
                os.environ.get("AETHERRA_HUB_RESET_ENGINE_ON_START", "0").lower()
                in {"1", "true", "yes", "on"}
            ),
            observer_aware_enabled=(
                os.environ.get("AETHERRA_OBSERVER_AWARE_ENABLED", "0").lower()
                in {"1", "true", "yes", "on"}
            ),
            sse_replay_max_age_s=int(
                os.environ.get("AETHERRA_SSE_REPLAY_MAX_AGE_S", "0") or 0
            ),
            sse_replay_max_events=int(
                os.environ.get("AETHERRA_SSE_REPLAY_MAX_EVENTS", "0") or 0
            ),
            stream_soft_timeout_s=int(
                os.environ.get("AETHERRA_STREAM_SOFT_TIMEOUT_S", "0") or 0
            ),
            test_reset_engine=(
                os.environ.get("AETHERRA_TEST_RESET_ENGINE", "0").lower()
                in {"1", "true", "yes", "on"}
            ),
        )


settings = Settings.from_env()
