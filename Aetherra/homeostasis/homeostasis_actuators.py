#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎛️ Aetherra Homeostasis Actuators
===================================

Implements idempotent system adjustment operations for the homeostasis system.
Provides safe, reversible actions that can be taken to correct system drift
and maintain stability across all Aetherra components.

The actuators interface with:
- Plugin orchestrator for plugin management
- Memory system for configuration adjustments
- Model system for fallback switching
- Hub for connectivity management
- Service registry for service operations
- Kernel for task and resource management

All actions are designed to be:
- Idempotent (safe to repeat)
- Auditable (fully logged)
- Reversible (rollback plans)
- Policy-compliant (safety checked)

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

# Third party imports
import yaml

# Aetherra imports
from aetherra_service_registry import get_service_registry

from .audit_trace_layer import get_audit_layer

logger = logging.getLogger(__name__)


@dataclass
class ActuatorResult:
    """Result of an actuator action."""

    success: bool
    message: str
    rollback_data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    side_effects: Optional[List[str]] = None


class HomeostasisActuators:
    """
    Provides idempotent system adjustment operations for homeostasis control.

    All actuator methods are designed to be safe, repeatable, and reversible.
    Each action includes comprehensive logging and rollback capabilities.
    """

    def __init__(self, policy_path: Optional[str] = None):
        """Initialize the homeostasis actuators."""
        self.policy_path = policy_path or "Aetherra/homeostasis/configs/homeostasis_policy.yaml"
        self.policy = self._load_policy()

        # Track action history for rollback
        self.action_history: List[Dict[str, Any]] = []
        self.rollback_stack: List[Dict[str, Any]] = []

        # Cache for service registry and other frequently accessed services
        self._registry_cache: Optional[Any] = None
        self._cache_expire_time: float = 0.0
        self._cache_duration: float = 30.0  # seconds

        logger.info("🎛️ Homeostasis actuators initialized")

    def _load_policy(self) -> Dict[str, Any]:
        """Load policy configuration from YAML file."""
        try:
            policy_file = Path(self.policy_path)
            if policy_file.exists():
                with open(policy_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    if not isinstance(data, dict):
                        logger.warning(
                            f"Policy file at {self.policy_path} did not contain a mapping; using defaults"
                        )
                        return {}
                    return cast(Dict[str, Any], data)
            else:
                logger.warning(f"Policy file not found at {self.policy_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Failed to load policy from {self.policy_path}: {e}")
            return {}

    async def _get_service_registry(self) -> Optional[Any]:
        """Get service registry with caching."""
        current_time = time.time()
        if self._registry_cache and current_time < self._cache_expire_time:
            return self._registry_cache

        try:
            registry = await get_service_registry()
            self._registry_cache = registry
            self._cache_expire_time = current_time + self._cache_duration
            return registry
        except Exception as e:
            logger.debug(f"Failed to get service registry: {e}")
            return None

    def _record_action(
        self, action_type: str, target: str, parameters: Dict[str, Any], result: ActuatorResult
    ):
        """Record action in history for audit and rollback."""
        action_record = {
            "timestamp": time.time(),
            "action_type": action_type,
            "target": target,
            "parameters": parameters.copy(),
            "success": result.success,
            "message": result.message,
            "rollback_data": result.rollback_data,
            "execution_time": result.execution_time,
        }

        self.action_history.append(action_record)

        # If successful and has rollback data, add to rollback stack
        if result.success and result.rollback_data:
            self.rollback_stack.append(action_record)

        logger.info(
            f"📝 Recorded action: {action_type} on {target} - {'✅' if result.success else '❌'}"
        )

    def _guardian_requester(self, action: Any | None = None) -> str:
        requester = None
        if action is not None:
            requester = getattr(action, "guardian_requester", None) or getattr(
                action, "requester", None
            )
        return str(requester or "homeostasis").strip() or "homeostasis"

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "homeostasis" and capability in {
            "homeostasis:actuate",
            "homeostasis:rollback",
            "security:modify",
        }:
            return True
        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_capabilities_for_action(self, action: Any) -> tuple[str, ...]:
        action_type = str(getattr(action, "action_type", "") or "")
        target_service = str(getattr(action, "target_service", "") or "")
        capabilities = ["homeostasis:actuate"]
        target_lower = f"{target_service} {action_type}".lower()
        if any(marker in target_lower for marker in ("security", "policy", "capability")):
            capabilities.append("security:modify")
        return tuple(capabilities)

    def _guardian_preflight_action(self, action: Any) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        action_type = str(getattr(action, "action_type", "") or "").strip()
        target_service = str(getattr(action, "target_service", "") or "").strip()
        parameters = getattr(action, "parameters", {}) or {}
        if not isinstance(parameters, dict):
            parameters = {}
        priority = getattr(getattr(action, "priority", None), "name", None) or str(
            getattr(action, "priority", "unknown")
        )
        controller_name = str(getattr(action, "controller_name", "") or "homeostasis")
        reason = str(getattr(action, "reason", "") or "")

        decision = evaluate_intent(
            IntentDeclaration(
                requester=self._guardian_requester(action),
                subsystem="homeostasis",
                action="homeostasis.actuate",
                target="homeostasis:actuator",
                purpose=reason or f"Execute homeostasis actuator {action_type}",
                capabilities=self._guardian_capabilities_for_action(action),
                evidence=(
                    f"homeostasis_action:{action_type}",
                    f"target_service:{target_service or 'system'}",
                ),
                reversible=True,
                rollback_plan="use homeostasis actuator rollback or restore previous service state",
                metadata={
                    "action_type": action_type,
                    "target_service": target_service,
                    "priority": str(priority).lower(),
                    "controller_name": controller_name,
                    "parameter_keys": tuple(sorted(str(key) for key in parameters)),
                    "reason_present": bool(reason.strip()),
                    "requires_confirmation": bool(
                        getattr(action, "requires_confirmation", False)
                    ),
                },
            ),
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied Homeostasis actuator action {action_type}: {decision.reason}"
            )

    def _guardian_preflight_rollback(self, requester: str = "homeostasis") -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        decision = evaluate_intent(
            IntentDeclaration(
                requester=str(requester or "homeostasis"),
                subsystem="homeostasis",
                action="homeostasis.rollback",
                target="homeostasis:actuator_history",
                purpose="Rollback the most recent Homeostasis actuator action",
                capabilities=("homeostasis:rollback",),
                evidence=("rollback_last_action",),
                reversible=True,
                rollback_plan="inspect action history and re-run the reverted actuator if rollback was unsafe",
                metadata={"rollback_stack_depth": len(self.rollback_stack)},
            ),
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"Guardian denied Homeostasis actuator rollback: {decision.reason}"
            )

    async def execute_action(self, action) -> bool:
        """Execute a control action with comprehensive audit tracing."""
        self._guardian_preflight_action(action)
        start_time = time.time()
        audit_layer = get_audit_layer()

        # Get pre-action metrics for audit trail
        pre_action_metrics = {}
        try:
            # Collect current system state for correlation analysis
            pre_action_metrics = {
                "timestamp": time.time(),
                "memory_usage": 0.0,  # Would be populated by actual metrics
                "stability_score": 0.5,  # Placeholder
                "error_rate": 0.0,
                "system_load": 0.0,
            }
        except Exception as e:
            logger.warning(f"Could not collect pre-action metrics: {e}")

        # Start audit trace
        trace_id = await audit_layer.start_action_trace(
            action_type=action.action_type,
            target_service=action.target_service,
            parameters=action.parameters,
            priority=action.priority.name,
            controller_name=action.controller_name,
            reason=action.reason,
            controller_state={
                "estimated_impact": action.estimated_impact,
                "timeout": action.timeout,
                "requires_confirmation": action.requires_confirmation,
            },
            pre_action_metrics=pre_action_metrics,
        )

        try:
            # Route to appropriate actuator method
            if action.action_type == "increase_plugin_timeouts":
                result = await self.adjust_plugin_timeouts(action.target_service, action.parameters)
            elif action.action_type == "optimize_plugin_timeouts":
                result = await self.optimize_plugin_timeouts(
                    action.target_service, action.parameters
                )
            elif action.action_type == "optimize_memory_cache":
                result = await self.optimize_memory_cache(action.target_service, action.parameters)
            elif action.action_type == "increase_task_workers":
                result = await self.adjust_task_workers(action.target_service, action.parameters)
            elif action.action_type == "adjust_learning_rate":
                result = await self.adjust_learning_rate(action.target_service, action.parameters)
            elif action.action_type == "reconnect_hub":
                result = await self.reconnect_hub(action.target_service, action.parameters)
            elif action.action_type == "restart_service_registry":
                result = await self.restart_service(action.target_service, action.parameters)
            else:
                result = ActuatorResult(
                    success=False, message=f"Unknown action type: {action.action_type}"
                )

            result.execution_time = time.time() - start_time

            # Collect post-action metrics
            post_action_metrics = {}
            try:
                post_action_metrics = {
                    "timestamp": time.time(),
                    "memory_usage": 0.0,  # Would be populated by actual metrics
                    "stability_score": 0.5,  # Placeholder
                    "error_rate": 0.0,
                    "system_load": 0.0,
                }
            except Exception as e:
                logger.warning(f"Could not collect post-action metrics: {e}")

            # Complete audit trace
            await audit_layer.complete_action_trace(
                trace_id=trace_id,
                success=result.success,
                message=result.message,
                rollback_data=result.rollback_data,
                immediate_effects={
                    "execution_time": result.execution_time,
                    "side_effects": result.side_effects or [],
                },
                post_action_metrics=post_action_metrics,
            )

            # Record action for traditional audit and rollback
            self._record_action(
                action.action_type, action.target_service, action.parameters, result
            )

            return result.success

        except Exception as e:
            # Complete audit trace with error
            await audit_layer.complete_action_trace(
                trace_id=trace_id,
                success=False,
                message=f"Execution error: {str(e)}",
                immediate_effects={"error": str(e)},
            )

            logger.error(f"Error executing action {action.action_type}: {e}")
            return False

    async def execute_action_via_kernel(self, action) -> bool:
        """Execute an action using the kernel task envelope when available.

        Falls back to direct execute_action if kernel submission isn't available.
        """
        try:
            # Local import to avoid hard dependency at module import time
            from aetherra_kernel_loop import get_kernel  # type: ignore

            kernel = get_kernel()
            # Map action priority to kernel queue priority
            priority = "normal"
            try:
                from .homeostasis_core import ActionPriority  # type: ignore

                pr = getattr(action, "priority", None)
                if pr in (ActionPriority.CRITICAL, ActionPriority.EMERGENCY, ActionPriority.HIGH):
                    priority = "high"
                elif pr == ActionPriority.LOW:
                    priority = "background"
                else:
                    priority = "normal"
            except Exception:
                priority = "normal"

            # Submit and wait for result (boolean ok)
            res = await kernel.submit_actuator_action_and_wait(
                action_type=getattr(action, "action_type", ""),
                target_service=getattr(action, "target_service", ""),
                parameters=getattr(action, "parameters", {}) or {},
                controller_name=getattr(action, "controller_name", "homeostasis"),
                reason=getattr(action, "reason", "kernel_envelope"),
                timeout_sec=float(getattr(action, "timeout", 0) or 0),
                priority=priority,
            )
            if isinstance(res, dict) and "ok" in res:
                return bool(res.get("ok"))
            return bool(res)
        except Exception as e:
            logger.debug(f"[ACT] Kernel submission unavailable, executing directly: {e}")
            return await self.execute_action(action)

    # Plugin System Actuators

    async def adjust_plugin_timeouts(
        self, target: str, parameters: Dict[str, Any]
    ) -> ActuatorResult:
        """Adjust plugin timeout values to improve success rates."""
        try:
            multiplier = parameters.get("multiplier", 1.5)
            if multiplier <= 0 or multiplier > 5.0:
                return ActuatorResult(
                    success=False, message=f"Invalid timeout multiplier: {multiplier}"
                )

            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find plugin-related services
            plugin_services = []
            for service_name, service_info in registry.services.items():
                if "plugin" in service_name.lower():
                    plugin_services.append((service_name, service_info))

            if not plugin_services:
                return ActuatorResult(success=True, message="No plugin services found to adjust")

            # Adjust timeouts for each plugin service
            adjusted_services = []
            rollback_data: Dict[str, Any] = {"original_timeouts": {}}

            for service_name, service_info in plugin_services:
                if hasattr(service_info.instance, "timeout_config"):
                    current_timeout = getattr(
                        service_info.instance.timeout_config, "default_timeout", 30.0
                    )
                    new_timeout = current_timeout * multiplier

                    # Store original for rollback
                    rollback_data["original_timeouts"][service_name] = current_timeout

                    # Apply new timeout
                    service_info.instance.timeout_config.default_timeout = new_timeout
                    adjusted_services.append(service_name)

                    logger.debug(
                        f"Adjusted timeout for {service_name}: {current_timeout} → {new_timeout}"
                    )

            if adjusted_services:
                return ActuatorResult(
                    success=True,
                    message=f"Adjusted timeouts for {len(adjusted_services)} plugin services",
                    rollback_data=rollback_data,
                )
            else:
                return ActuatorResult(success=True, message="No plugin timeouts needed adjustment")

        except Exception as e:
            return ActuatorResult(success=False, message=f"Failed to adjust plugin timeouts: {e}")

    async def optimize_plugin_timeouts(
        self, target: str, parameters: Dict[str, Any]
    ) -> ActuatorResult:
        """Optimize plugin timeouts by reducing them when success rates are high."""
        try:
            reduction_factor = parameters.get("reduction_factor", 0.9)
            if reduction_factor <= 0.5 or reduction_factor >= 1.0:
                return ActuatorResult(
                    success=False, message=f"Invalid reduction factor: {reduction_factor}"
                )

            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find plugin services with high success rates
            optimized_services = []
            rollback_data: Dict[str, Any] = {"original_timeouts": {}}

            for service_name, service_info in registry.list_services().items():
                if (
                    "plugin" in service_name.lower()
                    and service_info.status.value == "healthy"
                    and hasattr(service_info.instance, "timeout_config")
                ):
                    current_timeout = getattr(
                        service_info.instance.timeout_config, "default_timeout", 30.0
                    )
                    new_timeout = max(5.0, current_timeout * reduction_factor)  # Minimum 5 seconds

                    # Store original for rollback
                    rollback_data["original_timeouts"][service_name] = current_timeout

                    # Apply optimized timeout
                    service_info.instance.timeout_config.default_timeout = new_timeout
                    optimized_services.append(service_name)

                    logger.debug(
                        f"Optimized timeout for {service_name}: {current_timeout} → {new_timeout}"
                    )

            # Return success even if no services were optimized (nothing to do is OK)
            if not optimized_services:
                return ActuatorResult(
                    success=True,
                    message="No plugin services with timeout_config found to optimize",
                )

            return ActuatorResult(
                success=True,
                message=f"Optimized timeouts for {len(optimized_services)} plugin services",
                rollback_data=rollback_data,
            )

        except Exception as e:
            logger.warning(f"Failed to optimize plugin timeouts: {e}", exc_info=True)
            return ActuatorResult(success=False, message=f"Failed to optimize plugin timeouts: {e}")

    # Memory System Actuators

    async def optimize_memory_cache(
        self, target: str, parameters: Dict[str, Any]
    ) -> ActuatorResult:
        """Optimize memory system cache configuration."""
        try:
            cache_size_multiplier = parameters.get("cache_size_multiplier", 1.5)
            if cache_size_multiplier <= 0 or cache_size_multiplier > 3.0:
                return ActuatorResult(
                    success=False, message=f"Invalid cache size multiplier: {cache_size_multiplier}"
                )

            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find memory system service
            engine_service = registry.get_service_info("aetherra_engine")
            if not engine_service or not engine_service.instance:
                return ActuatorResult(success=False, message="Aetherra engine service not found")

            memory_system = getattr(engine_service.instance, "memory_system", None)
            if not memory_system:
                return ActuatorResult(success=False, message="Memory system not found in engine")

            # Adjust cache configuration
            rollback_data: Dict[str, Any] = {"original_cache_config": {}}

            if hasattr(memory_system, "cache_config"):
                cache_config = memory_system.cache_config

                # Store original values for rollback
                original_size = getattr(cache_config, "max_cache_size", 1000)
                rollback_data["original_cache_config"]["max_cache_size"] = original_size

                # Apply new cache size
                new_size = int(original_size * cache_size_multiplier)
                cache_config.max_cache_size = new_size

                logger.debug(f"Adjusted memory cache size: {original_size} → {new_size}")

                return ActuatorResult(
                    success=True,
                    message=f"Optimized memory cache size from {original_size} to {new_size}",
                    rollback_data=rollback_data,
                )
            else:
                return ActuatorResult(
                    success=True, message="Memory system does not support cache optimization"
                )

        except Exception as e:
            return ActuatorResult(success=False, message=f"Failed to optimize memory cache: {e}")

    # Task and Kernel Actuators

    async def adjust_task_workers(self, target: str, parameters: Dict[str, Any]) -> ActuatorResult:
        """Adjust the number of task workers to manage latency."""
        try:
            worker_count_delta = parameters.get("worker_count_delta", 1)
            if abs(worker_count_delta) > 5:
                return ActuatorResult(
                    success=False, message=f"Worker count delta too large: {worker_count_delta}"
                )

            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find kernel or task management service
            kernel_service = registry.get_service_info("aetherra_kernel")
            if not kernel_service or not kernel_service.instance:
                # Service doesn't exist - not a failure, just nothing to do
                return ActuatorResult(
                    success=True, message="Kernel service not found - no workers to adjust"
                )

            kernel_instance = kernel_service.instance

            # Adjust worker pool if available
            if hasattr(kernel_instance, "task_pool_config"):
                pool_config = kernel_instance.task_pool_config
                current_workers = getattr(pool_config, "max_workers", 4)
                new_workers = max(1, min(16, current_workers + worker_count_delta))

                rollback_data = {"original_worker_count": current_workers}

                pool_config.max_workers = new_workers

                logger.debug(f"Adjusted task workers: {current_workers} → {new_workers}")

                return ActuatorResult(
                    success=True,
                    message=f"Adjusted task workers from {current_workers} to {new_workers}",
                    rollback_data=rollback_data,
                )
            else:
                # Kernel exists but doesn't support worker adjustment - success with info
                return ActuatorResult(
                    success=True, message="Kernel does not support worker adjustment"
                )

        except Exception as e:
            logger.warning(f"Failed to adjust task workers: {e}", exc_info=True)
            return ActuatorResult(success=False, message=f"Failed to adjust task workers: {e}")

    # Cognitive System Actuators

    async def adjust_learning_rate(self, target: str, parameters: Dict[str, Any]) -> ActuatorResult:
        """Adjust learning rate for cognitive systems."""
        try:
            new_learning_rate = parameters.get("new_learning_rate", 0.01)

            # Safety check
            if new_learning_rate < 0.0001 or new_learning_rate > 0.2:
                return ActuatorResult(
                    success=False, message=f"Learning rate outside safe bounds: {new_learning_rate}"
                )

            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find cognitive/learning services
            engine_service = registry.get_service_info("aetherra_engine")
            if not engine_service or not engine_service.instance:
                return ActuatorResult(success=False, message="Aetherra engine service not found")

            engine_instance = engine_service.instance

            # Adjust learning rate if supported
            if hasattr(engine_instance, "learning_config"):
                learning_config = engine_instance.learning_config
                current_rate = getattr(learning_config, "learning_rate", 0.01)

                rollback_data = {"original_learning_rate": current_rate}

                learning_config.learning_rate = new_learning_rate

                logger.debug(f"Adjusted learning rate: {current_rate} → {new_learning_rate}")

                return ActuatorResult(
                    success=True,
                    message=f"Adjusted learning rate from {current_rate} to {new_learning_rate}",
                    rollback_data=rollback_data,
                )
            else:
                return ActuatorResult(
                    success=True, message="Engine does not support learning rate adjustment"
                )

        except Exception as e:
            return ActuatorResult(success=False, message=f"Failed to adjust learning rate: {e}")

    # Hub and Connectivity Actuators

    async def reconnect_hub(self, target: str, parameters: Dict[str, Any]) -> ActuatorResult:
        """Reconnect to the Aetherra Hub."""
        try:
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            # Find Hub service
            hub_service = registry.get_service_info("aetherra_hub")
            if not hub_service or not hub_service.instance:
                # Hub not found - not a failure if it's not registered
                return ActuatorResult(
                    success=True, message="Hub service not found in registry - nothing to reconnect"
                )

            hub_instance = hub_service.instance

            # Attempt reconnection if supported
            if hasattr(hub_instance, "reconnect"):
                await hub_instance.reconnect()

                # Give it a moment to establish connection
                await asyncio.sleep(2.0)

                # Check connection status
                if hasattr(hub_instance, "is_connected") and hub_instance.is_connected():
                    return ActuatorResult(success=True, message="Successfully reconnected to Hub")
                else:
                    return ActuatorResult(
                        success=False,
                        message="Reconnection attempted but connection not established",
                    )
            else:
                # Hub exists but doesn't support reconnect - success with info
                return ActuatorResult(
                    success=True, message="Hub service does not support reconnection"
                )

        except Exception as e:
            logger.warning(f"Failed to reconnect Hub: {e}", exc_info=True)
            return ActuatorResult(success=False, message=f"Failed to reconnect Hub: {e}")

    # Service Management Actuators

    async def restart_service(self, target: str, parameters: Dict[str, Any]) -> ActuatorResult:
        """Restart a specific service."""
        try:
            # This is a high-impact action, proceed carefully
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            service_info = registry.get_service_info(target)
            if not service_info:
                return ActuatorResult(success=False, message=f"Service not found: {target}")

            # Store pre-restart state for rollback
            rollback_data = {
                "service_name": target,
                "pre_restart_status": service_info.status.value,
                "restart_time": time.time(),
            }

            # Attempt service restart
            if hasattr(service_info.instance, "restart"):
                await service_info.instance.restart()

                # Wait for restart to complete
                await asyncio.sleep(5.0)

                # Check if service is back online
                updated_service = registry.get_service_info(target)
                if updated_service and updated_service.status.value == "HEALTHY":
                    return ActuatorResult(
                        success=True,
                        message=f"Successfully restarted service: {target}",
                        rollback_data=rollback_data,
                    )
                else:
                    return ActuatorResult(
                        success=False,
                        message=f"Service restart completed but service not healthy: {target}",
                    )
            else:
                return ActuatorResult(
                    success=False, message=f"Service does not support restart: {target}"
                )

        except Exception as e:
            return ActuatorResult(success=False, message=f"Failed to restart service {target}: {e}")

    # Rollback and Recovery

    async def rollback_last_action(self) -> ActuatorResult:
        """Rollback the last successful action."""
        self._guardian_preflight_rollback()
        if not self.rollback_stack:
            return ActuatorResult(success=False, message="No actions available for rollback")

        try:
            last_action = self.rollback_stack.pop()
            action_type = last_action["action_type"]
            rollback_data = last_action["rollback_data"]

            if not rollback_data:
                return ActuatorResult(
                    success=False, message=f"No rollback data available for action: {action_type}"
                )

            # Perform rollback based on action type
            if action_type in ["increase_plugin_timeouts", "optimize_plugin_timeouts"]:
                return await self._rollback_plugin_timeouts(rollback_data)
            elif action_type == "optimize_memory_cache":
                return await self._rollback_memory_cache(rollback_data)
            elif action_type == "adjust_task_workers":
                return await self._rollback_task_workers(rollback_data)
            elif action_type == "adjust_learning_rate":
                return await self._rollback_learning_rate(rollback_data)
            else:
                return ActuatorResult(
                    success=False, message=f"Rollback not implemented for action: {action_type}"
                )

        except Exception as e:
            return ActuatorResult(success=False, message=f"Failed to rollback action: {e}")

    async def _rollback_plugin_timeouts(self, rollback_data: Dict[str, Any]) -> ActuatorResult:
        """Rollback plugin timeout changes."""
        try:
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            original_timeouts = rollback_data.get("original_timeouts", {})
            restored_count = 0

            for service_name, original_timeout in original_timeouts.items():
                service_info = registry.get_service_info(service_name)
                if service_info and hasattr(service_info.instance, "timeout_config"):
                    service_info.instance.timeout_config.default_timeout = original_timeout
                    restored_count += 1

            return ActuatorResult(
                success=True, message=f"Rolled back timeouts for {restored_count} services"
            )

        except Exception as e:
            return ActuatorResult(success=False, message=f"Rollback failed: {e}")

    async def _rollback_memory_cache(self, rollback_data: Dict[str, Any]) -> ActuatorResult:
        """Rollback memory cache changes."""
        try:
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            engine_service = registry.get_service_info("aetherra_engine")
            if not engine_service:
                return ActuatorResult(success=False, message="Engine service not found")

            memory_system = getattr(engine_service.instance, "memory_system", None)
            if not memory_system or not hasattr(memory_system, "cache_config"):
                return ActuatorResult(success=False, message="Memory cache config not found")

            original_config = rollback_data.get("original_cache_config", {})
            original_size = original_config.get("max_cache_size")

            if original_size:
                memory_system.cache_config.max_cache_size = original_size
                return ActuatorResult(
                    success=True, message=f"Rolled back memory cache size to {original_size}"
                )

            return ActuatorResult(success=False, message="No original cache size found")

        except Exception as e:
            return ActuatorResult(success=False, message=f"Rollback failed: {e}")

    async def _rollback_task_workers(self, rollback_data: Dict[str, Any]) -> ActuatorResult:
        """Rollback task worker changes."""
        try:
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            kernel_service = registry.get_service_info("aetherra_kernel")
            if not kernel_service:
                return ActuatorResult(success=False, message="Kernel service not found")

            original_count = rollback_data.get("original_worker_count")
            if original_count and hasattr(kernel_service.instance, "task_pool_config"):
                kernel_service.instance.task_pool_config.max_workers = original_count
                return ActuatorResult(
                    success=True, message=f"Rolled back worker count to {original_count}"
                )

            return ActuatorResult(success=False, message="Cannot rollback worker count")

        except Exception as e:
            return ActuatorResult(success=False, message=f"Rollback failed: {e}")

    async def _rollback_learning_rate(self, rollback_data: Dict[str, Any]) -> ActuatorResult:
        """Rollback learning rate changes."""
        try:
            registry = await self._get_service_registry()
            if not registry:
                return ActuatorResult(success=False, message="Service registry not available")

            engine_service = registry.get_service_info("aetherra_engine")
            if not engine_service:
                return ActuatorResult(success=False, message="Engine service not found")

            original_rate = rollback_data.get("original_learning_rate")
            if original_rate and hasattr(engine_service.instance, "learning_config"):
                engine_service.instance.learning_config.learning_rate = original_rate
                return ActuatorResult(
                    success=True, message=f"Rolled back learning rate to {original_rate}"
                )

            return ActuatorResult(success=False, message="Cannot rollback learning rate")

        except Exception as e:
            return ActuatorResult(success=False, message=f"Rollback failed: {e}")

    # Status and Monitoring

    def get_actuator_status(self) -> Dict[str, Any]:
        """Get status of the actuator system."""
        return {
            "actions_executed": len(self.action_history),
            "rollback_actions_available": len(self.rollback_stack),
            "last_action_time": self.action_history[-1]["timestamp"]
            if self.action_history
            else None,
            "policy_loaded": bool(self.policy),
            "registry_cache_valid": self._cache_expire_time > time.time(),
        }

    def get_action_history(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history."""
        return self.action_history[-count:] if self.action_history else []

    def clear_rollback_stack(self):
        """Clear the rollback stack (use with caution)."""
        cleared_count = len(self.rollback_stack)
        self.rollback_stack.clear()
        logger.info(f"🧹 Cleared {cleared_count} rollback actions")


if __name__ == "__main__":
    # Test the actuators
    import asyncio

    async def test_actuators():
        actuators = HomeostasisActuators()
        print(f"Actuator status: {actuators.get_actuator_status()}")

    asyncio.run(test_actuators())
