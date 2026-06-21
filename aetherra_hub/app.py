"""Flask app factory for modular hub server.

Incrementally registers extracted blueprints; legacy monolith can be phased out.
"""

from __future__ import annotations

# Standard library imports
import asyncio
import contextlib
import logging
import os

# Third party imports
from flask import Flask

# Optional CORS support with dynamic import to avoid type stub errors
try:
    # Standard library imports
    import importlib

    _flask_cors = importlib.import_module("flask_cors")
    CORS = getattr(_flask_cors, "CORS", None)
except Exception:  # pragma: no cover
    CORS = None

# Local imports
from .blueprints import (  # pylint: disable=unused-import
    agents,
    ai_ask,
    ai_stream,
    chat,
    coding,
    consciousness,  # consciousness state API
    frontend,  # static file serving for Lyrixa UI
    guardian,
    health,
    homeostasis,  # new
    interactive,  # Interactive Lyrixa emotions & expressions
    keb,
    kernel,
    klm,
    maintenance,
    memory,  # memory graph stub
    metrics,
    openapi,
    peers,  # federation stub
    plugins,
    policy,
    qfac_admin,
    quantum,  # new
    runtime_ui,
    scripts,  # new
    security,  # new
    self_improvement,  # new
    self_incorporation,  # new
    site_status,
    telemetry,  # new
    trainer,  # new
)
from .config import Settings, settings

logger = logging.getLogger(__name__)

# As more blueprints are extracted, import them here and add to the list below.

BLUEPRINTS = [
    openapi.bp,
    metrics.bp,
    health.bp,
    guardian.bp,
    site_status.bp,
    qfac_admin.bp,
    kernel.bp,
    klm.bp,
    keb.bp,
    plugins.bp,
    maintenance.bp,
    homeostasis.bp,
    consciousness.bp,  # Consciousness state API
    interactive.bp,  # Interactive Lyrixa emotions & expressions
    agents.bp,
    chat.bp,
    coding.bp,
    policy.bp,
    ai_ask.bp,
    ai_stream.bp,
    quantum.bp,
    telemetry.bp,
    trainer.bp,
    peers.bp,
    memory.bp,
    self_incorporation.bp,
    self_improvement.bp,
    scripts.bp,
    security.bp,
    runtime_ui.bp,
    # Frontend MUST be last - catches all remaining routes for SPA
    frontend.bp,
]


