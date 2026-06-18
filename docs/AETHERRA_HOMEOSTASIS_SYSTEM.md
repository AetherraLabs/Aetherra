# Aetherra Homeostasis System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Aetherra's Homeostasis System provides autonomous system stability and equilibrium control for the entire
Aetherra OS. Like an autonomic nervous system, it continuously monitors system health, detects drift from
optimal operating conditions, and automatically applies corrective actions to maintain system stability and
ensure reliable operation.

## Completion strategy

Homeostasis must mature in layers. Autonomous correction is useful only after the system can first observe,
diagnose, and recommend clearly.

1. **Observation**: answer what is happening through metrics, health, state, pressure, and risk. No actions.
2. **Diagnosis**: explain why it is happening through bounded causal categories such as memory pressure,
   agent overload, service degradation, trust collapse, or Guardian containment. No actions.
3. **Recommendation**: propose what should be done, with expected impact and risk. No execution.
4. **Controlled Action**: submit recommended actions to Guardian and Security before execution.
5. **Learning**: measure whether corrections worked and improve future recommendations.

Current completion focus: **Phase 5 - Learning**

Completion status: **Functional foundation complete; advanced adaptive optimization remains future work.**

## Architecture overview

The homeostasis system operates on a closed-loop control principle with four primary layers:

- **Sensing Layer**: Continuous metric collection from all system components
- **Analysis Layer**: Trend detection, deviation analysis, and health assessment
- **Control Layer**: PID-based control decisions and corrective action planning
- **Actuation Layer**: Safe execution of corrective actions across system components

Key properties:

- Autonomous operation with minimal human intervention required
- Real-time monitoring and sub-minute response capabilities
- Graceful degradation when monitoring sources are unavailable
- Policy-driven safety constraints preventing destructive actions
- Integration with all major Aetherra subsystems

## Guardian enforcement

Guardian protects the Homeostasis paths that can change operating mode, execute actions, trigger emergency state, or notify/escalate alerts:

- Hub `/api/homeostasis/actuators/execute`, `/mode`, `/emergency_stop`, `/reset_emergency`, and `/rollback` declare Guardian intents before control-plane execution.
- `HomeostasisOrchestrator.set_controller_mode`, `emergency_stop`, and `reset_emergency_stop` also declare Guardian intents directly, so callers below the Hub layer cannot bypass policy.
- `HomeostasisActuators.execute_action` and rollback paths declare Guardian intents before direct actuator mutation or rollback-stack changes.
- `HomeostasisController` autonomous action planning declares Guardian intent before placing corrective actions into the pending-action queue.
- `IntelligentAlertManager` alert escalation and notification dispatch declare Guardian intent before severity/counter changes or outbound notification work.
- Strict capability mode blocks explicit external callers without `homeostasis:control`, `homeostasis:emergency`, `homeostasis:actuate`, `homeostasis:rollback`, `homeostasis:escalate`, or notification capabilities.
- Security, policy, or capability-affecting actuator work requests `security:modify` in addition to Homeostasis capabilities.
- Audit metadata records modes, action types, target services, priorities, parameter keys, alert IDs/severities, and channel names without storing raw actuator parameters or notification payloads.

Remaining Guardian scope:

- Keep future runtime setpoint mutation, adaptive-threshold mutation, sleep-mode control, maintenance-mode toggles, or distributed node control APIs behind Guardian before enabling them.

## Phase 1 - Observation

Implemented files:

- `Aetherra/homeostasis/observation.py`
- `Aetherra/homeostasis/stability_metrics.py`
- Hub endpoint: `GET /api/homeostasis/observation`

Observation is read-only. It does not set controller mode, queue control actions, execute actuators,
trigger emergency state, mutate rollback stacks, write Guardian approvals, or run autonomous correction.

The observation report answers:

- **Metrics**: current observed values for core, cognitive, and service-health signals.
- **Health**: latest health status and score from the metrics collector.
- **State**: controller mode, emergency-stop state, pending action count, supervisor runlevel, and actuator history size.
- **Pressure**: per-metric pressure classification against setpoints: `nominal`, `elevated`, `high`, or `critical`.
- **Risk**: aggregate risk level, bounded score, and contributing factors.

This phase intentionally stops before diagnosis, recommendation, or execution.

## Phase 2 - Diagnosis

Implemented files:

- `Aetherra/homeostasis/diagnosis.py`
- Hub endpoint: `GET /api/homeostasis/diagnosis`

Diagnosis is read-only. It explains likely causes from the observation report without proposing or executing
corrective actions.

The diagnosis report currently uses bounded causal categories:

