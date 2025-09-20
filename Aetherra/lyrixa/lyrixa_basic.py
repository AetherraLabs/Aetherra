#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🤖 Lyrixa Basic AI Assistant
============================

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

This is the BASIC LYRIXA - A simple AI Assistant with two core functions:
1. AI Chat Interface
2. Aetherra Hub (Plugin Store) Interface

This is the foundation that users get when they install Aetherra OS.
Additional functionality comes through plugins installed via the Hub.

Architecture:
- Requires Aetherra OS to run (hard dependency)
- Simple, clean interface with just chat and plugin store
- Dynamic expansion through user-installed plugins
"""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# Persistent memory access
try:
    # Aetherra imports
    from aetherra_persistent_memory import get_persistent_memory_system
except Exception:
    get_persistent_memory_system = None

# Windows console UTF-8 setup for emoji support
if sys.platform == "win32":
    try:
        stdout_reconf = getattr(sys.stdout, "reconfigure", None)
        if callable(stdout_reconf):
            stdout_reconf(encoding="utf-8", errors="replace")
        stderr_reconf = getattr(sys.stderr, "reconfigure", None)
        if callable(stderr_reconf):
            stderr_reconf(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("lyrixa_basic.log", encoding="utf-8", errors="replace"),
    ],
)
logger = logging.getLogger(__name__)


class LyrixaBasicAssistant:
    """
    LYRIXA BASIC AI ASSISTANT

    The core Lyrixa experience: AI Chat + Plugin Hub
    Everything else comes through plugins installed from the Hub.
    """

    def __init__(self) -> None:
        self.aetherra_os_connected = False
        self.service_registry = None
        self.hub_connector = None
        self.ai_chat_system = None
        self.plugin_manager = None
        self.installed_plugins = {}
        self.gui_app = None
        self.main_window = None
        self.workspace_tools = None  # optional: in-process workspace analysis/editing

    async def initialize(self) -> bool:
        """Initialize Basic Lyrixa with OS dependency check."""
        try:
            logger.info("🤖 INITIALIZING LYRIXA BASIC AI ASSISTANT")
            logger.info("=" * 50)
            logger.info("Powered by Aetherra Labs — Official Steward & Operator")

            # STEP 1: Check Aetherra OS dependency (CRITICAL)
            logger.info("[OS] Checking Aetherra OS dependency...")
            if not await self._check_aetherra_os():
                logger.error("[CRITICAL] Aetherra OS not running - Lyrixa cannot start")
                logger.error("           Please start Aetherra OS first")
                return False

            # STEP 2: Initialize AI Chat System
            logger.info("[CHAT] Initializing AI Chat Assistant...")
            self.ai_chat_system = await self._initialize_ai_chat()
            if not self.ai_chat_system:
                logger.error("[ERROR] Failed to initialize AI Chat system")
                return False
            logger.info("[OK] AI Chat Assistant ready")

            # STEP 3: Initialize Aetherra Hub Interface
            logger.info("[HUB] Connecting to Aetherra Hub...")
            self.hub_connector = await self._initialize_hub_connector()
            if not self.hub_connector:
                logger.warning("[WARN] Hub connection failed - plugin features limited")
            else:
                logger.info("[OK] Aetherra Hub connected")

            # STEP 4: Initialize lightweight Workspace Tools (self-discovery/repair)
            # Uses Lyrixa Chat Service directly for repo awareness and safe edits
            try:
                self.workspace_tools = await self._initialize_workspace_tools()
                if self.workspace_tools:
                    logger.info("[OK] Workspace Tools ready (scan/suggest/apply)")
                else:
                    logger.info("[INFO] Workspace Tools unavailable (optional)")
            except Exception as e:
                logger.info(f"[INFO] Workspace Tools init skipped: {e}")

            # STEP 5: Check for installed plugins
            logger.info("[PLUGINS] Scanning for installed plugins...")
            await self._load_installed_plugins()

            logger.info("[READY] Lyrixa Basic AI Assistant initialized successfully")
            logger.info("[BRANDING] Powered by Aetherra Labs")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Initialization failed: {e}")
            return False

    async def _check_aetherra_os(self) -> bool:
        """Check if Aetherra OS is running (hard dependency)."""
        try:
            # --- Configuration knobs (env overrides) ---
            # Maximum time to wait for OS readiness (default 45s, clamp 5-180)
            try:
                wait_total = int(os.getenv("LYRIXA_WAIT_FOR_OS_SECONDS", "45"))
            except Exception:
                wait_total = 45
            wait_total = max(5, min(wait_total, 180))

            # Poll interval (seconds) when waiting for readiness
            try:
                poll_interval = float(os.getenv("LYRIXA_OS_POLL_INTERVAL", "2"))
            except Exception:
                poll_interval = 2.0
            poll_interval = max(0.25, min(poll_interval, 10.0))

            # Minimum number of services considered a healthy OS (default 3).
            # Allow lowering for lightweight / headless development.
            try:
                min_services = int(os.getenv("LYRIXA_MIN_OS_SERVICES", "3"))
            except Exception:
                min_services = 3
            min_services = max(0, min(min_services, 50))

            # If set, skip waiting entirely and continue in degraded mode
            skip_wait = os.getenv("LYRIXA_SKIP_OS_WAIT", "0") == "1"
            # If set, after timeout continue startup (degraded) instead of hard fail
            allow_degraded = (
                os.getenv("LYRIXA_ALLOW_DEGRADED_START", "0") == "1" or skip_wait
            )

            if skip_wait:
                logger.info(
                    "[OS] Skip wait requested (LYRIXA_SKIP_OS_WAIT=1); attempting immediate registry access"
                )

            # Base Hub URL (configurable); support legacy AETHERRA_WEB_PORT / AETHERRA_HUB_PORT overrides
            hub_port = (
                os.getenv("AETHERRA_HUB_PORT")
                or os.getenv("AETHERRA_WEB_PORT")
                or "3001"
            )
            hub_host = os.getenv("AETHERRA_HUB_HOST", "localhost")
            base_hub = os.getenv(
                "AETHERRA_HUB_BASE_URL", f"http://{hub_host}:{hub_port}"
            ).rstrip("/")

            # Allow reverting to legacy single-endpoint probe for stability
            legacy_mode = os.getenv("LYRIXA_OS_LEGACY_DETECTION", "0") == "1"

            # Candidate endpoints (new mode); legacy uses only root
            if legacy_mode:
                hub_probe_urls = [f"{base_hub}/"]
            else:
                hub_probe_urls = [
                    f"{base_hub}/health",
                    f"{base_hub}/api/health",
                    f"{base_hub}/api/plugins",
                    f"{base_hub}/",  # fallback root
                ]

            if legacy_mode:
                logger.info(
                    "[OS] Legacy detection mode enabled (LYRIXA_OS_LEGACY_DETECTION=1)"
                )

            # Check if Aetherra Hub is running (indicates OS is active)
            # The Hub runs on internal marketplace server; any healthy response is acceptable
            # Standard library imports
            import urllib.error
            import urllib.request

            elapsed = 0
            attempt = 1
            # Fast path: if minimum required services is 0, treat as logically connected
            if min_services == 0 and not skip_wait:
                try:
                    # Aetherra imports
                    from aetherra_service_registry import get_service_registry

                    self.service_registry = await get_service_registry()
                    logger.info(
                        "[OS] Bypassing service count check (LYRIXA_MIN_OS_SERVICES=0) — continuing in lightweight mode"
                    )
                    self.aetherra_os_connected = True
                    return True
                except Exception:
                    # Fall through to normal loop if registry can't be obtained yet
                    pass

            while elapsed <= wait_total or skip_wait:
                try:
                    # Quick HTTP check to Aetherra Hub across candidate endpoints
                    hub_ok = False
                    last_status = None
                    for url in hub_probe_urls:
                        try:
                            with urllib.request.urlopen(url, timeout=2.5) as response:
                                last_status = response.status
                                if (
                                    200 <= response.status < 500
                                ):  # even 404 proves server up
                                    hub_ok = True
                                    break
                        except Exception:
                            continue
                    if hub_ok:
                        logger.info(
                            f"[OS] Hub responsive at {url} (status={last_status})"
                        )
                        # Attempt registry enrichment but don't fail if it errors
                        try:
                            # Aetherra imports
                            from aetherra_service_registry import get_service_registry

                            self.service_registry = await get_service_registry()
                        except Exception as reg_err:
                            logger.debug(
                                f"[OS] Registry fetch after hub check failed: {reg_err}"
                            )
                        self.aetherra_os_connected = True
                        return True
                except (
                    urllib.error.URLError,
                    urllib.error.HTTPError,
                    ConnectionRefusedError,
                    OSError,
                ):
                    # Hub not responding, try other methods
                    pass

                # Fallback in same loop: Try direct service registry connection
                try:
                    # Aetherra imports
                    from aetherra_service_registry import get_service_registry

                    self.service_registry = await get_service_registry()
                    if self.service_registry:
                        services = self.service_registry.list_services()
                        # Fast success path: if core identifiers present, accept even if below min_services
                        core_names = {
                            "aetherra_hub",
                            "plugin_discovery",
                            "service_registry",
                            "registry",
                        }
                        present = set(services.keys())
                        if present & core_names:
                            if len(services) >= min_services or legacy_mode:
                                logger.info(
                                    f"[OS] Registry core services detected ({len(services)} total) — proceeding"
                                )
                                self.aetherra_os_connected = True
                                return True
                        if len(services) >= min_services:
                            logger.info(
                                f"[OS] Connected to Aetherra OS ({len(services)} services >= {min_services} required)"
                            )
                            self.aetherra_os_connected = True
                            return True
                        else:
                            if not skip_wait:
                                logger.info(
                                    f"[OS] OS not ready yet (attempt {attempt}): {len(services)} services < {min_services}; waiting..."
                                )
                            else:
                                logger.info(
                                    f"[OS] Degraded start: only {len(services)} services (< {min_services}) but skip wait enabled"
                                )
                                self.aetherra_os_connected = False
                                return True  # proceed degraded
                    else:
                        if not skip_wait:
                            logger.info(
                                f"[OS] Service registry unavailable (attempt {attempt}); waiting..."
                            )
                        else:
                            logger.info(
                                "[OS] Service registry not ready but skip wait enabled; proceeding in degraded mode"
                            )
                            return True
                except Exception:
                    # Likely OS not ready or registry not reachable yet
                    logger.debug(
                        f"[OS] Registry check failed (attempt {attempt}); will retry"
                    )

                if skip_wait:
                    # One immediate iteration only when skip_wait is set
                    break

                if elapsed >= wait_total:
                    break

                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                attempt += 1

            # Final diagnostic: try one last registry snapshot for operator insight
            diag_services = {}
            try:
                # Aetherra imports
                from aetherra_service_registry import get_service_registry

                reg = await get_service_registry()
                diag_services = {
                    name: info.status.value
                    for name, info in reg.list_services().items()
                }
            except Exception as diag_err:
                logger.debug(f"[OS] Final diagnostic registry fetch failed: {diag_err}")

            if allow_degraded:
                logger.warning(
                    f"[OS] Aetherra OS not ready after {wait_total}s (services < {min_services}). Continuing in degraded mode (limited features). Current services: {diag_services}"
                )
                self.aetherra_os_connected = False
                return True

            logger.error(
                f"[OS] Aetherra OS not ready after {wait_total}s. Observed services: {diag_services}. Set LYRIXA_ALLOW_DEGRADED_START=1 to bypass or adjust LYRIXA_MIN_OS_SERVICES."
            )
            return False

        except Exception as e:
            logger.debug(f"[OS] Aetherra OS check failed: {e}")
            return False

    async def _initialize_ai_chat(self):
        """Initialize the AI Chat system with multi-model support."""
        try:
            # First attempt: use advanced LyrixaChatService for richer awareness
            try:
                # Aetherra imports
                from Aetherra.lyrixa.chat.lyrixa_chat_service import (
                    ChatOptions,
                    LyrixaChatService,
                )

                class _AdvancedChatWrapper:
                    def __init__(self) -> None:
                        self._svc: Optional[LyrixaChatService] = None  # type: ignore[name-defined]

                    async def initialize(self) -> None:
                        self._svc = LyrixaChatService(workspace_root=Path(os.getcwd()))  # type: ignore[name-defined]
                        await self._svc.initialize()
                        return True

                    async def send_message(self, message: str):
                        if not self._svc:
                            raise RuntimeError("advanced chat not initialized")
                        resp = await self._svc.chat(message, ChatOptions())  # type: ignore[name-defined]
                        return resp  # GUI now supports ChatResponse objects

                adv = _AdvancedChatWrapper()
                ok = await adv.initialize()
                if ok:
                    logger.info("[CHAT] Using advanced LyrixaChatService backend")
                    return adv
            except Exception as e:
                logger.debug(
                    f"[CHAT] Advanced LyrixaChatService unavailable, fallback to basic: {e}"
                )

            # Create a simple chat system with model fallback
            class BasicChatSystem:
                def __init__(self) -> None:
                    self.current_model = None
                    self.available_models = []
                    self._pmemory = None
                    self._detect_available_models()

                async def _ensure_memory(self):
                    if self._pmemory is None and get_persistent_memory_system:
                        try:
                            self._pmemory = await get_persistent_memory_system()
                        except Exception:
                            self._pmemory = None

                def _is_ownership_query(self, message: str) -> bool:
                    m = (message or "").lower()
                    keys = [
                        "who owns aetherra",
                        "who owns aetherra labs",
                        "owner of aetherra",
                        "owner of aetherra labs",
                        "ownership of aetherra",
                        "ownership of aetherra labs",
                        "who founded aetherra",
                        "who founded aetherra labs",
                    ]
                    return any(k in m for k in keys)

                async def _ownership_reply(self, message: str) -> str:
                    try:
                        await self._ensure_memory()
                        if not self._pmemory:
                            return "I don't have a record of ownership."

                        # Prefer verified ownership facts
                        facts = await self._pmemory.recall_by_tag("ownership", limit=5)
                        verified = [f for f in facts if f.get("verified")]
                        if not verified:
                            # Fallback semantic search
                            cands = await self._pmemory.retrieve(
                                "Aetherra Labs ownership",
                                limit=5,
                                memory_type="fact",
                            )
                            verified = [c for c in cands if c.get("verified")]
                        if verified:
                            verified.sort(
                                key=lambda x: x.get("created_at", ""), reverse=True
                            )
                            return str(
                                verified[0].get("content")
                                or "I don't have a record of ownership."
                            )
                        return "I don't have a record of ownership."
                    except Exception:
                        return "I don't have a record of ownership."

                def _detect_available_models(self):
                    """Detect available AI models with funding check."""
                    models = []

                    # Check funded models
                    if os.getenv("OPENAI_API_KEY"):
                        models.append(
                            {"name": "OpenAI GPT", "type": "funded", "priority": 1}
                        )
                    if os.getenv("ANTHROPIC_API_KEY"):
                        models.append(
                            {"name": "Claude", "type": "funded", "priority": 2}
                        )
                    if os.getenv("GOOGLE_API_KEY"):
                        models.append(
                            {"name": "Gemini", "type": "funded", "priority": 3}
                        )

                    # Always add Ollama as fallback
                    models.append({"name": "Ollama", "type": "local", "priority": 99})

                    self.available_models = sorted(models, key=lambda x: x["priority"])
                    self.current_model = self.available_models[0] if models else None

                async def send_message(self, message: str) -> str:
                    """Send message and get AI response with smart fallback."""
                    # Hard guard against ownership hallucinations
                    if self._is_ownership_query(message):
                        return await self._ownership_reply(message)

                    for model in self.available_models:
                        try:
                            if model["type"] == "funded":
                                response = await self._try_funded_model(model, message)
                                if response:
                                    return response
                            elif model["type"] == "local":
                                response = await self._try_ollama(message)
                                if response:
                                    return response
                        except Exception as e:
                            logger.debug(f"Model {model['name']} failed: {e}")
                            continue

                    return "I'm sorry, I'm having trouble connecting to AI services. Please check your configuration."

                async def _try_funded_model(
                    self, model: dict, message: str
                ) -> Optional[str]:
                    """Try to use a funded AI model (OpenAI supported)."""
                    name = model.get("name")
                    if name == "OpenAI GPT" and os.getenv("OPENAI_API_KEY"):
                        try:
                            # Lazy import to avoid hard dependency when key isn't set
                            # Third party imports
                            import openai  # type: ignore

                            api_key = os.getenv("OPENAI_API_KEY")
                            # Prefer gpt-4o-mini if available; allow override
                            model_name = os.getenv("LYRIXA_OPENAI_MODEL", "gpt-4o-mini")
                            logger.info(f"[AI] Using OpenAI model: {model_name}")

                            # Build a lightweight persona-aware prompt
                            system_prompt = (
                                "You are Lyrixa, a friendly, concise AI assistant for the Aetherra OS. "
                                "Give helpful, specific answers. If asked about Aetherra, explain its purpose and components clearly."
                                " When asked who owns Aetherra or Aetherra Labs, do not speculate; if you do not have a verified record,"
                                " respond exactly: 'I don't have a record of ownership.'"
                            )

                            client = openai.OpenAI(api_key=api_key)  # type: ignore
                            resp = client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": message},
                                ],
                                temperature=float(
                                    os.getenv("LYRIXA_OPENAI_TEMPERATURE", "0.7")
                                ),
                                max_tokens=int(
                                    os.getenv("LYRIXA_OPENAI_MAX_TOKENS", "512")
                                ),
                            )
                            content = (
                                resp.choices[0].message.content  # type: ignore[attr-defined]
                                if getattr(resp, "choices", None)
                                else None
                            )
                            if content:
                                return content
                        except Exception as e:  # fall back silently
                            logger.debug(f"OpenAI call failed: {e}")
                            return None

                    # Other funded backends can be wired similarly later
                    return None

                async def _try_ollama(self, message: str) -> Optional[str]:
                    """Try to use local Ollama as fallback by calling its HTTP API."""
                    try:
                        # Standard library imports
                        import json as _json
                        import urllib.request as _ureq

                        model = os.getenv("LYRIXA_OLLAMA_MODEL", "llama3")
                        url = os.getenv(
                            "LYRIXA_OLLAMA_URL", "http://localhost:11434/api/generate"
                        )
                        logger.info(f"[AI] Using Ollama model: {model}")

                        # Persona-aware prompt
                        prompt = (
                            "You are Lyrixa, a helpful AI assistant for the Aetherra OS. "
                            "Answer clearly and concisely. If asked about Aetherra, explain it simply with specifics. "
                            "When asked who owns Aetherra or Aetherra Labs, do not speculate; if you do not have a verified record,"
                            " respond exactly: 'I don't have a record of ownership.'\n\n"
                            f"User: {message}\nLyrixa:"
                        )

                        req = _ureq.Request(
                            url,
                            data=_json.dumps(
                                {
                                    "model": model,
                                    "prompt": prompt,
                                    "stream": False,
                                }
                            ).encode("utf-8"),
                            headers={"Content-Type": "application/json"},
                            method="POST",
                        )
                        with _ureq.urlopen(
                            req, timeout=float(os.getenv("LYRIXA_OLLAMA_TIMEOUT", "15"))
                        ) as resp:
                            payload = _json.loads(
                                resp.read().decode("utf-8", errors="replace")
                            )
                            text = (
                                payload.get("response") or payload.get("message") or ""
                            )
                            return text.strip() or None
                    except Exception as e:
                        logger.debug(f"Ollama call failed: {e}")
                        return None

            return BasicChatSystem()

        except Exception as e:
            logger.error(f"[ERROR] AI Chat initialization failed: {e}")
            return None

    async def _initialize_hub_connector(self):
        """Initialize connection to Aetherra Hub for plugin discovery."""
        try:
            # Create a basic hub connector
            class BasicHubConnector:
                def __init__(self) -> None:
                    self.connected = False
                    self.available_plugins = []

                async def connect(self) -> bool:
                    """Connect to Aetherra Hub."""
                    try:
                        # Try to connect to local hub server
                        # Third party imports
                        import aiohttp

                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                "http://localhost:3001/api/plugins"
                            ) as response:
                                if response.status == 200:
                                    hub_data = await response.json()
                                    # Extract plugins array from Hub response
                                    self.available_plugins = hub_data.get("plugins", [])
                                    self.connected = True
                                    return True
                    except Exception:
                        pass

                    # Mock some plugins if hub not available
                    self.available_plugins = [
                        {
                            "name": "code-editor",
                            "display_name": "Code Editor",
                            "description": "Advanced code editing capabilities",
                            "version": "1.0.0",
                            "category": "development",
                        },
                        {
                            "name": "system-tools",
                            "display_name": "System Tools",
                            "description": "System monitoring and management tools",
                            "version": "1.0.0",
                            "category": "utilities",
                        },
                    ]
                    return True

                async def get_available_plugins(self) -> list:
                    """Get list of available plugins from hub."""
                    return self.available_plugins

                async def install_plugin(self, plugin_name: str) -> bool:
                    """Install a plugin from the hub."""
                    try:
                        logger.info(f"[HUB] Installing plugin: {plugin_name}")

                        # Create Lyrixa plugins directory
                        lyrixa_plugins_dir = Path(__file__).parent / "plugins"
                        lyrixa_plugins_dir.mkdir(parents=True, exist_ok=True)

                        # Get plugin info from Hub
                        response = urllib.request.urlopen(
                            "http://localhost:3001/api/plugins"
                        )
                        plugins_data = json.loads(response.read())

                        # Find the plugin
                        plugin_info = None
                        for plugin in plugins_data.get("plugins", []):
                            if plugin.get("name") == plugin_name:
                                plugin_info = plugin
                                break

                        if not plugin_info:
                            logger.error(f"[HUB] Plugin '{plugin_name}' not found")
                            return False

                        logger.info(
                            f"[HUB] Found plugin: {plugin_info.get('description', 'No description')}"
                        )

                        # --- Resolve source path (may be missing from hub payload) ---
                        source_path: Path | None = None

                        if plugin_info.get("local_path"):
                            source_path = Path(plugin_info["local_path"]).resolve()
                        else:
                            logger.info(
                                f"[HUB] Plugin '{plugin_name}' missing local_path; attempting discovery fallback"
                            )
                            # Attempt dynamic discovery
                            try:
                                # Aetherra imports
                                from aetherra_plugin_discovery import (
                                    AetherraPluginDiscovery,
                                )

                                disc = AetherraPluginDiscovery()
                                await disc.discover_all_plugins()
                                md = disc.discovered_plugins.get(plugin_name)
                                if md and md.local_path:
                                    source_path = Path(md.local_path).resolve()
                                    logger.info(
                                        f"[HUB] Resolved local path via discovery: {source_path}"
                                    )
                            except Exception as disc_err:
                                logger.debug(
                                    f"[HUB] Discovery fallback failed for {plugin_name}: {disc_err}"
                                )

                            # Heuristic search if still unresolved
                            if source_path is None:
                                candidates: list[Path] = []
                                plugins_root = Path("Aetherra/plugins").resolve()
                                candidates.append(plugins_root / plugin_name)
                                candidates.append(plugins_root / f"{plugin_name}.py")
                                # Scan for single file matching plugin_name inside plugins root
                                try:
                                    for py in plugins_root.glob("*.py"):
                                        if py.stem == plugin_name:
                                            candidates.append(py)
                                except Exception:
                                    pass
                                for cand in candidates:
                                    if cand.exists():
                                        source_path = cand
                                        logger.info(
                                            f"[HUB] Heuristic resolved plugin '{plugin_name}' to {cand}"
                                        )
                                        break

                        if source_path is None:
                            logger.error(
                                f"[HUB] No installation method available for plugin: {plugin_name} (unable to resolve local source)"
                            )
                            return False

                        # Standard library imports
                        import shutil

                        if source_path.is_file():
                            dest_path = lyrixa_plugins_dir / source_path.name
                            shutil.copy2(source_path, dest_path)
                            logger.info(
                                f"[HUB] Installed single-file plugin to: {dest_path}"
                            )
                        elif source_path.is_dir():
                            dest_path = lyrixa_plugins_dir / plugin_name
                            if dest_path.exists():
                                shutil.rmtree(dest_path)
                            shutil.copytree(source_path, dest_path)
                            logger.info(
                                f"[HUB] Installed directory plugin to: {dest_path}"
                            )
                        else:
                            logger.error(
                                f"[HUB] Resolved source path does not exist or is not a file/dir: {source_path}"
                            )
                            return False

                        # Create installation record
                        install_record = {
                            "name": plugin_name,
                            "version": plugin_info.get("version", "1.0.0"),
                            "description": plugin_info.get("description", ""),
                            "installed_at": plugin_info.get("registered_at", ""),
                            "source": "hub",
                            "category": plugin_info.get("category", "utility"),
                        }

                        # Save to installed plugins registry
                        registry_file = lyrixa_plugins_dir / "installed_plugins.json"
                        registry = {}
                        if registry_file.exists():
                            with open(registry_file, encoding="utf-8") as f:
                                registry = json.load(f)

                        registry[plugin_name] = install_record

                        with open(registry_file, "w", encoding="utf-8") as f:
                            json.dump(registry, f, indent=2, ensure_ascii=False)

                        logger.info(
                            f"[HUB] Plugin '{plugin_name}' installed successfully!"
                        )
                        return True

                    except Exception as e:
                        logger.error(f"[HUB] Plugin installation failed: {e}")
                        return False

            connector = BasicHubConnector()
            await connector.connect()
            return connector

        except Exception as e:
            logger.error(f"[ERROR] Hub connector initialization failed: {e}")
            return None

    async def _initialize_workspace_tools(self):
        """Optionally wire local workspace awareness and safe edits via Lyrixa Chat Service."""
        try:
            # Lazy import to avoid hard dependency
            # Aetherra imports
            from Aetherra.lyrixa.chat.lyrixa_chat_service import (
                ChatOptions,
                LyrixaChatService,
            )

            class BasicWorkspaceTools:
                def __init__(self, root: Path) -> None:
                    self.root = Path(root)
                    self._svc: Optional[LyrixaChatService] = None  # type: ignore[name-defined]

                async def initialize(self) -> None:
                    self._svc = LyrixaChatService(workspace_root=self.root)  # type: ignore[name-defined]
                    await self._svc.initialize()
                    return True

                async def scan(self) -> dict:
                    if not self._svc:
                        raise RuntimeError("workspace tools not initialized")
                    # Private but stable helper for summary awareness
                    return await self._svc._workspace_awareness(summary_only=True)  # type: ignore[attr-defined]

                async def suggest(self, hint: str = "", limit: int = 3):
                    if not self._svc:
                        raise RuntimeError("workspace tools not initialized")
                    return await self._svc.suggest_fixes(hint=hint, limit=limit)

                async def apply(
                    self, suggestion: dict, edit_root: Optional[Path] = None
                ):
                    if not self._svc:
                        raise RuntimeError("workspace tools not initialized")
                    opts = ChatOptions(
                        edit_root=Path(edit_root) if edit_root else self.root
                    )  # type: ignore[name-defined]
                    ok, change = await self._svc.apply_fix(
                        suggestion, edit_root=opts.edit_root
                    )
                    return ok, change

            tools = BasicWorkspaceTools(root=Path(os.getcwd()))
            ok = await tools.initialize()
            return tools if ok else None
        except Exception as e:
            logger.debug(f"[WorkspaceTools] init failed: {e}")
            return None

    async def _load_installed_plugins(self):
        """Load any plugins that are already installed."""
        try:
            # Check for installed plugins
            lyrixa_plugins_dir = Path(__file__).parent / "plugins"
            registry_file = lyrixa_plugins_dir / "installed_plugins.json"

            plugin_count = 0
            if registry_file.exists():
                with open(registry_file, encoding="utf-8") as f:
                    registry = json.load(f)
                    plugin_count = len(registry)

                logger.info(f"[PLUGINS] Found {plugin_count} installed plugins:")
                for name, info in registry.items():
                    logger.info(
                        f"[PLUGINS]   • {name} v{info.get('version', '?')} - {info.get('description', 'No description')}"
                    )
            else:
                logger.info(f"[PLUGINS] Found {plugin_count} installed plugins")

        except Exception as e:
            logger.warning(f"[WARN] Plugin loading failed: {e}")

    def start_gui(self) -> bool:
        """Start the Basic Lyrixa GUI."""
        try:
            # Third party imports
            from PySide6.QtWidgets import QApplication

            # Add the current directory to path for imports
            current_dir = Path(__file__).parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))

            # Third party imports
            from lyrixa_basic_gui import LyrixaBasicWindow

            # Create Qt Application
            self.gui_app = QApplication.instance() or QApplication(sys.argv)
            # Include stewardship branding in application name (concise)
            self.gui_app.setApplicationName(
                "Lyrixa Basic AI Assistant · Powered by Aetherra Labs"
            )
            self.gui_app.setApplicationVersion("1.0.0")

            # Create Basic Lyrixa window
            self.main_window = LyrixaBasicWindow(
                ai_chat=self.ai_chat_system,
                hub_connector=self.hub_connector,
                service_registry=self.service_registry,
            )

            # Show window
            self.main_window.show()

            logger.info("[GUI] Lyrixa Basic AI Assistant GUI launched")
            logger.info("=" * 50)
            logger.info("🤖 AI CHAT: Ask me anything!")
            logger.info("🔌 AETHERRA HUB: Install plugins to expand my capabilities")
            logger.info("⚡ Powered by Aetherra Labs")
            logger.info("=" * 50)

            # Start Qt event loop
            return self.gui_app.exec()  # nosec B102: Qt application execution == 0

        except ImportError:
            logger.error(
                "[ERROR] GUI dependencies not available. Install with: pip install PySide6"
            )
            return False
        except Exception as e:
            logger.error(f"[ERROR] GUI startup failed: {e}")
            return False


async def main():
    """Main entry point for Lyrixa Basic."""
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(description="Lyrixa Basic AI Assistant")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    # Create and initialize Lyrixa Basic
    lyrixa = LyrixaBasicAssistant()

    if not await lyrixa.initialize():
        logger.error("[CRITICAL] Lyrixa Basic initialization failed")
        return 1

    if args.cli:
        # CLI mode for testing
        logger.info("[CLI] Lyrixa Basic running in CLI mode")
        print(
            "Lyrixa> Type 'quit' to exit. Use :scan, :suggest, :apply for workspace tools."
        )

        # Check if AI chat system is initialized
        if not lyrixa.ai_chat_system:
            print("Error: AI chat system not initialized")
            return 1

        # simple in-memory last suggestions list for :apply
        last_suggestions = []

        while True:
            try:
                user_input = input("You> ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    break

                # Workspace tools commands (optional)
                if user_input.startswith(":") and lyrixa.workspace_tools:
                    cmd = user_input[1:].strip()
                    if cmd == "scan":
                        try:
                            summary = await lyrixa.workspace_tools.scan()
                            print("Lyrixa> Workspace summary:")
                            print(f" - root: {summary.get('root')}")
                            print(f" - total_py_files: {summary.get('total_py_files')}")
                            keys = summary.get("key_components", [])
                            if keys:
                                print(" - key_components:")
                                for k in keys[:10]:
                                    print(f"   • {k}")
                            else:
                                print(" - key_components: []")
                        except Exception as e:
                            print(f"Lyrixa> Scan failed: {e}")
                        continue
                    if cmd.startswith("suggest"):
                        try:
                            hint = cmd[len("suggest") :].strip()
                            last_suggestions = await lyrixa.workspace_tools.suggest(
                                hint=hint or "", limit=5
                            )
                            if not last_suggestions:
                                print("Lyrixa> No suggestions found.")
                            else:
                                print("Lyrixa> Suggestions:")
                                for i, s in enumerate(last_suggestions, 1):
                                    title = s.get("title") or s.get("action")
                                    print(f" {i}. {title} — {s.get('file')}")
                        except Exception as e:
                            print(f"Lyrixa> Suggest failed: {e}")
                        continue
                    if cmd.startswith("apply"):
                        try:
                            parts = cmd.split()
                            idx = 1
                            if len(parts) > 1 and parts[1].isdigit():
                                idx = int(parts[1])
                            if not last_suggestions:
                                print(
                                    "Lyrixa> No cached suggestions. Run :suggest first."
                                )
                            else:
                                sel = (
                                    last_suggestions[idx - 1]
                                    if 1 <= idx <= len(last_suggestions)
                                    else last_suggestions[0]
                                )
                                ok, change = await lyrixa.workspace_tools.apply(sel)
                                if ok:
                                    print(f"Lyrixa> Applied: {change}")
                                else:
                                    print(f"Lyrixa> Not applied: {change}")
                        except Exception as e:
                            print(f"Lyrixa> Apply failed: {e}")
                        continue
                    if cmd in {"help", "?"}:
                        print(
                            "Lyrixa> Workspace commands: :scan | :suggest [hint] | :apply [n]"
                        )
                        continue

                response = await lyrixa.ai_chat_system.send_message(user_input)
                # Pretty-print ChatResponse objects (advanced backend)
                if not isinstance(response, (str, dict)) and hasattr(response, "text"):
                    try:
                        txt = getattr(response, "text", "")
                        awareness = getattr(response, "awareness", {}) or {}
                        # Small awareness addendum: indicate path if available, number of evidence items
                        extra_parts = []
                        if isinstance(awareness, dict):
                            ev = awareness.get("evidence")
                            if isinstance(ev, list) and ev:
                                extra_parts.append(f"evidence={len(ev)}")
                            cb = awareness.get("confidence_breakdown") or awareness.get(
                                "confidence"
                            )
                            if isinstance(cb, dict):
                                ov = cb.get("overall")
                                try:
                                    if ov is not None:
                                        extra_parts.append(f"conf={float(ov):.2f}")
                                except Exception:
                                    pass
                        extra = (
                            (" [" + ", ".join(extra_parts) + "]") if extra_parts else ""
                        )
                        print(f"Lyrixa> {txt}{extra}")
                    except Exception:
                        print(f"Lyrixa> {response}")
                else:
                    print(f"Lyrixa> {response}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        return 0
    else:
        # GUI mode
        return 0 if lyrixa.start_gui() else 1


if __name__ == "__main__":
    # Run in project root
    os.chdir(Path(__file__).parent.parent.parent)
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
