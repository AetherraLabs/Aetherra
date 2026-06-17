# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Enhanced Plugin Manager
=======================

Advanced plugin management system for Lyrixa with dynamic loading,
lifecycle management, and comprehensive analytics integration.
"""

# Standard library imports
import importlib
import importlib.util
import logging
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent
from Aetherra.guardian.containment import active_containments_for_intent
from Aetherra.guardian.models import ContainmentAction
from Aetherra.security.audit_ledger import AuditLedgerError, SecurityAuditLedger

logger = logging.getLogger(__name__)

try:
    from Aetherra.aetherra_core.system.security_system import append_security_audit_entry
except Exception:  # pragma: no cover - fallback when module unavailable

    def append_security_audit_entry(
        actor: str,
        event_type: str,
        *,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[Path]:
        return None


try:
    # Aetherra imports
    from Aetherra.security.capabilities import has_capability
except Exception:

    def has_capability(requester: str, capability: str) -> bool:  # type: ignore
        return True


try:
    # Aetherra imports
    from Aetherra.security.plugin_signing import verify_plugin_signature
except Exception:

    def verify_plugin_signature(manifest: dict) -> bool:  # type: ignore
        return True


try:
    # Aetherra imports
    from Aetherra.security.sandbox import (
        IsolatedCallSpec,
        IsolatedExecutionError,
        ensure_memory_budget,
        run_isolated,
        run_with_timeout,
    )
    from Aetherra.security.sandbox import (
        MemoryBudgetExceeded as _SandboxMemoryBudgetExceeded,  # type: ignore
    )
    from Aetherra.security.sandbox import (
        TimeBudgetExceeded as _SandboxTimeBudgetExceeded,  # type: ignore
    )

    # Bind exception aliases to expected names
    TimeBudgetExceeded = _SandboxTimeBudgetExceeded  # type: ignore
    MemoryBudgetExceeded = _SandboxMemoryBudgetExceeded  # type: ignore
except Exception:

    def run_with_timeout(func, args=None, kwargs=None, timeout_sec: float = 5.0):  # type: ignore
        return func(*(args or ()), **(kwargs or {}))

    IsolatedCallSpec = None  # type: ignore

    class IsolatedExecutionError(Exception):  # type: ignore
        pass

    def run_isolated(*_args, **_kwargs):  # type: ignore
        raise IsolatedExecutionError("process isolation is unavailable")


def _is_production_profile() -> bool:
    profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
    return profile in {"prod", "production"}


def _safe_mode_enabled() -> bool:
    try:
        from Aetherra.aetherra_core.system.security_system import is_safe_mode_enabled

        return is_safe_mode_enabled()
    except Exception:
        return (os.getenv("AETHERRA_SAFE_MODE", "") or "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }


def _plugin_signing_strict_enabled() -> bool:
    if os.getenv("AETHERRA_PROD_UNSAFE_ALLOW", "0") == "1":
        return False
    return os.getenv("AETHERRA_PLUGIN_SIGNING_STRICT", "0") == "1" or _is_production_profile()

    def ensure_memory_budget(max_mb):  # type: ignore
        return None

    class TimeBudgetExceeded(Exception):  # type: ignore
        def __init__(self, message: str = "Time budget exceeded"):
            super().__init__(message)

    class MemoryBudgetExceeded(Exception):  # type: ignore
        def __init__(self, message: str = "Memory budget exceeded"):
            super().__init__(message)


def _get_security_audit_path() -> Optional[Path]:
    path_value = os.getenv("AETHERRA_SECURITY_AUDIT_PATH")
    if path_value:
        return Path(path_value)

    workspace_root = os.getenv("AETHERRA_WORKSPACE_ROOT")
    if workspace_root:
        return Path(workspace_root) / ".aetherra" / "security" / "plugin_audit.jsonl"

    try:
        return Path(__file__).resolve().parents[3] / ".aetherra" / "security" / "plugin_audit.jsonl"
    except Exception:
        return None


def _write_security_audit_entry(
    plugin_name: str,
    event_type: str,
    *,
    reason: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        audit_path = _get_security_audit_path()
        if not audit_path:
            return
        SecurityAuditLedger(audit_path).append(
            actor=plugin_name,
            event_type=event_type,
            reason=reason,
            details=details or {},
            extra={"plugin_name": plugin_name},
        )

        append_security_audit_entry(
            plugin_name,
            event_type,
            reason=reason,
            details={**(details or {}), "plugin_audit_path": str(audit_path)},
        )
    except (AuditLedgerError, OSError, TypeError, ValueError) as exc:
        logger.error("Unable to append plugin security audit event: %s", exc)


class PluginState:
    """Plugin state management."""

    # Required plugin metadata
    name = "enhanced_plugin_manager"
    description = "PluginState - Auto-generated description"
    input_schema = {
        "type": "object",
        "properties": {"input": {"type": "string", "description": "Input data"}},
        "required": ["input"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"},
        },
    }
    created_by = "Plugin System Auto-Fixer"

    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginManager:
    """Enhanced plugin management system."""

    def __init__(self, plugins_dir: str | None = None):
        self.plugins_dir = plugins_dir or os.path.join(os.path.dirname(__file__))
        self.plugins = {}
        self.plugin_states = {}
        self.plugin_metadata = {}
        self.event_handlers = {}
        self.auto_reload = False
        self.monitoring_thread = None

        # Analytics integration
        self.analytics = None
        self._initialize_analytics()
        # Internal: retain module objects for policy checks/signing
        self._plugin_modules = {}

    def _initialize_analytics(self):
        """Initialize plugin analytics if available."""
        try:
            # Local imports
            from .plugin_analytics import PluginAnalyticsIntegration  # type: ignore

            self.analytics = PluginAnalyticsIntegration()
        except ImportError:
            self.analytics = None

    def track_plugin_event(
        self, plugin_name: str, event: str, extra_context: Optional[Dict] = None
    ):
        """Track plugin events using analytics integration."""
        if self.analytics:
            context = {"plugin_name": plugin_name}
            if extra_context:
                context.update(extra_context)
            if event == "load_attempt":
                self.analytics.record_plugin_action(plugin_name, "load_attempt", context)
            elif event == "load_success":
                self.analytics.record_plugin_action(plugin_name, "load_success", context)
            elif event == "unload":
                self.analytics.record_plugin_action(plugin_name, "unload", context)
            elif event == "execute_start":
                self.analytics.record_plugin_action(plugin_name, "execute_start", context)
            elif event == "execute_end":
                self.analytics.record_plugin_action(plugin_name, "execute_end", context)
            elif event == "load_error":
                self.analytics.record_plugin_error(
                    plugin_name, Exception("Load error occurred"), context
                )
            elif event == "execute_error":
                self.analytics.record_plugin_error(
                    plugin_name, Exception("Execution error occurred"), context
                )

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory."""
        plugins = []

        if not os.path.exists(self.plugins_dir):
            return plugins

        for file in os.listdir(self.plugins_dir):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_name = file[:-3]  # Remove .py extension

                # Skip system files
                if plugin_name in [
                    "plugin_manager",
                    "enhanced_plugin_manager",
                    "plugin_analytics",
                    "plugin_quality_control",
                ]:
                    continue

                plugins.append(plugin_name)

        return plugins

    def load_plugin(self, plugin_name: str, force_reload: bool = False) -> bool:
        """Load a plugin with comprehensive error handling."""
        if not self._guardian_allows_plugin_load(plugin_name, force_reload=force_reload):
            return False

        try:
            self.plugin_states[plugin_name] = PluginState.LOADING

            # Analytics tracking
            self.track_plugin_event(plugin_name, "load_attempt")

            # Check if already loaded
            if plugin_name in self.plugins and not force_reload:
                self.plugin_states[plugin_name] = PluginState.ACTIVE
                return True

            # Import the plugin module
            module_path = f"lyrixa.plugins.{plugin_name}"
            if plugin_name in sys.modules and force_reload:
                importlib.reload(sys.modules[plugin_name])

            try:
                module = importlib.import_module(module_path)
            except ImportError as exc:
                # Try direct import
                spec = importlib.util.spec_from_file_location(
                    plugin_name, os.path.join(self.plugins_dir, f"{plugin_name}.py")
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError(f"Could not load spec for {plugin_name}") from exc

            # Keep module reference for policy checks
            self._plugin_modules[plugin_name] = module

            # Look for plugin class or main function
            plugin_instance = None

            # Try to find a plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "execute")
                    and attr_name.lower().endswith("plugin")
                ):
                    plugin_instance = attr()
                    break

            # If no plugin class, look for main function
            if not plugin_instance and hasattr(module, "main"):
                plugin_instance = module

            if plugin_instance:
                self.plugins[plugin_name] = plugin_instance
                self.plugin_states[plugin_name] = PluginState.ACTIVE

                # Load metadata
                self._load_plugin_metadata(plugin_name, module)

                # Trigger loaded event
                self._trigger_event("plugin_loaded", plugin_name)

                # Analytics tracking
                self.track_plugin_event(plugin_name, "load_success")

                return True
            else:
                self.plugin_states[plugin_name] = PluginState.ERROR
                return False

        except Exception as e:
            self.plugin_states[plugin_name] = PluginState.ERROR

            # Analytics tracking
            self.track_plugin_event(plugin_name, "load_error", {"error": str(e)})

            print(f"Error loading plugin {plugin_name}: {e}")
            return False

    def _guardian_allows_plugin_load(self, plugin_name: str, *, force_reload: bool = False) -> bool:
        """Authorize a plugin module load before importing untrusted code."""

        plugin_file = Path(self.plugins_dir) / f"{plugin_name}.py"
        intent = IntentDeclaration(
            requester="plugin_manager",
            subsystem="plugin_manager",
            action="plugin.load",
            target=plugin_name,
            purpose="Load plugin module through PluginManager",
            capabilities=("plugin:load",),
            expected_outcome="Plugin module is imported and made available for execution",
            reversible=True,
            rollback_plan="Unload the plugin and remove it from the active plugin registry",
            evidence=(f"plugin:{plugin_name}", f"plugin_file:{plugin_file.name}"),
            metadata={
                "plugin_name": plugin_name,
                "force_reload": bool(force_reload),
                "plugin_file": plugin_file.name,
            },
        )
        if self._apply_plugin_containment(plugin_name, intent):
            return False

        guardian_decision = evaluate_intent(
            intent,
            capability_checker=has_capability,
        )
        if guardian_decision.status in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            return True

        self.plugin_states[plugin_name] = PluginState.DISABLED
        _write_security_audit_entry(
            plugin_name,
            "plugin_denied",
            reason=guardian_decision.reason,
            details={
                "requester": "plugin_manager",
                "capability": "plugin:load",
                "guardian_decision": guardian_decision.to_audit_dict(),
            },
        )
        print(
            f"Guardian denied load for plugin: {plugin_name} "
            f"({guardian_decision.reason})"
        )
        return False

    def _load_plugin_metadata(self, plugin_name: str, module: Any):
        """Load plugin metadata from module attributes."""
        metadata = {
            "name": plugin_name,
            "version": getattr(module, "__version__", "1.0.0"),
            "description": getattr(module, "__doc__", "").strip(),
            "author": getattr(module, "__author__", "Unknown"),
            "dependencies": getattr(module, "__dependencies__", []),
            "tags": getattr(module, "__tags__", []),
            "category": getattr(module, "__category__", "general"),
            "loaded_at": datetime.now().isoformat(),
        }

        self.plugin_metadata[plugin_name] = metadata

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin safely."""
        try:
            if plugin_name not in self.plugins:
                return False

            # Call cleanup if available
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, "cleanup"):
                plugin.cleanup()

            # Remove from plugins
            del self.plugins[plugin_name]
            self.plugin_states[plugin_name] = PluginState.INACTIVE
            if plugin_name in self._plugin_modules:
                del self._plugin_modules[plugin_name]

            # Trigger unloaded event
            self._trigger_event("plugin_unloaded", plugin_name)

            # Analytics tracking
            self.track_plugin_event(plugin_name, "unload")

            return True

        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Execute a plugin with policy, quotas, signing checks, and analytics."""
        intent = IntentDeclaration(
            requester=f"plugin:{plugin_name}",
            subsystem="plugin_manager",
            action="plugin.execute",
            target=plugin_name,
            purpose="Execute plugin through PluginManager",
            capabilities=("execute",),
            reversible=False,
            evidence=(f"plugin:{plugin_name}",),
            metadata={"plugin_name": plugin_name},
        )
        if self._apply_plugin_containment(plugin_name, intent):
            return None

        if plugin_name not in self.plugins and not self.load_plugin(plugin_name):
            return None

        try:
            if _safe_mode_enabled():
                _write_security_audit_entry(
                    plugin_name,
                    "plugin_denied",
                    reason="safe_mode",
                    details={"requester": f"plugin:{plugin_name}", "capability": "execute"},
                )
                print(f"Safe mode denied execution for plugin: {plugin_name}")
                return None

            guardian_decision = evaluate_intent(
                intent,
                capability_checker=has_capability,
            )
            if guardian_decision.status not in {
                GuardianStatus.ALLOW,
                GuardianStatus.ALLOW_LIMITED,
            }:
                _write_security_audit_entry(
                    plugin_name,
                    "plugin_denied",
                    reason=guardian_decision.reason,
                    details={
                        "requester": f"plugin:{plugin_name}",
                        "capability": "execute",
                        "guardian_decision": guardian_decision.to_audit_dict(),
                    },
                )
                print(
                    f"Guardian denied execution for plugin: {plugin_name} "
                    f"({guardian_decision.reason})"
                )
                return None

            plugin = self.plugins[plugin_name]
            module = self._plugin_modules.get(plugin_name)

            # Optional: signing strict mode
            if _plugin_signing_strict_enabled():
                try:
                    manifest = getattr(module, "MANIFEST", None) if module else None
                    if manifest and not verify_plugin_signature(manifest):
                        _write_security_audit_entry(
                            plugin_name,
                            "plugin_denied",
                            reason="signature_verification_failed",
                            details={"strict_signing": True},
                        )
                        print(f"Signing verification failed for plugin: {plugin_name}")
                        return None
                except Exception as exc:
                    _write_security_audit_entry(
                        plugin_name,
                        "plugin_denied",
                        reason="signature_check_failed",
                        details={"strict_signing": True, "error": str(exc)},
                    )
                    print(f"Signing check failed for plugin: {plugin_name}")
                    return None

            # Analytics tracking - start
            start_time = time.time()
            self.track_plugin_event(plugin_name, "execute_start")

            # Quotas
            try:
                max_runtime = float(os.environ.get("AETHERRA_PLUGIN_MAX_RUNTIME_SEC", "5"))
            except Exception:
                max_runtime = 5.0
            max_mb = None
            try:
                if os.environ.get("AETHERRA_PLUGIN_MAX_MEM_MB"):
                    max_mb = float(os.environ.get("AETHERRA_PLUGIN_MAX_MEM_MB", ""))
            except Exception:
                max_mb = None

            def _call():
                if hasattr(plugin, "execute"):
                    return plugin.execute(*args, **kwargs)
                elif hasattr(plugin, "main"):
                    return plugin.main(*args, **kwargs)
                else:
                    return None

            isolation_mode = os.environ.get(
                "AETHERRA_PLUGIN_ISOLATION",
                "process" if _is_production_profile() else "thread",
            ).strip().lower()
            if isolation_mode == "process":
                if IsolatedCallSpec is None or module is None:
                    raise IsolatedExecutionError(
                        "plugin cannot be reconstructed in an isolated worker"
                    )
                callable_name = "execute" if hasattr(plugin, "execute") else "main"
                class_name = (
                    plugin.__class__.__name__ if plugin is not module else None
                )
                module_name = str(getattr(module, "__name__", plugin_name))
                module_path = getattr(module, "__file__", None)
                result = run_isolated(
                    IsolatedCallSpec(
                        module_name=module_name,
                        module_path=str(module_path) if module_path else None,
                        class_name=class_name,
                        callable_name=callable_name,
                    ),
                    args=args,
                    kwargs=kwargs,
                    timeout_sec=max_runtime,
                    max_memory_mb=max_mb,
                )
            elif isolation_mode == "thread":
                ensure_memory_budget(max_mb)
                result = run_with_timeout(_call, timeout_sec=max_runtime)
            else:
                raise IsolatedExecutionError(
                    f"unsupported plugin isolation mode: {isolation_mode}"
                )

            _write_security_audit_entry(
                plugin_name,
                "plugin_executed",
                reason="success",
                details={"runtime_sec": round(time.time() - start_time, 6)},
            )

            # Analytics tracking - success
            execution_time = time.time() - start_time
            self.track_plugin_event(
                plugin_name,
                "execute_success",
                {
                    "execution_time": execution_time,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                },
            )

            return result

        except (
            TimeBudgetExceeded,
            MemoryBudgetExceeded,
            IsolatedExecutionError,
        ) as e:
            _write_security_audit_entry(
                plugin_name,
                "plugin_denied",
                reason="quota_exceeded",
                details={"error": str(e)},
            )
            self.track_plugin_event(plugin_name, "execute_error", {"error": str(e)})
            print(f"Quota violation executing plugin {plugin_name}: {e}")
            return None
        except Exception as e:
            # Analytics tracking - error
            _write_security_audit_entry(
                plugin_name,
                "plugin_denied",
                reason="execution_error",
                details={"error": str(e)},
            )
            self.track_plugin_event(plugin_name, "execute_error", {"error": str(e)})

            print(f"Error executing plugin {plugin_name}: {e}")
            return None

    def _apply_plugin_containment(
        self, plugin_name: str, intent: IntentDeclaration
    ) -> bool:
        """Apply active Guardian containment actions for a plugin intent."""

        containments = active_containments_for_intent(intent)
        if not containments:
            return False
        for containment in containments:
            action = containment.get("action")
            containment_id = containment.get("containment_id")
            if action == ContainmentAction.DISABLE_PLUGIN:
                if plugin_name in self.plugins:
                    self.unload_plugin(plugin_name)
                self.plugin_states[plugin_name] = PluginState.DISABLED
                self._plugin_modules.pop(plugin_name, None)
                _write_security_audit_entry(
                    plugin_name,
                    "plugin_contained",
                    reason="disable_plugin",
                    details={"containment_id": containment_id},
                )
                return True
            if action in {
                ContainmentAction.BLOCK_ACTION,
                ContainmentAction.ISOLATE_SUBSYSTEM,
                ContainmentAction.EMERGENCY_STOP,
            }:
                self.plugin_states[plugin_name] = PluginState.DISABLED
                _write_security_audit_entry(
                    plugin_name,
                    "plugin_contained",
                    reason=str(action),
                    details={"containment_id": containment_id},
                )
                return True
        return False

    def execute_chain(self, user_message: str) -> str:
        """Execute a chain of plugins based on the user message."""
        try:
            # Example logic: iterate through plugins and execute matching ones
            for _plugin_name, plugin in self.plugins.items():
                if hasattr(plugin, "process_message"):
                    response = plugin.process_message(user_message)
                    if response:
                        return response

            # Fallback if no plugin processes the message
            return "No plugin could process the message."
        except Exception as e:
            return f"Error executing plugin chain: {e}"

    def get_plugin_info(self, plugin_name: str) -> Dict:
        """Get comprehensive plugin information."""
        info = {
            "name": plugin_name,
            "state": self.plugin_states.get(plugin_name, PluginState.INACTIVE),
            "loaded": plugin_name in self.plugins,
            "metadata": self.plugin_metadata.get(plugin_name, {}),
            "analytics": {},
        }

        # Add analytics data
        if self.analytics:
            info["analytics"] = self.analytics.get_plugin_analytics(plugin_name)

        return info

    def list_plugins(self) -> Dict[str, Dict]:
        """List all available plugins with their information."""
        discovered = self.discover_plugins()
        plugin_list = {}

        for plugin_name in discovered:
            plugin_list[plugin_name] = self.get_plugin_info(plugin_name)

        return plugin_list

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin completely."""
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)

        return self.load_plugin(plugin_name, force_reload=True)

    def enable_auto_reload(self, check_interval: int = 5):
        """Enable automatic plugin reloading on file changes."""
        self.auto_reload = True

        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(
                target=self._monitor_plugins, args=(check_interval,), daemon=True
            )
            self.monitoring_thread.start()

    def disable_auto_reload(self):
        """Disable automatic plugin reloading."""
        self.auto_reload = False

    def _monitor_plugins(self, check_interval: int):
        """Monitor plugins for file changes."""
        file_times = {}

        while self.auto_reload:
            try:
                for plugin_name in list(self.plugins.keys()):
                    plugin_file = os.path.join(self.plugins_dir, f"{plugin_name}.py")

                    if os.path.exists(plugin_file):
                        current_time = os.path.getmtime(plugin_file)

                        if (
                            plugin_name in file_times
                            and current_time > file_times[plugin_name]
                        ):
                            print(f"Reloading changed plugin: {plugin_name}")
                            self.reload_plugin(plugin_name)

                        file_times[plugin_name] = current_time

                time.sleep(check_interval)

            except Exception as e:
                print(f"Error monitoring plugins: {e}")
                time.sleep(check_interval)

    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def _trigger_event(self, event: str, *args, **kwargs):
        """Trigger an event and call all registered handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler for {event}: {e}")

    def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary."""
        if not self.analytics:
            return {"error": "Analytics not available"}

        return {
            "total_plugins": len(self.discover_plugins()),
            "loaded_plugins": len(self.plugins),
            "plugin_states": dict(self.plugin_states),
            "analytics": self.analytics.get_dashboard_data(),
        }

    def export_configuration(self) -> Dict:
        """Export current plugin configuration."""
        return {
            "plugins_dir": self.plugins_dir,
            "loaded_plugins": list(self.plugins.keys()),
            "plugin_states": dict(self.plugin_states),
            "plugin_metadata": dict(self.plugin_metadata),
            "auto_reload": self.auto_reload,
            "exported_at": datetime.now().isoformat(),
        }

    def import_configuration(self, config: Dict) -> bool:
        """Import plugin configuration."""
        try:
            # Load specified plugins
            for plugin_name in config.get("loaded_plugins", []):
                self.load_plugin(plugin_name)

            # Set auto-reload if specified
            if config.get("auto_reload", False):
                self.enable_auto_reload()

            return True

        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False


# Global plugin manager instance
plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return plugin_manager
