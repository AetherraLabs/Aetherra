# 🧬 Aetherra Homeostasis System

**Autonomous System Stability and Equilibrium Control**

The Aetherra Homeostasis System provides autonomous system stability and equilibrium control for the entire Aetherra OS. Like an autonomic nervous system, it continuously monitors system health, detects drift from optimal operating conditions, and automatically applies corrective actions to maintain system stability.

## 🎯 Core Purpose

**"When the OS is running, all systems are running and performing their tasks"** continuously and safely, with automatic correction if any metric drifts past bounds.

## 🏗️ Architecture

The homeostasis system is built on a layered design with four main components:

### 1. 🔍 Sensing (Stability Metrics)
**File**: `stability_metrics.py`

Continuously ingests metrics from across the system:
- **Core**: Task throughput/latency, queue depth, memory RTT/timeouts, exception counters, plugin load success, Hub connectivity, GUI heartbeat
- **Cognitive**: Learning rate & cycle time, confidence/uncertainty, model fallbacks, reflection stability
- **Sources**: Service registry, self-improvement engine, plugin system, memory system, Hub connectivity, GUI systems

### 2. 🎯 Setpoints (Target Configuration)
**File**: `configs/setpoints.yaml`

Defines target bands and SLOs for all monitored metrics:
- Plugin load success ≥ 85%
- Memory query timeout p95 ≤ 120ms
- Exception-suppression trend ≤ +5/hour
- Hub WS reconnects ≤ 1/24h
- GUI heartbeat ≤ 5s
- Learning rate optimal range: 0.001-0.1

### 3. 🧠 Controllers (Control Logic)
**File**: `homeostasis_core.py`

Implements PID and bang-bang controllers:
- **PID Controllers**: For continuous variables (learning rate, timeouts, cache sizes)
- **Bang-Bang Controllers**: For binary states (service restarts, connection recovery)
- **Rate Limiting**: Debounce and cooldown to prevent oscillation
- **Policy Enforcement**: Safety constraints and human confirmation requirements

### 4. 🎛️ Actuators (System Actions)
**File**: `homeostasis_actuators.py`

Executes idempotent corrective actions:
- **Plugin Management**: Adjust timeouts, restart failed plugins, modify concurrency
- **Memory Optimization**: Switch storage modes, tune cache sizes, adjust retry budgets
- **Model Management**: Fallback to alternative providers, load shedding during high demand
- **Hub/IO**: Trigger reconnections, adjust stream frequencies, toggle background tasks
- **Service Management**: Restart unhealthy services, modify resource allocation

### 5. 🎯 Supervision (System Health)
**File**: `system_supervisor.py`

Manages system runlevels and service availability:
- **Runlevels**: BOOTING → DEGRADED → ONLINE → DRAINING → OFFLINE
- **Service Monitoring**: Tracks health of all critical services
- **Automatic Recovery**: Restarts failed services within policy limits
- **Health Publishing**: Reports system state to Lyrixa dashboards

## 🚀 Getting Started

### Installation and Setup

The homeostasis system is automatically integrated into Aetherra OS. To manually initialize:

```python
from Aetherra.homeostasis import start_homeostasis_system

# Start the complete homeostasis system
orchestrator = await start_homeostasis_system()

# Check system health
health = await orchestrator.get_system_health_status()
print(f"System health: {health['supervisor']['system_health']['runlevel']}")
```

### Configuration

Edit the configuration files in `Aetherra/homeostasis/configs/`:

1. **setpoints.yaml**: Adjust target values and control parameters
2. **homeostasis_policy.yaml**: Modify safety rules and operational policies

### Operating Modes

The system operates in several modes:

- **Observe Only**: Monitor metrics but take no actions
- **Advisory**: Suggest actions but don't execute them
- **Active Limited**: Execute safe, non-disruptive actions only
- **Active**: Full homeostasis control with all actuators
- **Emergency**: Immediate safety actions only

```python
# Change operating mode
await orchestrator.set_controller_mode(ControllerMode.ACTIVE_LIMITED)

# Emergency stop
await orchestrator.emergency_stop("Manual intervention required")
```

## 📊 Monitoring and Observability

### Health Dashboard Integration

The homeostasis system publishes health data to Lyrixa dashboards:

- Current setpoints vs actual values
- Control decisions and action history
- Cooldown timers and rate limits
- Policy compliance status

### Metrics and Alerts

Key metrics to monitor:

- **Mean Time to Steady State (MTSS)**: Target < 5 minutes
- **Action Success Rate**: Target > 95%
- **False Positive Rate**: Target < 5%
- **Policy Violation Count**: Target = 0

### Debugging and Troubleshooting