- `memory_pressure`
- `agent_or_kernel_overload`
- `service_degradation`
- `cognitive_instability`
- `interface_degradation`
- `controller_backlog`
- `emergency_state`
- `guardian_containment`

This phase intentionally stops before recommendation or execution.

## Phase 3 - Recommendation

Implemented files:

- `Aetherra/homeostasis/recommendation.py`
- Hub endpoint: `GET /api/homeostasis/recommendations`

Recommendation is read-only. It suggests bounded actions from diagnosis causes, includes expected impact,
priority, evidence, required capabilities, and an explicit `requires_guardian` flag. It does not execute
actuators or mutate Homeostasis state.

Execution remains reserved for Phase 4, where Guardian reviews and Security enforces the proposed action
before any actuator runs.

## Phase 4 - Controlled Action

Implemented endpoint:

- `POST /api/homeostasis/recommendations/execute`

Controlled action execution requires:

- a current recommendation from the live observation/diagnosis/recommendation chain
- exact `action_type` and `target_service` match
- explicit `confirm_execution: true`
- an executable recommendation requiring `homeostasis:actuate`
- Hub control authorization
- Guardian review immediately before actuator execution
- Security capability enforcement through Guardian's capability checks

This endpoint refuses stale, missing, unconfirmed, or non-actuator recommendations. It does not make
Homeostasis autonomous by default; it provides a controlled bridge from recommendation to action.

## Phase 5 - Learning

Implemented behavior:

- controlled actuator execution records a bounded Guardian outcome through the signed Security audit ledger
- the outcome is linked to the Guardian decision audit ID
- `GET /api/homeostasis/learning` returns a read-only effectiveness summary from signed Guardian decisions and outcomes
- outcome metadata records completion/failure, affected count, rollback state, and bounded numeric metrics
- raw actuator parameters and private runtime payloads are not written to the Guardian audit record

This provides the first learning substrate: Homeostasis can now ask whether a controlled correction worked
by correlating recommendation, Guardian decision, actuator result, and signed outcome audit record. Adaptive
self-tuning remains future work and must stay behind Guardian before activation.

## Completion criteria

Homeostasis is complete for the current foundation milestone when:

- observation answers what is happening without side effects
- diagnosis explains likely causes without action
- recommendation proposes bounded actions without execution
- controlled action requires Hub control auth, explicit confirmation, current recommendation matching, Guardian review, and Security capability enforcement
- controlled actions write signed decision and outcome records
- learning reports summarize signed outcomes without mutating policy or setpoints
- future self-tuning, adaptive threshold mutation, maintenance-mode changes, sleep-mode control, or distributed node control remain disabled or Guardian-gated before activation

## Core components

### 1) Stability Metrics Collection

File: `Aetherra/homeostasis/stability_metrics.py`

The metrics collection system continuously gathers health signals from across the Aetherra ecosystem:

**Core System Metrics:**

- Task throughput and latency (from HMR audit counters)
- Queue depth and processing backlogs
- Memory RTT, timeouts, and error rates
- Exception suppression counters
- Plugin load success rates and timeout frequencies
- Hub connectivity and WebSocket health status
- GUI responsiveness and heartbeat monitoring

**Cognitive System Metrics:**

- Learning rate and cycle time from AI components
- Confidence and uncertainty levels in decision making
- Model fallback rates and cognitive stability indicators
- Reflection system stability and insight generation rates

**Service Availability Metrics:**

- Service registry health and service count tracking
- Kernel loop health and OS runlevel monitoring
- Component heartbeat and lifecycle state tracking

Key APIs:

- `collect_snapshot() -> MetricSnapshot`: Gather complete system state
- `get_metric_trend(metric_name, time_window) -> MetricTrend`: Analyze metric trends
- `get_health_summary() -> dict`: Overall system health assessment
- `start_continuous_collection(interval)`: Background monitoring

### 2) Setpoints Configuration

File: `Aetherra/homeostasis/configs/setpoints.yaml`

Defines target operating parameters and acceptable bounds for all monitored metrics:

**Target Setpoints:**

- Plugin load success ≥ 85% (target: 95%)
- Memory query RTT ≤ 120ms (target: 50ms)
- Task latency p95 ≤ 250ms (target: 100ms)
- Exception suppression trend ≤ +5/hour (target: 0/hour)
- Hub WebSocket reconnects ≤ 3/day (target: 0/day)
- GUI heartbeat interval ≤ 5s (target: 1s)

**Control Parameters:**

- PID controller gains (Kp=1.0, Ki=0.1, Kd=0.05)
- Action thresholds and rate limiting
- Debounce timers and cooldown periods
- Operating mode configurations

### 3) Homeostasis Core Controller

File: `Aetherra/homeostasis/homeostasis_core.py`

