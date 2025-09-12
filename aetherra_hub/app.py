"""Flask app factory for modular hub server.

Incrementally registers extracted blueprints; legacy monolith can be phased out.
"""

from __future__ import annotations

import asyncio
import logging
import os

from flask import Flask

try:
    from flask_cors import CORS  # optional
except Exception:  # pragma: no cover
    CORS = None  # type: ignore

from .blueprints import (
    ai_ask,
    ai_stream,
    chat,
    health,
    keb,
    kernel,
    klm,
    memory,  # memory graph stub
    metrics,
    openapi,
    peers,  # federation stub
    plugins,
    quantum,  # new
    site_status,
    telemetry,  # new
    trainer,  # new
)  # pylint: disable=unused-import
from .config import Settings, settings

logger = logging.getLogger(__name__)

# As more blueprints are extracted, import them here and add to the list below.

BLUEPRINTS = [
    openapi.bp,
    metrics.bp,
    health.bp,
    site_status.bp,
    kernel.bp,
    klm.bp,
    keb.bp,
    plugins.bp,
    chat.bp,
    ai_ask.bp,
    ai_stream.bp,
    quantum.bp,
    telemetry.bp,
    trainer.bp,
    peers.bp,
    memory.bp,
]


def create_app(cfg: Settings | None = None) -> Flask:
    cfg = cfg or settings
    app = Flask(__name__)
    # Attach settings for downstream blueprints / hooks
    app.settings = cfg  # type: ignore[attr-defined]

    # Early production hardening guard (fail-fast for insecure posture)
    def _prod_security_guard():
        profile = (os.environ.get("AETHERRA_PROFILE", "") or "").lower()
        if profile not in ("prod", "production"):
            return
        if os.environ.get("AETHERRA_PROD_UNSAFE_ALLOW", "0") == "1":
            logger.warning(
                "[SEC] UNSAFE OVERRIDE: AETHERRA_PROD_UNSAFE_ALLOW=1 set; skipping hardening boot guard"
            )
            return
        failures: list[str] = []
        # AI API token enforcement
        api_enabled = os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1"
        if api_enabled:
            require_token = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            token_present = bool(
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            )
            if not require_token or not token_present:
                failures.append("AI API enabled without enforced + configured token")
        # Capability strictness
        if os.environ.get("AETHERRA_REQUIRE_CAPABILITIES", "0") != "1":
            failures.append(
                "Capabilities enforcement not enabled (AETHERRA_REQUIRE_CAPABILITIES=1)"
            )
        # Script & plugin signing strictness
        if os.environ.get("AETHERRA_SCRIPT_VERIFY_STRICT", "0") != "1":
            failures.append(
                "Script strict verification not enabled (AETHERRA_SCRIPT_VERIFY_STRICT=1)"
            )
        if os.environ.get("AETHERRA_SIGNING_STRICT", "0") != "1":
            failures.append(
                "Plugin signing strict not enabled (AETHERRA_SIGNING_STRICT=1)"
            )
        # Network strictness baseline
        if os.environ.get("AETHERRA_NET_STRICT", "0") != "1":
            # Auto-enable with safe allowlist if not set
            os.environ.setdefault("AETHERRA_NET_STRICT", "1")
            os.environ.setdefault(
                "AETHERRA_NETWORK_ALLOWLIST", "localhost,127.0.0.1,.aetherra.dev"
            )
            logger.info(
                "[NET] Auto-enabled strict network policy with default allowlist"
            )
        if failures:
            msg = (
                "[SEC][ABORT] Insecure production posture detected:\n - "
                + "\n - ".join(failures)
                + "\nSet required env vars or (temporary) AETHERRA_PROD_UNSAFE_ALLOW=1 to bypass."
            )
            logger.error(msg)
            raise RuntimeError("production_security_guard_failed")

    _prod_security_guard()

    if CORS:
        try:
            CORS(app)  # type: ignore
        except Exception:
            logger.warning("CORS init failed")

    for bp in BLUEPRINTS:
        if bp.name == "plugins":  # register with prefix for cleaner route paths
            app.register_blueprint(bp, url_prefix="/api/plugins")
        else:
            app.register_blueprint(bp)

    # Optional engine reset on startup (test/support use-cases)
    def _maybe_reset_engine():
        if not (
            os.environ.get("AETHERRA_HUB_RESET_ENGINE_ON_START", "0") == "1"
            or os.environ.get("AETHERRA_TEST_RESET_ENGINE", "0") == "1"
        ):
            return
        try:
            from aetherra_service_registry import (  # type: ignore
                get_service_registry,
            )

            async def _do():
                reg = await get_service_registry()
                try:
                    await reg.unregister_service("aetherra_engine")
                except Exception:
                    pass

            # Run quickly (non-blocking degrade if fails)
            asyncio.run(_do())
            logger.info(
                "Engine reset requested by env var; unregistered existing engine instance if present"
            )
        except Exception:
            logger.warning("Engine reset requested but failed", exc_info=False)

    _maybe_reset_engine()

    @app.get("/api/ping")
    def _ping():  # simple liveness
        return {"pong": True}

    @app.before_request
    def _log_req():  # lightweight request logging
        try:
            if getattr(app, "settings", None) and app.settings.log_requests:  # type: ignore[attr-defined]
                from flask import request

                logger.info("REQ %s %s", request.method, request.path)
        except Exception:
            pass

    return app