```python
# Get comprehensive status
status = await orchestrator.get_system_health_status()

# View recent actions
actions = await orchestrator.get_action_history(20)

# Force metrics collection
snapshot = await orchestrator.force_metric_collection()

# Export health report
report_path = await orchestrator.export_health_report()
```

## 🛡️ Safety and Governance

### Safety Guardrails

The system includes comprehensive safety measures:

- **Protected Systems**: Security sandbox, authentication, encryption keys never under homeostasis control
- **Rate Limits**: Maximum actions per minute/hour to prevent oscillation
- **Bounds Checking**: Learning rate, timeout multipliers, worker counts within safe ranges
- **Human Confirmation**: Destructive operations require manual approval

### Policy Framework

All actions are governed by policies defined in `homeostasis_policy.yaml`:

- **Risk Levels**: Low/Medium/High/Critical with appropriate approval workflows
- **Emergency Conditions**: Automatic halt triggers for safety
- **Audit Requirements**: Full logging and retention policies
- **Rollback Capability**: All actions can be reversed

### Emergency Procedures

```python
# Emergency stop (halts all homeostasis actions)
await orchestrator.emergency_stop("Security incident detected")

# Reset after resolving issue
await orchestrator.reset_emergency_stop()

# Rollback last action if needed
success = await orchestrator.rollback_last_action()
```

## 🧪 Testing and Validation

### Unit Tests

Run the homeostasis test suite:

```bash
# Run all homeostasis tests
pytest tests/unit/homeostasis/ -v

# Run specific test categories
pytest tests/unit/homeostasis/test_homeostasis_basic.py -v
```

### Integration Testing

The system includes failure injection tests to validate auto-recovery:

- Memory system offline scenarios
- Plugin timeout spike simulation
- Hub connection drop testing
- Model fallback verification

### Simulation Mode

Test control decisions without taking real actions:

```python
# Enable simulation mode
controller.set_mode(ControllerMode.ADVISORY)

# Review suggested actions
actions = await controller.step()
for action in actions:
    print(f"Would execute: {action.action_type} - {action.reason}")
```

## 🔧 Development and Extension

### Adding New Metrics

1. Add metric collection to `stability_metrics.py`
2. Define setpoints in `setpoints.yaml`
3. Create control loop in `homeostasis_core.py`
4. Implement actuators in `homeostasis_actuators.py`

### Custom Actuators

```python
class CustomActuator(HomeostasisActuators):
    async def custom_action(self, target: str, parameters: dict) -> ActuatorResult:
        # Implement custom system adjustment
        return ActuatorResult(success=True, message="Custom action completed")
```

### Policy Extensions

Extend the policy framework in `homeostasis_policy.yaml`:

```yaml
action_policies:
  custom_system:
    allow_automatic_adjustment: true
    max_adjustment_factor: 2.0
    require_confirmation: false
```

## 🤝 Integration Points

### Lyrixa Integration

- Health status publishing to dashboards
- User notification for manual confirmations
- Operating mode synchronization

### Hub Coordination

- Plugin action synchronization
- System health reporting
- Maintenance window coordination

### Service Registry

- Service health monitoring
- Dependency management
- Restart coordination

## 📈 Performance and Scaling

### Resource Usage

- **CPU**: Low impact, ~1-2% during normal operation
- **Memory**: ~50MB for metric buffers and control state
- **Network**: Minimal, only for service communication
- **Storage**: Config files (~100KB) plus audit logs

### Scaling Considerations

- Metric collection scales with number of monitored services
- Control loops are independent and can be disabled individually
- Action rate limits prevent system overload

## 🔍 Troubleshooting

### Common Issues

**Q: Homeostasis not taking any actions**
A: Check operating mode (`get_controller_status()`) and ensure system is in `ACTIVE` mode

**Q: Actions being blocked**
A: Review policy violations in status output and check safety guardrails

**Q: Metrics not collecting**
A: Verify service registry connectivity and service health

**Q: Emergency stop triggered**
A: Check logs for trigger condition and resolve underlying issue before reset

### Debug Logging

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger("Aetherra.homeostasis").setLevel(logging.DEBUG)
```

## 📚 References

- [Aetherra Memory System](../docs/AETHERRA_MEMORY_SYSTEM.md)
- [Aetherra Kernel System](../docs/AETHERRA_KERNEL_SYSTEM.md)
- [Service Registry Documentation](../docs/SERVICE_REGISTRY.md)
- [System Architecture Overview](../docs/PROJECT_OVERVIEW.md)

## 📄 License

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

---

**Aetherra Homeostasis System** - Keeping your AI OS stable and resilient 🧬✨
