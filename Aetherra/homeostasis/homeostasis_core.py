#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Aetherra Homeostasis Core Controller
========================================

Implements PID-based control loops for autonomous system stability.
Processes metrics from the stability monitoring system and generates
corrective actions to maintain system equilibrium.

The controller implements:
- Damped PID controllers for continuous variables
- Bang-bang/hysteresis controllers for binary states
- Rate limiting and debounce to prevent oscillation
- Policy-driven safety constraints
- Action queuing and execution coordination

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# Third party imports
import yaml

# Aetherra imports
from Aetherra.aetherra_core.system.security_system import (
    is_homeostasis_restricted,
    is_safe_mode_enabled,
)

from .stability_metrics import MetricSnapshot, StabilityMetrics, get_stability_metrics

if TYPE_CHECKING:
    from .homeostasis_actuators import HomeostasisActuators

logger = logging.getLogger(__name__)


class ControllerMode(Enum):
    """Operating modes for the homeostasis controller."""

    OBSERVE_ONLY = "observe_only"
    ADVISORY = "advisory"
    ACTIVE_LIMITED = "active_limited"
    ACTIVE = "active"
    EMERGENCY = "emergency"
    DISABLED = "disabled"


class ActionPriority(Enum):
    """Priority levels for control actions."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ControlAction:
    """Represents a control action to be executed."""

    action_type: str
    target_service: str
    parameters: Dict[str, Any]
    priority: ActionPriority
    timestamp: float
    controller_name: str
    reason: str
    estimated_impact: float = 0.0
    rollback_plan: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    timeout: float = 300.0  # seconds


@dataclass
class ControllerState:
    """State tracking for a single PID controller."""

    metric_name: str
    setpoint: float
    current_value: float
    error: float
    integral_error: float
    derivative_error: float
    last_error: float
    last_update: float
    output: float
    actions_taken: int = 0
    last_action_time: float = 0.0


@dataclass
class ControlLoop:
    """Configuration and state for a control loop."""

    name: str
    metric_name: str
    controller_type: str  # "pid", "bang_bang", "hysteresis"
    setpoint: float
    kp: float = 1.0  # Proportional gain
    ki: float = 0.1  # Integral gain
    kd: float = 0.0  # Derivative gain
    output_min: float = -10.0
    output_max: float = 10.0
    integral_min: float = -10.0
    integral_max: float = 10.0
    deadband: float = 0.1  # Ignore errors smaller than this
    action_threshold: float = 2.0  # Trigger action when |output| > threshold
    max_actions_per_hour: int = 10
    enabled: bool = True
    state: Optional[ControllerState] = None


class HomeostasisController:
    """
    Main homeostasis controller implementing PID and bang-bang control loops
    for autonomous system stability management.
    """

    def __init__(
        self,
        metrics: Optional[StabilityMetrics] = None,
        actuators: Optional["HomeostasisActuators"] = None,
        config_path: Optional[str] = None,
        policy_path: Optional[str] = None,
    ):
        """Initialize the homeostasis controller."""
        self.metrics = metrics or get_stability_metrics()
        self.actuators = actuators

        # Configuration paths
        self.config_path = config_path or "Aetherra/homeostasis/configs/setpoints.yaml"
        self.policy_path = policy_path or "Aetherra/homeostasis/configs/homeostasis_policy.yaml"

        # Load configurations
        self.setpoints = self._load_config(self.config_path)
        self.policy = self._load_config(self.policy_path)

        # Operating state
        self.mode = ControllerMode.OBSERVE_ONLY
        self.running = False
        self.control_loops: Dict[str, ControlLoop] = {}

        # Action management
        self.pending_actions: deque = deque()
        self.action_history: deque = deque(maxlen=1000)
        self.action_counts: Dict[str, List[float]] = defaultdict(list)

        # Timing
        self.control_interval = 30.0  # seconds between control decisions
        self.last_control_time = 0.0
        self.last_metrics_time = 0.0

        # Safety and policy
        self._emergency_stop = False
        self.policy_violations: List[Dict[str, Any]] = []
        self.confirmation_pending: Dict[str, ControlAction] = {}

        # Statistics
        self.stats = {
            "control_cycles": 0,
            "actions_executed": 0,
            "actions_blocked": 0,
            "policy_violations": 0,
            "emergency_stops": 0,
            "mean_time_to_steady_state": 0.0,
        }

        # Initialize control loops
        self._initialize_control_loops()

        logger.info("🧠 Homeostasis controller initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if not isinstance(data, dict):
                        return {}
                    return data
            else:
                logger.warning(f"Config file not found at {config_path}, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}

    def _initialize_control_loops(self):
        """Initialize control loops based on configuration."""
        # Get control parameters from setpoints
        control_params = self.setpoints.get("control_parameters", {})
        pid_gains = control_params.get("pid_gains", {})
        action_thresholds = control_params.get("action_thresholds", {})

        # Default PID gains
        default_kp = pid_gains.get("proportional", 1.0)
        default_ki = pid_gains.get("integral", 0.1)
        default_kd = pid_gains.get("derivative", 0.0)
        default_threshold = action_thresholds.get("low_threshold", 2.0)

        # Create control loops for key metrics
        core_metrics = self.setpoints.get("core_metrics", {})
        cognitive_metrics = self.setpoints.get("cognitive_metrics", {})

        # Core system control loops
        self._create_control_loop(
            "plugin_success_control",
            "plugin_load_success",
            core_metrics.get("plugin_load_success", {}).get("target", 95.0),
            kp=default_kp,
            ki=default_ki,
            kd=default_kd,
            action_threshold=default_threshold,
        )

        self._create_control_loop(
            "memory_rtt_control",
            "memory_rtt",
            core_metrics.get("memory_rtt", {}).get("target", 50.0),
            kp=default_kp * 0.5,
            ki=default_ki,
            kd=default_kd,
            action_threshold=default_threshold,
        )

        self._create_control_loop(
            "task_latency_control",
            "task_latency",
            core_metrics.get("task_latency", {}).get("target", 100.0),
            kp=default_kp * 0.8,
            ki=default_ki,
            kd=default_kd * 2.0,
            action_threshold=default_threshold,
        )

        # Cognitive system control loops
        self._create_control_loop(
            "learning_rate_control",
            "learning_rate",
            cognitive_metrics.get("learning_rate", {}).get("target", 0.01),
            kp=default_kp * 0.1,
            ki=default_ki * 0.1,
            kd=0.0,
            action_threshold=0.5,  # More sensitive for learning rate
        )

        self._create_control_loop(
            "confidence_control",
            "confidence_level",
            cognitive_metrics.get("confidence_level", {}).get("target", 0.8),
            kp=default_kp * 0.5,
            ki=default_ki * 0.5,
            kd=0.0,
            action_threshold=1.0,
        )

        # Service availability bang-bang controllers
        self._create_bang_bang_controller(
            "hub_connection_control",
            "hub_connection",
            1.0,  # target: connected
            action_threshold=0.5,
        )

        self._create_bang_bang_controller(
            "registry_health_control",
            "registry_health",
            1.0,  # target: healthy
            action_threshold=0.5,
        )

        logger.info(f"🔧 Initialized {len(self.control_loops)} control loops")

    def _create_control_loop(
        self,
        name: str,
        metric_name: str,
        setpoint: float,
        kp: float = 1.0,
        ki: float = 0.1,
        kd: float = 0.0,
        action_threshold: float = 2.0,
        max_actions_per_hour: int = 10,
    ):
        """Create a PID control loop."""
        control_loop = ControlLoop(
            name=name,
            metric_name=metric_name,
            controller_type="pid",
            setpoint=setpoint,
            kp=kp,
            ki=ki,
            kd=kd,
            action_threshold=action_threshold,
            max_actions_per_hour=max_actions_per_hour,
            state=ControllerState(
                metric_name=metric_name,
                setpoint=setpoint,
                current_value=setpoint,
                error=0.0,
                integral_error=0.0,
                derivative_error=0.0,
                last_error=0.0,
                last_update=time.time(),
                output=0.0,
            ),
        )

        self.control_loops[name] = control_loop
        logger.debug(f"Created PID control loop: {name} for {metric_name}")

    def _create_bang_bang_controller(
        self,
        name: str,
        metric_name: str,
        setpoint: float,
        action_threshold: float = 0.5,
        max_actions_per_hour: int = 20,
    ):
        """Create a bang-bang (on/off) controller."""
        control_loop = ControlLoop(
            name=name,
            metric_name=metric_name,
            controller_type="bang_bang",
            setpoint=setpoint,
            action_threshold=action_threshold,
            max_actions_per_hour=max_actions_per_hour,
            state=ControllerState(
                metric_name=metric_name,
                setpoint=setpoint,
                current_value=setpoint,
                error=0.0,
                integral_error=0.0,
                derivative_error=0.0,
                last_error=0.0,
                last_update=time.time(),
                output=0.0,
            ),
        )

        self.control_loops[name] = control_loop
        logger.debug(f"Created bang-bang controller: {name} for {metric_name}")

    async def step(self) -> List[ControlAction]:
        """Execute one control step and return generated actions."""
        if self._emergency_stop:
            logger.warning("🚨 Emergency stop active, skipping control step")
            return []

        current_time = time.time()

        # Check if it's time for control action
        if current_time - self.last_control_time < self.control_interval:
            return []

        # Get current metrics
        snapshot = self.metrics.get_current_snapshot()
        if not snapshot:
            logger.debug("No metrics snapshot available, collecting new one")
            snapshot = await self.metrics.collect_snapshot()

        if not snapshot:
            logger.warning("Failed to collect metrics snapshot")
            return []

        # Check operating mode and time windows
        if not self._should_take_action(current_time):
            return []

        self.last_control_time = current_time
        self.last_metrics_time = snapshot.timestamp
        self.stats["control_cycles"] += 1

        # Process all control loops
        actions = []
        for loop_name, control_loop in self.control_loops.items():
            if not control_loop.enabled:
                continue

            loop_actions = await self._process_control_loop(control_loop, snapshot, current_time)
            actions.extend(loop_actions)

        # Filter and prioritize actions
        actions = self._filter_and_prioritize_actions(actions)

        # Apply policy constraints
        actions = self._apply_policy_constraints(actions)

        # Queue actions for execution
        for action in actions:
            self.pending_actions.append(action)

        logger.debug(f"🎛️ Control step generated {len(actions)} actions")
        return actions

    async def _process_control_loop(
        self, control_loop: ControlLoop, snapshot: MetricSnapshot, current_time: float
    ) -> List[ControlAction]:
        """Process a single control loop and generate actions."""
        if not control_loop.state:
            return []

        # Get current metric value
        current_value = getattr(snapshot, control_loop.metric_name, None)
        if current_value is None:
            logger.debug(f"Metric {control_loop.metric_name} not available in snapshot")
            return []

        # Update controller state
        state = control_loop.state
        state.current_value = float(current_value)
        state.error = control_loop.setpoint - state.current_value

        # Check if error is within deadband
        if abs(state.error) < control_loop.deadband:
            state.output = 0.0
            return []

        # Calculate controller output based on type
        if control_loop.controller_type == "pid":
            output = self._calculate_pid_output(control_loop, current_time)
        elif control_loop.controller_type == "bang_bang":
            output = self._calculate_bang_bang_output(control_loop)
        else:
            logger.warning(f"Unknown controller type: {control_loop.controller_type}")
            return []

        state.output = output
        state.last_update = current_time

        # Check if action should be taken
        if abs(output) < control_loop.action_threshold:
            return []

        # Check rate limits
        if not self._check_action_rate_limit(control_loop.name, current_time):
            logger.debug(f"Rate limit exceeded for {control_loop.name}")
            return []

        # Generate appropriate action
        actions = self._generate_actions_for_controller(control_loop, output, current_time)

        # Update action tracking
        if actions:
            state.actions_taken += len(actions)
            state.last_action_time = current_time

        return actions

    def _calculate_pid_output(self, control_loop: ControlLoop, current_time: float) -> float:
        """Calculate PID controller output."""
        state = control_loop.state
        if state is None:
            logger.error(f"ControllerState is None for control loop: {control_loop.name}")
            return 0.0
        dt = current_time - state.last_update

        if dt <= 0:
            dt = 0.1  # Minimum time step

        # Proportional term
        p_term = control_loop.kp * state.error

        # Integral term with clamping
        state.integral_error += state.error * dt
        state.integral_error = max(
            control_loop.integral_min, min(control_loop.integral_max, state.integral_error)
        )
        i_term = control_loop.ki * state.integral_error

        # Derivative term
        if dt > 0:
            state.derivative_error = (state.error - state.last_error) / dt
        else:
            state.derivative_error = 0.0
        d_term = control_loop.kd * state.derivative_error

        # Calculate total output
        output = p_term + i_term + d_term

        # Clamp output
        output = max(control_loop.output_min, min(control_loop.output_max, output))

        # Update state
        state.last_error = state.error

        logger.debug(
            f"PID {control_loop.name}: P={p_term:.3f}, I={i_term:.3f}, D={d_term:.3f}, Out={output:.3f}"
        )

        return output

    def _calculate_bang_bang_output(self, control_loop: ControlLoop) -> float:
        """Calculate bang-bang controller output."""
        state = control_loop.state

        if state is None:
            logger.error(f"ControllerState is None for control loop: {control_loop.name}")
            return 0.0

        if abs(state.error) > control_loop.action_threshold:
            # Full output in direction to correct error
            output = control_loop.output_max if state.error > 0 else control_loop.output_min
        else:
            output = 0.0

        logger.debug(f"Bang-bang {control_loop.name}: Error={state.error:.3f}, Out={output:.3f}")

        return output

    def _check_action_rate_limit(self, controller_name: str, current_time: float) -> bool:
        """Check if controller action rate is within limits."""
        # Clean old timestamps (older than 1 hour)
        hour_ago = current_time - 3600.0
        self.action_counts[controller_name] = [
            t for t in self.action_counts[controller_name] if t > hour_ago
        ]

        # Get rate limit for this controller
        control_loop = self.control_loops.get(controller_name)
        if not control_loop:
            return False

        max_per_hour = control_loop.max_actions_per_hour
        current_count = len(self.action_counts[controller_name])

        return current_count < max_per_hour

    def _generate_actions_for_controller(
        self, control_loop: ControlLoop, output: float, current_time: float
    ) -> List[ControlAction]:
        """Generate specific actions based on controller output."""
        actions = []

        # Map controller outputs to specific actuator actions
        if control_loop.name == "plugin_success_control":
            if output > 0:  # Need to improve plugin success rate
                actions.append(
                    ControlAction(
                        action_type="increase_plugin_timeouts",
                        target_service="plugin_system",
                        parameters={"multiplier": min(2.0, 1.0 + output * 0.1)},
                        priority=ActionPriority.MEDIUM,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason=f"Plugin success rate {control_loop.state.current_value:.1f}% below target {control_loop.setpoint:.1f}%"
                        if control_loop.state is not None
                        else f"Plugin success rate below target {control_loop.setpoint:.1f}%",
                    )
                )
            elif output < -2.0:  # Plugin success is too high, can optimize
                actions.append(
                    ControlAction(
                        action_type="optimize_plugin_timeouts",
                        target_service="plugin_system",
                        parameters={"reduction_factor": 0.9},
                        priority=ActionPriority.LOW,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason=f"Plugin success rate {control_loop.state.current_value:.1f}% allows optimization"
                        if control_loop.state is not None
                        else "Plugin success rate allows optimization",
                    )
                )

        elif control_loop.name == "memory_rtt_control":
            if output > 0:  # Memory RTT too high
                actions.append(
                    ControlAction(
                        action_type="optimize_memory_cache",
                        target_service="memory_system",
                        parameters={"cache_size_multiplier": min(2.0, 1.0 + output * 0.05)},
                        priority=ActionPriority.MEDIUM,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason=f"Memory RTT {control_loop.state.current_value:.1f}ms above target {control_loop.setpoint:.1f}ms"
                        if control_loop.state is not None
                        else f"Memory RTT above target {control_loop.setpoint:.1f}ms",
                    )
                )

        elif control_loop.name == "task_latency_control":
            if output > 0:  # Task latency too high
                actions.append(
                    ControlAction(
                        action_type="increase_task_workers",
                        target_service="kernel_system",
                        parameters={"worker_count_delta": min(3, int(output))},
                        priority=ActionPriority.MEDIUM,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason=f"Task latency {control_loop.state.current_value:.1f}ms above target {control_loop.setpoint:.1f}ms"
                        if control_loop.state is not None
                        else f"Task latency above target {control_loop.setpoint:.1f}ms",
                    )
                )

        elif control_loop.name == "learning_rate_control":
            if abs(output) > 0.1:  # Adjust learning rate
                new_rate = max(0.001, min(0.1, control_loop.setpoint - output * 0.001))
                actions.append(
                    ControlAction(
                        action_type="adjust_learning_rate",
                        target_service="cognitive_system",
                        parameters={"new_learning_rate": new_rate},
                        priority=ActionPriority.LOW,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason=f"Learning rate {control_loop.state.current_value:.4f} needs adjustment"
                        if control_loop.state is not None
                        else "Learning rate needs adjustment",
                    )
                )

        elif control_loop.name == "hub_connection_control":
            if output > 0:  # Hub not connected
                actions.append(
                    ControlAction(
                        action_type="reconnect_hub",
                        target_service="hub_system",
                        parameters={},
                        priority=ActionPriority.HIGH,
                        timestamp=current_time,
                        controller_name=control_loop.name,
                        reason="Hub connection lost",
                    )
                )

        elif control_loop.name == "registry_health_control" and output > 0:  # Registry not healthy
            actions.append(
                ControlAction(
                    action_type="restart_service_registry",
                    target_service="service_registry",
                    parameters={},
                    priority=ActionPriority.HIGH,
                    timestamp=current_time,
                    controller_name=control_loop.name,
                    reason="Service registry unhealthy",
                    requires_confirmation=True,
                )
            )

        return actions

    def _filter_and_prioritize_actions(self, actions: List[ControlAction]) -> List[ControlAction]:
        """Filter duplicate actions and sort by priority."""
        # Remove duplicates based on action_type and target_service
        unique_actions: Dict[Tuple[str, str], ControlAction] = {}
        for action in actions:
            key = (action.action_type, action.target_service)
            if (
                key not in unique_actions
                or action.priority.value > unique_actions[key].priority.value
            ):
                unique_actions[key] = action

        # Sort by priority (highest first)
        sorted_actions = sorted(
            unique_actions.values(), key=lambda a: a.priority.value, reverse=True
        )

        return sorted_actions

    def _apply_policy_constraints(self, actions: List[ControlAction]) -> List[ControlAction]:
        """Apply policy constraints and safety checks to actions."""
        constrained_actions = []

        for action in actions:
            # Check if action is allowed in current mode
            if not self._is_action_allowed(action):
                logger.info(f"🚫 Action blocked by operating mode: {action.action_type}")
                self.stats["actions_blocked"] += 1
                continue

            # Check safety guardrails
            if not self._check_safety_guardrails(action):
                logger.warning(f"⚠️ Action blocked by safety guardrails: {action.action_type}")
                self.stats["actions_blocked"] += 1
                self._record_policy_violation("safety_guardrail", action)
                continue

            # Check human confirmation requirements
            if self._requires_human_confirmation(action):
                action.requires_confirmation = True
                logger.info(f"🤔 Action requires human confirmation: {action.action_type}")

            constrained_actions.append(action)

        return constrained_actions

    def _should_take_action(self, current_time: float) -> bool:
        """Check if actions should be taken based on mode and time windows."""
        if self.mode == ControllerMode.DISABLED:
            return False

        if self.mode == ControllerMode.OBSERVE_ONLY:
            return False

        # Check change windows from policy
        operating_modes = self.setpoints.get("operating_modes", {})
        change_windows = operating_modes.get("change_windows", {})

        # Get current time of day
        current_dt = datetime.fromtimestamp(current_time)
        current_time_str = current_dt.strftime("%H:%M")

        # Check if we're in peak hours (observe only)
        peak_hours = change_windows.get("peak_hours", {})
        if peak_hours:
            start_time = peak_hours.get("start", "09:00")
            end_time = peak_hours.get("end", "17:00")

            if start_time <= current_time_str <= end_time:
                return False  # Observe only during peak hours

        return True

    def _is_action_allowed(self, action: ControlAction) -> bool:
        """Check if action is allowed in current operating mode."""
        if self.mode == ControllerMode.OBSERVE_ONLY:
            return False

        if self.mode == ControllerMode.ADVISORY:
            return False  # Only suggest, don't execute

        if self.mode == ControllerMode.ACTIVE_LIMITED:
            # Check allowed actuators
            operating_modes = self.setpoints.get("operating_modes", {})
            modes = operating_modes.get("modes", {})
            limited_mode = modes.get("active_limited", {})
            allowed_actuators = limited_mode.get("allowed_actuators", [])

            if "all" not in allowed_actuators and action.action_type not in allowed_actuators:
                return False

        return True

    def _check_safety_guardrails(self, action: ControlAction) -> bool:
        """Check action against safety guardrails."""
        safety_guardrails = self.policy.get("safety_guardrails", {})

        # Check never_exceed limits
        never_exceed = safety_guardrails.get("never_exceed", {})

        if action.action_type == "adjust_learning_rate":
            new_rate = action.parameters.get("new_learning_rate", 0.01)
            max_rate = never_exceed.get("max_learning_rate", 0.2)
            min_rate = never_exceed.get("min_learning_rate", 0.0001)

            if new_rate > max_rate or new_rate < min_rate:
                return False

        # Check protected systems
        protected_systems = safety_guardrails.get("protected_systems", [])
        return action.target_service not in protected_systems

    def _requires_human_confirmation(self, action: ControlAction) -> bool:
        """Check if action requires human confirmation."""
        human_confirmation = self.policy.get("human_confirmation", {})
        require_confirmation = human_confirmation.get("require_confirmation", [])

        return any(action.action_type == req.get("action_type") for req in require_confirmation)

    def _record_policy_violation(self, violation_type: str, action: ControlAction):
        """Record a policy violation."""
        violation = {
            "timestamp": time.time(),
            "type": violation_type,
            "action": action.action_type,
            "target": action.target_service,
            "reason": f"Policy violation: {violation_type}",
        }

        self.policy_violations.append(violation)
        self.stats["policy_violations"] += 1

        logger.warning(f"⚠️ Policy violation: {violation}")

    async def execute_pending_actions(self) -> List[Tuple[ControlAction, bool]]:
        """Execute all pending actions and return results."""
        if not self.actuators:
            logger.warning("No actuators available for action execution")
            return []

        results = []

        while self.pending_actions:
            action = self.pending_actions.popleft()

            # Check if action requires confirmation and is pending
            if action.requires_confirmation and action not in self.confirmation_pending.values():
                self.confirmation_pending[action.action_type] = action
                logger.info(f"🤔 Action pending confirmation: {action.action_type}")
                continue

            # Execute action (kernel envelope when available)
            try:
                # Prefer kernel envelope for DLQ/backpressure handling
                exec_method = getattr(self.actuators, "execute_action_via_kernel", None)
                if callable(exec_method):
                    import asyncio as _asyncio  # local to avoid top-level import churn

                    _res = exec_method(action)
                    success = await _res if _asyncio.iscoroutine(_res) else bool(_res)
                else:
                    success = await self.actuators.execute_action(action)
                results.append((action, success))

                if success:
                    self.stats["actions_executed"] += 1
                    self.action_counts[action.controller_name].append(action.timestamp)
                    logger.info(f"✅ Action executed: {action.action_type}")
                else:
                    logger.warning(f"❌ Action failed: {action.action_type}")

                # Record action in history
                self.action_history.append(
                    {
                        "timestamp": action.timestamp,
                        "action_type": action.action_type,
                        "target": action.target_service,
                        "success": success,
                        "controller": action.controller_name,
                        "reason": action.reason,
                    }
                )

            except Exception as e:
                logger.error(f"Error executing action {action.action_type}: {e}")
                results.append((action, False))

        return results

    def set_mode(self, mode: ControllerMode):
        """Set the operating mode of the controller."""
        if is_safe_mode_enabled() or is_homeostasis_restricted():
            logger.warning("🚫 Homeostasis mode change blocked by security restrictions")
            self.mode = ControllerMode.OBSERVE_ONLY
            self.pending_actions.clear()
            return

        old_mode = self.mode
        self.mode = mode
        logger.info(f"🎛️ Controller mode changed: {old_mode.value} → {mode.value}")

        # Clear pending actions if switching to observe mode
        if mode in [ControllerMode.OBSERVE_ONLY, ControllerMode.DISABLED]:
            self.pending_actions.clear()
            logger.info("🧹 Cleared pending actions due to mode change")

    def emergency_stop(self):
        """Trigger emergency stop of all homeostasis actions."""
        if is_safe_mode_enabled() or is_homeostasis_restricted():
            logger.warning("🚫 Homeostasis emergency stop blocked by security restrictions")
            return

        self._emergency_stop = True
        self.pending_actions.clear()
        self.confirmation_pending.clear()
        self.stats["emergency_stops"] += 1

        logger.critical("🚨 EMERGENCY STOP ACTIVATED - All homeostasis actions halted")

    def reset_emergency_stop(self):
        """Reset emergency stop condition."""
        self._emergency_stop = False
        logger.info("✅ Emergency stop reset - Homeostasis can resume")

    def get_controller_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the controller."""
        return {
            "mode": self.mode.value,
            "running": self.running,
            "emergency_stop": self._emergency_stop,
            "control_loops": len(self.control_loops),
            "pending_actions": len(self.pending_actions),
            "confirmation_pending": len(self.confirmation_pending),
            "last_control_time": self.last_control_time,
            "last_metrics_time": self.last_metrics_time,
            "stats": self.stats.copy(),
            "policy_violations": len(self.policy_violations),
        }

    def get_control_loop_status(self) -> Dict[str, Any]:
        """Get detailed status of all control loops."""
        loop_status = {}

        for name, loop in self.control_loops.items():
            state = loop.state
            if state:
                loop_status[name] = {
                    "metric": loop.metric_name,
                    "type": loop.controller_type,
                    "enabled": loop.enabled,
                    "setpoint": loop.setpoint,
                    "current_value": state.current_value,
                    "error": state.error,
                    "output": state.output,
                    "actions_taken": state.actions_taken,
                    "last_action_time": state.last_action_time,
                    "last_update": state.last_update,
                }

        return loop_status

    async def start(self):
        """Start the homeostasis controller."""
        if self.running:
            logger.warning("Controller is already running")
            return

        self.running = True
        self.mode = ControllerMode.ACTIVE  # Start in active mode

        logger.info("🚀 Homeostasis controller started")

        # Main control loop
        while self.running:
            try:
                # Execute control step
                await self.step()

                # Execute pending actions
                await self.execute_pending_actions()

                # Sleep until next control interval
                await asyncio.sleep(self.control_interval)

            except asyncio.CancelledError:
                logger.info("🛑 Controller stopped")
                break
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                await asyncio.sleep(self.control_interval)

    def stop(self):
        """Stop the homeostasis controller."""
        self.running = False
        logger.info("🛑 Homeostasis controller stopping")


if __name__ == "__main__":
    # Test the controller
    import asyncio

    async def test_controller():
        controller = HomeostasisController()
        print(f"Controller status: {controller.get_controller_status()}")
        print(f"Control loops: {controller.get_control_loop_status()}")

    asyncio.run(test_controller())