def create_app(cfg: Settings | None = None) -> Flask:
    cfg = cfg or settings
    app = Flask(__name__)
    # Attach settings for downstream blueprints / hooks
    app.settings = cfg  # type: ignore[attr-defined]

    # Early production hardening guard (fail-fast for insecure posture)
    def _prod_security_guard() -> None:
        profile = (os.environ.get("AETHERRA_PROFILE", "") or "").lower()
        if profile not in ("prod", "production"):
            return
        if os.environ.get("AETHERRA_PROD_UNSAFE_ALLOW", "0") == "1":
            logger.warning(
                "[SEC] UNSAFE OVERRIDE: AETHERRA_PROD_UNSAFE_ALLOW=1 set; skipping hardening boot guard"
            )
            return
        failures: list[str] = []
        warnings: list[str] = []

        # AI API token enforcement
        api_enabled = os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1"
        if api_enabled:
            require_token_env = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0")
            require_token = require_token_env == "1"  # noqa: S105 - env flag sentinel
            token_present = bool(
                os.environ.get("AETHERRA_AI_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            )
            logger.info(
                "[SEC][DIAG] AI API security check: require_token=%s token_present=%s token_len=%s hub_token_len=%s",
                require_token,
                token_present,
                len(os.environ.get("AETHERRA_AI_API_TOKEN", "")),
                len(os.environ.get("AETHERRA_HUB_CONTROL_TOKEN", "")),
            )
            if not require_token:
                failures.append(
                    "AI API token enforcement not enabled (AETHERRA_AI_API_REQUIRE_TOKEN=1)"
                )
            elif not token_present:
                failures.append(
                    "AI API token enforcement failed (AETHERRA_AI_API_REQUIRE_TOKEN=1 but no token present)"
                )

        # Hub control token check
        if not os.environ.get("AETHERRA_HUB_CONTROL_TOKEN"):
            warnings.append("Hub control token not set (AETHERRA_HUB_CONTROL_TOKEN)")

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

        # STORM shadow mode enforcement in production
        storm_enabled = os.environ.get("AETHERRA_MEMORY_STORM", "0") == "1"
        if storm_enabled:
            shadow_mode = os.environ.get("AETHERRA_STORM_SHADOW_MODE", "0") == "1"
            if not shadow_mode:
                warnings.append(
                    "STORM enabled without shadow mode (AETHERRA_STORM_SHADOW_MODE=1 recommended for prod)"
                )

        # Network strictness baseline
        net_strict = os.environ.get("AETHERRA_NET_STRICT", "0")
        if net_strict != "1":
            # Auto-enable with safe allowlist if not set
            os.environ.setdefault("AETHERRA_NET_STRICT", "1")
            default_allowlist = "localhost,127.0.0.1,.aetherra.dev"
            os.environ.setdefault("AETHERRA_NETWORK_ALLOWLIST", default_allowlist)
            logger.info(
                "[NET] Auto-enabled strict network policy with allowlist: %s",
                os.environ.get("AETHERRA_NETWORK_ALLOWLIST"),
            )
        else:
            # Log the active allowlist for visibility
            allowlist = os.environ.get("AETHERRA_NETWORK_ALLOWLIST", "")
            logger.info(
                "[NET] Network strict mode active with allowlist: %s",
                allowlist or "(none)",
            )

        if warnings:
            logger.warning(
                "[SEC] Production security warnings:\n - %s", "\n - ".join(warnings)
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
            CORS(app)
        except Exception as exc:
            logger.warning("CORS init failed: %s", exc, exc_info=True)

    for bp in BLUEPRINTS:
        if bp.name == "plugins":  # register with prefix for cleaner route paths
            app.register_blueprint(bp, url_prefix="/api/plugins")
        else:
            app.register_blueprint(bp)
    ai_stream.register_websocket_routes(app)

    # Optional engine reset on startup (test/support use-cases)
    def _maybe_reset_engine() -> None:
        if not (
            os.environ.get("AETHERRA_HUB_RESET_ENGINE_ON_START", "0") == "1"
            or os.environ.get("AETHERRA_TEST_RESET_ENGINE", "0") == "1"
        ):
            return
        try:
            # Aetherra imports
            from aetherra_service_registry import get_service_registry

            async def _do() -> None:
                reg = await get_service_registry()
                with contextlib.suppress(Exception):
                    await reg.unregister_service("aetherra_engine")

            # Run quickly (non-blocking degrade if fails)
            asyncio.run(_do())
            logger.info(
                "Engine reset requested by env var; unregistered existing engine instance if present"
            )
        except Exception as exc:
            logger.warning("Engine reset requested but failed: %s", exc, exc_info=True)

    _maybe_reset_engine()

    @app.get("/api/ping")
    def _ping() -> dict[str, bool]:  # simple liveness
        return {"pong": True}

    # --- Service registry integration: register hub + self-heartbeat ---
    try:
        import threading
        import time as _time

        _hub_hb_thread: threading.Thread | None = None
        _hub_hb_stop = False  # nonlocal via closure

        class _HubService:
            async def heartbeat(self):  # registry heartbeat hook
                return True

            async def ping(self):  # supervisor optional ping hook
                return True

            def is_alive(self):  # registry stale detector hook
                return True

        def _start_registry_hb_thread() -> None:
            nonlocal _hub_hb_thread
            if _hub_hb_thread is not None and _hub_hb_thread.is_alive():
                return

            def _runner() -> None:
                # Local import in thread to avoid import-time coupling
                try:
                    import asyncio as _asyncio

                    from aetherra_service_registry import (
                        get_service_registry as _get_reg,
                    )
                    from aetherra_service_registry import (
                        register_service as _reg,
                    )
                    from aetherra_service_registry import (
                        update_heartbeat as _hb,
                    )

                    # One-time registration
                    try:
                        _asyncio.run(
                            _reg(
                                "aetherra_hub",
                                _HubService(),
                                metadata={
                                    "version": getattr(app.settings, "version", "1"),  # type: ignore[attr-defined]
                                    "url": f"http://127.0.0.1:{getattr(app.settings, 'port', 3001)}",  # type: ignore[attr-defined]
                                    "self_heartbeat": True,
                                },
                                dependencies=["aetherra_engine"],
                            )
                        )
                        # Mark self-heartbeat in registry metadata (best-effort)
                        try:
                            reg = _asyncio.run(_get_reg())
                            with contextlib.suppress(Exception):
                                reg.mark_service_self_heartbeat("aetherra_hub", True)
                        except Exception as exc:
                            logger.debug(
                                "Hub registry self-heartbeat marker failed: %s",
                                exc,
                                exc_info=True,
                            )
                    except Exception as exc:
                        logger.debug(
                            "Hub service registration failed: %s", exc, exc_info=True
                        )

                    # Heartbeat loop
                    try:
                        interval = 45.0
                        try:
                            interval = float(
                                os.environ.get("AETHERRA_HUB_HEARTBEAT_SEC", "45") or 45
                            )
                        except (TypeError, ValueError):
                            interval = 45.0
                        while not _hub_hb_stop:
                            with contextlib.suppress(Exception):
                                _asyncio.run(_hb("aetherra_hub"))
                            # split sleep for quicker teardown
                            slept = 0.0
                            step = min(1.0, interval)
                            while not _hub_hb_stop and slept < interval:
                                _time.sleep(step)
                                slept += step
                    except Exception as exc:
                        logger.debug("Hub heartbeat loop failed: %s", exc, exc_info=True)
                except Exception as exc:
                    logger.warning(
                        "Hub registry heartbeat thread failed to initialize: %s",
                        exc,
                        exc_info=True,
                    )

            _hub_hb_thread = threading.Thread(
                target=_runner, name="hub-registry-heartbeat", daemon=True
            )
            _hub_hb_thread.start()

        @app.before_first_request
        def _on_first_request() -> None:
            # Start registry registration + heartbeat in background
            try:
                _start_registry_hb_thread()
            except Exception as exc:
                logger.warning(
                    "Unable to start Hub registry heartbeat thread: %s",
                    exc,
                    exc_info=True,
                )
                logger.debug(
                    "[REG] hub registry heartbeat thread failed to start", exc_info=True
                )

        @app.teardown_appcontext
        def _on_teardown(exception=None):  # noqa: ARG001
            # Signal heartbeat thread to stop
            nonlocal _hub_hb_stop
            _hub_hb_stop = True
    except Exception as _e:  # pragma: no cover - defensive
        logger.debug("[REG] Hub registry integration unavailable: %s", _e)

    @app.before_request
    def _log_req() -> None:  # lightweight request logging
        try:
            if getattr(app, "settings", None) and app.settings.log_requests:  # type: ignore[attr-defined]
                # Third party imports
                from flask import request

                logger.info("REQ %s %s", request.method, request.path)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("[REQLOG] request logging suppressed due to error: %s", exc)

    return app
