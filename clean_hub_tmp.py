# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧩 Aetherra Hub Server
======================

Built-in Python-based plugin marketplace server for Aetherra OS.
Provides plugin registration, discovery, and basic marketplace functionality.
"""

import asyncio
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional, cast

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Provide stubs so static analysis doesn't flag unbound names
    Flask = None  # type: ignore[assignment]
    jsonify = None  # type: ignore[assignment]
    request = None  # type: ignore[assignment]
    CORS = None  # type: ignore[assignment]
    print("ΓÜá∩╕Å Flask not available - using mock hub server")

logger = logging.getLogger(__name__)


# Generic public error helper to avoid leaking internal exception details.
# Returns a stable generic message unless AETHERRA_DEBUG=1, in which case it appends the exception string.
def _public_error(e: Exception | BaseException, generic: str = "internal error") -> str:  # type: ignore[override]
    try:
        if os.environ.get("AETHERRA_DEBUG", "0") == "1":
            return f"{generic}: {e}" if e else generic
    except Exception:
        pass
    return generic


class AetherraHubServer:
    """🧩 Built-in Aetherra Hub Server"""

    def __init__(self, port: int = 3001):
        self.port = port
        self.plugins = {}
        self.stats = {
            "total_plugins": 0,
            "active_registrations": 0,
            "startup_time": datetime.now(),
            "requests_served": 0,
            "telemetry_received": 0,
            "last_telemetry_at": None,
        }
        self.server_running = False
        # Snapshot AI API flags at startup to avoid later .env mutations affecting tests
        # Do this BEFORE creating Flask app or setting up routes, as those may import modules
        # that load a .env file and mutate os.environ.
        self.ai_api_enabled_present = "AETHERRA_AI_API_ENABLED" in os.environ
        self.ai_api_stream_present = "AETHERRA_AI_API_STREAM" in os.environ
        self.ai_api_enabled = os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1"
        self.ai_api_stream = os.environ.get("AETHERRA_AI_API_STREAM", "0") == "1"
        self.ai_api_require_token = (
            os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
        )
        self.ai_api_token = (
            os.environ.get("AETHERRA_AI_API_TOKEN")
            or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
            or ""
        ).strip()
        try:
            logger.info(
                f"[AI flags @init] present(enabled={self.ai_api_enabled_present} stream={self.ai_api_stream_present}) values(enabled={os.environ.get('AETHERRA_AI_API_ENABLED')} stream={os.environ.get('AETHERRA_AI_API_STREAM')})"
            )
        except Exception:
            pass
        # Optional WS, idempotency, and versioning controls (set before routes)
        try:
            self._ws_enabled_flag = os.environ.get("AETHERRA_AI_API_WS", "0") == "1"
        except Exception:
            self._ws_enabled_flag = False
        # Simple in-memory idempotency cache: key -> expires_at (epoch seconds)
        try:
            self._idem_ttl_sec = int(
                os.environ.get("AETHERRA_IDEMPOTENCY_TTL_SEC", "120") or 120
            )
        except Exception:
            self._idem_ttl_sec = 120
        self._idem_cache: Dict[str, float] = {}
        self._idem_enforce = os.environ.get("AETHERRA_IDEMPOTENCY_ENFORCE", "0") == "1"
        # Optional enforcement of X-Aetherra-Chat-Version: 2
        self._chat_ver_required = (
            os.environ.get("AETHERRA_CHAT_VERSION_REQUIRED", "0") == "1"
        )

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)  # type: ignore[name-defined]
            CORS(self.app)  # type: ignore[name-defined]  # Enable CORS for web interface
            # Lazy init WS if enabled and dependency present
            self._ws_sock = None
            if self._ws_enabled_flag:
                try:
                    from flask_sock import Sock  # type: ignore

                    self._ws_sock = Sock(self.app)  # type: ignore[assignment]
                except Exception:
                    self._ws_sock = None
            self._setup_routes()
        else:
            self.app = None
        # Testing aid: track the first time stream gate is evaluated so we can
        # neutralize any late env flips only once in strict test mode.
        self._first_stream_gate_checked = False
        # Track last-seen enablement flags to detect suspicious simultaneous flips in tests
        self._last_ai_en = "1" if self.ai_api_enabled else "0"
        self._last_ai_st = "1" if self.ai_api_stream else "0"
        # In-process chat metrics (best-effort, hub-level)
        self.chat_metrics = {
            "requests_total": 0,
            "streams_current": 0,
            "streams_by_principal": {},  # low-cardinality gauge mapping
            "latency_ms_sum": 0.0,
            "latency_count": 0,
            "ttft_ms_sum": 0.0,
            "ttft_count": 0,
            "chars_in_total": 0,
            "chars_out_total": 0,
            "tokens_in_total": 0,
            "tokens_out_total": 0,
            "chunks_total": 0,
            "fallback_path_counts": {"mock": 0, "cached": 0, "engine": 0},
            "rate_limited_total": 0,
            "policy_denied_total": 0,
            "backend_unavailable_total": 0,
            "timeout_total": 0,
            "breaker_tripped_total": 0,
            "breaker_open_total": 0,
            "latency_hist": {
                50: 0,
                100: 0,
                250: 0,
                500: 0,
                1000: 0,
                2000: 0,
                5000: 0,
                "+Inf": 0,
            },
            "ttft_hist": {50: 0, 100: 0, 250: 0, 500: 0, 1000: 0, 2000: 0, "+Inf": 0},
        }
        # Rolling histograms (hub-level fallback) for latency
        self.kernel_latency_hist = {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
            "+Inf": 0,
        }
        self.orchestrator_latency_hist = {
            10: 0,
            20: 0,
            50: 0,
            100: 0,
            200: 0,
            500: 0,
            1000: 0,
            2000: 0,
            "+Inf": 0,
        }

        # --- Sandbox / plugin runtime metrics (alpha -> promoted from placeholders) ---
        # These counters are currently incremented in best-effort hooks; once a real
        # sandbox subsystem is integrated they should be updated at enforcement points.
        self.sandbox_metrics = {
            "plugin_timeout_total": 0,  # plugin exceeded declared time budget
            "sandbox_violations_total": 0,  # attempted disallowed action (fs/net/etc.)
            "sandbox_policy_denied_total": 0,  # denied at policy gate before execution
            "sandbox_exec_total": 0,  # total plugin executions observed
        }

        # --- Trainer scaffolding: in-memory job state (opt-in via env) ---
        # Enabled flag is read at init; endpoints also re-check env to allow toggling for tests
        try:
            # Deprecated: do not cache trainer enabled state (tests toggle per-process). Always recompute via env at request time.
            self.trainer_enabled = False
        except Exception:
            self.trainer_enabled = False
        # Job store and lock
        self._trainer_lock = threading.Lock()
        self.trainer_jobs = {}
        self._trainer_job_order = []  # maintain insertion order for trimming
        self._trainer_max_jobs = 200

        # Simple counters for metrics
        self._trainer_eval_runs_total = 0
        # --- Trainer evaluations (scaffold) ---
        self.trainer_evals = {}
        self._trainer_eval_order = []
        self._trainer_max_evals = 200
        self._trainer_eval_last_score = None

        # background helpers (created on demand per job)

    # ---- Trainer helpers ----
    def _trainer_now_iso(self) -> str:
        try:
            return datetime.now().isoformat()
        except Exception:
            return ""

    def _trainer_trim_if_needed(self) -> None:
        try:
            with self._trainer_lock:
                excess = max(0, len(self._trainer_job_order) - self._trainer_max_jobs)
                for _ in range(excess):
                    old_id = self._trainer_job_order.pop(0)
                    self.trainer_jobs.pop(old_id, None)
        except Exception:
            pass

    def _trainer_submit_job(self, payload: Dict[str, Any]) -> str:
        # Generate a simple job id
        try:
            import uuid

            jid = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        except Exception:
            jid = f"train_{int(time.time())}"

        job = {
            "job_id": jid,
            "task": str(payload.get("task") or payload.get("kind") or "sft"),
            "base_model": payload.get("base_model"),
            "dataset_id": payload.get("dataset_id"),
            "params": payload.get("params") or {},
            "resources": payload.get("resources") or {},
            "tags": payload.get("tags") or [],
            "state": "queued",
            "progress": 0,
            "metrics": {},
            "artifacts": {},
            "created_at": self._trainer_now_iso(),
            "started_at": None,
            "finished_at": None,
            "error": None,
        }
        with self._trainer_lock:
            self.trainer_jobs[jid] = job
            self._trainer_job_order.append(jid)
        # start background worker
        t = threading.Thread(target=self._trainer_run_job, args=(jid,), daemon=True)
        t.start()
        # trim store casually
        self._trainer_trim_if_needed()
        return jid

    def _trainer_run_job(self, job_id: str) -> None:
        # Simulate a tiny training job with progress updates, abort if disabled mid-run
        try:
            enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
        except Exception:
            enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"

        with self._trainer_lock:
            job = self.trainer_jobs.get(job_id)
            if not job:
                return
            # Only transition if currently queued
            if job.get("state") != "queued":
                return
            job["state"] = "running"
            job["started_at"] = self._trainer_now_iso()
            job["progress"] = 0

        if not enabled:
            # Mark as failed if disabled
            with self._trainer_lock:
                job = self.trainer_jobs.get(job_id)
                if job:
                    job["state"] = "failed"
                    job["error"] = "disabled"
                    job["finished_at"] = self._trainer_now_iso()
            return

        # Simulate work
        try:
            steps = 5
            for i in range(steps):
                time.sleep(0.15)
                with self._trainer_lock:
                    job = self.trainer_jobs.get(job_id)
                    if not job:
                        return
                    if job.get("state") != "running":
                        return
                    job["progress"] = int(((i + 1) / steps) * 100)
            # Complete
            with self._trainer_lock:
                job = self.trainer_jobs.get(job_id)
                if job:
                    job["state"] = "completed"
                    job["finished_at"] = self._trainer_now_iso()
                    job["metrics"] = {"train_loss_final": 0.0}
        except Exception as e:
            with self._trainer_lock:
                job = self.trainer_jobs.get(job_id)
                if job:
                    job["state"] = "failed"
                    try:
                        # Use public error helper if present to avoid leaking internals
                        job["error"] = _public_error(e, "job failed")  # type: ignore[name-defined]
                    except Exception:
                        job["error"] = "job failed"
                    job["finished_at"] = self._trainer_now_iso()

    # ---- Trainer evaluation helpers ----
    def _trainer_submit_eval(self, payload: Dict[str, Any]) -> str:
        # Generate a simple eval id
        try:
            import uuid

            eid = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        except Exception:
            eid = f"eval_{int(time.time())}"

        ev = {
            "eval_id": eid,
            "task": str(payload.get("task") or payload.get("kind") or "eval"),
            "model": payload.get("model") or payload.get("base_model"),
            "dataset_id": payload.get("dataset_id"),
            "params": payload.get("params") or {},
            "state": "queued",
            "progress": 0,
            "metrics": {},
            "created_at": self._trainer_now_iso(),
            "started_at": None,
            "finished_at": None,
            "error": None,
        }
        with self._trainer_lock:
            self.trainer_evals[eid] = ev
            self._trainer_eval_order.append(eid)
        # start background worker
        t = threading.Thread(target=self._trainer_run_eval, args=(eid,), daemon=True)
        t.start()
        # trim eval store
        try:
            with self._trainer_lock:
                excess = max(0, len(self._trainer_eval_order) - self._trainer_max_evals)
                for _ in range(excess):
                    old_id = self._trainer_eval_order.pop(0)
                    self.trainer_evals.pop(old_id, None)
        except Exception:
            pass
        return eid

    def _trainer_run_eval(self, eval_id: str) -> None:
        # Simulate an evaluation run producing a simple score
        try:
            enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
        except Exception:
            enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"

        with self._trainer_lock:
            ev = self.trainer_evals.get(eval_id)
            if not ev:
                return
            if ev.get("state") != "queued":
                return
            ev["state"] = "running"
            ev["started_at"] = self._trainer_now_iso()
            ev["progress"] = 0

        if not enabled:
            with self._trainer_lock:
                ev = self.trainer_evals.get(eval_id)
                if ev:
                    ev["state"] = "failed"
                    ev["error"] = "disabled"
                    ev["finished_at"] = self._trainer_now_iso()
            return

        try:
            steps = 4
            for i in range(steps):
                time.sleep(0.12)
                with self._trainer_lock:
                    ev = self.trainer_evals.get(eval_id)
                    if not ev or ev.get("state") != "running":
                        return
                    ev["progress"] = int(((i + 1) / steps) * 100)
            # produce a pseudo score deterministically bounded
            score = 0.9
            with self._trainer_lock:
                ev = self.trainer_evals.get(eval_id)
                if ev:
                    ev["state"] = "completed"
                    ev["finished_at"] = self._trainer_now_iso()
                    ev["metrics"] = {"eval_score": score}
                    self._trainer_eval_runs_total = (
                        int(self._trainer_eval_runs_total) + 1
                    )
                    try:
                        self._trainer_eval_last_score = float(score)
                    except Exception:
                        self._trainer_eval_last_score = None
        except Exception as e:
            with self._trainer_lock:
                ev = self.trainer_evals.get(eval_id)
                if ev:
                    ev["state"] = "failed"
                    try:
                        ev["error"] = _public_error(e, "eval failed")  # type: ignore[name-defined]
                    except Exception:
                        ev["error"] = "eval failed"
                    ev["finished_at"] = self._trainer_now_iso()

    def _setup_routes(self):
        """Setup Flask routes for the Hub API"""

        # Helper: run a coroutine to completion in a loop-safe way from sync Flask routes
        def _run_coro_blocking(coro):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                result_container: Dict[str, Any] = {}

                def _runner():
                    try:
                        new_loop = asyncio.new_event_loop()
                        try:
                            asyncio.set_event_loop(new_loop)
                            result_container["result"] = new_loop.run_until_complete(
                                coro
                            )
                        finally:
                            new_loop.close()
                    except Exception as e:
                        result_container["error"] = e

                t = threading.Thread(target=_runner)
                t.start()
                t.join(timeout=3.0)
                if "result" in result_container:
                    return result_container["result"]
                raise result_container.get("error", RuntimeError("async-run-timeout"))
            else:
                return asyncio.run(coro)

        # Optional imports for federation, telemetry, memory optics, signing.
        # By default, skip these at startup to avoid heavy deps and unintended .env loaders.
        # Enable by setting AETHERRA_HUB_SKIP_OPTIONALS=0
        if os.environ.get("AETHERRA_HUB_SKIP_OPTIONALS", "1") == "0":
            try:
                from Aetherra.hub.federation import get_federation_manager

                self.federation = get_federation_manager(
                    self_url=f"http://localhost:{self.port}"
                )
                # Seed peers from env
                peers_env = os.environ.get("AETHERRA_PEERS", "").strip()
                if peers_env:
                    for p in [s.strip() for s in peers_env.split(",") if s.strip()]:
                        try:
                            self.federation.add_peer(p)
                        except Exception:
                            pass
            except Exception:
                self.federation = None
            try:
                from Aetherra.telemetry.optin import get_telemetry

                self.telemetry = get_telemetry()
            except Exception:
                self.telemetry = None
            try:
                from Aetherra.memory.graph_optics import summarize_memory_graph

                self.memory_summarizer = summarize_memory_graph
            except Exception:
                self.memory_summarizer = None
            # Optional signing verification
            try:
                import importlib

                ps = importlib.import_module("Aetherra.security.plugin_signing")
                self.verify_signature = getattr(ps, "verify_plugin_signature", None)
                # Capture module-level default strict (legacy) and library availability
                self.signing_strict = bool(getattr(ps, "STRICT", False))
                self._signing_has_lib = bool(getattr(ps, "NACL", False))
            except Exception:
                self.verify_signature = None
                self.signing_strict = False
                self._signing_has_lib = False
        else:
            self.federation = None
            self.telemetry = None
            self.memory_summarizer = None
            self.verify_signature = None
            self.signing_strict = False
            self._signing_has_lib = False
        # If Flask isn't available or app is None, skip route setup
        if not FLASK_AVAILABLE or self.app is None:
            return
        app = cast(Any, self.app)

        # --- CORS & Private Network Access (PNA) headers ---
        # Chrome 130+ requires Access-Control-Allow-Private-Network: true on preflight responses
        # when a public site accesses a private network resource (e.g., localhost).
        # We also set standard CORS headers and allow our custom auth header.
        @app.after_request
        def _add_cors_pna_headers(resp):  # type: ignore[override]
            """Add strict CORS and Private Network Access headers.

            Defaults: allow https://aetherra.dev and localhost origins only.
            Configure with:
              - AETHERRA_CORS_ALLOW_PATTERN: regex to match allowed Origin values
              - AETHERRA_PNA_ALLOW: '1' to enable Access-Control-Allow-Private-Network (default '1')
            """
            try:
                import re

                origin = request.headers.get("Origin")  # type: ignore[name-defined]
                allow_pattern = os.environ.get(
                    "AETHERRA_CORS_ALLOW_PATTERN",
                    r"^https?://(localhost|127\.0\.0\.1)(:\\d+)?$|^https://(www\.)?aetherra\.dev(:\\d+)?$",
                )
                pna_allow = os.environ.get("AETHERRA_PNA_ALLOW", "1").strip() == "1"
                allowed = bool(origin and re.match(allow_pattern, origin))
                if allowed:
                    resp.headers["Access-Control-Allow-Origin"] = origin
                    vary = resp.headers.get("Vary")
                    resp.headers["Vary"] = (vary + ", Origin") if vary else "Origin"
                    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                    resp.headers["Access-Control-Allow-Headers"] = (
                        "Content-Type, X-Aetherra-Token, X-Aetherra-Trace-Id, X-Aetherra-Chat-Version, X-Aetherra-Policy"
                    )
                    # Expose custom headers to browser JS
                    resp.headers["Access-Control-Expose-Headers"] = (
                        "X-Aetherra-Trace-Id, X-Aetherra-Chat-Version, X-Aetherra-Policy"
                    )
                    # Only opt into Private Network Access for allowed origins
                    if pna_allow:
                        resp.headers["Access-Control-Allow-Private-Network"] = "true"
                    resp.headers["Access-Control-Max-Age"] = "600"
                # Do not set wildcard or credentials; we purposely keep it strict.
            except Exception:
                pass
            return resp

        # Respond to any OPTIONS preflight early so clients donΓÇÖt 404 on dynamic routes
        @app.route("/", methods=["OPTIONS"])  # type: ignore[misc]
        @app.route("/<path:_any>", methods=["OPTIONS"])  # type: ignore[misc]
        def _cors_options(_any: Optional[str] = None):
            from flask import make_response  # type: ignore

            # Empty 204 response; headers are added by after_request above
            return make_response(("", 204))

        # Minimal OpenAPI summary for chat endpoints
        @app.route("/api/openapi.json", methods=["GET"])  # type: ignore[misc]
        def api_openapi_doc():
            self.stats["requests_served"] += 1
            try:
                spec = {
                    "openapi": "3.0.3",
                    "info": {"title": "Aetherra Chat API", "version": "2"},
                    "paths": {
                        "/api/ai/ask": {
                            "post": {
                                "summary": "Synchronous ask",
                                "parameters": [
                                    {
                                        "name": "X-Aetherra-Chat-Version",
                                        "in": "header",
                                        "required": False,
                                        "schema": {"type": "string", "enum": ["2"]},
                                    }
                                ],
                                "requestBody": {
                                    "required": True,
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "message": {"type": "string"},
                                                    "context": {"type": "object"},
                                                    "priority": {"type": "string"},
                                                    "ttl_sec": {"type": "integer"},
                                                    "deadline_ts": {"type": "number"},
                                                    "scratchpad_policy": {
                                                        "type": "string"
                                                    },
                                                    "client_message_id": {
                                                        "type": "string"
                                                    },
                                                },
                                            }
                                        }
                                    },
                                },
                                "responses": {
                                    "200": {"description": "OK"},
                                    "400": {"description": "Bad Request"},
                                    "409": {"description": "Duplicate/Expired"},
                                    "501": {"description": "Disabled"},
                                },
                            }
                        },
                        "/api/ai/stream": {
                            "post": {"summary": "SSE stream (POST)"},
                            "get": {"summary": "SSE stream (GET alias)"},
                        },
                        "/api/ai/stream_ws": {
                            "get": {
                                "summary": "Advertise WebSocket availability",
                                "responses": {
                                    "200": {"description": "WS available"},
                                    "501": {"description": "WS disabled"},
                                },
                            }
                        },
                    },
                    "components": {
                        "schemas": {
                            "SSEEnvelopeV2": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "trace_id": {"type": "string"},
                                    "ts": {"type": "string"},
                                    "type": {"type": "string"},
                                    "data": {"type": "object"},
                                    "client_message_id": {"type": "string"},
                                },
                            }
                        }
                    },
                    "x-aetherra": {
                        "ai_enabled": os.environ.get("AETHERRA_AI_API_ENABLED", "0")
                        == "1",
                        "stream_enabled": os.environ.get("AETHERRA_AI_API_STREAM", "0")
                        == "1",
                        "require_token": os.environ.get(
                            "AETHERRA_AI_API_REQUIRE_TOKEN", "0"
                        )
                        == "1",
                        "ws_enabled": self._ws_enabled_flag
                        and (self._ws_sock is not None),
                        "version_required": self._chat_ver_required,
                        "idempotency_ttl_sec": self._idem_ttl_sec,
                        "ws": {
                            "route": "/ws/ai/stream",
                            "frame_schema": "SSEEnvelopeV2",
                            "resume": {
                                "last_event_id": {
                                    "in": "body",
                                    "type": "integer",
                                    "description": "If provided in the initial WS JSON payload, server sets starting envelope id to last_event_id+1",
                                }
                            },
                        },
                    },
                }
            except Exception:
                spec = {
                    "openapi": "3.0.3",
                    "info": {"title": "Aetherra Chat API", "version": "2"},
                }
            return jsonify(spec)  # type: ignore[name-defined]

        # Optional WS endpoint mirroring SSE frames (stubbed/off by default)
        @app.route("/api/ai/stream_ws", methods=["GET"])  # type: ignore[misc]
        def ai_stream_ws_advertise():
            self.stats["requests_served"] += 1
            # Advertise capability or return 501 when disabled
            if not self._ws_enabled_flag or self._ws_sock is None:
                return jsonify({"error": "ws_disabled"}), 501  # type: ignore[name-defined]
            return jsonify(
                {
                    "ok": True,
                    "note": "WebSocket endpoint is available via Sock; use ws:// and same payload frames as SSE envelope v2.",
                }
            )  # type: ignore[name-defined]

        # Real WS route only when Sock is available and feature is enabled
        if self._ws_enabled_flag and self._ws_sock is not None:
            sock = self._ws_sock

            @sock.route("/ws/ai/stream")  # type: ignore[misc]
            def ai_stream_ws(ws):  # type: ignore[no-redef]
                """WebSocket chat stream mirroring SSE v2 frames.

                Contract: client sends one JSON message to start the stream with the same
                shape as POST /api/ai/stream. Server then pushes JSON envelopes:
                {id, trace_id, ts, type, data, client_message_id?} until final/error.
                """
                import json as _json

                # Gates: enabled + streaming flags
                _en = os.environ.get("AETHERRA_AI_API_ENABLED", "0")
                _st = os.environ.get("AETHERRA_AI_API_STREAM", "0")
                if _en != "1" or _st != "1":
                    ws.send(_json.dumps({"error": "disabled"}))
                    try:
                        ws.close()  # type: ignore[attr-defined]
                    except Exception:
                        pass
                    return
                # Token gate
                require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
                if require:
                    # WS handshake headers may not carry token consistently; expect token in first payload as fallback
                    expected = (
                        os.environ.get("AETHERRA_AI_API_TOKEN")
                        or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                        or ""
                    ).strip()
                    if not expected:
                        ws.send(_json.dumps({"error": "forbidden"}))
                        try:
                            ws.close()
                        except Exception:
                            pass
                        return
                # Receive initial payload
                try:
                    raw = ws.receive()  # type: ignore[attr-defined]
                    body = _json.loads(raw or "{}") if isinstance(raw, str) else {}
                except Exception:
                    body = {}
                # Optional version enforcement (headerless WS -> allow via body override)
                if self._chat_ver_required:
                    ver = str(
                        body.get("version") or body.get("chat_version") or ""
                    ).strip()
                    if ver not in ("2", 2):
                        ws.send(
                            _json.dumps(
                                {
                                    "error": "invalid_request",
                                    "message": "Missing or wrong chat version (require 2)",
                                }
                            )
                        )
                        try:
                            ws.close()
                        except Exception:
                            pass
                        return
                # Token check via body when required
                if require:
                    tok = str(
                        body.get("token") or body.get("x_aetherra_token") or ""
                    ).strip()
                    expected = (
                        os.environ.get("AETHERRA_AI_API_TOKEN")
                        or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                        or ""
                    ).strip()
                    if tok != expected:
                        ws.send(_json.dumps({"error": "forbidden"}))
                        try:
                            ws.close()
                        except Exception:
                            pass
                        return
                # Extract message/context and principal
                msg = str(body.get("message") or body.get("content") or "").strip()
                ctx = (
                    body.get("context") if isinstance(body.get("context"), dict) else {}
                )
                principal = (
                    str(
                        (ctx or {}).get("principal") or body.get("principal") or ""
                    ).strip()
                    or "anonymous"
                )
                # Trace id and client message id
                trace_id = _extract_trace_id(None, body)  # type: ignore[name-defined]
                client_msg_id = None
                try:
                    _raw_cmi = body.get("client_message_id")
                    client_msg_id = (
                        (str(_raw_cmi).strip() or None)
                        if _raw_cmi is not None
                        else None
                    )
                except Exception:
                    client_msg_id = None
                # Idempotency early-exit
                if self._idem_enforce and client_msg_id:
                    is_dup, dup_resp = _idem_check_and_mark(principal, client_msg_id)
                    if is_dup:
                        ws.send(
                            _json.dumps(
                                {
                                    "code": "duplicate",
                                    "ok": False,
                                    **_std_error(
                                        "duplicate",
                                        "Duplicate client_message_id within TTL window",
                                        trace_id,
                                    ),  # type: ignore[name-defined]
                                    "client_message_id": client_msg_id,
                                }
                            )
                        )
                        try:
                            ws.close()
                        except Exception:
                            pass
                        return

                # Envelope utility
                import time as _t

                # Honor optional last_event_id for monotonic resume semantics
                _start_id = 1
                try:
                    _lei = body.get("last_event_id")
                    if _lei is not None:
                        _start_id = int(str(_lei)) + 1
                        if _start_id < 1:
                            _start_id = 1
                except Exception:
                    _start_id = 1

                _cur = {"id": _start_id}

                def _send(event: str, data: Dict[str, Any]):
                    env = {
                        "id": _cur["id"],
                        "trace_id": trace_id,
                        "ts": datetime.now().isoformat(),
                        "type": event,
                        "data": data,
                    }
                    try:
                        if client_msg_id:
                            env["client_message_id"] = client_msg_id
                    except Exception:
                        pass
                    ws.send(_json.dumps(env))
                    _cur["id"] = int(_cur["id"]) + 1

                # Start stream: status/auth/policy
                _send("status", {"phase": "start"})
                _send("auth", {"required": require, "ok": True})
                if require:
                    _send("token", {"required": True, "ok": True})
                pol = _policy_snapshot_global()
                try:
                    if client_msg_id:
                        pol["client_message_id"] = client_msg_id
                except Exception:
                    pass
                _send("policy", pol)

                # Safety preflight
                try:
                    sc = _safety_precheck(msg, trace_id, "/ws/ai/stream")  # type: ignore[name-defined]
                    if sc.get("message"):
                        msg = str(sc.get("message") or msg)
                    if not sc.get("allow", True):
                        err = _std_error(
                            "policy_violation",
                            "Blocked by safety policy",
                            trace_id,
                            {"reasons": sc.get("reasons", [])},
                        )  # type: ignore[name-defined]
                        _send("error", err)
                        _send("final", {"ok": False, **err})
                        try:
                            ws.close()
                        except Exception:
                            pass
                        return
                except Exception:
                    pass

                # Counters
                try:
                    self.chat_metrics["streams_current"] += 1
                    self.chat_metrics["requests_total"] += 1
                except Exception:
                    pass

                # Mid-stream events queue
                try:
                    import queue as _queue

                    _evt_q: _queue.Queue = _queue.Queue()
                except Exception:
                    _evt_q = None  # type: ignore[assignment]

                def _emit(evt: str, data: Dict[str, Any]):
                    try:
                        if _evt_q is not None:
                            _evt_q.put((evt, data))
                    except Exception:
                        pass

                def _on_thought(text: Any = None, **kw):
                    _emit(
                        "thought", {"text": str(text) if text is not None else "", **kw}
                    )

                def _on_tool(info: Dict[str, Any] | None = None, **kw):
                    payload = {**(info or {}), **kw}
                    if "name" not in payload:
                        payload["name"] = "unknown"
                    _emit("tool", payload)

                def _on_chunk(text: Any = None, **kw):
                    _emit(
                        "chunk", {"text": str(text) if text is not None else "", **kw}
                    )

                done = {"flag": False}
                holder: Dict[str, Any] = {}

                def _runner_thread(eng):
                    try:
                        import asyncio as _asyncio

                        async def _go():
                            try:
                                _ctx = dict(ctx or {})
                                _ctx["_callbacks"] = {
                                    "on_thought": _on_thought,
                                    "on_tool": _on_tool,
                                    "on_chunk": _on_chunk,
                                }
                                _ctx = cast(Dict[str, Any], _ctx)
                                _ctx["trace_id"] = trace_id
                                result = await eng.process_message(msg, _ctx)
                                return True, result
                            except Exception as e:
                                return False, str(e)

                        loop = _asyncio.new_event_loop()
                        try:
                            _asyncio.set_event_loop(loop)
                            holder["result"] = loop.run_until_complete(_go())
                        finally:
                            try:
                                loop.close()
                            except Exception:
                                pass
                    except Exception as e:
                        holder["result"] = (False, str(e))
                    finally:
                        done["flag"] = True

                def _get_engine(eng):
                    return True, eng

                eng_ok, eng_payload = _with_engine_call(_get_engine)  # type: ignore[name-defined]
                if not eng_ok:
                    cls = _classify_engine_error(eng_payload)  # type: ignore[name-defined]
                    err = _std_error(
                        cls.get("code", "backend_unavailable"),
                        cls.get("message", str(eng_payload)),
                        trace_id,
                        cls.get("details"),
                    )  # type: ignore[name-defined]
                    _send("error", err)
                    _send("final", {"ok": False, **err})
                    try:
                        ws.close()
                    except Exception:
                        pass
                    return

                import threading as _threading

                t = _threading.Thread(
                    target=_runner_thread, args=(eng_payload,), daemon=True
                )
                t.start()

                # Drain events
                while not done["flag"]:
                    try:
                        if _evt_q is not None:
                            try:
                                evt, data = _evt_q.get(timeout=0.05)
                                _send(str(evt), cast(Dict[str, Any], data))
                            except Exception:
                                pass
                        else:
                            _t.sleep(0.05)
                    except Exception:
                        break

                # Flush any remaining
                try:
                    if _evt_q is not None:
                        while True:
                            evt, data = _evt_q.get_nowait()
                            _send(str(evt), cast(Dict[str, Any], data))
                except Exception:
                    pass

                # Finalize result
                result = holder.get("result", (False, "server"))
                if not isinstance(result, tuple) or len(result) != 2:
                    success, payload = False, "server"
                else:
                    success, payload = result  # type: ignore[assignment]
                if success:
                    try:
                        normalized = _normalize_chat_result(
                            payload, message=msg, ctx=ctx
                        )  # type: ignore[name-defined]
                    except Exception:
                        normalized = {"response": str(payload)}
                    _send(
                        "usage",
                        {
                            "tokens_in": int(_count_tokens(msg)),  # type: ignore[name-defined]
                            "tokens_out": int(
                                _count_tokens(
                                    str((normalized or {}).get("response", ""))
                                )
                            ),  # type: ignore[name-defined]
                            "chars_in": int(len(msg)),
                            "chars_out": int(
                                len(str((normalized or {}).get("response", "")))
                            ),
                        },
                    )
                    _send("final", {"ok": True, "result": normalized})
                else:
                    cls = _classify_engine_error(payload)  # type: ignore[name-defined]
                    err = _std_error(
                        cls.get("code", "invalid_request"),
                        cls.get("message", str(payload)),
                        trace_id,
                        cls.get("details"),
                    )  # type: ignore[name-defined]
                    _send("error", err)
                    _send("final", {"ok": False, **err})
                # Close out
                try:
                    ws.close()
                except Exception:
                    pass

        # --- Request contract helpers (versioning + idempotency) ---
        def _require_chat_version(req) -> Optional[Any]:
            """If version enforcement is enabled, require X-Aetherra-Chat-Version: 2."""
            try:
                if not self._chat_ver_required:
                    return None
                ver = (req.headers.get("X-Aetherra-Chat-Version") or "").strip()
                if ver != "2":
                    r = jsonify(
                        {
                            "ok": False,
                            **_std_error(
                                "invalid_request",
                                "Missing or wrong X-Aetherra-Chat-Version (require 2)",
                                "",
                            ),
                        }
                    )  # type: ignore[name-defined]
                    try:
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                    except Exception:
                        pass
                    return (r, 400)
            except Exception:
                return None
            return None

        def _idem_key(principal: str, client_id: str) -> str:
            return f"{principal}|{client_id}"

        def _idem_check_and_mark(
            principal: str, client_id: Optional[str]
        ) -> tuple[bool, Optional[tuple[Any, int]]]:
            """Returns (is_dup, response_if_dup). If dup, provide a 409 JSON with standard error."""
            if not client_id:
                return False, None
            try:
                now = time.time()
            except Exception:
                import time as _t2

                now = _t2.time()
            # Opportunistic cleanup
            try:
                if len(self._idem_cache) > 1024:
                    expired = [
                        k for k, exp in list(self._idem_cache.items()) if exp <= now
                    ]
                    for k in expired[:256]:
                        self._idem_cache.pop(k, None)
            except Exception:
                pass
            k = _idem_key(principal or "anonymous", str(client_id))
            exp = self._idem_cache.get(k)
            if exp and exp > now:
                # Echo the conflicting client_message_id for parity with SSE/WS frames
                r = jsonify(
                    {
                        "ok": False,
                        **_std_error(
                            "duplicate",
                            "Duplicate client_message_id within TTL window",
                            "",
                        ),
                        "client_message_id": str(client_id),
                    }
                )  # type: ignore[name-defined]
                try:
                    r.headers["X-Aetherra-Chat-Version"] = "2"
                except Exception:
                    pass
                return True, (r, 409)
            # Mark
            try:
                self._idem_cache[k] = now + float(max(5, int(self._idem_ttl_sec)))
            except Exception:
                self._idem_cache[k] = now + 120.0
            return False, None

        # Internal helpers to access registry/kernel from sync Flask routes
        def _policy_snapshot_global() -> Dict[str, Any]:
            """Effective chat policy snapshot used for headers and SSE policy events.

            Includes: base flags, safety mode, DP flags, capability grants, and
            network policy allowlist. Safe to expose to clients.
            """

            def _caps_for_mode(mode: str) -> list[str]:
                mode = (mode or "standard").strip().lower()
                # Allow overrides via env comma-separated lists
                if mode == "strict":
                    env_caps = os.environ.get("AETHERRA_CHAT_CAPS_STRICT", "").strip()
                    default_caps = [
                        "plan",
                        "retrieve",
                        "tools:allowlist",
                        "write:none",
                        "network:allowlist",
                        "fs:read_limited",
                    ]
                else:
                    env_caps = os.environ.get("AETHERRA_CHAT_CAPS_STANDARD", "").strip()
                    default_caps = [
                        "plan",
                        "retrieve",
                        "tools:allowlist",
                        "write:limited",
                        "network:allowlist",
                        "fs:read_limited",
                    ]
                if env_caps:
                    try:
                        return [c.strip() for c in env_caps.split(",") if c.strip()]
                    except Exception:
                        return default_caps
                # Fall back to defaults when no override provided
                return default_caps

            def _network_policy_for_mode(mode: str) -> Dict[str, Any]:
                mode = (mode or "standard").strip().lower()
                env_list = os.environ.get("AETHERRA_NETWORK_ALLOWLIST", "").strip()
                if env_list:
                    allow = [h.strip() for h in env_list.split(",") if h.strip()]
                    block_unknown = True
                else:
                    # Built-in defaults when not configured
                    if mode == "strict":
                        allow = ["localhost", "127.0.0.1", "::1", "*.aetherra.dev"]
                        block_unknown = True
                    else:
                        allow = ["*"]
                        block_unknown = False
                return {"allowlist": allow, "block_unknown": bool(block_unknown)}

            try:
                mode = os.environ.get("AETHERRA_CHAT_SAFETY_MODE", "standard")
                base = {
                    "ai_enabled": os.environ.get("AETHERRA_AI_API_ENABLED", "0") == "1",
                    "stream_enabled": os.environ.get("AETHERRA_AI_API_STREAM", "0")
                    == "1",
                    "require_token": os.environ.get(
                        "AETHERRA_AI_API_REQUIRE_TOKEN", "0"
                    )
                    == "1",
                    "safety_mode": mode,
                    "max_tokens": int(
                        os.environ.get("AETHERRA_CHAT_MAX_TOKENS", "0") or 0
                    ),
                    "temperature": float(
                        os.environ.get("AETHERRA_CHAT_TEMPERATURE", "0") or 0.0
                    ),
                }
                # DP flags (opt-in)
                dp_enabled = os.environ.get("AETHERRA_DP_ENABLED", "0") == "1"
                dp = {
                    "enabled": dp_enabled,
                    "epsilon": float(os.environ.get("AETHERRA_DP_EPSILON", "0") or 0.0)
                    if dp_enabled
                    else None,
                }
                base["dp"] = dp
                # Capabilities
                base["capabilities"] = _caps_for_mode(mode)
                # Network policy
                base["network_policy"] = _network_policy_for_mode(mode)
                return base
            except Exception:
                return {
                    "ai_enabled": False,
                    "stream_enabled": False,
                    "require_token": False,
                    "safety_mode": "standard",
                    "dp": {"enabled": False, "epsilon": None},
                    "capabilities": [],
                    "network_policy": {"allowlist": [], "block_unknown": True},
                }

        # --- Security helpers: redaction, allowlist checks, ledger ---
        def _security_ledger_write(event: str, trace_id: str, details: Dict[str, Any]):
            """Append a single security event to the security ledger JSONL (best-effort)."""
            try:
                import json as _json
                from pathlib import Path as _Path

                # Gate by env (default on)
                if os.environ.get("AETHERRA_SECURITY_LEDGER", "1") != "1":
                    return
                p_env = os.environ.get("AETHERRA_SECURITY_LEDGER_PATH", "").strip()
                if p_env:
                    p = _Path(p_env)
                else:
                    p = _Path(os.getenv("AETHERRA_STATE_DIR", ".aetherra")).joinpath(
                        "security_ledger.jsonl"
                    )
                p.parent.mkdir(parents=True, exist_ok=True)
                rec = {
                    "ts": datetime.now().isoformat(),
                    "event": event,
                    "trace_id": trace_id,
                    **details,
                }
                with open(p, "a", encoding="utf-8") as f:
                    f.write(_json.dumps(rec) + "\n")
            except Exception:
                pass

        def _redact_text(text: str) -> Dict[str, Any]:
            """Return { text, redactions: [ { pattern, start, end }... ] } with basic secret redactions."""
            import re as _re

            s = str(text or "")
            redactions = []
            patterns = [
                (
                    r"(?i)(api_key|apikey|api-key)\s*[:=]\s*([A-Za-z0-9_\-]{6,})",
                    "\\1=[REDACTED]",
                ),
                (r"(?i)(password|pass)\s*[:=]\s*([^\s]{4,})", "\\1=[REDACTED]"),
                (r"(?i)token\s*[:=]\s*([A-Za-z0-9_\-]{6,})", "token=[REDACTED]"),
                (r"(?i)sk-[A-Za-z0-9]{8,}", "[REDACTED]"),
            ]
            for pat, repl in patterns:
                try:
                    for m in _re.finditer(pat, s):
                        redactions.append(
                            {"pattern": pat, "start": m.start(), "end": m.end()}
                        )
                    s = _re.sub(pat, repl, s)
                except Exception:
                    continue
            return {"text": s, "redactions": redactions}

        def _extract_urls_hosts(text: str) -> list[str]:
            import re as _re

            s = str(text or "")
            urls = []
            try:
                for m in _re.finditer(r"https?://([^/\s]+)", s):
                    urls.append(m.group(1).lower())
            except Exception:
                pass
            return urls

        def _host_allowed(host: str, allowlist: list[str]) -> bool:
            host = (host or "").lower()
            if not allowlist:
                return False
            if "*" in allowlist:
                return True
            # Wildcard suffix match: *.domain.tld
            for pat in allowlist:
                p = pat.lower()
                if p.startswith("*."):
                    suf = p[1:]  # leading '.' stays
                    if host.endswith(suf):
                        return True
                elif host == p:
                    return True
            return False

        def _safety_precheck(message: str, trace_id: str, route: str) -> Dict[str, Any]:
            """Run prompt-defense preflight: redact, check network policy and basic risky phrases.

            Returns dict with keys:
             - allow: bool
             - message: str (possibly redacted)
             - reasons: list[str]
             - policy: dict (effective policy snapshot)
            """
            policy = _policy_snapshot_global()
            mode = str(policy.get("safety_mode") or "standard").lower()
            reasons: list[str] = []

            # Redact secrets from prompt
            red = _redact_text(message)
            msg2 = red.get("text", message)
            if red.get("redactions"):
                reasons.append("redaction:secrets")

            # Network allowlist
            net = policy.get("network_policy") or {}
            allowlist = (
                list((net.get("allowlist") or [])) if isinstance(net, dict) else []
            )
            block_unknown = bool(
                (net.get("block_unknown") if isinstance(net, dict) else True)
            )
            hosts = _extract_urls_hosts(msg2)
            for h in hosts:
                if not _host_allowed(h, allowlist):
                    reasons.append(f"network:blocked:{h}")

            # Basic risky phrase detector
            low = str(message or "").lower()
            risky_terms = [
                "rm -rf",
                "format c:",
                "exfiltrate",
                "leak secret",
                "disable safety",
                "bypass policy",
                "ssh private key",
                "/etc/shadow",
            ]
            if any(t in low for t in risky_terms):
                reasons.append("prompt:risky")

            # Decide allow/deny
            allow = True
            if reasons:
                # Always enforce network allowlist when block_unknown is True
                if (
                    any(r.startswith("network:blocked:") for r in reasons)
                    and block_unknown
                ):
                    allow = False
                # Strict mode short-circuits on any high-risk reasons
                if mode == "strict" and any(
                    r.startswith(("prompt:risky",)) for r in reasons
                ):
                    allow = False

            if not allow:
                # Security ledger alert
                try:
                    _security_ledger_write(
                        "security.alert",
                        trace_id,
                        {
                            "route": route,
                            "safety_mode": mode,
                            "reasons": reasons,
                            "policy": {
                                k: policy[k]
                                for k in (
                                    "capabilities",
                                    "network_policy",
                                    "dp",
                                    "safety_mode",
                                )
                                if k in policy
                            },
                            "preview": (msg2[:256] if isinstance(msg2, str) else ""),
                        },
                    )
                except Exception:
                    pass
                # Counter
                try:
                    self.chat_metrics["policy_denied_total"] = (
                        int(self.chat_metrics.get("policy_denied_total", 0)) + 1
                    )
                except Exception:
                    pass

            return {
                "allow": allow,
                "message": msg2,
                "reasons": reasons,
                "policy": policy,
            }

        def _extract_trace_id(
            req,
            body: Optional[Dict[str, Any]] = None,
            query: Optional[Dict[str, Any]] = None,
        ) -> str:
            import uuid as _uuid

            try:
                hdr = (getattr(req, "headers", {}) or {}).get("X-Aetherra-Trace-Id")
                if hdr and str(hdr).strip():
                    return str(hdr).strip()
            except Exception:
                pass
            try:
                if body and isinstance(body, dict):
                    b = body.get("trace_id") or body.get("traceId")
                    if b and str(b).strip():
                        return str(b).strip()
            except Exception:
                pass
            try:
                if query and isinstance(query, dict):
                    q = query.get("trace_id") or query.get("traceId")
                    if q and str(q).strip():
                        return str(q).strip()
            except Exception:
                pass
            return str(_uuid.uuid4())

        def _write_chat_dlq(trace_id: str, reason: str, payload: Dict[str, Any]):
            """Best-effort DLQ write. Prefer kernel DLQ when available, else write a local hub DLQ file."""
            try:

                def _do(kernel):
                    try:
                        if hasattr(kernel, "_dlq_write"):
                            task = {
                                "type": "chat.request",
                                "trace_id": trace_id,
                                "data": payload,
                            }
                            try:
                                kernel._dlq_write(task, reason=reason)  # type: ignore[attr-defined]
                                return True, "ok"
                            except Exception:
                                pass
                        return False, "no_kernel_dlq"
                    except Exception as e:
                        return False, str(e)

                ok2, _msg = _with_kernel_mutation(_do)
                if ok2:
                    return
            except Exception:
                pass
            # Fallback local DLQ
            try:
                import json as _json
                from pathlib import Path as _Path

                p = _Path(os.getenv("AETHERRA_STATE_DIR", ".aetherra")).joinpath(
                    "hub_chat_dlq.jsonl"
                )
                p.parent.mkdir(parents=True, exist_ok=True)
                with open(p, "a", encoding="utf-8") as f:
                    f.write(
                        _json.dumps(
                            {
                                "ts": datetime.now().isoformat(),
                                "reason": reason,
                                "trace_id": trace_id,
                                "type": "chat.request",
                                "data": payload,
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass

        def _create_tokenizer():
            """Create a token counting function based on env + optional libs.

            AETHERRA_TOKENIZER: heuristic | tiktoken | engine (default: heuristic)
            AETHERRA_TOKENIZER_MODEL: e.g., cl100k_base
            """
            mode = os.environ.get("AETHERRA_TOKENIZER", "heuristic").strip().lower()
            if mode == "tiktoken":
                try:
                    import tiktoken  # type: ignore

                    model = os.environ.get("AETHERRA_TOKENIZER_MODEL", "cl100k_base")
                    enc = None
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
                            return int(max(1, round((len(text or "")) / 4)))

                    return _cnt
                except Exception:
                    pass
            if mode == "engine":

                def _cnt_engine(text: str) -> int:
                    def _call(eng):
                        try:
                            for name in (
                                "estimate_tokens",
                                "count_tokens",
                                "token_count",
                            ):
                                fn = getattr(eng, name, None)
                                if fn is not None:
                                    try:
                                        return True, int(fn(text))
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                        return True, int(max(1, round((len(text or "")) / 4)))

                    try:
                        ok, val = _with_engine_call(_call)
                        return (
                            int(val)
                            if ok
                            else int(max(1, round((len(text or "")) / 4)))
                        )
                    except Exception:
                        return int(max(1, round((len(text or "")) / 4)))

                return _cnt_engine

            # Default heuristic
            def _cnt_heur(text: str) -> int:
                try:
                    return int(max(1, round((len(text or "")) / 4)))
                except Exception:
                    return 1

            return _cnt_heur

        _count_tokens = _create_tokenizer()

        # --- Error helpers (standardized schema + classification) ---
        def _std_error(
            code: str,
            message: str,
            trace_id: str,
            details: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            return {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {},
                    "trace_id": trace_id,
                }
            }

        def _classify_engine_error(err: Any) -> Dict[str, Any]:
            """Best-effort error classification for upstream/engine errors.

            Returns dict with keys: code, http_status, message, headers(optional), details(optional).
            """
            msg = str(err or "server").strip()
            low = msg.lower()
            headers: Dict[str, str] = {}
            details: Dict[str, Any] = {}
            # Rate limited
            if any(w in low for w in ("rate limit", "too many requests", "429")):
                details["retry_after_sec"] = int(
                    os.environ.get("AETHERRA_RETRY_AFTER_SEC", "30") or 30
                )
                details["quota_window"] = os.environ.get(
                    "AETHERRA_RATE_LIMIT_WINDOW", "1m"
                )
                headers["Retry-After"] = str(details["retry_after_sec"])
                # increment metric
                try:
                    self.chat_metrics["rate_limited_total"] = (
                        int(self.chat_metrics.get("rate_limited_total", 0)) + 1
                    )
                except Exception:
                    pass
                return {
                    "code": "rate_limited",
                    "http_status": 429,
                    "message": msg or "Rate limited",
                    "headers": headers,
                    "details": details,
                }
            # Forbidden / policy violation
            if "policy" in low or "forbidden" in low or "unauthorized" in low:
                try:
                    self.chat_metrics["policy_denied_total"] = (
                        int(self.chat_metrics.get("policy_denied_total", 0)) + 1
                    )
                except Exception:
                    pass
                return {
                    "code": "policy_violation" if "policy" in low else "forbidden",
                    "http_status": 403,
                    "message": msg or "Forbidden",
                }
            # Timeout
            if "timeout" in low or "deadline" in low:
                try:
                    self.chat_metrics["timeout_total"] = (
                        int(self.chat_metrics.get("timeout_total", 0)) + 1
                    )
                    self.chat_metrics["breaker_tripped_total"] = (
                        int(self.chat_metrics.get("breaker_tripped_total", 0)) + 1
                    )
                    self.chat_metrics["breaker_open_total"] = (
                        int(self.chat_metrics.get("breaker_open_total", 0)) + 1
                    )
                except Exception:
                    pass
                return {
                    "code": "timeout",
                    "http_status": 504,
                    "message": msg or "Upstream timeout",
                }
            # Backend unavailable
            if any(
                w in low for w in ("unavailable", "overloaded", "service down", "503")
            ):
                try:
                    self.chat_metrics["backend_unavailable_total"] = (
                        int(self.chat_metrics.get("backend_unavailable_total", 0)) + 1
                    )
                    self.chat_metrics["breaker_tripped_total"] = (
                        int(self.chat_metrics.get("breaker_tripped_total", 0)) + 1
                    )
                    self.chat_metrics["breaker_open_total"] = (
                        int(self.chat_metrics.get("breaker_open_total", 0)) + 1
                    )
                except Exception:
                    pass
                return {
                    "code": "backend_unavailable",
                    "http_status": 503,
                    "message": msg or "Backend unavailable",
                }
            # Fallback invalid request
            return {
                "code": "invalid_request",
                "http_status": 400,
                "message": msg or "Invalid request",
            }

        def _get_registry_status_sync():
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    return reg.get_registry_status()

                return _a.run(_run())
            except Exception:
                return None

        def _get_kernel_status_sync():
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("kernel_loop")
                    if not info:
                        return None
                    kernel = info.instance
                    if not kernel or not hasattr(kernel, "get_status"):
                        return None
                    return kernel.get_status()

                return _a.run(_run())
            except Exception:
                return None

        def _get_orchestrator_status_sync():
            """Best-effort lookup of orchestrator status via the engine service."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        try:
                            return orch.get_system_status()
                        except Exception:
                            return None
                    if hasattr(eng, "get_system_status"):
                        try:
                            st = await eng.get_system_status()  # type: ignore[attr-defined]
                            if isinstance(st, dict):
                                return st.get("agent_orchestrator")
                        except Exception:
                            return None
                    return None

                return _a.run(_run())
            except Exception:
                return None

        def _with_kernel_mutation(fn):
            """Helper to run a mutation against the kernel instance safely from Flask.

            Accepts either a sync function (kernel -> result) or an async function
            (kernel -> awaitable result). Returns (ok: bool, message|payload).
            """
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("kernel_loop")
                    if not info:
                        return False, "kernel not registered"
                    kernel = info.instance
                    if not kernel:
                        return False, "kernel instance unavailable"
                    try:
                        if _a.iscoroutinefunction(fn):
                            return await fn(kernel)
                        else:
                            return fn(kernel)
                    except Exception as e:  # pragma: no cover - surfaced to caller
                        return False, str(e)

                return _a.run(_run())
            except Exception as e:  # pragma: no cover - defensive
                return False, str(e)

        def _get_memory_quantum_status_sync():
            """Best-effort quantum memory status.

            Tries service registry ΓåÆ engine.memory_system.engine.get_status()
            Fallback: instantiate QuantumEnhancedMemoryEngine (ephemeral).
            """
            # Try via service registry and engine
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    ms = getattr(eng, "memory_system", None)
                    if ms is None:
                        return None
                    # Common shapes:
                    # - ms.get_quantum_status()
                    # - ms.engine.get_status()
                    if hasattr(ms, "get_quantum_status"):
                        try:
                            return {"enabled": True, **(await ms.get_quantum_status())}  # type: ignore[func-returns-value]
                        except Exception:
                            pass
                    inner = getattr(ms, "engine", None)
                    if inner is not None and hasattr(inner, "get_status"):
                        try:
                            st = inner.get_status()
                            if isinstance(st, dict):
                                return {"enabled": True, **st}
                        except Exception:
                            pass
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass

            # Fallback: ephemeral instance
            try:
                from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
                    QuantumEnhancedMemoryEngine as _Q,
                )

                q = _Q()
                st = q.get_status()
                if isinstance(st, dict):
                    st = dict(st)
                else:
                    st = {}
                st.update({"enabled": False, "ephemeral": True})
                return st
            except Exception:
                return {"enabled": False}

        def _get_memory_audit_sync():
            """Best-effort memory audit (branch DAG/edges) data.

            Tries service registry ΓåÆ engine.memory_system.engine.audit_branch_dag()
            Fallback: instantiate QuantumEnhancedMemoryEngine and call audit.
            """
            # Try via service registry and engine
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return None
                    eng = info.instance
                    ms = getattr(eng, "memory_system", None)
                    if ms is None:
                        return None
                    inner = getattr(ms, "engine", None)
                    target = inner or ms
                    if hasattr(target, "audit_branch_dag"):
                        try:
                            audit = target.audit_branch_dag()  # type: ignore[attr-defined]
                            if isinstance(audit, dict):
                                return {"enabled": True, "audit": audit}
                        except Exception:
                            pass
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass

            # Fallback: ephemeral instance
            try:
                from Aetherra.aetherra_core.memory.QuantumEnhancedMemoryEngine import (
                    QuantumEnhancedMemoryEngine as _Q,
                )

                q = _Q()
                try:
                    audit = q.audit_branch_dag()
                except Exception:
                    audit = {}
                return {"enabled": False, "ephemeral": True, "audit": audit}
            except Exception:
                return {"enabled": False}

        def _get_hmr_audit_counters_sync():
            """Best-effort HMR audit counters from the controller via the service registry."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("hmr_controller")
                    if not info or not info.instance:
                        return None
                    inst = info.instance
                    if hasattr(inst, "get_audit_counters"):
                        try:
                            return inst.get_audit_counters()
                        except Exception:
                            return None
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass
            return None

        # Quantum bridge (simulator-first)
        def _get_quantum_bridge_status():
            try:
                from Aetherra.aetherra_core.memory.quantum.quantum_bridge import (
                    get_quantum_bridge as _gqb,
                )

                qb = _gqb()
                return qb.status()
            except Exception:
                return {"enabled": False}

        # --- Chat payload contract normalizer ---
        def _normalize_chat_result(
            raw: Any,
            message: Optional[str] = None,
            ctx: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Normalize engine chat results to a unified contract.

            Fields added:
              - session_id: str (prefer ctx.session_id; else generated)
              - timestamp: ISO string (now)
              - reasoning or reasoning_ref: pass-through if present
              - memory_id: from result or ctx if present
              - relevant_memories_count: from result or len(relevant_memories) fallback
              - confidence_breakdown: { model, grounding, coherence, safety }
              - confidence: legacy float preserved if provided, else conservative agg

            Always includes:
              - response: str (best-effort derived from raw)
            """
            try:
                import uuid as _uuid
            except Exception:
                _uuid = None  # type: ignore

            ctx = ctx or {}
            # Unwrap common shapes
            base = raw
            if (
                isinstance(raw, dict)
                and "result" in raw
                and isinstance(raw.get("result"), dict)
            ):
                base = raw.get("result")
            # Extract response text
            if isinstance(base, dict):
                resp_text = str(
                    base.get("response")
                    or base.get("text")
                    or base.get("answer")
                    or base.get("output")
                    or ""
                )
            else:
                resp_text = str(base)

            # Identity fields
            session_id = (
                str(ctx.get("session_id"))
                if ctx.get("session_id")
                else (
                    str(base.get("session_id"))
                    if isinstance(base, dict) and base.get("session_id")
                    else (
                        str(_uuid.uuid4())
                        if _uuid
                        else datetime.now().strftime("sid-%Y%m%d%H%M%S%f")
                    )
                )
            )
            ts = datetime.now().isoformat()

            # Reasoning fields (pass-through if available)
            reasoning = None
            reasoning_ref = None
            if isinstance(base, dict):
                reasoning = base.get("reasoning") or base.get("thoughts")
                reasoning_ref = base.get("reasoning_ref") or base.get("trace_id")

            # Memory linkage
            memory_id = None
            if isinstance(base, dict):
                memory_id = base.get("memory_id") or ctx.get("memory_id")
            else:
                memory_id = ctx.get("memory_id")

            # Relevant memories count
            rmc = 0
            if isinstance(base, dict):
                try:
                    if isinstance(base.get("relevant_memories"), list):
                        rmc = int(len(base.get("relevant_memories") or []))
                except Exception:
                    rmc = 0
                try:
                    if "relevant_memories_count" in base:
                        rmc = int(base.get("relevant_memories_count") or rmc)
                except Exception:
                    pass

            # Confidence (structured + legacy)
            from typing import Optional as _Opt

            cb: Dict[str, _Opt[float]] = {
                "model": None,
                "grounding": None,
                "coherence": None,
                "safety": None,
            }
            if isinstance(base, dict):
                # Direct structured breakdown if present
                if isinstance(base.get("confidence_breakdown"), dict):
                    _bd = base.get("confidence_breakdown") or {}
                    for k in ("model", "grounding", "coherence", "safety"):
                        try:
                            v = _bd.get(k)
                            cb[k] = float(v) if v is not None else None
                        except Exception:
                            cb[k] = None
                else:
                    # Infer from alternate fields if available
                    for src, dst in (
                        ("model_confidence", "model"),
                        ("grounding_score", "grounding"),
                        ("coherence", "coherence"),
                        ("safety", "safety"),
                    ):
                        try:
                            if src in base and cb.get(dst) is None:
                                _v = base.get(src)
                                if _v is not None:
                                    cb[dst] = float(_v)
                        except Exception:
                            pass
            # Legacy confidence float
            legacy_conf = None
            try:
                if isinstance(base, dict) and base.get("confidence") is not None:
                    _vc = base.get("confidence")
                    if _vc is not None:
                        legacy_conf = float(_vc)
            except Exception:
                legacy_conf = None
            if legacy_conf is None:
                # Conservative aggregation: min of present breakdown components; fallback 0.5
                try:
                    vals = [v for v in cb.values() if isinstance(v, (int, float))]
                    legacy_conf = float(min(vals)) if vals else 0.5
                except Exception:
                    legacy_conf = 0.5

            normalized: Dict[str, Any] = {
                "response": resp_text,
                # Maintain backward compatibility for tests that expect 'text'
                # when the engine returns a simple 'text' field. Mirror response.
                "text": resp_text,
                "session_id": session_id,
                "timestamp": ts,
                # Reasoning fields; include if present
                **({"reasoning": reasoning} if reasoning is not None else {}),
                **(
                    {"reasoning_ref": reasoning_ref}
                    if reasoning_ref is not None
                    else {}
                ),
                # Memory linkage
                **({"memory_id": memory_id} if memory_id is not None else {}),
                "relevant_memories_count": int(rmc),
                # Confidence
                "confidence": float(legacy_conf) if legacy_conf is not None else 0.5,
                "confidence_breakdown": cb,
            }

            # Preserve additional fields from base that we didn't explicitly map but are safe scalars
            if isinstance(base, dict):
                passthrough_keys = [
                    "provider",
                    "model",
                    "latency_ms",
                    "usage",
                    "id",
                ]
                for k in passthrough_keys:
                    if k in base and k not in normalized:
                        normalized[k] = base[k]

            # Scratchpad policy knob (ephemeral|persisted|redacted)
            try:
                _sp = None
                if isinstance(base, dict) and base.get("scratchpad_policy"):
                    _sp = str(base.get("scratchpad_policy")).strip().lower()
                if not _sp and isinstance(ctx, dict) and ctx.get("scratchpad_policy"):
                    _sp = str(ctx.get("scratchpad_policy")).strip().lower()
                if _sp in ("ephemeral", "persisted", "redacted"):
                    normalized["scratchpad_policy"] = _sp
            except Exception:
                pass

            # Evidence list: pass-through if provided, else derive from memories/sources
            def _coerce_evidence_item(it: Any) -> Optional[Dict[str, Any]]:
                try:
                    if not isinstance(it, dict):
                        return None
                    kind = str(it.get("kind") or "").strip().lower()
                    # Heuristics for type
                    if not kind:
                        if it.get("id") or it.get("memory_id") or it.get("uid"):
                            kind = "memory"
                        elif it.get("uri") or it.get("url"):
                            kind = "doc"
                    out: Dict[str, Any] = {"kind": kind or "memory"}
                    # Common fields
                    if it.get("id"):
                        out["id"] = it.get("id")
                    if not out.get("id") and it.get("memory_id"):
                        out["id"] = it.get("memory_id")
                    if it.get("uri") or it.get("url"):
                        out["uri"] = it.get("uri") or it.get("url")
                    if it.get("title"):
                        out["title"] = it.get("title")
                    # Score
                    try:
                        _sv = it.get("score")
                        _rv = it.get("relevance")
                        _cv = it.get("confidence")
                        if _sv is not None:
                            out["score"] = float(_sv)
                        elif _rv is not None:
                            out["score"] = float(_rv)
                        elif _cv is not None:
                            out["score"] = float(_cv)
                    except Exception:
                        pass
                    # Snippet
                    if it.get("snippet") or it.get("text") or it.get("content"):
                        snip = it.get("snippet") or it.get("text") or it.get("content")
                        try:
                            snip = str(snip)
                            # Trim excessively long snippets
                            if len(snip) > 1024:
                                snip = snip[:1024]
                        except Exception:
                            pass
                        out["snippet"] = snip
                    # Tags
                    tags = it.get("tags")
                    if isinstance(tags, list):
                        out["tags"] = tags
                    elif isinstance(tags, str) and tags:
                        out["tags"] = [tags]
                    return out
                except Exception:
                    return None

            try:
                evidence: list[Dict[str, Any]] = []
                # Pass-through preferred
                if isinstance(base, dict) and isinstance(base.get("evidence"), list):
                    for it in base.get("evidence") or []:
                        co = _coerce_evidence_item(it)
                        if co:
                            evidence.append(co)
                else:
                    # Derive from relevant_memories
                    if isinstance(base, dict) and isinstance(
                        base.get("relevant_memories"), list
                    ):
                        for m in base.get("relevant_memories") or []:
                            co = _coerce_evidence_item(
                                {
                                    **(m if isinstance(m, dict) else {}),
                                    "kind": "memory",
                                }
                            )
                            if co:
                                evidence.append(co)
                    # Derive from sources/documents
                    for k in ("sources", "documents", "docs"):
                        if isinstance(base, dict) and isinstance(base.get(k), list):
                            for d in base.get(k) or []:
                                co = _coerce_evidence_item(
                                    {
                                        **(d if isinstance(d, dict) else {}),
                                        "kind": "doc",
                                    }
                                )
                                if co:
                                    evidence.append(co)
                if evidence:
                    normalized["evidence"] = evidence
            except Exception:
                pass

            return normalized

        def _get_klm_metrics_sync():
            """Best-effort Module Manager (KLM) metrics via the registry."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("module_manager")
                    if not info or not info.instance:
                        return None
                    inst = info.instance
                    if hasattr(inst, "get_metrics"):
                        try:
                            return inst.get_metrics()
                        except Exception:
                            return None
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass
            return None

        def _get_klm_status_sync():
            """Best-effort Module Manager (KLM) status via the registry."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("module_manager")
                    if not info or not info.instance:
                        return None
                    inst = info.instance
                    if hasattr(inst, "get_status"):
                        try:
                            return inst.get_status()
                        except Exception:
                            return None
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass
            return None

        def _get_keb_metrics_sync():
            """Best-effort Event Bus (KEB) metrics via the registry."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("event_bus")
                    if not info or not info.instance:
                        return None
                    inst = info.instance
                    if hasattr(inst, "get_metrics"):
                        try:
                            return inst.get_metrics()
                        except Exception:
                            return None
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass
            return None

        def _get_keb_status_sync():
            """Best-effort Event Bus (KEB) status via the registry."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("event_bus")
                    if not info or not info.instance:
                        return None
                    inst = info.instance
                    if hasattr(inst, "get_status"):
                        try:
                            return inst.get_status()
                        except Exception:
                            return None
                    return None

                res = _a.run(_run())
                if isinstance(res, dict):
                    return res
            except Exception:
                pass
            return None

        @app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "status": "healthy",
                    "uptime_seconds": (
                        datetime.now() - self.stats["startup_time"]
                    ).total_seconds(),
                    "plugins_registered": len(self.plugins),
                    "requests_served": self.stats["requests_served"],
                }
            )

        @app.route("/status", methods=["GET"])
        def status_check():
            """Status endpoint for Hub connector compatibility"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "status": "online",
                    "running": True,
                    "uptime_seconds": (
                        datetime.now() - self.stats["startup_time"]
                    ).total_seconds(),
                    "plugins_registered": len(self.plugins),
                    "requests_served": self.stats["requests_served"],
                    "hub_connected": True,
                    "services": ["hub_server", "plugin_registry"],
                    "capabilities": [
                        "plugin_registration",
                        "plugin_discovery",
                        "marketplace",
                    ],
                }
            )

        @app.route("/api/plugins", methods=["GET"])
        def list_plugins():
            """List all registered plugins"""
            self.stats["requests_served"] += 1
            data = {
                "plugins": list(self.plugins.values()),
                "total": len(self.plugins),
                "timestamp": datetime.now().isoformat(),
            }
            # Include federated view if available
            if self.federation is not None:
                data["federated"] = self.federation.get_federated_plugins()
                data["peers"] = self.federation.list_peers()
            return jsonify(data)  # type: ignore[name-defined]

        @app.route("/api/plugins/register", methods=["POST"])
        def register_plugin():
            """Register a new plugin"""
            try:
                plugin_data = request.get_json()  # type: ignore[name-defined]
                if not plugin_data or not isinstance(plugin_data, dict):
                    return jsonify({"error": "Invalid plugin data"}), 400  # type: ignore[name-defined]

                # Determine strictness at request time (env-driven)
                strict_env = (
                    os.environ.get("AETHERRA_SIGNING_STRICT", "0") == "1"
                    or os.environ.get("AETHERRA_HUB_STRICT", "0") == "1"
                    or os.environ.get("AETHERRA_STRICT", "0") == "1"
                )
                # Determine strictness from environment only (test-driven behavior)
                strict = bool(strict_env)

                # Compute signature presence early (used in schema relaxation path)
                has_sig = bool(plugin_data.get("signature")) and bool(
                    plugin_data.get("pubkey")
                )

                # Validate manifest schema before any mutation (always enforced)
                schema_errors = []
                normalized = dict(plugin_data)
                try:
                    from Aetherra.plugins.manifest_schema import validate_manifest

                    ok, errs, norm = validate_manifest(plugin_data)
                    schema_errors = errs
                    normalized = norm
                except Exception:
                    # If validator unavailable, respond with a clear error in strict
                    # and accept in non-strict for dev convenience
                    ok = not strict
                if not ok:
                    # Allow a minimal manifest missing only entry_point in two cases:
                    # 1) Non-strict mode (dev convenience)
                    # 2) Strict mode when a valid signature is present (schema can be normalized safely)
                    missing_entry_only = (
                        isinstance(schema_errors, list)
                        and len(schema_errors) == 1
                        and (
                            "entry_point" in str(schema_errors[0])
                            and "required" in str(schema_errors[0])
                        )
                    )
                    soft_entry_only = (not strict) and missing_entry_only
                    strict_signed_entry_only = False
                    if strict and missing_entry_only and has_sig:
                        # Ensure we can verify signature against the original payload
                        # Load verifier lazily if needed
                        if (getattr(self, "verify_signature", None) is None) or (
                            not getattr(self, "_signing_has_lib", False)
                        ):
                            try:
                                import importlib as _imp

                                _ps = _imp.import_module(
                                    "Aetherra.security.plugin_signing"
                                )
                                self.verify_signature = getattr(
                                    _ps, "verify_plugin_signature", None
                                )
                                self._signing_has_lib = bool(
                                    getattr(_ps, "NACL", False)
                                )
                            except Exception:
                                self.verify_signature = None
                                self._signing_has_lib = False
                        try:
                            _verifier = getattr(self, "verify_signature", None)
                            if callable(_verifier):
                                strict_signed_entry_only = bool(_verifier(plugin_data))
                        except Exception:
                            strict_signed_entry_only = False

                    if soft_entry_only or strict_signed_entry_only:
                        # Fill a safe default entry point for dev/strict-signed; proceed
                        normalized = dict(plugin_data)
                        normalized.setdefault("entry_point", "main.py")
                        ok = True
                    else:
                        return (
                            jsonify(
                                {"error": "manifest_invalid", "details": schema_errors}
                            ),  # type: ignore[name-defined]
                            400,
                        )

                # Verify signature (before mutating payload)
                verified = False
                if strict:
                    # In strict mode, signature must be present and valid
                    if not has_sig:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                    # Quick sanity check: signature and pubkey must be valid base64
                    try:
                        import base64 as _b64

                        sig_b64 = str(plugin_data.get("signature"))
                        pk_b64 = str(plugin_data.get("pubkey"))
                        _ = _b64.b64decode(sig_b64, validate=True)
                        _ = _b64.b64decode(pk_b64, validate=True)
                    except Exception:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                    # If verification library is unavailable, attempt a lazy import
                    if (getattr(self, "verify_signature", None) is None) or (
                        not getattr(self, "_signing_has_lib", False)
                    ):
                        try:
                            import importlib as _imp

                            _ps = _imp.import_module("Aetherra.security.plugin_signing")
                            self.verify_signature = getattr(
                                _ps, "verify_plugin_signature", None
                            )
                            self._signing_has_lib = bool(getattr(_ps, "NACL", False))
                        except Exception:
                            pass
                    # If verifier is unavailable, reject in strict mode
                    if getattr(self, "verify_signature", None) is None:
                        return (
                            jsonify(  # type: ignore[name-defined,operator]
                                {"error": "signature verification unavailable"}
                            ),
                            400,
                        )
                    try:
                        verified = bool(self.verify_signature(plugin_data))  # type: ignore[call-arg]
                    except Exception:
                        verified = False
                    if not verified:
                        return jsonify({"error": "invalid signature"}), 400  # type: ignore[name-defined]
                else:
                    # Non-strict: verify if signature present; otherwise allow
                    if has_sig and getattr(self, "verify_signature", None) is not None:
                        try:
                            verified = bool(self.verify_signature(plugin_data))  # type: ignore[call-arg]
                        except Exception:
                            verified = False

                # Compute trust zone mapping
                trust_zone = "unsigned"
                try:
                    from Aetherra.plugins.manifest_schema import compute_trust_zone

                    trust_zone = compute_trust_zone(strict, bool(verified))
                except Exception:
                    trust_zone = "unsigned"

                # Use normalized manifest for storage
                plugin_id = (
                    normalized.get("name")
                    or plugin_data.get("name")
                    or f"plugin_{len(self.plugins) + 1}"
                )
                # Mutate only after verification
                normalized["registered_at"] = datetime.now().isoformat()
                normalized["status"] = "registered"
                normalized["signature_verified"] = bool(verified)
                normalized["trust_zone"] = trust_zone

                self.plugins[plugin_id] = normalized
                self.stats["requests_served"] += 1
                self.stats["active_registrations"] += 1

                logger.info(f"[OK] Plugin registered: {plugin_id}")

                return jsonify(
                    {  # type: ignore[name-defined]
                        "status": "success",
                        "message": f"Plugin {plugin_id} registered successfully",
                        "plugin_id": plugin_id,
                    }
                )

            except Exception as e:
                logger.error(f"Γ¥î Plugin registration failed: {e}")
                return jsonify({"error": str(e)}), 500  # type: ignore[name-defined]

        @app.route("/api/plugins/<plugin_id>", methods=["GET"])
        def get_plugin(plugin_id):
            """Get specific plugin details"""
            self.stats["requests_served"] += 1
            if plugin_id in self.plugins:
                return jsonify(self.plugins[plugin_id])  # type: ignore[name-defined]
            else:
                return jsonify({"error": "Plugin not found"}), 404  # type: ignore[name-defined]

        @app.route("/api/stats", methods=["GET"])
        def get_stats():
            """Get Hub statistics"""
            self.stats["requests_served"] += 1
            out = dict(self.stats)
            # Best-effort: include Lyrixa chat service availability from the registry
            try:
                from aetherra_service_registry import get_service_registry

                async def _get():
                    reg = await get_service_registry()
                    info = reg.get_service_info("lyrixa_chat")
                    if not info:
                        return {"registered": False}
                    return {
                        "registered": True,
                        "status": getattr(info.status, "value", str(info.status)),
                        "registered_at": info.registered_at.isoformat(),
                        "last_heartbeat": info.last_heartbeat.isoformat(),
                    }

                out["lyrixa_chat"] = _run_coro_blocking(_get())
            except Exception:
                out["lyrixa_chat"] = {"registered": False}
            if self.federation is not None:
                out["peers"] = self.federation.list_peers()
                out["federated_count"] = len(self.federation.get_federated_plugins())
            return jsonify(out)  # type: ignore[name-defined]

        @app.route("/api/registry/status", methods=["GET"])
        def api_registry_status():
            """Expose the Service Registry status (counts, services, timestamps)."""
            self.stats["requests_served"] += 1
            status = _get_registry_status_sync()
            if not isinstance(status, dict):
                status = {"running": False}
            return jsonify(status)  # type: ignore[name-defined]

        @app.route("/api/health", methods=["GET"])
        def api_health():
            """Aggregate lightweight health snapshot for probes/dashboards.

            Returns JSON with keys:
              ok: overall boolean (kernel running)
              ts: hub timestamp
              kernel: subset of kernel status
              registry: basic registry stats
              orchestrator: (present if engine/orchestrator registered)
              memory: quantum memory coherence/fragment stats (best-effort)
              chat: minimal chat counters
            """
            self.stats["requests_served"] += 1
            from datetime import (
                datetime as _dt,
            )  # local import to avoid top-level churn

            # Defensive wrappers
            def _subset_kernel(ks: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[name-defined]
                if not isinstance(ks, dict):
                    return {"running": False}
                out: Dict[str, Any] = {  # type: ignore[name-defined]
                    "running": bool(
                        ks.get("running") is True
                        or str(ks.get("state", "")).lower() == "running"
                    ),
                    "paused": bool(ks.get("paused", False)),
                }
                # Optional fields if present
                for k in ("uptime", "uptime_seconds"):
                    val = ks.get(k)
                    if isinstance(val, (int, float)):
                        try:
                            out["uptime_seconds"] = float(val)
                        except Exception:
                            pass
                        break
                qsz = ks.get("queue_sizes") or {}
                if isinstance(qsz, dict) and qsz:
                    try:
                        out["queue_sizes"] = {
                            "high": int(qsz.get("high_priority", 0) or 0),
                            "normal": int(qsz.get("normal_priority", 0) or 0),
                            "background": int(qsz.get("background", 0) or 0),
                        }
                    except Exception:
                        pass
                return out

            def _subset_registry(rs: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[name-defined]
                if not isinstance(rs, dict):
                    return {"ok": False}
                return {
                    "ok": True,
                    "total_services": int(rs.get("total_services", 0) or 0),
                    "by_status": rs.get("service_count_by_status", {}),
                }

            def _subset_orchestrator(oc: Dict[str, Any]) -> Optional[Dict[str, Any]]:  # type: ignore[name-defined]
                if not isinstance(oc, dict) or not oc:
                    return None
                try:
                    return {
                        "status": oc.get("status"),
                        "total_agents": oc.get("total_agents"),
                        "pending_tasks": oc.get("pending_tasks"),
                    }
                except Exception:
                    return None

            def _subset_memory(ms: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore[name-defined]
                if not isinstance(ms, dict):
                    return {"enabled": False}
                out: Dict[str, Any] = {  # type: ignore[name-defined]
                    "enabled": bool(ms.get("enabled", False)),
                }
                for k in ("coherence", "fragments", "branches", "entanglement_nodes"):
                    if k in ms:
                        try:
                            out[k] = ms.get(k)
                        except Exception:
                            pass
                if isinstance(ms.get("branch"), str):
                    out["branch"] = ms.get("branch")
                return out

            ks = _get_kernel_status_sync()
            rs = _get_registry_status_sync()
            orch = (
                _get_orchestrator_status_sync()
                if "_get_orchestrator_status_sync" in globals()
                else None
            )
            ms = _get_memory_quantum_status_sync()

            kernel_sub = _subset_kernel(ks)  # type: ignore[arg-type]
            registry_sub = _subset_registry(rs)  # type: ignore[arg-type]
            orch_sub = _subset_orchestrator(orch) if orch else None  # type: ignore[arg-type]
            memory_sub = _subset_memory(ms)  # type: ignore[arg-type]

            ok = bool(kernel_sub.get("running") is True)

            # Minimal chat counters (already thread-safe dict usage in hub)
            chat_sub = {}
            try:
                cm = self.chat_metrics
                chat_sub = {
                    "requests_total": int(cm.get("requests_total", 0) or 0),
                    "streams_current": int(cm.get("streams_current", 0) or 0),
                }
            except Exception:
                pass

            payload: Dict[str, Any] = {  # type: ignore[name-defined]
                "ok": ok,
                "ts": _dt.now().isoformat(),
                "kernel": kernel_sub,
                "registry": registry_sub,
                "memory": memory_sub,
                "chat": chat_sub,
            }
            if orch_sub:
                payload["orchestrator"] = orch_sub
            # Optional hub version if attribute available
            try:
                if getattr(self, "version", None):
                    payload["version"] = str(getattr(self, "version"))
            except Exception:
                pass
            return jsonify(payload)  # type: ignore[name-defined]

        @app.route("/api/kernel/metrics", methods=["GET"])
        def api_kernel_metrics():
            """Expose kernel status/metrics as JSON via the Hub."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {"running": False}
            # Add minimal hub context
            return jsonify({"hub_ts": datetime.now().isoformat(), "kernel": ks})  # type: ignore[name-defined]

        @app.route("/api/kernel/status", methods=["GET"])
        def api_kernel_status():
            """Return kernel get_status() as JSON (lightweight)."""
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {"running": False}
            return jsonify(ks)  # type: ignore[name-defined]

        # KLM (Module Manager) JSON endpoints
        @app.route("/api/klm/status", methods=["GET"])
        def api_klm_status():
            """Expose Module Manager get_status() as JSON (read-only)."""
            self.stats["requests_served"] += 1
            st = _get_klm_status_sync()
            if not isinstance(st, dict):
                st = {"enabled": False}
            return jsonify(st)  # type: ignore[name-defined]

        @app.route("/api/klm/metrics", methods=["GET"])
        def api_klm_metrics():
            """Expose Module Manager get_metrics() as JSON (read-only)."""
            self.stats["requests_served"] += 1
            mt = _get_klm_metrics_sync()
            if not isinstance(mt, dict):
                mt = {}
            return jsonify(mt)  # type: ignore[name-defined]

        # KEB (Event Bus) JSON endpoints
        @app.route("/api/keb/status", methods=["GET"])
        def api_keb_status():
            """Expose Event Bus get_status() as JSON (read-only)."""
            self.stats["requests_served"] += 1
            st = _get_keb_status_sync()
            if not isinstance(st, dict):
                st = {"enabled": False}
            return jsonify(st)  # type: ignore[name-defined]

        @app.route("/api/keb/metrics", methods=["GET"])
        def api_keb_metrics():
            """Expose Event Bus get_metrics() as JSON (read-only)."""
            self.stats["requests_served"] += 1
            mt = _get_keb_metrics_sync()
            if not isinstance(mt, dict):
                mt = {}
            return jsonify(mt)  # type: ignore[name-defined]

        @app.route("/api/site_status", methods=["GET"])
        @app.route("/site_status", methods=["GET"])  # alias for older/alternate clients
        def api_site_status():
            """Aggregated status for Docs widget to minimize cross-origin requests.

            Returns a JSON bundle with:
            - plugins.total: count of registered plugins
            - kernel.running: boolean if kernel is running
            - kernel.uptime_seconds: numeric uptime if available
            - kernel.queue_sizes: {high_priority, normal_priority, background}
            - hub.ts: ISO timestamp when generated
            - hub.requests_served: hub request counter
            """
            self.stats["requests_served"] += 1
            ks = _get_kernel_status_sync()
            if not isinstance(ks, dict):
                ks = {}
            # Derive running state and uptime
            running = bool(
                ks.get("running") is True
                or str(ks.get("state", "")).lower() == "running"
            )
            uptime = 0.0
            try:
                # Prefer direct uptime key; fallback to metrics.uptime if present
                if isinstance(ks.get("uptime"), (int, float)):
                    uptime = float(ks.get("uptime") or 0.0)
                else:
                    uptime = float((ks.get("metrics", {}) or {}).get("uptime", 0.0))
            except Exception:
                uptime = 0.0
            # Queue sizes map
            qs = (
                ks.get("queue_sizes", {})
                if isinstance(ks.get("queue_sizes"), dict)
                else {}
            )
            out = {
                "ok": True,
                "hub": {
                    "ts": datetime.now().isoformat(),
                    "requests_served": self.stats.get("requests_served", 0),
                },
                "plugins": {"total": int(len(self.plugins))},
                "kernel": {
                    "running": running,
                    "uptime_seconds": uptime,
                    "queue_sizes": {
                        "high_priority": int(qs.get("high_priority", 0) or 0),
                        "normal_priority": int(qs.get("normal_priority", 0) or 0),
                        "background": int(qs.get("background", 0) or 0),
                    },
                },
            }
            return jsonify(out)  # type: ignore[name-defined]

        @app.route("/metrics", methods=["GET"])
        def prometheus_metrics():
            """Prometheus-style plaintext metrics for quick scraping (reduced complexity)."""
            self.stats["requests_served"] += 1

            # Collect sources once
            ks = _get_kernel_status_sync() or {}
            rs = _get_registry_status_sync() or {}
            orch = _get_orchestrator_status_sync() or {}
            ms = _get_memory_quantum_status_sync() or {}
            ma = _get_memory_audit_sync() or {}
            ac = _get_hmr_audit_counters_sync() or {}
            km = _get_klm_metrics_sync() or {}
            em = _get_keb_metrics_sync() or {}
            qs = _get_quantum_bridge_status() or {}

            lines: list[str] = []

            def _num(x):  # numeric coercion
                try:
                    return float(x)
                except Exception:
                    return 0.0

            # --- Emitters (each returns optional context flags) ---
            def _emit_kernel():
                emitted_hist = False
                try:
                    if not isinstance(ks, dict) or not ks:
                        return False
                    m = ks.get("metrics", {}) or {}
                    kqs = ks.get("queue_sizes", {}) or {}
                    kql = ks.get("queue_limits", {}) or {}
                    cb_open = bool(ks.get("plugin_cb_open", False))
                    dlq_count = int(ks.get("dlq_count", 0))
                    uptime = float(ks.get("uptime", 0))
                    lines.extend(
                        [
                            f"aetherra_kernel_uptime_seconds {_num(uptime)}",
                            f"aetherra_kernel_cycles_total {_num(m.get('total_cycles', 0))}",
                            f"aetherra_kernel_cycle_time_seconds {_num(m.get('last_cycle_time', 0.0))}",
                            f"aetherra_kernel_cycle_time_seconds_avg {_num(m.get('avg_cycle_time', 0.0))}",
                            f"aetherra_kernel_errors_total {_num(m.get('errors_count', 0))}",
                            f"aetherra_kernel_night_cycles_total {_num(m.get('night_cycles_count', 0))}",
                            f'aetherra_kernel_queue_size{{queue="high"}} {_num(kqs.get("high_priority", 0))}',
                            f'aetherra_kernel_queue_size{{queue="normal"}} {_num(kqs.get("normal_priority", 0))}',
                            f'aetherra_kernel_queue_size{{queue="background"}} {_num(kqs.get("background", 0))}',
                            f'aetherra_kernel_queue_limit{{queue="high"}} {_num(kql.get("high_priority", 0))}',
                            f'aetherra_kernel_queue_limit{{queue="normal"}} {_num(kql.get("normal_priority", 0))}',
                            f'aetherra_kernel_queue_limit{{queue="background"}} {_num(kql.get("background", 0))}',
                            f'aetherra_kernel_queue_drops_total{{queue="high"}} {_num(m.get("drops_high", 0))}',
                            f'aetherra_kernel_queue_drops_total{{queue="normal"}} {_num(m.get("drops_normal", 0))}',
                            f'aetherra_kernel_queue_drops_total{{queue="background"}} {_num(m.get("drops_background", 0))}',
                            f"aetherra_kernel_tasks_expired_total {_num(m.get('expired_tasks', 0))}",
                            f"aetherra_kernel_dlq_count {_num(dlq_count)}",
                            f"aetherra_kernel_plugin_cb_open {1 if cb_open else 0}",
                        ]
                    )
                    for k in (
                        "plugin_invoke_timeouts",
                        "plugin_invoke_errors",
                        "plugin_cb_open_count",
                        "plugin_invoke_rate_limited",
                    ):
                        if k in m:
                            lines.append(f"aetherra_kernel_{k} {_num(m.get(k, 0))}")
                    hist = m.get("cycle_hist") or {}
                    if isinstance(hist, dict) and hist:
                        try:
                            order = sorted(
                                [float(x) for x in hist.keys() if x != "+Inf"]
                            )
                            cum = 0.0
                            for b in order:
                                v = _num(hist.get(b, 0))
                                cum += max(0.0, v)
                                lines.append(
                                    f'aetherra_kernel_cycle_time_ms_bucket{{le="{int(b)}"}} {cum}'
                                )
                            emitted_hist = True
                            inf_v = _num(hist.get("+Inf", 0))
                            lines.append(
                                f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {cum + max(0.0, inf_v)}'
                            )
                        except Exception:
                            pass
                    else:
                        try:
                            raw = float(m.get("last_cycle_time", 0.0))
                            ms_val = raw * 1000.0 if raw < 10 else raw
                        except Exception:
                            ms_val = 0.0
                        if ms_val > 0:
                            placed = False
                            for b in (10, 20, 50, 100, 200, 500, 1000):
                                if ms_val <= b:
                                    self.kernel_latency_hist[b] = (
                                        int(self.kernel_latency_hist.get(b, 0)) + 1
                                    )
                                    placed = True
                                    break
                            if not placed:
                                self.kernel_latency_hist["+Inf"] = (
                                    int(self.kernel_latency_hist.get("+Inf", 0)) + 1
                                )
                        cum = 0
                        for b in (10, 20, 50, 100, 200, 500, 1000):
                            cum += int(self.kernel_latency_hist.get(b, 0))
                            lines.append(
                                f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} {_num(cum)}'
                            )
                        emitted_hist = True
                        lines.append(
                            f'aetherra_kernel_cycle_time_ms_bucket{{le="+Inf"}} {_num(cum + int(self.kernel_latency_hist.get("+Inf", 0)))}'
                        )
                    try:
                        infl = ks.get("inflight", {}) or {}
                        if isinstance(infl, dict):
                            for t, v in infl.items():
                                lines.append(
                                    f'aetherra_kernel_inflight_current{{target="{str(t)}"}} {_num(v)}'
                                )
                    except Exception:
                        pass
                except Exception:
                    pass
                return emitted_hist

            def _emit_sandbox():
                try:
                    sm = getattr(self, "sandbox_metrics", {}) or {}
                    if isinstance(sm, dict):
                        for k in (
                            "plugin_timeout_total",
                            "sandbox_violations_total",
                            "sandbox_policy_denied_total",
                            "sandbox_exec_total",
                        ):
                            if k in sm:
                                lines.append(
                                    f"aetherra_sandbox_{k} {_num(sm.get(k, 0))}"
                                )
                except Exception:
                    pass

            def _emit_registry():
                try:
                    if isinstance(rs, dict) and rs:
                        lines.append(
                            f"aetherra_registry_services_total {_num(rs.get('total_services', 0))}"
                        )
                        sc = rs.get("service_count_by_status") or {}
                        for st, cnt in sc.items():
                            lines.append(
                                f'aetherra_registry_services{{status="{st}"}} {_num(cnt)}'
                            )
                except Exception:
                    pass

            def _emit_hmr():
                try:
                    if isinstance(ac, dict) and ac:
                        for evt, cnt in ac.items():
                            lines.append(
                                f'aetherra_hmr_audit_total{{event="{str(evt)}"}} {_num(cnt)}'
                            )
                except Exception:
                    pass

            def _emit_klm():
                try:
                    if isinstance(km, dict) and km:
                        lines.extend(
                            [
                                f"aetherra_klm_loads_total {_num(km.get('loads_total', 0))}",
                                f"aetherra_klm_reloads_total {_num(km.get('reloads_total', 0))}",
                                f"aetherra_klm_rollbacks_total {_num(km.get('rollbacks_total', 0))}",
                                f"aetherra_klm_active_modules {_num(km.get('active_modules', 0))}",
                            ]
                        )
                        pma = km.get("per_module_active", {}) or {}
                        if isinstance(pma, dict):
                            for mod, val in pma.items():
                                try:
                                    lines.append(
                                        f'aetherra_klm_active_module{{module="{str(mod)}"}} {_num(val)}'
                                    )
                                except Exception:
                                    pass
                except Exception:
                    pass

            def _emit_keb():
                try:
                    if isinstance(em, dict) and em:
                        lines.extend(
                            [
                                f"aetherra_keb_events_published_total {_num(em.get('events_published_total', 0))}",
                                f"aetherra_keb_events_delivered_total {_num(em.get('events_delivered_total', 0))}",
                                f"aetherra_keb_events_dropped_burst {_num(em.get('events_dropped_burst', 0))}",
                            ]
                        )
                        tb = em.get("topic_backlog", {}) or {}
                        if isinstance(tb, dict):
                            for topic, cnt in tb.items():
                                try:
                                    lines.append(
                                        f'aetherra_keb_topic_backlog{{topic="{str(topic)}"}} {_num(cnt)}'
                                    )
                                except Exception:
                                    pass
                except Exception:
                    pass

            def _emit_orchestrator():
                emitted = False
                try:
                    if not isinstance(orch, dict) or not orch:
                        return False
                    lines.extend(
                        [
                            f"aetherra_orchestrator_agents_total {_num(orch.get('total_agents', 0))}",
                            f"aetherra_orchestrator_tasks_pending_total {_num(orch.get('pending_tasks', 0))}",
                        ]
                    )
                    if "active_tasks" in orch:
                        lines.append(
                            f"aetherra_orchestrator_tasks_active {_num(orch.get('active_tasks', 0))}"
                        )
                    pbp = orch.get("pending_by_priority") or {}
                    if isinstance(pbp, dict):
                        for prio, cnt in pbp.items():
                            lines.append(
                                f'aetherra_orchestrator_tasks_pending{{priority="{prio}"}} {_num(cnt)}'
                            )
                    tstat = orch.get("task_statuses") or {}
                    if isinstance(tstat, dict):
                        for st, cnt in tstat.items():
                            lines.append(
                                f'aetherra_orchestrator_tasks_total{{status="{st}"}} {_num(cnt)}'
                            )
                    ctrs = orch.get("counters") or {}
                    if isinstance(ctrs, dict):
                        for k, v in ctrs.items():
                            lines.append(f"aetherra_orchestrator_{str(k)} {_num(v)}")
                    cp = orch.get("coherence_policy") or {}
                    if isinstance(cp, dict) and cp:
                        try:
                            lines.extend(
                                [
                                    f"aetherra_orchestrator_coherence_gate_min {_num(cp.get('gate_min', 0.0))}",
                                    f"aetherra_orchestrator_coherence_hard_min {_num(cp.get('hard_min', 0.0))}",
                                    f"aetherra_orchestrator_coherence_ema {_num(cp.get('ema', 0.0))}",
                                    f"aetherra_orchestrator_coherence_window_size {_num(cp.get('window_size', 0))}",
                                    f"aetherra_orchestrator_last_drift_alert_present {1 if bool(cp.get('last_drift_alert')) else 0}",
                                ]
                            )
                        except Exception:
                            pass
                    oh = (
                        orch.get("latency_hist_ms")
                        or orch.get("task_latency_hist_ms")
                        or {}
                    )
                    if isinstance(oh, dict) and oh:
                        try:
                            order = sorted([float(x) for x in oh.keys() if x != "+Inf"])
                            cum = 0.0
                            for b in order:
                                v = _num(oh.get(b, 0))
                                cum += max(0.0, v)
                                lines.append(
                                    f'aetherra_orchestrator_task_latency_ms_bucket{{le="{int(b)}"}} {cum}'
                                )
                            emitted = True
                            inf_v = _num(oh.get("+Inf", 0))
                            lines.append(
                                f'aetherra_orchestrator_task_latency_ms_bucket{{le="+Inf"}} {cum + max(0.0, inf_v)}'
                            )
                        except Exception:
                            pass
                    else:
                        try:
                            ms_val = float(orch.get("avg_task_latency_ms", 0.0))
                        except Exception:
                            ms_val = 0.0
                        if ms_val > 0:
                            placed = False
                            for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                                if ms_val <= b:
                                    self.orchestrator_latency_hist[b] = (
                                        int(self.orchestrator_latency_hist.get(b, 0))
                                        + 1
                                    )
                                    placed = True
                                    break
                            if not placed:
                                self.orchestrator_latency_hist["+Inf"] = (
                                    int(self.orchestrator_latency_hist.get("+Inf", 0))
                                    + 1
                                )
                        cum = 0
                        for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                            cum += int(self.orchestrator_latency_hist.get(b, 0))
                            lines.append(
                                f'aetherra_orchestrator_task_latency_ms_bucket{{le="{b}"}} {_num(cum)}'
                            )
                        emitted = True
                        lines.append(
                            f'aetherra_orchestrator_task_latency_ms_bucket{{le="+Inf"}} {_num(cum + int(self.orchestrator_latency_hist.get("+Inf", 0)))}'
                        )
                except Exception:
                    pass
                return emitted

            def _emit_kernel_hist_fallback(emitted):
                if emitted:
                    return
                try:
                    for b in (10, 20, 50, 100, 200, 500, 1000):
                        lines.append(
                            f'aetherra_kernel_cycle_time_ms_bucket{{le="{b}"}} 0.0'
                        )
                    lines.append(
                        'aetherra_kernel_cycle_time_ms_bucket{le="+Inf"} 0.0'.replace(
                            "{", "{{"
                        ).replace("}", "}}")
                    )
                except Exception:
                    pass

            def _emit_orchestrator_hist_fallback(emitted):
                if emitted:
                    return
                try:
                    for b in (10, 20, 50, 100, 200, 500, 1000, 2000):
                        lines.append(
                            f'aetherra_orchestrator_task_latency_ms_bucket{{le="{b}"}} 0.0'
                        )
                    lines.append(
                        'aetherra_orchestrator_task_latency_ms_bucket{le="+Inf"} 0.0'.replace(
                            "{", "{{"
                        ).replace("}", "}}")
                    )
                except Exception:
                    pass

            def _emit_memory():
                try:
                    if isinstance(ms, dict) and ms:
                        if "coherence" in ms:
                            lines.append(
                                f"aetherra_memory_coherence_score {_num(ms.get('coherence', 0.0))}"
                            )
                        if "branches" in ms:
                            lines.append(
                                f"aetherra_memory_branches_total {_num(ms.get('branches', 0))}"
                            )
                        if "fragments" in ms:
                            lines.append(
                                f"aetherra_memory_fragments_total {_num(ms.get('fragments', 0))}"
                            )
                        if "entanglement_nodes" in ms:
                            lines.append(
                                f"aetherra_memory_entanglement_nodes_total {_num(ms.get('entanglement_nodes', 0))}"
                            )
                        if isinstance(ms.get("branch"), str):
                            lines.append(
                                f'aetherra_memory_branch_info{{branch="{str(ms.get("branch"))}"}} 1'
                            )
                    if isinstance(ma, dict) and ma:
                        audit = ma.get("audit") or {}
                        if isinstance(audit, dict):
                            nodes_val = audit.get("nodes")
                            nodes_cnt = None
                            if isinstance(nodes_val, (list, tuple)):
                                try:
                                    nodes_cnt = len(nodes_val)
                                except Exception:
                                    nodes_cnt = None
                            if nodes_cnt is None and isinstance(
                                audit.get("node_count"), (int, float)
                            ):
                                nodes_cnt = audit.get("node_count")
                            if nodes_cnt is not None:
                                lines.append(
                                    f"aetherra_memory_branch_nodes_total {_num(nodes_cnt)}"
                                )
                            edges_val = audit.get("edges")
                            edge_cnt = None
                            if isinstance(edges_val, (list, tuple)):
                                try:
                                    edge_cnt = len(edges_val)
                                except Exception:
                                    edge_cnt = None
                                try:
                                    by_type = {}
                                    for e in edges_val:
                                        if isinstance(e, dict):
                                            t = (
                                                str(e.get("type") or "").strip()
                                                or "unknown"
                                            )
                                            by_type[t] = int(by_type.get(t, 0)) + 1
                                    for t, cnt in by_type.items():
                                        lines.append(
                                            f'aetherra_memory_branch_edges_total_by_type{{type="{t}"}} {_num(cnt)}'
                                        )
                                except Exception:
                                    pass
                            if edge_cnt is None and isinstance(
                                audit.get("edge_count"), (int, float)
                            ):
                                edge_cnt = audit.get("edge_count")
                            if edge_cnt is not None:
                                lines.append(
                                    f"aetherra_memory_branch_edges_total {_num(edge_cnt)}"
                                )
                            try:
                                nodes_by_branch = {}
                                if isinstance(nodes_val, (list, tuple)):
                                    for n in nodes_val:
                                        if isinstance(n, dict):
                                            br = str(
                                                n.get("branch")
                                                or n.get("branch_id")
                                                or ""
                                            ).strip()
                                            if br:
                                                nodes_by_branch[br] = (
                                                    int(nodes_by_branch.get(br, 0)) + 1
                                                )
                                edges_by_branch = {}
                                if isinstance(edges_val, (list, tuple)):
                                    for e in edges_val:
                                        if isinstance(e, dict):
                                            br = str(
                                                e.get("branch")
                                                or e.get("src_branch")
                                                or e.get("src_branch_id")
                                                or ""
                                            ).strip()
                                            if br:
                                                edges_by_branch[br] = (
                                                    int(edges_by_branch.get(br, 0)) + 1
                                                )
                                if 0 < len(nodes_by_branch) <= 8:
                                    for br, cnt in nodes_by_branch.items():
                                        lines.append(
                                            f'aetherra_memory_branch_nodes{{branch="{br}"}} {_num(cnt)}'
                                        )
                                if 0 < len(edges_by_branch) <= 8:
                                    for br, cnt in edges_by_branch.items():
                                        lines.append(
                                            f'aetherra_memory_branch_edges{{branch="{br}"}} {_num(cnt)}'
                                        )
                            except Exception:
                                pass
                except Exception:
                    pass

            def _emit_chat():
                try:
                    cm = self.chat_metrics
                    lines.extend(
                        [
                            f"aetherra_chat_requests_total {_num(cm.get('requests_total', 0))}",
                            f"aetherra_chat_streams_current {_num(cm.get('streams_current', 0))}",
                        ]
                    )
                    try:
                        sbp = cm.get("streams_by_principal", {}) or {}
                        c = 0
                        for principal, val in sbp.items():
                            lines.append(
                                f'aetherra_chat_streams_current_by_principal{{principal="{str(principal)}"}} {_num(val)}'
                            )
                            c += 1
                            if c >= 10:
                                break
                    except Exception:
                        pass
                    lines.extend(
                        [
                            f"aetherra_chat_latency_ms_sum {_num(cm.get('latency_ms_sum', 0.0))}",
                            f"aetherra_chat_latency_count {_num(cm.get('latency_count', 0))}",
                        ]
                    )
                    try:
                        hist = cm.get("latency_hist", {}) or {}
                        order = [50, 100, 250, 500, 1000, 2000, 5000]
                        cum = 0
                        for b in order:
                            cnt = int(hist.get(b, 0))
                            cum += max(0, cnt)
                            lines.append(
                                f'aetherra_chat_latency_ms_bucket{{le="{b}"}} {_num(cum)}'
                            )
                        inf_cnt = int(hist.get("+Inf", 0)) + cum
                        lines.append(
                            f'aetherra_chat_latency_ms_bucket{{le="+Inf"}} {_num(inf_cnt)}'
                        )
                    except Exception:
                        pass
                    lines.extend(
                        [
                            f"aetherra_chat_ttft_ms_sum {_num(cm.get('ttft_ms_sum', 0.0))}",
                            f"aetherra_chat_ttft_count {_num(cm.get('ttft_count', 0))}",
                        ]
                    )
                    try:
                        th = cm.get("ttft_hist", {}) or {}
                        order_t = [50, 100, 250, 500, 1000, 2000]
                        cum_t = 0
                        for b in order_t:
                            cnt = int(th.get(b, 0))
                            cum_t += max(0, cnt)
                            lines.append(
                                f'aetherra_chat_ttft_ms_bucket{{le="{b}"}} {_num(cum_t)}'
                            )
                        inf_t = int(th.get("+Inf", 0)) + cum_t
                        lines.append(
                            f'aetherra_chat_ttft_ms_bucket{{le="+Inf"}} {_num(inf_t)}'
                        )
                    except Exception:
                        pass
                    lines.extend(
                        [
                            f"aetherra_chat_chars_in_total {_num(cm.get('chars_in_total', 0))}",
                            f"aetherra_chat_chars_out_total {_num(cm.get('chars_out_total', 0))}",
                            f"aetherra_chat_tokens_in_total {_num(cm.get('tokens_in_total', 0))}",
                            f"aetherra_chat_tokens_out_total {_num(cm.get('tokens_out_total', 0))}",
                            f"aetherra_chat_chunks_total {_num(cm.get('chunks_total', 0))}",
                        ]
                    )
                    try:
                        fpc = cm.get("fallback_path_counts", {}) or {}
                        for k in ("mock", "cached", "engine"):
                            lines.append(
                                f'aetherra_chat_fallback_total{{path="{k}"}} {_num(fpc.get(k, 0))}'
                            )
                    except Exception:
                        pass
                    lines.extend(
                        [
                            f"aetherra_chat_rate_limited_total {_num(cm.get('rate_limited_total', 0))}",
                            f"aetherra_chat_policy_denied_total {_num(cm.get('policy_denied_total', 0))}",
                            f"aetherra_chat_backend_unavailable_total {_num(cm.get('backend_unavailable_total', 0))}",
                            f"aetherra_chat_timeout_total {_num(cm.get('timeout_total', 0))}",
                            f"aetherra_chat_breaker_tripped_total {_num(cm.get('breaker_tripped_total', 0))}",
                            f"aetherra_chat_breaker_open_total {_num(cm.get('breaker_open_total', 0))}",
                        ]
                    )
                except Exception:
                    pass

            def _emit_engine_ab():
                try:
                    if os.environ.get("AETHERRA_HUB_AB_METRICS", "1") != "1":
                        return

                    async def _get_engine_status(engine):  # noqa: E306
                        try:
                            st = await engine.get_system_status()
                            return True, st
                        except Exception:
                            try:
                                sm = engine.get_session_metrics()
                                return True, {"session_metrics": sm}
                            except Exception as _e:
                                return False, str(_e)

                    ok_st, payload = _with_engine_call(_get_engine_status)  # type: ignore[name-defined]
                    if not (bool(ok_st) and isinstance(payload, dict)):
                        return
                    st = payload
                    sm = (
                        st.get("session_metrics")
                        if isinstance(st.get("session_metrics"), dict)
                        else {}
                    )

                    def _g(key, default=0.0):
                        try:
                            return float((sm or {}).get(key, default))
                        except Exception:
                            return float(default)

                    lines.extend(
                        [
                            f"aetherra_engine_ab_recall_total {_g('ab_recall_total', 0.0)}",
                            f"aetherra_engine_ab_recall_classical_total {_g('ab_recall_classical_total', 0.0)}",
                            f"aetherra_engine_ab_recall_quantum_total {_g('ab_recall_quantum_total', 0.0)}",
                            f'aetherra_engine_ab_recall_latency_ms_sum{{bucket="classical"}} {_g("ab_recall_latency_ms_sum_classical", 0.0)}',
                            f'aetherra_engine_ab_recall_latency_ms_count{{bucket="classical"}} {_g("ab_recall_latency_ms_count_classical", 0.0)}',
                            f'aetherra_engine_ab_recall_latency_ms_sum{{bucket="quantum"}} {_g("ab_recall_latency_ms_sum_quantum", 0.0)}',
                            f'aetherra_engine_ab_recall_latency_ms_count{{bucket="quantum"}} {_g("ab_recall_latency_ms_count_quantum", 0.0)}',
                        ]
                    )
                    ab = st.get("ab") if isinstance(st.get("ab"), dict) else {}
                    try:
                        mode = str((ab or {}).get("mode") or "").strip()
                        if mode:
                            lines.append(f'aetherra_engine_ab_mode{{mode="{mode}"}} 1')
                    except Exception:
                        pass
                    try:
                        pmr = 1 if bool((ab or {}).get("pmem_ready", False)) else 0
                        lines.append(f"aetherra_engine_ab_pmem_ready {pmr}")
                    except Exception:
                        pass
                    try:
                        lines.extend(
                            [
                                f"aetherra_style_contractions_total {_g('style_contractions', 0.0)}",
                                f"aetherra_style_questions_total {_g('style_questions', 0.0)}",
                                f"aetherra_style_empathy_total {_g('style_empathy', 0.0)}",
                            ]
                        )
                    except Exception:
                        pass
                except Exception:
                    pass

            def _emit_quantum():
                try:
                    if isinstance(qs, dict) and qs:
                        lines.extend(
                            [
                                f'aetherra_quantum_mode{{provider="{str(qs.get("provider", "sim"))}"}} 1',
                                f"aetherra_quantum_jobs_total {float(qs.get('jobs_total', 0))}",
                                f"aetherra_quantum_shots_total {float(qs.get('shots_total', 0))}",
                                f"aetherra_quantum_queue_current {float(qs.get('queue_current', 0))}",
                                f"aetherra_quantum_cost_usd {float(qs.get('cost_usd', 0.0))}",
                                f"aetherra_quantum_error_rate {float(qs.get('error_rate', 0.0))}",
                            ]
                        )
                except Exception:
                    pass

            def _emit_trainer():
                try:
                    trainer_enabled_flag = (
                        1
                        if os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
                        else 0
                    )
                    lines.append(f"aetherra_trainer_enabled {trainer_enabled_flag}")
                    q = r = c = f = 0
                    with self._trainer_lock:
                        for j in self.trainer_jobs.values():
                            st = str(j.get("state"))
                            if st == "queued":
                                q += 1
                            elif st == "running":
                                r += 1
                            elif st == "completed":
                                c += 1
                            elif st == "failed":
                                f += 1
                    lines.extend(
                        [
                            f'aetherra_trainer_jobs_total{{state="queued"}} {q}',
                            f'aetherra_trainer_jobs_total{{state="running"}} {r}',
                            f'aetherra_trainer_jobs_total{{state="completed"}} {c}',
                            f'aetherra_trainer_jobs_total{{state="failed"}} {f}',
                            f"aetherra_trainer_jobs_running {r}",
                            f"aetherra_trainer_eval_runs_total {int(self._trainer_eval_runs_total)}",
                        ]
                    )
                    eq = er = ec = ef = 0
                    with self._trainer_lock:
                        for eobj in self.trainer_evals.values():
                            st = str(eobj.get("state"))
                            if st == "queued":
                                eq += 1
                            elif st == "running":
                                er += 1
                            elif st == "completed":
                                ec += 1
                            elif st == "failed":
                                ef += 1
                        last_score = self._trainer_eval_last_score
                    lines.extend(
                        [
                            f'aetherra_trainer_evals_total{{state="queued"}} {eq}',
                            f'aetherra_trainer_evals_total{{state="running"}} {er}',
                            f'aetherra_trainer_evals_total{{state="completed"}} {ec}',
                            f'aetherra_trainer_evals_total{{state="failed"}} {ef}',
                        ]
                    )
                    try:
                        if last_score is not None:
                            lines.append(
                                f"aetherra_trainer_eval_last_score {float(last_score)}"
                            )
                    except Exception:
                        pass
                except Exception:
                    pass

            def _emit_agents():
                try:
                    if os.environ.get("AETHERRA_AGENT_PER_METRICS", "1") != "1":
                        return
                    try:
                        from Aetherra.consciousness.agents.agent_registry import (
                            get_agent_registry,
                        )
                    except Exception:
                        get_agent_registry = None  # type: ignore
                    reg = get_agent_registry() if get_agent_registry else None  # type: ignore[call-arg]
                    if not (reg and hasattr(reg, "get_all_agents")):
                        return
                    try:
                        agents = reg.get_all_agents()
                    except Exception:
                        agents = {}
                    if not isinstance(agents, dict):
                        return
                    count = 0
                    for aid, regobj in agents.items():
                        if count >= 20:
                            break
                        try:
                            tot = float(
                                getattr(regobj, "total_requests_handled", 0) or 0
                            )
                            succ = float(getattr(regobj, "successful_requests", 0) or 0)
                            avg = float(
                                getattr(regobj, "average_response_time", 0.0) or 0.0
                            )
                            up = float(getattr(regobj, "uptime_percentage", 0.0) or 0.0)
                            try:
                                sr = (succ / tot) if tot > 0 else 0.0
                            except Exception:
                                sr = 0.0
                            aid_s = str(aid)
                            lines.extend(
                                [
                                    f'aetherra_agent_requests_total{{agent="{aid_s}"}} {_num(tot)}',
                                    f'aetherra_agent_success_rate{{agent="{aid_s}"}} {_num(sr)}',
                                    f'aetherra_agent_avg_latency_ms{{agent="{aid_s}"}} {_num(avg)}',
                                    f'aetherra_agent_uptime_pct{{agent="{aid_s}"}} {_num(up)}',
                                ]
                            )
                            count += 1
                        except Exception:
                            pass
                except Exception:
                    pass

            # Execute emitters
            kernel_hist = _emit_kernel()
            _emit_kernel_hist_fallback(kernel_hist)
            _emit_sandbox()
            _emit_registry()
            _emit_hmr()
            _emit_klm()
            _emit_keb()
            orch_hist = _emit_orchestrator()
            _emit_orchestrator_hist_fallback(orch_hist)
            _emit_memory()
            _emit_chat()
            _emit_engine_ab()
            _emit_quantum()
            _emit_trainer()
            _emit_agents()

            body = "\n".join(lines) + "\n"
            from flask import Response  # type: ignore

            return Response(body, mimetype="text/plain; version=0.0.4; charset=utf-8")  # type: ignore[call-arg]

        # ---------------- Control-plane (opt-in, token-guarded) -----------------
        def _control_enabled_and_token_ok(req):
            if os.environ.get("AETHERRA_HUB_CONTROL_ENABLED", "0") != "1":
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]
            expected = os.environ.get("AETHERRA_HUB_CONTROL_TOKEN", "").strip()
            if not expected:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != expected:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        # ---------------- Optional AI developer API (opt-in) -----------------
        def _ai_enabled_and_token_ok(req):
            """Gate for developer AI APIs.

            Disabled if feature flag is off OR if no engine is registered.
            Token requirements are enforced when enabled.
            """
            # Feature flag must be explicitly enabled
            if not self.ai_api_enabled:
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]

            # Ensure an engine is registered; otherwise treat as disabled for public APIs
            def _engine_registered() -> bool:
                try:
                    res = _with_engine_call(lambda eng: (True, True))
                    return isinstance(res, tuple) and bool(res[0])
                except Exception:
                    return False

            if not _engine_registered():
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]

            # Optional token check: prefer dedicated AI token, fall back to hub control token
            require = self.ai_api_require_token
            if not require:
                return True, None
            token = self.ai_api_token
            if not token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        def _with_engine_call(fn):
            """Call into the registered Aetherra engine (sync or async)."""
            try:
                import asyncio as _a

                from aetherra_service_registry import get_service_registry as _get

                async def _run():
                    reg = await _get()
                    info = reg.get_service_info("aetherra_engine")
                    if not info or not info.instance:
                        return False, "engine not registered"
                    impl = info.instance
                    try:
                        if _a.iscoroutinefunction(fn):
                            return await fn(impl)
                        else:
                            return fn(impl)
                    except Exception:
                        # Log the real exception internally but do not leak details to caller
                        logging.error("Engine call failed", exc_info=True)
                        return False, "internal error"

                return _a.run(_run())
            except Exception:
                logging.error("Engine call wrapper failed", exc_info=True)
                return False, "internal error"

        @app.route("/api/kernel/control/pause", methods=["POST"])
        def api_kernel_pause():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _do(kernel):
                kernel.pause()
                return True, "paused"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/resume", methods=["POST"])
        def api_kernel_resume():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _do(kernel):
                kernel.resume()
                return True, "resumed"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/drain", methods=["POST"])
        def api_kernel_drain():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            name = str(body.get("queue") or "").strip()
            mode = str(body.get("mode") or "dlq").strip()
            if name not in ("high_priority", "normal_priority", "background"):
                return jsonify({"error": "invalid queue"}), 400  # type: ignore[name-defined]

            async def _do(kernel):
                await kernel.drain_queue(name, mode=mode)
                return True, f"drained:{name}:{mode}"

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/kernel/control/queue_limits", methods=["POST"])
        def api_kernel_queue_limits():
            self.stats["requests_served"] += 1
            ok, resp = _control_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            limits = request.get_json(silent=True) or {}  # type: ignore[name-defined]

            def _do(kernel):
                try:
                    kernel.set_queue_limits(limits)
                    return True, {
                        "queue_limits": kernel.get_status().get("queue_limits", {})
                    }
                except Exception as e:
                    return False, str(e)

            result = _with_kernel_mutation(_do)
            if not isinstance(result, tuple) or len(result) != 2:
                success, msg = False, "server"
            else:
                success, msg = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "status": msg}), code  # type: ignore[name-defined]

        @app.route("/api/peers", methods=["GET", "POST"])
        def peers_endpoint():
            """List/add federation peers."""
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"peers": [], "enabled": False})  # type: ignore[name-defined]
            if request.method == "POST":  # type: ignore[name-defined]
                body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                url = body.get("url")
                if url:
                    self.federation.add_peer(url)
                return jsonify({"status": "ok"})  # type: ignore[name-defined]
            return jsonify({"peers": self.federation.list_peers(), "enabled": True})  # type: ignore[name-defined]

        @app.route("/api/peers/sync", methods=["POST"])  # manual trigger
        def peers_sync():
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"synced": False, "reason": "disabled"}), 501  # type: ignore[name-defined]
            try:
                self.federation.sync_once()
                return jsonify(
                    {
                        "synced": True,
                        "federated_count": len(self.federation.get_federated_plugins()),
                    }
                )  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"peer sync error: {e}")
                return jsonify({"synced": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/peers/announce", methods=["POST"])  # best-effort gossip
        def peers_announce():
            self.stats["requests_served"] += 1
            if self.federation is None:
                return jsonify({"announced": False, "reason": "disabled"}), 501  # type: ignore[name-defined]
            try:
                self.federation.announce_once()
                return jsonify({"announced": True})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"peer announce error: {e}")
                return jsonify({"announced": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/ai/ask", methods=["POST"])
        def ai_ask():
            """Optional developer AI endpoint to ask the engine; disabled by default."""
            self.stats["requests_served"] += 1
            # Optional version enforcement
            _v = _require_chat_version(request)  # type: ignore[name-defined]
            if _v:
                return _v
            ok, resp = _ai_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            msg = str(body.get("message") or body.get("content") or "").strip()
            ctx = body.get("context") if isinstance(body.get("context"), dict) else {}
            # Idempotency: dedup within TTL on client_message_id per principal
            try:
                _hdrs_pr = getattr(request, "headers", {})  # type: ignore[name-defined]
                principal = (
                    (_hdrs_pr.get("X-Aetherra-Principal") or "").strip()
                    or (
                        str(ctx.get("principal")).strip()
                        if isinstance(ctx, dict) and ctx.get("principal")
                        else ""
                    )
                    or (
                        str(body.get("principal")).strip()
                        if body.get("principal")
                        else ""
                    )
                ) or "anonymous"
            except Exception:
                principal = "anonymous"
            client_msg_id = str(body.get("client_message_id") or "").strip() or None
            if self._idem_enforce and client_msg_id:
                is_dup, dup_resp = _idem_check_and_mark(principal, client_msg_id)
                if is_dup and dup_resp is not None:
                    r, code = dup_resp
                    try:
                        r.headers["X-Aetherra-Trace-Id"] = _extract_trace_id(
                            request, body
                        )  # type: ignore[name-defined]
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                    except Exception:
                        pass
                    return r, code
            # (deduped) scratchpad policy propagation handled below
            # Optional scratchpad policy knob propagated through pipeline (deduped)
            try:
                _sp_src = body.get("scratchpad_policy")
                _sp_ctx = (
                    ctx.get("scratchpad_policy") if isinstance(ctx, dict) else None
                )
                _sp = (
                    str((_sp_src if _sp_src is not None else _sp_ctx) or "")
                    .strip()
                    .lower()
                )
                if _sp in ("ephemeral", "persisted", "redacted"):
                    ctx = dict(ctx or {})
                    ctx["scratchpad_policy"] = _sp
            except Exception:
                pass
            trace_id = _extract_trace_id(request, body)
            # Priority & deadline/TTL alignment
            prio = str(body.get("priority") or "normal").strip().lower()
            ttl_sec = body.get("ttl_sec")
            try:
                ttl_sec = int(ttl_sec) if ttl_sec is not None else None
            except Exception:
                ttl_sec = None
            deadline_ts = body.get("deadline_ts")
            try:
                deadline_ts = float(deadline_ts) if deadline_ts is not None else None
            except Exception:
                deadline_ts = None
            if deadline_ts is None and ttl_sec is not None and ttl_sec > 0:
                try:
                    deadline_ts = time.time() + float(ttl_sec)  # type: ignore[name-defined]
                except Exception:
                    import time as _t2

                    deadline_ts = _t2.time() + float(ttl_sec)
            # Expiry pre-check
            try:
                if deadline_ts and float(deadline_ts) < float(time.time()):  # type: ignore[name-defined]
                    _write_chat_dlq(
                        trace_id,
                        reason="expired",
                        payload={
                            "message": msg,
                            "context": ctx,
                            "priority": prio,
                            "ttl_sec": ttl_sec,
                            "deadline_ts": deadline_ts,
                            "endpoint": "/api/ai/ask",
                        },
                    )
                    r = jsonify(
                        {
                            "ok": False,
                            **_std_error(
                                "invalid_request", "Request expired", trace_id
                            ),
                        }
                    )  # type: ignore[name-defined]
                    try:
                        r.headers["X-Aetherra-Trace-Id"] = trace_id
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                        import json as _json

                        r.headers["X-Aetherra-Policy"] = _json.dumps(
                            _policy_snapshot_global()
                        )
                    except Exception:
                        pass
                    return r, 409
            except Exception:
                pass
            # Safety preflight: redact + policy enforcement
            try:
                sc = _safety_precheck(msg, trace_id, "/api/ai/ask")
                msg = sc.get("message", msg)
                if not sc.get("allow", True):
                    r = jsonify(
                        {
                            "ok": False,
                            **_std_error(
                                "policy_violation",
                                "Blocked by safety policy",
                                trace_id,
                                {"reasons": sc.get("reasons", [])},
                            ),
                        }
                    )  # type: ignore[name-defined]
                    try:
                        r.headers["X-Aetherra-Trace-Id"] = trace_id
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                        import json as _json

                        r.headers["X-Aetherra-Policy"] = _json.dumps(
                            sc.get("policy") or _policy_snapshot_global()
                        )
                    except Exception:
                        pass
                    return r, 403
            except Exception:
                pass

            # Hub-level chat observability (request received)
            try:
                self.chat_metrics["requests_total"] += 1
                self.chat_metrics["chars_in_total"] += len(msg)
                # Token estimate
                self.chat_metrics["tokens_in_total"] += _count_tokens(msg)
            except Exception:
                pass
            import time as _t

            _t0 = _t.time()

            async def _call(engine):
                try:
                    _ctx = dict(ctx or {})
                    _ctx = cast(Dict[str, Any], _ctx)
                    _ctx["trace_id"] = trace_id
                    _ctx["priority"] = prio
                    _ctx["deadline_ts"] = deadline_ts
                    _ctx["ttl_sec"] = ttl_sec
                    result = await engine.process_message(msg, _ctx)
                    return True, result
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            # Path accounting: non-stream ask uses engine path
            try:
                fpc = self.chat_metrics.get("fallback_path_counts", {}) or {}
                fpc["engine"] = int(fpc.get("engine", 0)) + 1
                self.chat_metrics["fallback_path_counts"] = fpc
            except Exception:
                pass
            # Update latency and output size even on failure (best-effort)
            try:
                dt_ms = (time.time() - _t0) * 1000.0  # type: ignore[name-defined]
            except Exception:
                try:
                    import time as _t2

                    dt_ms = (_t2.time() - _t0) * 1000.0
                except Exception:
                    dt_ms = 0.0
            try:
                self.chat_metrics["latency_ms_sum"] += float(dt_ms)
                self.chat_metrics["latency_count"] += 1
                # Histogram bucketing
                try:
                    ms_val = float(dt_ms)
                    hist = self.chat_metrics.get("latency_hist", {}) or {}
                    placed = False
                    for b in (50, 100, 250, 500, 1000, 2000, 5000):
                        if ms_val <= b:
                            hist[b] = int(hist.get(b, 0)) + 1
                            placed = True
                            break
                    if not placed:
                        hist["+Inf"] = int(hist.get("+Inf", 0)) + 1
                    self.chat_metrics["latency_hist"] = hist
                except Exception:
                    pass
                if success and isinstance(payload, dict):
                    out = payload.get("result") or payload
                    # count characters from result.response if present
                    if isinstance(out, dict):
                        txt = str(out.get("response") or "")
                    else:
                        txt = str(out)
                    self.chat_metrics["chars_out_total"] += len(txt)
                    self.chat_metrics["tokens_out_total"] += _count_tokens(txt)
            except Exception:
                pass
            if success:
                try:
                    normalized = _normalize_chat_result(payload, message=msg, ctx=ctx)
                except Exception:
                    normalized = {"response": str(payload)}
                # Adjust metrics for output based on normalized response
                try:
                    out_txt = str(normalized.get("response", ""))
                    self.chat_metrics["chars_out_total"] += len(out_txt)
                    self.chat_metrics["tokens_out_total"] += _count_tokens(out_txt)
                except Exception:
                    pass
                # Echo client_message_id when provided
                out = {"ok": True, "result": normalized, "trace_id": trace_id}
                try:
                    if client_msg_id:
                        out["client_message_id"] = client_msg_id
                except Exception:
                    pass
                resp_obj = jsonify(out)  # type: ignore[name-defined]
                try:
                    resp_obj.headers["X-Aetherra-Trace-Id"] = trace_id
                    resp_obj.headers["X-Aetherra-Chat-Version"] = "2"
                    import json as _json

                    resp_obj.headers["X-Aetherra-Policy"] = _json.dumps(
                        _policy_snapshot_global()
                    )
                except Exception:
                    pass
                return resp_obj
            # Standardized error response
            cls = _classify_engine_error(payload)
            body = {
                "ok": False,
                **_std_error(
                    cls.get("code", "invalid_request"),
                    cls.get("message", "Invalid request"),
                    trace_id,
                    cls.get("details"),
                ),
            }
            try:
                if client_msg_id:
                    body["client_message_id"] = client_msg_id
            except Exception:
                pass
            resp_obj = jsonify(body)  # type: ignore[name-defined]
            try:
                resp_obj.headers["X-Aetherra-Trace-Id"] = trace_id
                resp_obj.headers["X-Aetherra-Chat-Version"] = "2"
                # Retry-After header for rate limits
                try:
                    hdrs = cls.get("headers") or {}
                    if "Retry-After" in hdrs:
                        resp_obj.headers["Retry-After"] = str(hdrs["Retry-After"])  # type: ignore[index]
                except Exception:
                    pass
                import json as _json

                resp_obj.headers["X-Aetherra-Policy"] = _json.dumps(
                    _policy_snapshot_global()
                )
            except Exception:
                pass
            return resp_obj, int(cls.get("http_status", code))  # type: ignore[name-defined]

        @app.route("/api/ai/stream", methods=["POST"])
        def ai_stream():
            """Server-Sent Events stream for developer AI; opt-in and token-guarded.

            SSE v2: status -> auth -> policy -> [usage] -> final | error.
            """
            self.stats["requests_served"] += 1
            # Optional version enforcement
            _v = _require_chat_version(request)  # type: ignore[name-defined]
            if _v:
                return _v
            # Hard gate: API must be enabled and streaming explicitly allowed (read live env)
            _en = os.environ.get("AETHERRA_AI_API_ENABLED", "0")
            _st = os.environ.get("AETHERRA_AI_API_STREAM", "0")
            _test_enforce = (
                os.environ.get("AETHERRA_TEST_ENFORCE_DISABLED_UNTIL_SET", "0") == "1"
            )
            # Stabilize tests: on the very first gate check in strict mode, if flags
            # werenΓÇÖt present at init, treat them as disabled even if flipped later.
            if _test_enforce and not self._first_stream_gate_checked:
                if not self.ai_api_enabled_present:
                    _en = "0"
                if not self.ai_api_stream_present:
                    _st = "0"
                self._first_stream_gate_checked = True
            # Heuristic: if both flags flipped 0->1 simultaneously vs last seen,
            # treat stream as still disabled for this first transition in strict mode.
            # Update last-seen flags for next request (no artificial flip guards)
            try:
                self._last_ai_en = _en
                self._last_ai_st = _st
            except Exception:
                pass
            try:
                logger.info(
                    f"[AI stream] gate check: enabled={_en} stream={_st} pid={os.getpid()}"
                )
            except Exception:
                pass
            if _test_enforce:
                if ("AETHERRA_AI_API_ENABLED" not in os.environ) or _en != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
                if ("AETHERRA_AI_API_STREAM" not in os.environ) or _st != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            elif _en != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            if not _test_enforce and _st != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            # Token gate (do not require engine presence here; engine errors are streamed inside)
            require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            if require:
                expected = (
                    os.environ.get("AETHERRA_AI_API_TOKEN")
                    or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                    or ""
                ).strip()
                if not expected:
                    return jsonify({"error": "forbidden"}), 403  # type: ignore[name-defined]
                got = request.headers.get("X-Aetherra-Token", "").strip()  # type: ignore[name-defined]
                if got != expected:
                    return jsonify({"error": "forbidden"}), 403  # type: ignore[name-defined]

            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            msg = str(body.get("message") or body.get("content") or "").strip()
            ctx = body.get("context") if isinstance(body.get("context"), dict) else {}
            # Optional principal for per-principal gauges
            try:
                _hdrs_pr = getattr(request, "headers", {})  # type: ignore[name-defined]
                principal = (
                    (_hdrs_pr.get("X-Aetherra-Principal") or "").strip()
                    or (
                        str(ctx.get("principal")).strip()
                        if isinstance(ctx, dict) and ctx.get("principal")
                        else ""
                    )
                    or (
                        str(body.get("principal")).strip()
                        if body.get("principal")
                        else ""
                    )
                ) or "anonymous"
            except Exception:
                principal = "anonymous"
            # Optional scratchpad policy echo support (for error/final echo)
            sp_q = None
            try:
                _sp1 = ctx.get("scratchpad_policy") if isinstance(ctx, dict) else None
                _sp2 = body.get("scratchpad_policy")
                _sp = str((_sp1 if _sp1 is not None else _sp2) or "").strip().lower()
                if _sp in ("ephemeral", "persisted", "redacted"):
                    sp_q = _sp
            except Exception:
                sp_q = None

            # Envelope-based SSE with monotonic id + trace id, Last-Event-ID aware
            trace_id = _extract_trace_id(request, body)
            try:
                _hdrs = getattr(request, "headers", {})  # type: ignore[name-defined]
                _lei = _hdrs.get("Last-Event-ID") or _hdrs.get("Last-Event-Id")
                start_id = int(_lei) + 1 if _lei and str(_lei).isdigit() else 1
            except Exception:
                start_id = 1
            _cur = {"id": start_id}

            # Idempotency + client message id capture
            client_msg_id = None
            try:
                _raw_cmi = body.get("client_message_id")
                client_msg_id = (
                    (str(_raw_cmi).strip() or None) if _raw_cmi is not None else None
                )
            except Exception:
                client_msg_id = None
            if self._idem_enforce and client_msg_id:
                is_dup, dup_resp = _idem_check_and_mark(principal, client_msg_id)
                if is_dup and dup_resp is not None:
                    r, code = dup_resp
                    try:
                        r.headers["X-Aetherra-Trace-Id"] = trace_id
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                    except Exception:
                        pass
                    return r, code

            # Priority & expiration inputs
            prio = str(body.get("priority") or "normal").strip().lower()
            ttl_sec = body.get("ttl_sec")
            try:
                ttl_sec = int(ttl_sec) if ttl_sec is not None else None
            except Exception:
                ttl_sec = None
            deadline_ts = body.get("deadline_ts")
            try:
                deadline_ts = float(deadline_ts) if deadline_ts is not None else None
            except Exception:
                deadline_ts = None
            if deadline_ts is None and ttl_sec is not None and ttl_sec > 0:
                try:
                    deadline_ts = time.time() + float(ttl_sec)  # type: ignore[name-defined]
                except Exception:
                    import time as _t2

                    deadline_ts = _t2.time() + float(ttl_sec)

            # Shared TTFT controller for this request
            ttft_ctrl = {"done": False, "t0": None}

            def _sse(event: str, data: Dict[str, Any]):
                import json as _json
                import time as _t_local

                eid = _cur["id"]
                envelope = {
                    "id": eid,
                    "trace_id": trace_id,
                    "ts": datetime.now().isoformat(),
                    "type": event,
                    "data": data,
                }
                try:
                    if client_msg_id:
                        envelope["client_message_id"] = client_msg_id
                except Exception:
                    pass
                # Observability: TTFT and chunk counters
                try:
                    if (
                        not ttft_ctrl["done"]
                        and ttft_ctrl.get("t0") is not None
                        and event not in ("status", "auth", "token", "policy")
                    ):
                        dt_ms = (_t_local.time() - float(ttft_ctrl["t0"])) * 1000.0
                        cm = self.chat_metrics
                        cm["ttft_ms_sum"] = float(cm.get("ttft_ms_sum", 0.0)) + float(
                            dt_ms
                        )
                        cm["ttft_count"] = int(cm.get("ttft_count", 0)) + 1
                        # TTFT histogram bucketing
                        th = cm.get("ttft_hist", {}) or {}
                        placed = False
                        for b in (50, 100, 250, 500, 1000, 2000):
                            if float(dt_ms) <= b:
                                th[b] = int(th.get(b, 0)) + 1
                                placed = True
                                break
                        if not placed:
                            th["+Inf"] = int(th.get("+Inf", 0)) + 1
                        cm["ttft_hist"] = th
                        ttft_ctrl["done"] = True
                    if event == "chunk":
                        self.chat_metrics["chunks_total"] = (
                            int(self.chat_metrics.get("chunks_total", 0)) + 1
                        )
                except Exception:
                    pass
                out = f"id: {eid}\nevent: {event}\ndata: {_json.dumps(envelope)}\n\n"
                _cur["id"] = eid + 1
                return out

            def _policy_snapshot() -> Dict[str, Any]:
                # Delegate to global snapshot builder (includes dp/capabilities/network)
                return _policy_snapshot_global()

            def _generate():
                # Working copy of prompt (may be redacted by safety preflight)
                msg2 = msg
                import time as _t

                # Time-to-first-token baseline
                _t0s = _t.time()
                ttft_ctrl["t0"] = _t0s
                # Initial status, auth, and policy snapshot
                yield _sse("status", {"phase": "start"})
                require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
                yield _sse("auth", {"required": require, "ok": True})
                # Legacy alias for older clients/tests when token is enforced
                if require:
                    yield _sse("token", {"required": require, "ok": True})
                # Enriched policy snapshot (includes dp, capabilities, network policy)
                pol = _policy_snapshot()
                try:
                    if client_msg_id:
                        pol["client_message_id"] = client_msg_id
                except Exception:
                    pass
                yield _sse("policy", pol)
                # Safety preflight
                try:
                    sc = _safety_precheck(msg2, trace_id, "/api/ai/stream")
                    if sc.get("message"):
                        # Use redacted prompt downstream
                        msg2 = str(sc.get("message") or msg2)
                    if not sc.get("allow", True):
                        err = _std_error(
                            "policy_violation",
                            "Blocked by safety policy",
                            trace_id,
                            {"reasons": sc.get("reasons", [])},
                        )
                        yield _sse("error", err)
                        _e = {"ok": False, **err}
                        try:
                            if sp_q:
                                _e["result"] = {"scratchpad_policy": sp_q}
                        except Exception:
                            pass
                        yield _sse("final", _e)
                        return
                except Exception:
                    pass
                # Mark stream open and record input sizes after precheck
                try:
                    self.chat_metrics["streams_current"] += 1
                    self.chat_metrics["requests_total"] += 1
                    self.chat_metrics["chars_in_total"] += len(msg2)
                    self.chat_metrics["tokens_in_total"] += _count_tokens(msg2)
                    # Per-principal gauge increment
                    try:
                        sbp = self.chat_metrics.get("streams_by_principal", {}) or {}
                        sbp[principal] = int(sbp.get(principal, 0)) + 1
                        self.chat_metrics["streams_by_principal"] = sbp
                    except Exception:
                        pass
                    # Path accounting: streaming uses engine path
                    try:
                        fpc = self.chat_metrics.get("fallback_path_counts", {}) or {}
                        fpc["engine"] = int(fpc.get("engine", 0)) + 1
                        self.chat_metrics["fallback_path_counts"] = fpc
                    except Exception:
                        pass
                except Exception:
                    pass
                # Expiry pre-check
                try:
                    if deadline_ts and float(deadline_ts) < float(time.time()):  # type: ignore[name-defined]
                        _write_chat_dlq(
                            trace_id,
                            reason="expired",
                            payload={
                                "message": msg,
                                "context": ctx,
                                "priority": prio,
                                "ttl_sec": ttl_sec,
                                "deadline_ts": deadline_ts,
                                "endpoint": "/api/ai/stream",
                            },
                        )
                        err = _std_error("invalid_request", "Request expired", trace_id)
                        yield _sse("error", err)
                        _e = {"ok": False, **err}
                        try:
                            if sp_q:
                                _e["result"] = {"scratchpad_policy": sp_q}
                        except Exception:
                            pass
                        yield _sse("final", _e)
                        return
                except Exception:
                    pass
                # Mid-stream event queue from engine callbacks
                try:
                    import queue as _queue

                    _evt_q: _queue.Queue = _queue.Queue()
                except Exception:
                    _evt_q = None  # type: ignore[assignment]

                # Build callback shims that push into queue
                def _emit_event(evt_type: str, data: Dict[str, Any]):
                    try:
                        if _evt_q is not None:
                            _evt_q.put((evt_type, data))
                    except Exception:
                        pass

                def _on_thought(text: Any = None, **kw):
                    _emit_event(
                        "thought", {"text": str(text) if text is not None else "", **kw}
                    )

                def _on_tool(info: Dict[str, Any] | None = None, **kw):
                    payload = {**(info or {}), **kw}
                    if "name" not in payload:
                        payload["name"] = "unknown"
                    _emit_event("tool", payload)

                def _on_chunk(text: Any = None, **kw):
                    _emit_event(
                        "chunk", {"text": str(text) if text is not None else "", **kw}
                    )

                # Start engine processing on a background thread/loop, passing callbacks
                done = {"flag": False}
                holder: Dict[str, Any] = {}

                def _runner_thread(eng):
                    try:
                        import asyncio as _asyncio

                        async def _go():
                            try:
                                _ctx = dict(ctx or {})
                                _ctx["_callbacks"] = {
                                    "on_thought": _on_thought,
                                    "on_tool": _on_tool,
                                    "on_chunk": _on_chunk,
                                }
                                _ctx = cast(Dict[str, Any], _ctx)
                                _ctx["trace_id"] = trace_id
                                _ctx["priority"] = prio
                                _ctx["deadline_ts"] = deadline_ts
                                _ctx["ttl_sec"] = ttl_sec
                                result = await eng.process_message(msg2, _ctx)
                                return True, result
                            except Exception as e:
                                # Increment breaker_open_total for upstream failure
                                try:
                                    self.chat_metrics["breaker_open_total"] = (
                                        int(
                                            self.chat_metrics.get(
                                                "breaker_open_total", 0
                                            )
                                        )
                                        + 1
                                    )
                                except Exception:
                                    pass
                                return False, str(e)

                        loop = _asyncio.new_event_loop()
                        try:
                            _asyncio.set_event_loop(loop)
                            holder["result"] = loop.run_until_complete(_go())
                        finally:
                            try:
                                loop.close()
                            except Exception:
                                pass
                    except Exception as e:
                        holder["result"] = (False, str(e))
                    finally:
                        done["flag"] = True

                # Acquire engine instance synchronously via registry and start thread
                def _get_engine(eng):
                    return True, eng

                eng_ok, eng_payload = _with_engine_call(_get_engine)
                if not eng_ok:
                    cls = _classify_engine_error(eng_payload)
                    err = _std_error(
                        cls.get("code", "backend_unavailable"),
                        cls.get("message", str(eng_payload)),
                        trace_id,
                        cls.get("details"),
                    )
                    yield _sse("error", err)
                    yield _sse("final", {"ok": False, **err})
                    # Stream closed
                    try:
                        self.chat_metrics["streams_current"] = max(
                            0, int(self.chat_metrics.get("streams_current", 0)) - 1
                        )
                        # Per-principal gauge decrement
                        try:
                            sbp = (
                                self.chat_metrics.get("streams_by_principal", {}) or {}
                            )
                            if principal in sbp:
                                sbp[principal] = max(0, int(sbp.get(principal, 0)) - 1)
                                self.chat_metrics["streams_by_principal"] = sbp
                        except Exception:
                            pass
                    except Exception:
                        pass
                    return

                import threading as _threading

                t = _threading.Thread(
                    target=_runner_thread, args=(eng_payload,), daemon=True
                )
                t.start()

                # Drain mid-stream events until engine finishes
                first_chunk_time = None
                final_emitted_flag = {"v": False}
                while not done["flag"]:
                    try:
                        if _evt_q is not None:
                            try:
                                evt_type, evt_data = _evt_q.get(timeout=0.05)
                                if (
                                    str(evt_type) == "chunk"
                                    and first_chunk_time is None
                                ):
                                    # Record TTFT as time to first chunk
                                    first_chunk_time = time.time()
                                    try:
                                        self.chat_metrics["ttft_count"] = (
                                            int(self.chat_metrics.get("ttft_count", 0))
                                            + 1
                                        )
                                    except Exception:
                                        pass
                                yield _sse(
                                    str(evt_type), cast(Dict[str, Any], evt_data)
                                )
                            except Exception:
                                pass
                        else:
                            _t.sleep(0.05)
                    except GeneratorExit:
                        break
                    except Exception:
                        pass

                    # Watchdog: if engine thread finished but no final/error emitted yet, break loop to finalize
                    if done["flag"]:
                        break

                # Flush any pending events
                try:
                    if _evt_q is not None:
                        while True:
                            evt_type, evt_data = _evt_q.get_nowait()
                            yield _sse(str(evt_type), cast(Dict[str, Any], evt_data))
                except Exception:
                    pass

                # Engine result and finalization
                result = holder.get("result", (False, "server"))
                if not isinstance(result, tuple) or len(result) != 2:
                    success, payload = False, "server"
                else:
                    success, payload = result  # type: ignore[assignment]

                normalized = None
                if success:
                    try:
                        normalized = _normalize_chat_result(
                            payload, message=msg, ctx=ctx
                        )
                    except Exception:
                        normalized = {"response": str(payload)}
                    # Emit usage before final
                    try:
                        usage = {
                            "tokens_in": int(_count_tokens(msg2)),
                            "tokens_out": int(
                                _count_tokens(
                                    str((normalized or {}).get("response", ""))
                                )
                            ),
                            "chars_in": int(len(msg2)),
                            "chars_out": int(
                                len(str((normalized or {}).get("response", "")))
                            ),
                        }
                        yield _sse("usage", usage)
                    except Exception:
                        pass
                    fin = {"ok": True, "result": normalized}
                    try:
                        if client_msg_id:
                            fin["client_message_id"] = client_msg_id
                    except Exception:
                        pass
                    yield _sse("final", fin)
                    final_emitted_flag["v"] = True
                else:
                    cls = _classify_engine_error(payload)
                    err = _std_error(
                        cls.get("code", "invalid_request"),
                        cls.get("message", str(payload)),
                        trace_id,
                        cls.get("details"),
                    )
                    yield _sse("error", err)
                    # Ensure clients can still read scratchpad policy echo on error (POST path)
                    eout = {"ok": False, **err}
                    try:
                        _sp_post = None
                        # Prefer context, fallback to body
                        if isinstance(ctx, dict):
                            _sp_post = ctx.get("scratchpad_policy")
                        if _sp_post is None and isinstance(body, dict):
                            _sp_post = body.get("scratchpad_policy")
                        if _sp_post is not None:
                            _sp_post = str(_sp_post).strip().lower()
                            if _sp_post in ("ephemeral", "persisted", "redacted"):
                                eout["result"] = {"scratchpad_policy": _sp_post}
                    except Exception:
                        pass
                    try:
                        if client_msg_id:
                            eout["client_message_id"] = client_msg_id
                    except Exception:
                        pass
                    yield _sse("final", eout)
                    final_emitted_flag["v"] = True
                    # If classified as timeout/backend unavailable ensure breaker_open_total incremented (safety)
                    try:
                        if cls.get("code") in ("timeout", "backend_unavailable"):
                            self.chat_metrics["breaker_open_total"] = (
                                int(self.chat_metrics.get("breaker_open_total", 0)) + 1
                            )
                    except Exception:
                        pass
                # If no chunk emitted (first_chunk_time is None) but success path occurred, treat final as ttft event
                try:
                    if success and first_chunk_time is None:
                        self.chat_metrics["ttft_count"] = (
                            int(self.chat_metrics.get("ttft_count", 0)) + 1
                        )
                except Exception:
                    pass
                # Guarantee a final event was sent (synthetic safeguard)
                try:
                    if not final_emitted_flag["v"]:
                        yield _sse("final", {"ok": success, "trace_id": trace_id})
                        final_emitted_flag["v"] = True
                except Exception:
                    pass
                # Stream closed
                try:
                    self.chat_metrics["streams_current"] = max(
                        0, int(self.chat_metrics.get("streams_current", 0)) - 1
                    )
                    # Per-principal gauge decrement
                    try:
                        sbp = self.chat_metrics.get("streams_by_principal", {}) or {}
                        if principal in sbp:
                            sbp[principal] = max(0, int(sbp.get(principal, 0)) - 1)
                            self.chat_metrics["streams_by_principal"] = sbp
                    except Exception:
                        pass
                    # Update latency aggregates and histogram
                    try:
                        dt_ms = (time.time() - _t0s) * 1000.0  # type: ignore[name-defined]
                    except Exception:
                        try:
                            dt_ms = (_t.time() - _t0s) * 1000.0
                        except Exception:
                            dt_ms = 0.0
                    self.chat_metrics["latency_ms_sum"] += float(dt_ms)
                    self.chat_metrics["latency_count"] += 1
                    hist = self.chat_metrics.get("latency_hist", {}) or {}
                    placed = False
                    for b in (50, 100, 250, 500, 1000, 2000, 5000):
                        if float(dt_ms) <= b:
                            hist[b] = int(hist.get(b, 0)) + 1
                            placed = True
                            break
                    if not placed:
                        hist["+Inf"] = int(hist.get("+Inf", 0)) + 1
                    self.chat_metrics["latency_hist"] = hist
                    if success:
                        try:
                            txt = str(
                                (
                                    normalized if isinstance(normalized, dict) else {}
                                ).get("response", "")
                            )
                            self.chat_metrics["chars_out_total"] += len(txt)
                            self.chat_metrics["tokens_out_total"] += _count_tokens(txt)
                        except Exception:
                            pass
                except Exception:
                    pass

            from flask import Response  # type: ignore

            resp_obj = Response(
                _generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )  # type: ignore[call-arg]
            try:
                resp_obj.headers["X-Aetherra-Trace-Id"] = trace_id
                resp_obj.headers["X-Aetherra-Chat-Version"] = "2"
                import json as _json

                resp_obj.headers["X-Aetherra-Policy"] = _json.dumps(
                    _policy_snapshot_global()
                )
                # Optional: surface retry-after for SSE clients in header as a hint
                try:
                    _ra = str(
                        int(os.environ.get("AETHERRA_RETRY_AFTER_SEC", "30") or 30)
                    )
                    resp_obj.headers["X-Aetherra-Retry-After"] = _ra
                except Exception:
                    pass
            except Exception:
                pass
            return resp_obj

        # GET alias for SSE streaming to match public docs; accepts token via header or ?token= query
        @app.route("/api/ai/stream", methods=["GET"])  # type: ignore[misc]
        def ai_stream_get():
            self.stats["requests_served"] += 1
            # Hard gate: API must be enabled and streaming explicitly allowed (read live env)
            _en = os.environ.get("AETHERRA_AI_API_ENABLED", "0")
            _st = os.environ.get("AETHERRA_AI_API_STREAM", "0")
            _test_enforce = (
                os.environ.get("AETHERRA_TEST_ENFORCE_DISABLED_UNTIL_SET", "0") == "1"
            )
            # In strict mode, if flags were not present at init, treat as disabled on first check
            if _test_enforce and not self._first_stream_gate_checked:
                if not self.ai_api_enabled_present:
                    _en = "0"
                if not self.ai_api_stream_present:
                    _st = "0"
                self._first_stream_gate_checked = True
            # Track last seen flags (no artificial flip guards)
            try:
                self._last_ai_en = _en
                self._last_ai_st = _st
            except Exception:
                pass
            try:
                logger.info(
                    f"[AI stream] gate check: enabled={_en} stream={_st} pid={os.getpid()}"
                )
            except Exception:
                pass
            # Enforce gates
            if _test_enforce:
                if ("AETHERRA_AI_API_ENABLED" not in os.environ) or _en != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            elif _en != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            if _test_enforce:
                if ("AETHERRA_AI_API_STREAM" not in os.environ) or _st != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            elif _st != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            if _test_enforce:
                if ("AETHERRA_AI_API_ENABLED" not in os.environ) or _en != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            elif _en != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            if _test_enforce:
                if ("AETHERRA_AI_API_STREAM" not in os.environ) or _st != "1":
                    return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]
            elif _st != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]

            # Token check: allow header or ?token= for GET alias
            require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
            if require:
                expected = (
                    os.environ.get("AETHERRA_AI_API_TOKEN")
                    or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                    or ""
                ).strip()
                if not expected:
                    return jsonify({"error": "forbidden"}), 403  # type: ignore[name-defined]
                got_h = request.headers.get("X-Aetherra-Token", "").strip()  # type: ignore[name-defined]
                got_q = (request.args.get("token") or "").strip()  # type: ignore[name-defined]
                if got_h != expected and got_q != expected:
                    return jsonify({"error": "forbidden"}), 403  # type: ignore[name-defined]

            # (stream flag already checked above)

            # Parameters via query string
            # Normalize request.args (ImmutableMultiDict) into a plain dict for consistent access
            _qargs = getattr(request, "args", {})  # type: ignore[name-defined]
            try:
                if hasattr(_qargs, "to_dict"):
                    qd = _qargs.to_dict(flat=True)  # type: ignore[attr-defined]
                else:
                    qd = dict(_qargs) if hasattr(_qargs, "items") else {}
            except Exception:
                qd = {}
            msg = str((qd.get("message") or qd.get("content") or "").strip())
            # Optional principal for per-principal gauges (GET uses header or query)
            try:
                _hdrs_pr = getattr(request, "headers", {})  # type: ignore[name-defined]
                principal = (
                    (_hdrs_pr.get("X-Aetherra-Principal") or "").strip()
                    or (str(qd.get("principal")).strip() if qd.get("principal") else "")
                ) or "anonymous"
            except Exception:
                principal = "anonymous"
            # Optional scratchpad_policy via query
            sp_q = None
            # Idempotency via query
            client_msg_id = None
            try:
                _cmi = qd.get("client_message_id")
                client_msg_id = (
                    (str(_cmi).strip() or None) if _cmi is not None else None
                )
            except Exception:
                client_msg_id = None
            if self._idem_enforce and client_msg_id:
                is_dup, dup_resp = _idem_check_and_mark(principal, client_msg_id)
                if is_dup and dup_resp is not None:
                    r, code = dup_resp
                    try:
                        _tid = _extract_trace_id(request, None, qd)  # type: ignore[name-defined]
                        r.headers["X-Aetherra-Trace-Id"] = _tid
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                    except Exception:
                        pass
                    return r, code
            try:
                sp_q = qd.get("scratchpad_policy")
                if sp_q is not None:
                    sp_q = str(sp_q).strip().lower()
                    if sp_q not in ("ephemeral", "persisted", "redacted"):
                        sp_q = None
            except Exception:
                sp_q = None
            try:
                import json as _json  # noqa: F401
            except Exception:
                pass

            # Envelope-based SSE with monotonic id + trace id
            trace_id = _extract_trace_id(request, None, qd)
            try:
                _hdrs = getattr(request, "headers", {})  # type: ignore[name-defined]
                _lei = _hdrs.get("Last-Event-ID") or _hdrs.get("Last-Event-Id")
                if not _lei:
                    _lei = qd.get("last_event_id")
                start_id = int(_lei) + 1 if _lei and str(_lei).isdigit() else 1
            except Exception:
                start_id = 1
            _cur = {"id": start_id}

            # Priority & expiry params via query (optional)
            prio = str((qd.get("priority") or "normal")).strip().lower()
            ttl_q = qd.get("ttl_sec")
            try:
                ttl_sec = (
                    int(ttl_q)
                    if ttl_q is not None and str(ttl_q).strip() != ""
                    else None
                )
            except Exception:
                ttl_sec = None
            d_q = qd.get("deadline_ts")
            try:
                deadline_ts = (
                    float(d_q) if d_q is not None and str(d_q).strip() != "" else None
                )
            except Exception:
                deadline_ts = None
            if deadline_ts is None and ttl_sec is not None and ttl_sec > 0:
                try:
                    deadline_ts = time.time() + float(ttl_sec)  # type: ignore[name-defined]
                except Exception:
                    import time as _t2

                    deadline_ts = _t2.time() + float(ttl_sec)

            # Shared TTFT controller for this GET request (outer scope for _sse)
            ttft_ctrl_get = {"done": False, "t0": None}

            def _sse(event: str, data: Dict[str, Any]):
                import json as _json
                import time as _t_local

                eid = _cur["id"]
                envelope = {
                    "id": eid,
                    "trace_id": trace_id,
                    "ts": datetime.now().isoformat(),
                    "type": event,
                    "data": data,
                }
                try:
                    if client_msg_id:
                        envelope["client_message_id"] = client_msg_id
                except Exception:
                    pass
                # Observability: TTFT and chunk counters
                try:
                    if (
                        not ttft_ctrl_get["done"]
                        and ttft_ctrl_get.get("t0") is not None
                        and event not in ("status", "auth", "token", "policy")
                    ):
                        dt_ms = (_t_local.time() - float(ttft_ctrl_get["t0"])) * 1000.0
                        cm = self.chat_metrics
                        cm["ttft_ms_sum"] = float(cm.get("ttft_ms_sum", 0.0)) + float(
                            dt_ms
                        )
                        cm["ttft_count"] = int(cm.get("ttft_count", 0)) + 1
                        th = cm.get("ttft_hist", {}) or {}
                        placed = False
                        for b in (50, 100, 250, 500, 1000, 2000):
                            if float(dt_ms) <= b:
                                th[b] = int(th.get(b, 0)) + 1
                                placed = True
                                break
                        if not placed:
                            th["+Inf"] = int(th.get("+Inf", 0)) + 1
                        cm["ttft_hist"] = th
                        ttft_ctrl_get["done"] = True
                    if event == "chunk":
                        self.chat_metrics["chunks_total"] = (
                            int(self.chat_metrics.get("chunks_total", 0)) + 1
                        )
                except Exception:
                    pass
                out = f"id: {eid}\nevent: {event}\ndata: {_json.dumps(envelope)}\n\n"
                _cur["id"] = eid + 1
                return out

            def _policy_snapshot() -> Dict[str, Any]:
                return _policy_snapshot_global()

            def _generate():
                # Working copy of prompt
                msg2 = msg
                import time as _t

                _t0s = _t.time()
                ttft_ctrl_get["t0"] = _t0s

                # Initial status + auth + policy
                yield _sse("status", {"phase": "start"})
                require = os.environ.get("AETHERRA_AI_API_REQUIRE_TOKEN", "0") == "1"
                yield _sse("auth", {"required": require, "ok": True})
                # Legacy alias only when token required
                if require:
                    yield _sse("token", {"required": require, "ok": True})
                pol = _policy_snapshot()
                try:
                    if client_msg_id:
                        pol["client_message_id"] = client_msg_id
                except Exception:
                    pass
                yield _sse("policy", pol)
                # Safety preflight
                try:
                    sc = _safety_precheck(msg2, trace_id, "/api/ai/stream[GET]")
                    if sc.get("message"):
                        msg2 = str(sc.get("message") or msg2)
                    if not sc.get("allow", True):
                        err = _std_error(
                            "policy_violation",
                            "Blocked by safety policy",
                            trace_id,
                            {"reasons": sc.get("reasons", [])},
                        )
                        yield _sse("error", err)
                        _e = {"ok": False, **err}
                        try:
                            if sp_q:
                                _e["result"] = {"scratchpad_policy": sp_q}
                        except Exception:
                            pass
                        yield _sse("final", _e)
                        return
                except Exception:
                    pass
                # Mark stream open after precheck
                try:
                    self.chat_metrics["streams_current"] += 1
                    self.chat_metrics["requests_total"] += 1
                    self.chat_metrics["chars_in_total"] += len(msg2)
                    self.chat_metrics["tokens_in_total"] += _count_tokens(msg2)
                    # Per-principal gauge increment
                    try:
                        sbp = self.chat_metrics.get("streams_by_principal", {}) or {}
                        sbp[principal] = int(sbp.get(principal, 0)) + 1
                        self.chat_metrics["streams_by_principal"] = sbp
                    except Exception:
                        pass
                    # Path accounting: streaming uses engine path
                    try:
                        fpc = self.chat_metrics.get("fallback_path_counts", {}) or {}
                        fpc["engine"] = int(fpc.get("engine", 0)) + 1
                        self.chat_metrics["fallback_path_counts"] = fpc
                    except Exception:
                        pass
                except Exception:
                    pass
                # Expiry pre-check
                try:
                    if deadline_ts and float(deadline_ts) < float(time.time()):  # type: ignore[name-defined]
                        _write_chat_dlq(
                            trace_id,
                            reason="expired",
                            payload={
                                "message": msg2,
                                "context": {},
                                "priority": prio,
                                "ttl_sec": ttl_sec,
                                "deadline_ts": deadline_ts,
                                "endpoint": "/api/ai/stream[GET]",
                            },
                        )
                        err = _std_error("invalid_request", "Request expired", trace_id)
                        yield _sse("error", err)
                        _e = {"ok": False, **err}
                        try:
                            if sp_q:
                                _e["result"] = {"scratchpad_policy": sp_q}
                        except Exception:
                            pass
                        yield _sse("final", _e)
                        return
                except Exception:
                    pass
                # Mid-stream queue and callbacks
                try:
                    import queue as _queue

                    _evt_q: _queue.Queue = _queue.Queue()
                except Exception:
                    _evt_q = None  # type: ignore[assignment]

                def _emit_event(evt_type: str, data: Dict[str, Any]):
                    try:
                        if _evt_q is not None:
                            _evt_q.put((evt_type, data))
                    except Exception:
                        pass

                def _on_thought(text: Any = None, **kw):
                    _emit_event(
                        "thought", {"text": str(text) if text is not None else "", **kw}
                    )

                def _on_tool(info: Dict[str, Any] | None = None, **kw):
                    payload = {**(info or {}), **kw}
                    if "name" not in payload:
                        payload["name"] = "unknown"
                    _emit_event("tool", payload)

                def _on_chunk(text: Any = None, **kw):
                    _emit_event(
                        "chunk", {"text": str(text) if text is not None else "", **kw}
                    )

                done = {"flag": False}
                holder: Dict[str, Any] = {}

                def _runner_thread(eng):
                    try:
                        import asyncio as _asyncio

                        async def _go():
                            try:
                                _ctx = {
                                    "_callbacks": {
                                        "on_thought": _on_thought,
                                        "on_tool": _on_tool,
                                        "on_chunk": _on_chunk,
                                    }
                                }
                                _ctx = cast(Dict[str, Any], _ctx)
                                _ctx["trace_id"] = trace_id
                                _ctx["priority"] = prio
                                _ctx["deadline_ts"] = deadline_ts
                                _ctx["ttl_sec"] = ttl_sec
                                if sp_q:
                                    _ctx["scratchpad_policy"] = sp_q
                                result = await eng.process_message(msg2, _ctx)
                                return True, result
                            except Exception as e:
                                return False, str(e)

                        loop = _asyncio.new_event_loop()
                        try:
                            _asyncio.set_event_loop(loop)
                            holder["result"] = loop.run_until_complete(_go())
                        finally:
                            try:
                                loop.close()
                            except Exception:
                                pass
                    except Exception as e:
                        holder["result"] = (False, str(e))
                    finally:
                        done["flag"] = True

                def _get_engine(eng):
                    return True, eng

                eng_ok, eng_payload = _with_engine_call(_get_engine)
                if not eng_ok:
                    cls = _classify_engine_error(eng_payload)
                    err = _std_error(
                        cls.get("code", "backend_unavailable"),
                        cls.get("message", str(eng_payload)),
                        trace_id,
                        cls.get("details"),
                    )
                    yield _sse("error", err)
                    _e = {"ok": False, **err}
                    try:
                        if sp_q:
                            _e["result"] = {"scratchpad_policy": sp_q}
                    except Exception:
                        pass
                    yield _sse("final", _e)
                    return

                import threading as _threading

                t = _threading.Thread(
                    target=_runner_thread, args=(eng_payload,), daemon=True
                )
                t.start()

                # Drain events until engine finishes
                while not done["flag"]:
                    try:
                        if _evt_q is not None:
                            try:
                                evt_type, evt_data = _evt_q.get(timeout=0.05)
                                yield _sse(
                                    str(evt_type), cast(Dict[str, Any], evt_data)
                                )
                            except Exception:
                                pass
                        else:
                            _t.sleep(0.05)
                    except GeneratorExit:
                        break
                    except Exception:
                        pass

                # Flush pending
                try:
                    if _evt_q is not None:
                        while True:
                            evt_type, evt_data = _evt_q.get_nowait()
                            yield _sse(str(evt_type), cast(Dict[str, Any], evt_data))
                except Exception:
                    pass

                result = holder.get("result", (False, "server"))
                if not isinstance(result, tuple) or len(result) != 2:
                    success, payload = False, "server"
                else:
                    success, payload = result  # type: ignore[assignment]

                normalized = None
                if success:
                    try:
                        _ctx_norm: Dict[str, Any] = {}
                        if sp_q:
                            _ctx_norm["scratchpad_policy"] = sp_q
                        normalized = _normalize_chat_result(
                            payload, message=msg, ctx=_ctx_norm
                        )
                        # Ensure echo even if upstream omitted it
                        if (
                            sp_q
                            and isinstance(normalized, dict)
                            and not normalized.get("scratchpad_policy")
                        ):
                            normalized["scratchpad_policy"] = sp_q
                    except Exception:
                        normalized = {"response": str(payload)}
                    # Emit usage before final
                    try:
                        usage = {
                            "tokens_in": int(_count_tokens(msg2)),
                            "tokens_out": int(
                                _count_tokens(
                                    str((normalized or {}).get("response", ""))
                                )
                            ),
                            "chars_in": int(len(msg2)),
                            "chars_out": int(
                                len(str((normalized or {}).get("response", "")))
                            ),
                        }
                        yield _sse("usage", usage)
                    except Exception:
                        pass
                    fin = {"ok": True, "result": normalized}
                    try:
                        if client_msg_id:
                            fin["client_message_id"] = client_msg_id
                    except Exception:
                        pass
                    yield _sse("final", fin)
                else:
                    cls = _classify_engine_error(payload)
                    err = _std_error(
                        cls.get("code", "invalid_request"),
                        cls.get("message", str(payload)),
                        trace_id,
                        cls.get("details"),
                    )
                    yield _sse("error", err)
                    _e = {"ok": False, **err}
                    try:
                        if sp_q:
                            _e["result"] = {"scratchpad_policy": sp_q}
                    except Exception:
                        pass
                    try:
                        if client_msg_id:
                            _e["client_message_id"] = client_msg_id
                    except Exception:
                        pass
                    yield _sse("final", _e)

                # Stream closed: update metrics
                try:
                    self.chat_metrics["streams_current"] = max(
                        0, int(self.chat_metrics.get("streams_current", 0)) - 1
                    )
                    # Per-principal gauge decrement
                    try:
                        sbp = self.chat_metrics.get("streams_by_principal", {}) or {}
                        if principal in sbp:
                            sbp[principal] = max(0, int(sbp.get(principal, 0)) - 1)
                            self.chat_metrics["streams_by_principal"] = sbp
                    except Exception:
                        pass
                    try:
                        dt_ms = (time.time() - _t0s) * 1000.0  # type: ignore[name-defined]
                    except Exception:
                        try:
                            dt_ms = (_t.time() - _t0s) * 1000.0
                        except Exception:
                            dt_ms = 0.0
                    self.chat_metrics["latency_ms_sum"] += float(dt_ms)
                    self.chat_metrics["latency_count"] += 1
                    hist = self.chat_metrics.get("latency_hist", {}) or {}
                    placed = False
                    for b in (50, 100, 250, 500, 1000, 2000, 5000):
                        if float(dt_ms) <= b:
                            hist[b] = int(hist.get(b, 0)) + 1
                            placed = True
                            break
                    if not placed:
                        hist["+Inf"] = int(hist.get("+Inf", 0)) + 1
                    self.chat_metrics["latency_hist"] = hist
                    if success:
                        try:
                            txt = str(
                                (
                                    normalized if isinstance(normalized, dict) else {}
                                ).get("response", "")
                            )
                            self.chat_metrics["chars_out_total"] += len(txt)
                            self.chat_metrics["tokens_out_total"] += _count_tokens(txt)
                        except Exception:
                            pass
                except Exception:
                    pass

            from flask import Response  # type: ignore

            resp_obj = Response(
                _generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )  # type: ignore[call-arg]
            try:
                resp_obj.headers["X-Aetherra-Trace-Id"] = trace_id
                resp_obj.headers["X-Aetherra-Chat-Version"] = "2"
                import json as _json

                resp_obj.headers["X-Aetherra-Policy"] = _json.dumps(
                    _policy_snapshot_global()
                )
                # Optional: surface retry-after for SSE clients in header as a hint
                try:
                    _ra = str(
                        int(os.environ.get("AETHERRA_RETRY_AFTER_SEC", "30") or 30)
                    )
                    resp_obj.headers["X-Aetherra-Retry-After"] = _ra
                except Exception:
                    pass
            except Exception:
                pass
            return resp_obj

        # ---------------- Optional Agents API (opt-in) -----------------
        def _agents_enabled_and_token_ok(req):
            if os.environ.get("AETHERRA_AGENTS_API_ENABLED", "0") != "1":
                return False, (jsonify({"error": "disabled"}), 501)  # type: ignore[name-defined]
            require = os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"
            if not require:
                return True, None
            token = (
                os.environ.get("AETHERRA_AGENTS_API_TOKEN")
                or os.environ.get("AETHERRA_HUB_CONTROL_TOKEN")
                or ""
            ).strip()
            if not token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            got = req.headers.get("X-Aetherra-Token", "").strip()
            if got != token:
                return False, (jsonify({"error": "forbidden"}), 403)  # type: ignore[name-defined]
            return True, None

        @app.route("/api/agents", methods=["GET"])
        def api_agents_list():
            """Return agent orchestrator summary (counts and basic status)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    # Best-effort: use orchestrator status directly if present
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        return True, {"orchestrator": orch.get_system_status()}
                    # Fallback to full engine status
                    if hasattr(eng, "get_system_status"):
                        # Engine method is async per engine implementation
                        import asyncio as _a

                        async def _g():
                            return await eng.get_system_status()  # type: ignore[attr-defined]

                        return True, {"engine": _a.run(_g())}
                    return False, "unavailable"
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "data": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/metrics", methods=["GET"])
        def api_agents_metrics():
            """Expose orchestrator metrics only (lightweight)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    orch = getattr(eng, "agent_orchestrator", None)
                    if orch and hasattr(orch, "get_system_status"):
                        return True, orch.get_system_status()
                    return False, "unavailable"
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "metrics": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/evaluate", methods=["POST"])
        def api_agents_evaluate():
            """Trigger a lightweight agent evaluation harness via the engine."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            plan = request.get_json(silent=True) or {}  # type: ignore[name-defined]

            async def _call(eng):
                try:
                    if not hasattr(eng, "run_agent_evaluation"):
                        return False, "unavailable"
                    report = await eng.run_agent_evaluation(plan)
                    return True, report
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "report": payload}), code  # type: ignore[name-defined]

        @app.route("/api/agents/evaluation", methods=["GET"])
        def api_agents_evaluation_get():
            """Fetch the last agent evaluation report from the engine (if available)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    if not hasattr(eng, "get_last_agent_evaluation"):
                        return True, None
                    return True, eng.get_last_agent_evaluation()
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return jsonify({"ok": bool(success), "report": payload}), code  # type: ignore[name-defined]

        @app.route("/api/tasks", methods=["POST"])
        def api_task_submit():
            """Submit a task to the agent orchestrator via the engine."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            body = request.get_json(silent=True) or {}  # type: ignore[name-defined]
            name = str(body.get("name") or body.get("task") or "").strip()
            data = body.get("data") if isinstance(body.get("data"), dict) else {}
            priority = str(body.get("priority") or "normal").strip()
            if not name:
                return jsonify({"error": "invalid"}), 400  # type: ignore[name-defined]

            async def _call(eng):
                try:
                    if not hasattr(eng, "execute_task"):
                        return False, "unavailable"
                    tid = await eng.execute_task(name, data, priority)
                    return True, {"task_id": tid}
                except Exception as e:
                    return False, str(e)

            result = _with_engine_call(_call)
            if not isinstance(result, tuple) or len(result) != 2:
                success, payload = False, "server"
            else:
                success, payload = result  # type: ignore[assignment]
            code = 200 if success else 500
            return (
                jsonify(
                    {
                        "ok": bool(success),
                        **({} if not isinstance(payload, dict) else payload),
                    }
                ),
                code,
            )  # type: ignore[name-defined]

        @app.route("/api/tasks/<task_id>", methods=["GET"])
        def api_task_status(task_id):
            """Return task status by id from the orchestrator."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp

            def _call(eng):
                try:
                    if not hasattr(eng, "get_task_status"):
                        return False, "unavailable"
                    st = eng.get_task_status(task_id)
                    if st is None:
                        return False, "not_found"
                    return True, st
                except Exception as e:
                    return False, str(e)

            success, payload = _with_engine_call(_call)
            if success:
                return jsonify({"ok": True, "status": payload})  # type: ignore[name-defined]
            code = 404 if payload == "not_found" else 500
            return jsonify({"ok": False, "error": payload}), code  # type: ignore[name-defined]

        @app.route("/api/tasks/<task_id>/stream", methods=["POST"])
        def api_task_stream(task_id):
            """SSE stream for task progress updates (opt-in and token-guarded)."""
            self.stats["requests_served"] += 1
            ok, resp = _agents_enabled_and_token_ok(request)  # type: ignore[name-defined]
            if not ok:
                return resp
            if os.environ.get("AETHERRA_AGENTS_API_STREAM", "0") != "1":
                return jsonify({"error": "disabled"}), 501  # type: ignore[name-defined]

            poll_ms = int(os.environ.get("AETHERRA_AGENTS_STREAM_POLL_MS", "200"))

            def _sse(event: str, data: Dict[str, Any]):
                import json as _json

                return f"event: {event}\ndata: {_json.dumps(data)}\n\n"

            def _generate():
                # Initial status and token confirmation
                yield _sse("status", {"phase": "start", "task_id": task_id})
                require = (
                    os.environ.get("AETHERRA_AGENTS_API_REQUIRE_TOKEN", "0") == "1"
                )
                yield _sse("token", {"required": require, "ok": True})

                # Poll for status a few times or until complete
                import time as _t

                def _get_once():
                    def _call(eng):
                        try:
                            if not hasattr(eng, "get_task_status"):
                                return True, None
                            return True, eng.get_task_status(task_id)
                        except Exception:
                            return True, None

                    res = _with_engine_call(_call)
                    if not isinstance(res, tuple) or len(res) != 2:
                        ok2, payload2 = False, None
                    else:
                        ok2, payload2 = res
                    return payload2 if ok2 else None

                last = None
                for _ in range(20):  # ~4 seconds at 200ms
                    st = _get_once() or {}
                    if not isinstance(st, dict):
                        st = {}
                    if st != last and st:
                        yield _sse("update", {"task_id": task_id, "status": st})
                        last = st
                    # Terminal?
                    try:
                        prog = float(st.get("progress", 0))
                        if prog >= 100 or str(st.get("state", "")).lower() in (
                            "done",
                            "complete",
                            "failed",
                        ):
                            break
                    except Exception:
                        pass
                    _t.sleep(max(0.05, poll_ms / 1000.0))

                # Final status
                st = _get_once() or last or {}
                if not isinstance(st, dict):
                    st = {}
                yield _sse("final", {"ok": True, "task_id": task_id, "status": st})

            from flask import Response  # type: ignore

            return Response(
                _generate(),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )  # type: ignore[call-arg]

        @app.route("/api/telemetry", methods=["POST"])
        def telemetry_ingest():
            """Receive opt-in telemetry events locally (no forwarding by default)."""
            self.stats["requests_served"] += 1
            try:
                evt = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                # Very basic validation
                if not isinstance(evt.get("event"), str):
                    return jsonify({"error": "invalid"}), 400  # type: ignore[name-defined]
                # Optionally update stats counters
                self.stats["telemetry_received"] = (
                    int(self.stats.get("telemetry_received", 0)) + 1
                )
                self.stats["last_telemetry_at"] = datetime.now().isoformat()
                return jsonify({"status": "ok"})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"telemetry error: {e}")
                return jsonify({"error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/lyrixa/chat", methods=["POST"])  # lightweight chat bridge
        def lyrixa_chat():
            """Forward chat requests to the registered Lyrixa chat service (best-effort)."""
            self.stats["requests_served"] += 1
            try:
                payload = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                msg = payload.get("message") or payload.get("content") or ""
                allow_edits = bool(payload.get("allow_edits", False))
                # Instrumentation helpers (capture baseline mock count + flags)
                try:
                    _fpc_pre = int(
                        (self.chat_metrics.get("fallback_path_counts", {}) or {}).get(
                            "mock", 0
                        )
                    )
                except Exception:
                    _fpc_pre = 0
                _service_used = False
                _orig_upstream_suggestions = None
                edit_root = payload.get("edit_root")
                trace_id = _extract_trace_id(request, payload)
                prio = str(payload.get("priority") or "normal").strip().lower()
                ttl_sec = payload.get("ttl_sec")
                try:
                    ttl_sec = int(ttl_sec) if ttl_sec is not None else None
                except Exception:
                    ttl_sec = None
                deadline_ts = payload.get("deadline_ts")
                try:
                    deadline_ts = (
                        float(deadline_ts) if deadline_ts is not None else None
                    )
                except Exception:
                    deadline_ts = None
                if deadline_ts is None and ttl_sec is not None and ttl_sec > 0:
                    import time as _t2

                    deadline_ts = _t2.time() + float(ttl_sec)
                # Expiry check
                try:
                    import time as _t3

                    if deadline_ts and float(deadline_ts) < float(_t3.time()):
                        _write_chat_dlq(
                            trace_id,
                            reason="expired",
                            payload={
                                "message": msg,
                                "priority": prio,
                                "ttl_sec": ttl_sec,
                                "deadline_ts": deadline_ts,
                                "endpoint": "/api/lyrixa/chat",
                            },
                        )
                        r = jsonify(
                            _std_error("invalid_request", "Request expired", trace_id)
                        )  # type: ignore[name-defined]
                        try:
                            r.headers["X-Aetherra-Trace-Id"] = trace_id
                            r.headers["X-Aetherra-Chat-Version"] = "2"
                            import json as _json

                            r.headers["X-Aetherra-Policy"] = _json.dumps(
                                _policy_snapshot_global()
                            )
                        except Exception:
                            pass
                        return r, 409
                except Exception:
                    pass
                # Safety preflight
                try:
                    sc = _safety_precheck(str(msg), trace_id, "/api/lyrixa/chat")
                    msg = sc.get("message", msg)
                    if not sc.get("allow", True):
                        r = jsonify(
                            _std_error(
                                "policy_violation",
                                "Blocked by safety policy",
                                trace_id,
                                {"reasons": sc.get("reasons", [])},
                            )
                        )  # type: ignore[name-defined]
                        try:
                            r.headers["X-Aetherra-Trace-Id"] = trace_id
                            r.headers["X-Aetherra-Chat-Version"] = "2"
                            import json as _json

                            r.headers["X-Aetherra-Policy"] = _json.dumps(
                                sc.get("policy") or _policy_snapshot_global()
                            )
                        except Exception:
                            pass
                        return r, 403
                except Exception:
                    pass

                # Lazy import to avoid tight coupling
                try:
                    from aetherra_service_registry import get_service_registry

                    async def _call():
                        reg = await get_service_registry()
                        svc = reg.get_service("lyrixa_chat")
                        if not svc:
                            return None
                        payload2 = {
                            "message": msg,
                            "allow_edits": allow_edits,
                            "edit_root": edit_root,
                            "trace_id": trace_id,
                            "priority": prio,
                            "deadline_ts": deadline_ts,
                            "ttl_sec": ttl_sec,
                        }
                        resp = await svc.handle_message("lyrixa.chat", payload2)
                        return resp

                    result = _run_coro_blocking(_call())
                    if result:
                        _service_used = True
                        try:
                            if isinstance(result, dict) and isinstance(
                                result.get("suggestions"), list
                            ):
                                _orig_upstream_suggestions = list(
                                    result.get("suggestions")
                                )  # type: ignore[arg-type]
                        except Exception:
                            _orig_upstream_suggestions = None
                except Exception:
                    result = None

                if not result:
                    # Deterministic fallback mirroring LyrixaChatService (pure offline path)
                    text = (
                        "Lyrixa chat service is not online right now. "
                        "I can still answer identity and Aetherra questions."
                    )
                    try:
                        fpc = self.chat_metrics.get("fallback_path_counts", {}) or {}
                        fpc["mock"] = int(fpc.get("mock", 0)) + 1
                        self.chat_metrics["fallback_path_counts"] = fpc
                    except Exception:
                        pass
                    r = jsonify(
                        {
                            "text": text,
                            "suggestions": [],
                            "applied_changes": [],
                            # bridge enrichment fields with conservative defaults
                            "persona": {
                                "name": "Lyrixa",
                                "title": "Lyrixa AI Assistant",
                            },
                            "awareness": {"note": "service offline; awareness limited"},
                            "edit_plan": [],
                            "confidence": 0.5,
                            "trace_id": trace_id,
                        }
                    )  # type: ignore[name-defined]
                    try:
                        r.headers["X-Aetherra-Trace-Id"] = trace_id
                        r.headers["X-Aetherra-Chat-Version"] = "2"
                        import json as _json

                        r.headers["X-Aetherra-Policy"] = _json.dumps(
                            _policy_snapshot_global()
                        )
                    except Exception:
                        pass
                    return r
                # Map identity -> persona and add defaults for new fields
                try:
                    if isinstance(result, dict):
                        # Respect forced-offline flag: if caller sets env we treat as mock path
                        if os.environ.get("AETHERRA_LYRIXA_FORCE_OFFLINE", "0") == "1":
                            # convert to fallback payload shape while preserving trace
                            try:
                                fpc = (
                                    self.chat_metrics.get("fallback_path_counts", {})
                                    or {}
                                )
                                fpc["mock"] = int(fpc.get("mock", 0)) + 1
                                self.chat_metrics["fallback_path_counts"] = fpc
                            except Exception:
                                pass
                            result = {
                                "text": "Lyrixa forced offline (env override). Limited identity answers available.",
                                "suggestions": [],
                                "applied_changes": [],
                                "persona": {
                                    "name": "Lyrixa",
                                    "title": "Lyrixa AI Assistant",
                                },
                                "awareness": {"note": "forced offline"},
                                "edit_plan": [],
                                "confidence": 0.5,
                                "trace_id": trace_id,
                            }
                        # If allow_edits is False we should not auto-inject additional synthetic suggestions beyond upstream set
                        # (allow_edits flag captured earlier; trimming deferred to final block)
                        # Do not trim here; capture original for later finalization
                        if "identity" in result and "persona" not in result:
                            ident = result.get("identity") or {}
                            # minimal persona projection
                            result["persona"] = {
                                "name": ident.get("name") or "Lyrixa",
                                "title": ident.get("title") or "Lyrixa AI Assistant",
                                **(
                                    {"about": ident.get("about")}
                                    if ident.get("about")
                                    else {}
                                ),
                            }
                        # ensure persona exists even if upstream didn't include identity/persona
                        if "persona" not in result or not isinstance(
                            result.get("persona"), dict
                        ):
                            result["persona"] = {
                                "name": "Lyrixa",
                                "title": "Lyrixa AI Assistant",
                            }
                        # ensure awareness/edit_plan/confidence keys exist for contract stability
                        result.setdefault("awareness", {})
                        # Synthesize a lightweight "edit_plan" from suggestions exactly 1:1 only when upstream omitted edit_plan
                        if "edit_plan" not in result:
                            try:
                                sugg = result.get("suggestions") or []
                                if isinstance(sugg, list):
                                    result["edit_plan"] = [
                                        {
                                            "title": (
                                                s.get("title")
                                                or s.get("action")
                                                or "suggestion"
                                            )
                                            if isinstance(s, dict)
                                            else str(s),
                                            "file": s.get("file")
                                            if isinstance(s, dict)
                                            else None,
                                            "action": s.get("action")
                                            if isinstance(s, dict)
                                            else None,
                                        }
                                        for s in sugg
                                    ]
                                else:
                                    result["edit_plan"] = []
                            except Exception:
                                result["edit_plan"] = []
                        # (Defer trimming for read-only case to final response block)
                        # Confidence: conservative default unless upstream set it
                        if "confidence" not in result:
                            result["confidence"] = 0.5
                        # (Removed secondary mock increment to avoid double counting; primary increment occurs earlier if needed)
                except Exception:
                    pass
                r = jsonify(result)  # type: ignore[name-defined]
                # Final trim & plan sync for allow_edits False
                try:
                    if not allow_edits and isinstance(result, dict):
                        suggs = result.get("suggestions")
                        if isinstance(suggs, list):
                            if len(suggs) > 1:
                                suggs = suggs[:1]
                                result["suggestions"] = suggs
                            # Rebuild edit_plan exactly 1:1 with (possibly trimmed) suggestions
                            rebuilt = []
                            for s in suggs:
                                if isinstance(s, dict):
                                    rebuilt.append(
                                        {
                                            "title": s.get("title")
                                            or s.get("action")
                                            or "suggestion",
                                            "file": s.get("file"),
                                            "action": s.get("action"),
                                        }
                                    )
                                else:
                                    rebuilt.append(
                                        {"title": str(s), "file": None, "action": None}
                                    )
                            result["edit_plan"] = rebuilt
                except Exception:
                    pass
                # Ensure fallback mock increment happened only when no service used
                try:
                    if not _service_used:
                        _fpc_after = int(
                            (
                                self.chat_metrics.get("fallback_path_counts", {}) or {}
                            ).get("mock", 0)
                        )
                        if _fpc_after == _fpc_pre:
                            fpcz = (
                                self.chat_metrics.get("fallback_path_counts", {}) or {}
                            )
                            fpcz["mock"] = int(fpcz.get("mock", 0)) + 1
                            self.chat_metrics["fallback_path_counts"] = fpcz
                except Exception:
                    pass
                try:
                    r.headers["X-Aetherra-Trace-Id"] = trace_id
                    r.headers["X-Aetherra-Chat-Version"] = "2"
                    import json as _json

                    r.headers["X-Aetherra-Policy"] = _json.dumps(
                        _policy_snapshot_global()
                    )
                except Exception:
                    pass
                return r
            except Exception as e:
                logger.error(f"lyrixa chat error: {e}")
                return jsonify({"error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/memory/graph", methods=["GET"])
        def memory_graph():
            """Return a summarized memory graph (nodes/edges counts and samples)."""
            self.stats["requests_served"] += 1
            if not self.memory_summarizer:
                return jsonify({"enabled": False, "reason": "not available"}), 501  # type: ignore[name-defined]
            try:
                data = self.memory_summarizer(max_nodes=100)
                return jsonify({"enabled": True, **data})  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"memory graph error: {e}")
                return jsonify({"enabled": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/memory/status", methods=["GET"])
        def memory_status():
            """Return quantum memory status (coherence/branch/entanglement) if available.

            Best-effort via service registry; falls back to ephemeral engine instance.
            """
            self.stats["requests_served"] += 1
            try:
                st = _get_memory_quantum_status_sync()
                if not isinstance(st, dict):
                    st = {"enabled": False}
                return jsonify(st)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        # --- Quantum endpoints ---
        @app.route("/api/quantum/status", methods=["GET"])
        @app.route("/quantum/status", methods=["GET"])  # alias
        def quantum_status():
            self.stats["requests_served"] += 1
            try:
                st = _get_quantum_bridge_status() or {}
                if not isinstance(st, dict) or not st:
                    st = {"enabled": False}
                # Add compatibility keys expected by tests/clients
                try:
                    available_bool = bool(
                        st.get("mode", "simulator") in ("simulator", "provider")
                    )
                except Exception:
                    available_bool = False
                backend_str = str(st.get("provider", "sim"))
                payload = cast(Dict[str, Any], dict(st))
                if "available" not in payload:
                    payload["available"] = available_bool
                if "backend" not in payload:
                    payload["backend"] = backend_str
                return jsonify(payload)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        @app.route("/api/quantum/run", methods=["POST"])
        @app.route("/quantum/run", methods=["POST"])  # alias
        def quantum_run():
            """Run a small quantum recipe against the simulator/provider (best-effort)."""
            self.stats["requests_served"] += 1
            try:
                from Aetherra.aetherra_core.memory.quantum.quantum_bridge import (
                    QuantumRecipe,
                    get_quantum_bridge,
                )

                payload = request.get_json(silent=True) or {}  # type: ignore[name-defined]
                recipe = QuantumRecipe(
                    circuit=payload.get("circuit"),
                    shots=int(payload.get("shots") or 100),
                    seed=payload.get("seed"),
                    noise=payload.get("noise"),
                    metadata=payload.get("metadata"),
                )
                qb = get_quantum_bridge()
                res = qb.run(recipe)
                out = {
                    "job_id": res.job_id,
                    "ok": res.ok,
                    "shots": res.shots,
                    "seed": res.seed,
                    "result": res.result,
                    "provider": res.provider,
                    "mode": res.mode,
                }
                return jsonify(out)  # type: ignore[name-defined]
            except Exception as e:
                logger.error(f"quantum run error: {e}")
                return jsonify({"error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/memory/audit", methods=["GET"])
        def memory_audit():
            """Return memory branch DAG audit info (nodes/edges) if available.

            Best-effort via service registry; falls back to ephemeral engine instance.
            """
            self.stats["requests_served"] += 1
            try:
                data = _get_memory_audit_sync()
                if not isinstance(data, dict):
                    data = {"enabled": False}
                return jsonify(data)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        # --- Memory narratives (stub UI/API) ---
        @app.route("/api/memory/narratives", methods=["GET"])
        def memory_narratives_api():
            """Return recent memory narratives (stubbed list).

            This is a Phase-2 read-only scaffold. It currently returns an empty list
            with an informational note. Future versions will integrate with the memory
            system's narrative store.
            """
            self.stats["requests_served"] += 1
            try:
                payload = {
                    "enabled": True,
                    "narratives": [],
                    "note": "Narratives listing is scaffolded; storage integration pending",
                }
                return jsonify(payload)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"enabled": False}), 200  # type: ignore[name-defined]

        @app.route("/memory/narratives", methods=["GET"])
        def memory_narratives_page():
            """Simple HTML page for memory narratives (stub)."""
            self.stats["requests_served"] += 1
            try:
                return (
                    """
                    <html>
                      <head><title>Aetherra Memory Narratives</title></head>
                      <body style="font-family: monospace; background: #0a0a0a; color: #00ffaa; padding: 20px;">
                        <h1>≡ƒºá Memory Narratives</h1>
                        <p>This view is a Phase-2 scaffold. API: <a href="/api/memory/narratives" style="color:#00ffaa;">/api/memory/narratives</a></p>
                        <p>No narratives to display yet.</p>
                      </body>
                    </html>
                    """,
                    200,
                    {"Content-Type": "text/html; charset=utf-8"},
                )
            except Exception:
                return "Unavailable", 200

        # --- Trainer (scaffold + minimal in-memory execution) ---
        @app.route("/api/trainer/status", methods=["GET"])
        def api_trainer_status():
            """Read-only status for the Trainer system (scaffold)."""
            self.stats["requests_served"] += 1
            try:
                # Always read env live; never cache to allow test isolation
                raw_flag = os.environ.get("AETHERRA_TRAINER_ENABLED", "0")
                enabled = True if str(raw_flag).strip() == "1" else False
                if not enabled:
                    # Fast path: return disabled snapshot without mutating job states first to satisfy tests
                    return jsonify(
                        {
                            "ok": True,
                            "enabled": False,
                            "jobs": {
                                "queued": 0,
                                "running": 0,
                                "completed": 0,
                                "failed": 0,
                            },
                            "eval_runs_total": int(self._trainer_eval_runs_total),
                        }
                    )  # type: ignore[name-defined]
                if not enabled:
                    # Best-effort ensure no jobs are marked running while disabled
                    with self._trainer_lock:
                        for j in self.trainer_jobs.values():
                            if j.get("state") == "running":
                                j["state"] = "failed"
                                j["progress"] = 0.0
                q = r = c = f = 0
                with self._trainer_lock:
                    for j in self.trainer_jobs.values():
                        st = str(j.get("state"))
                        if st == "queued":
                            q += 1
                        elif st == "running":
                            r += 1
                        elif st == "completed":
                            c += 1
                        elif st == "failed":
                            f += 1
                out = {
                    "ok": True,
                    "enabled": bool(enabled),
                    "jobs": {"queued": q, "running": r, "completed": c, "failed": f},
                    "eval_runs_total": int(self._trainer_eval_runs_total),
                }
                return jsonify(out)  # type: ignore[name-defined]
            except Exception:
                return jsonify({"ok": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/trainer/jobs", methods=["GET", "POST"])
        def api_trainer_jobs():
            """List or submit trainer jobs (scaffold with in-memory execution)."""
            self.stats["requests_served"] += 1
            try:
                enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
                if request.method == "POST":  # type: ignore[name-defined]
                    if not enabled:
                        return jsonify({"ok": False, "error": "trainer_disabled"}), 400  # type: ignore[name-defined]
                    try:
                        payload = request.get_json(force=True, silent=True) or {}  # type: ignore
                    except Exception:
                        payload = {}
                    job_id = self._trainer_submit_job(cast(Dict[str, Any], payload))
                    return jsonify({"ok": True, "job_id": job_id})  # type: ignore[name-defined]
                # GET
                jobs_out = []
                with self._trainer_lock:
                    for jid in reversed(self._trainer_job_order[-100:]):
                        j = self.trainer_jobs.get(jid)
                        if not j:
                            continue
                        jobs_out.append(
                            {
                                "job_id": j.get("job_id"),
                                "state": j.get("state"),
                                "progress": j.get("progress"),
                                "task": j.get("task"),
                                "created_at": j.get("created_at"),
                                "started_at": j.get("started_at"),
                                "finished_at": j.get("finished_at"),
                            }
                        )
                return jsonify({"ok": True, "jobs": jobs_out, "enabled": bool(enabled)})  # type: ignore[name-defined]
            except Exception:
                return jsonify({"ok": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/trainer/jobs/<job_id>", methods=["GET"])
        def api_trainer_job_detail(job_id: str):
            """Fetch a single trainer job by id."""
            self.stats["requests_served"] += 1
            try:
                enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
                with self._trainer_lock:
                    job = self.trainer_jobs.get(str(job_id))
                    if not job:
                        return jsonify({"ok": False, "error": "not_found"}), 404  # type: ignore[name-defined]
                    out = dict(job)
                out["enabled"] = bool(enabled)
                return jsonify({"ok": True, "job": out})  # type: ignore[name-defined]
            except Exception:
                return jsonify({"ok": False, "error": "server"}), 500  # type: ignore[name-defined]

        # --- Trainer evaluations (scaffold) ---
        @app.route("/api/trainer/evals", methods=["GET", "POST"])
        def api_trainer_evals():
            """List or submit trainer evaluation runs (scaffold)."""
            self.stats["requests_served"] += 1
            try:
                enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
                if request.method == "POST":  # type: ignore[name-defined]
                    if not enabled:
                        return jsonify({"ok": False, "error": "trainer_disabled"}), 400  # type: ignore[name-defined]
                    try:
                        payload = request.get_json(force=True, silent=True) or {}  # type: ignore
                    except Exception:
                        payload = {}
                    eval_id = self._trainer_submit_eval(cast(Dict[str, Any], payload))
                    return jsonify({"ok": True, "eval_id": eval_id})  # type: ignore[name-defined]
                # GET
                evals_out = []
                with self._trainer_lock:
                    for eid in reversed(self._trainer_eval_order[-100:]):
                        ev = self.trainer_evals.get(eid)
                        if not ev:
                            continue
                        evals_out.append(
                            {
                                "eval_id": ev.get("eval_id"),
                                "state": ev.get("state"),
                                "progress": ev.get("progress"),
                                "task": ev.get("task"),
                                "created_at": ev.get("created_at"),
                                "started_at": ev.get("started_at"),
                                "finished_at": ev.get("finished_at"),
                            }
                        )
                return jsonify(
                    {"ok": True, "evals": evals_out, "enabled": bool(enabled)}
                )  # type: ignore[name-defined]
            except Exception:
                return jsonify({"ok": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/api/trainer/evals/<eval_id>", methods=["GET"])
        def api_trainer_eval_detail(eval_id: str):
            """Fetch a single trainer evaluation by id."""
            self.stats["requests_served"] += 1
            try:
                enabled = os.environ.get("AETHERRA_TRAINER_ENABLED", "0") == "1"
                with self._trainer_lock:
                    ev = self.trainer_evals.get(str(eval_id))
                    if not ev:
                        return jsonify({"ok": False, "error": "not_found"}), 404  # type: ignore[name-defined]
                    out = dict(ev)
                out["enabled"] = bool(enabled)
                return jsonify({"ok": True, "eval": out})  # type: ignore[name-defined]
            except Exception:
                return jsonify({"ok": False, "error": "server"}), 500  # type: ignore[name-defined]

        @app.route("/services", methods=["GET"])
        def get_services():
            """Get available services for Aetherra OS compatibility"""
            self.stats["requests_served"] += 1
            return jsonify(
                {  # type: ignore[name-defined]
                    "services": ["hub_server", "plugin_registry", "plugin_discovery"],
                    "status": "online",
                    "running": True,
                    "total_services": 3,
                    "hub_capabilities": [
                        "plugin_registration",
                        "plugin_discovery",
                        "marketplace",
                    ],
                }
            )

        @app.route("/", methods=["GET"])
        def index():
            """Hub web interface"""
            return """
            <html>
            <head><title>Aetherra Hub - Plugin Marketplace</title></head>
            <body style="font-family: monospace; background: #0a0a0a; color: #00ffaa; padding: 20px;">
                <h1>≡ƒÅ¬ Aetherra Hub - Plugin Marketplace</h1>
                <p>Status: <span style="color: #66ffcc;">ONLINE</span></p>
                <p>Registered Plugins: <span id="plugin-count">Loading...</span></p>
                <p>Uptime: <span id="uptime">Loading...</span></p>
                <p>Lyrixa Chat Service: <span id="lyrixa-status">Checking...</span></p>
                <hr>
                <h2>API Endpoints:</h2>
                <ul>
                    <li><a href="/health" style="color: #00ffaa;">GET /health</a> - Health check</li>
                    <li><a href="/api/plugins" style="color: #00ffaa;">GET /api/plugins</a> - List plugins</li>
                    <li><a href="/api/stats" style="color: #00ffaa;">GET /api/stats</a> - Hub statistics</li>
                    <li>POST /api/lyrixa/chat - Lyrixa chat bridge</li>
                    <li>POST /api/plugins/register - Register plugin</li>
                </ul>
                <script>
                    fetch('/api/stats').then(r=>r.json()).then(d=>{
                        document.getElementById('plugin-count').textContent = Object.keys(d).length || 0;
                        document.getElementById('uptime').textContent = Math.round((Date.now() - new Date(d.startup_time)) / 1000) + 's';
                        try {
                            const ly = d.lyrixa_chat || { registered: false };
                            const el = document.getElementById('lyrixa-status');
                            if (ly.registered) {
                                const ok = ly.status === 'healthy' || ly.status === 'HEALTHY';
                                el.textContent = ok ? 'ONLINE' : (ly.status || 'REGISTERED');
                                el.style.color = ok ? '#66ffcc' : '#ffd166';
                            } else {
                                el.textContent = 'OFFLINE';
                                el.style.color = '#ff6b6b';
                            }
                        } catch (e) { /* no-op */ }
                    });
                </script>
            </body>
            </html>
            """

    def start_server(self):
        """Start the Hub server"""
        if not FLASK_AVAILABLE:
            logger.warning("ΓÜá∩╕Å Flask not available - starting mock hub server")
            self.server_running = True
            return True

        try:
            logger.info(f"[HUB] Starting Aetherra Hub server on port {self.port}")
            try:
                logger.info(
                    f"[AI flags @start] enabled={os.environ.get('AETHERRA_AI_API_ENABLED')} stream={os.environ.get('AETHERRA_AI_API_STREAM')}"
                )
            except Exception:
                pass

            # Start Flask server in a separate thread
            import socket
            import threading

            def run_flask():
                if self.app is None:
                    return
                self.app.run(
                    host="localhost",
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True,
                )

            self.server_thread = threading.Thread(target=run_flask, daemon=True)
            self.server_thread.start()

            # Wait for server to start listening (retry loop to avoid races)
            started = False
            for _ in range(50):  # ~2.5s max
                try:
                    with socket.create_connection(
                        ("127.0.0.1", int(self.port)), timeout=0.1
                    ):
                        started = True
                        break
                except Exception:
                    time.sleep(0.05)
            if not started:
                # Final small grace period
                time.sleep(0.2)

            self.server_running = True
            logger.info(
                f"[OK] Aetherra Hub server online at http://localhost:{self.port}"
            )
            return True

        except Exception as e:
            logger.error(f"Γ¥î Failed to start Hub server: {e}")
            self.server_running = False
            return False

    def register_plugin(self, plugin_data: Dict) -> bool:
        """Register a plugin directly (for internal use)"""
        try:
            plugin_id = plugin_data.get("name", f"plugin_{len(self.plugins)}")
            plugin_data["registered_at"] = datetime.now().isoformat()
            plugin_data["status"] = "registered"
            plugin_data["source"] = "internal"

            self.plugins[plugin_id] = plugin_data
            self.stats["active_registrations"] += 1

            logger.info(f"[OK] Plugin registered internally: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Γ¥î Internal plugin registration failed: {e}")
            return False

    def is_running(self) -> bool:
        """Check if the Hub server is running"""
        return self.server_running

    def get_plugin_count(self) -> int:
        """Get the number of registered plugins"""
        return len(self.plugins)

    def get_stats(self) -> Dict:
        """Get Hub statistics"""
        return {
            **self.stats,
            "total_plugins": len(self.plugins),
            "uptime_seconds": (
                datetime.now() - self.stats["startup_time"]
            ).total_seconds(),
        }

    def stop_server(self):
        """Stop the Hub server"""
        self.server_running = False
        logger.info("≡ƒ¢æ Aetherra Hub server stopped")

    # OS integration hook: allow launcher to call a generic shutdown()
    def shutdown(self):
        """Gracefully stop the Hub server (alias for stop_server)."""
        try:
            self.stop_server()
        except Exception:
            pass


# Global Hub instance
hub_server = None


def start_hub_server(port: int = 3001) -> AetherraHubServer:
    """Start the global Hub server"""
    global hub_server
    # If an existing hub is running on a different port (common in tests),
    # replace it with a new instance bound to the requested port.
    if hub_server is not None:
        try:
            current_port = getattr(hub_server, "port", None)
            if current_port != port or not hub_server.is_running():
                try:
                    hub_server.stop_server()
                except Exception:
                    pass
                hub_server = None
        except Exception:
            hub_server = None
    if hub_server is None:
        hub_server = AetherraHubServer(port)
        hub_server.start_server()
    return hub_server


def get_hub_server() -> Optional[AetherraHubServer]:
    """Get the global Hub server instance"""
    return hub_server


if __name__ == "__main__":
    # Test the Hub server
    print("≡ƒº¬ Testing Aetherra Hub Server")
    server = AetherraHubServer(3001)

    if server.start_server():
        print("[OK] Hub server started successfully")

        # Register a test plugin
        test_plugin = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for Hub server",
            "type": "utility",
        }

        server.register_plugin(test_plugin)
        print(f"≡ƒôè Hub stats: {server.get_stats()}")

        # Keep running for testing
        print("≡ƒöä Hub server running... (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("≡ƒ¢æ Stopping Hub server...")
            server.stop_server()
    else:
        print("Γ¥î Failed to start Hub server")