The central control system that implements the homeostasis control loop:

**Control Loop Components:**

- Metric ingestion and preprocessing
- Deviation detection from target setpoints
- PID-based control decision making
- Action planning and safety validation
- Execution coordination with actuators

**Key Features:**

- Real-time monitoring with configurable intervals
- Trend analysis and predictive adjustments
- Safety-first action validation
- Graceful degradation handling
- Comprehensive logging and audit trails

Primary APIs:

- `start_homeostasis()`: Initialize continuous control loop
- `process_control_cycle()`: Execute single control iteration
- `evaluate_system_health()`: Assess current system state
- `plan_corrective_actions()`: Generate action plans for deviations
- `execute_actions()`: Coordinate action execution with actuators

### 4) System Actuators

File: `Aetherra/homeostasis/homeostasis_actuators.py`

Safe execution mechanisms for corrective actions across system components:

**Available Actuators:**

- **Service Management**: Restart services, adjust service parameters
- **Resource Tuning**: Memory cache adjustments, connection pool sizing
- **Performance Optimization**: Plugin reload, garbage collection triggers
- **Network Management**: Connection resets, timeout adjustments
- **Cognitive Tuning**: Learning rate adjustments, confidence thresholds
- **Emergency Actions**: Service isolation, graceful degradation modes

**Safety Features:**

- Pre-action validation and impact assessment
- Rate limiting and cooldown enforcement
- Rollback capabilities for reversible actions
- Dry-run mode for testing action plans
- Comprehensive audit logging

Key APIs:

- `execute_action(action_plan) -> ActionResult`: Execute validated actions
- `validate_action_safety(action) -> bool`: Pre-execution safety checks
- `get_available_actuators() -> list`: List of available action types
- `simulate_action_impact(action) -> dict`: Predict action effects

### 5) Intelligent Alert Management

File: `Aetherra/homeostasis/intelligent_alert_manager.py`

Advanced alerting system with context-aware notification and escalation:

**Alert Processing:**

- Real-time alert generation from metric deviations
- Context correlation and root cause analysis
- Alert prioritization and de-duplication
- Intelligent escalation based on severity and trends

**Notification Channels:**

- System logs with structured formatting
- Service registry integration for component notifications
- Hub-based alerting for external systems
- Lyrixa integration for natural language alerts

### 6) Night-Cycle Intelligence Integration

File: `Aetherra/homeostasis/night_cycle_integration.py`

Strategic Enhancement #5: Optimized resource allocation during low-activity periods:

**Intelligence Features:**

- Activity pattern recognition and prediction
- Intelligent resource redistribution during quiet periods
- Background optimization and predictive maintenance scheduling
- Sleep-mode coordination with configurable wake-up triggers
- Circadian rhythm alignment for optimal resource utilization

**Optimization Capabilities:**

- Scheduled maintenance during low-activity windows
- Predictive resource scaling based on usage patterns
- Energy-efficient operation modes
- Background cleanup and optimization tasks

### 7) Audit and Compliance Layer

File: `Aetherra/homeostasis/audit_trace_layer.py`

Comprehensive audit trail and compliance monitoring:

**Audit Features:**

- Complete action audit trails with timestamps
- Metric collection history and analysis
- Control decision rationale logging
- Performance impact tracking
- Compliance reporting and validation

**Compliance Monitoring:**

- SLO adherence tracking
- Policy compliance validation
- Security constraint enforcement
- Regulatory requirement monitoring

### 8) Multi-Node Coordination

File: `Aetherra/homeostasis/multi_node_coordination.py`

Distributed homeostasis across multiple Aetherra instances:

**Coordination Features:**

- Cross-node health state synchronization
- Distributed control decision making
- Load balancing and failover coordination
- Cluster-wide policy enforcement

## Integration points

### Service Registry Integration

The homeostasis system integrates deeply with the Aetherra Service Registry:

- Automatic discovery of monitoring targets
- Service health state reporting
- Dynamic actuator capability registration
- Cross-service coordination for complex actions

### Memory System Integration

Coordination with the Aetherra Memory System:

- Memory performance monitoring
- Query optimization based on usage patterns
- Cache warming during low-activity periods
- Memory leak detection and prevention

### Hub Connectivity Monitoring

Integration with the Aetherra Hub:

- WebSocket connection health monitoring
- API endpoint availability tracking
- Network latency and throughput monitoring
- External service dependency tracking

### AI Engine Coordination

Integration with cognitive systems:

- Learning rate optimization based on system load
- Confidence threshold adjustments
- Model performance monitoring
- Cognitive resource allocation optimization

## Configuration and policies

### Setpoints Configuration

The `setpoints.yaml` configuration defines:

- Target values and acceptable ranges for all metrics
- Control parameters and PID tuning
- Action thresholds and safety limits
- Operating mode definitions and change windows

### Policy Framework

File: `Aetherra/homeostasis/configs/homeostasis_policy.yaml`

Defines safety constraints and operational policies:

- Action authorization and validation rules
- Rate limiting and cooldown requirements
- Emergency escalation procedures
- Audit and compliance requirements

## Operating modes

### Observe-Only Mode

- Monitor metrics but take no corrective actions
- Generate alerts and recommendations only
- Used during system debugging and analysis

### Advisory Mode

- Generate action recommendations without execution
- Provide impact analysis and risk assessments
- Support human decision-making processes

### Active Limited Mode

- Execute safe, non-disruptive actions only
- Focus on performance tuning and optimization
- Avoid actions that could impact system availability

### Full Active Mode

- Complete autonomous operation with all actuators
- Real-time corrective actions across all system components
- Maximum system stability and performance optimization

## Monitoring and observability

### Health Dashboards

The homeostasis system provides comprehensive monitoring:

- Real-time metric visualization and trend analysis
- System health scoring and status indicators
- Alert history and escalation tracking
- Action execution results and impact analysis

### Metrics and Telemetry

Key observability features:

- Prometheus-compatible metric exposition
- Structured logging with correlation IDs
- Performance impact measurement
- Historical trend analysis and reporting

### Audit and Compliance Reporting

Comprehensive audit capabilities:

- Complete action audit trails
- Control decision rationale documentation
- SLO adherence and deviation reporting
- Compliance validation and certification support

## Implementation status

Current implementation state:

- ✅ Core metrics collection and analysis
- ✅ Phase 1 Observation report and read-only Hub API
- ✅ Phase 2 Diagnosis report and read-only Hub API
- ✅ Phase 3 Recommendation report and read-only Hub API
- ✅ Phase 4 Controlled recommendation execution with Guardian review
- ✅ Phase 5 Outcome correlation for controlled actions
- ✅ Phase 5 Learning report over signed Guardian outcomes
- ✅ Setpoints configuration and validation
- ✅ Basic PID control loop implementation
- ✅ Safety-validated actuator framework
- ✅ Intelligent alert management
- ✅ Night-cycle intelligence integration
- ✅ Comprehensive audit and compliance layer
- ✅ Multi-node coordination capabilities
- 🔄 Advanced predictive analytics (in development)
- 🔄 Machine learning-based optimization (planned)

## Troubleshooting

### Action Failures During Normal Operation

If you see repeated action failures in the console output like:

```text
❌ Action failed: reconnect_hub
❌ Action failed: increase_task_workers  
❌ Action failed: optimize_plugin_timeouts
```

This is **normal behavior** during development and indicates:

1. **Active Monitoring**: The homeostasis system is detecting potential optimization opportunities
2. **Action Gaps**: Some actuator implementations are still being developed
3. **System Health**: The overall system remains "HEALTHY" despite individual action failures

**Solutions:**

- **For Development**: This is expected behavior and doesn't indicate system problems
- **For Production**: Consider switching to "observe_only" or "advisory" mode in `setpoints.yaml`
- **For Debugging**: Check actuator implementations in `homeostasis_actuators.py`

### Service Degradation Alerts

When services show degraded status:

```text
Service 'aetherra_hub' status: healthy -> degraded
Failed vital checks: hub_link
```

This indicates:

1. **Heartbeat Issues**: Service hasn't reported health within expected timeframe (180s)
2. **Network Problems**: Connectivity issues between components
3. **Resource Constraints**: Service may be under heavy load

**Solutions:**

- Check service logs for specific error details
- Verify network connectivity between components
- Monitor resource usage (CPU, memory, disk)
- Consider restarting affected services if issues persist

### Memory Engine Initialization Messages

Frequent memory engine initialization messages:

```text
[OK] QuantumEnhancedMemoryEngine initialized
```

This is **normal operation** and indicates:

- Memory system is properly initializing connections
- Quantum-enhanced features are loading correctly
- System is maintaining memory subsystem health

## Design goals

- **Autonomy**: Minimal human intervention required for stable operation
- **Safety**: Fail-safe design with comprehensive validation and rollback
- **Performance**: Sub-minute response times with real-time monitoring
- **Reliability**: Graceful degradation and fault tolerance
- **Observability**: Complete visibility into system behavior and decisions
- **Compliance**: Full audit trails and policy enforcement
- **Integration**: Seamless coordination with all Aetherra subsystems

## Summary

The Aetherra Homeostasis System represents a critical foundation for autonomous OS operation, ensuring system stability,  
performance, and reliability through continuous monitoring and intelligent corrective actions.
