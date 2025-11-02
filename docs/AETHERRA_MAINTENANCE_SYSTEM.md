# Aetherra Maintenance System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Aetherra's Maintenance System provides autonomous system stability, continuous improvement, and adaptive evolution for the entire Aetherra OS. Like a self-healing organism with adaptive intelligence, it continuously monitors system health, learns from operational patterns, discovers and integrates new capabilities, and automatically maintains optimal system performance without human intervention.

The Maintenance System is composed of three integrated subsystems working in harmony:

- **Homeostasis System**: Real-time stability control and error correction
- **Self-Improvement Engine**: Pattern analysis and optimization proposal generation
- **Self-Incorporation Service**: Code discovery, classification, and safe integration

Together, these systems form a complete autonomous loop that ensures Aetherra remains stable, performant, and continuously evolving.

**For detailed Self-Improvement API documentation**, see [AETHERRA_SELF_IMPROVEMENT_API.md](./AETHERRA_SELF_IMPROVEMENT_API.md).

## Architecture overview

The Maintenance System operates as a closed-loop autonomous control system with three primary layers:

- **Stability Layer (Homeostasis)**: Real-time monitoring, error detection, and immediate corrective actions
- **Intelligence Layer (Self-Improvement)**: Pattern analysis, trend detection, and improvement proposal generation
- **Evolution Layer (Self-Incorporation)**: Code discovery, security evaluation, and safe capability integration

Key properties:

- Fully autonomous operation with zero human intervention required
- Real-time monitoring with sub-second error detection and correction
- Continuous learning from system performance and operational patterns
- Safe code integration with multi-tier trust model and ethics evaluation
- Complete audit trail for all actions and decisions
- Graceful degradation when components are unavailable
- Policy-driven safety constraints preventing destructive actions
- Integration with all major Aetherra subsystems

## System integration flow

```
┌──────────────────────────────────────────────────────────────┐
│                  AETHERRA MAINTENANCE SYSTEM                  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              HOMEOSTASIS SYSTEM                         │  │
│  │  • Collects metrics (15+ types)                        │  │
│  │  • Detects errors in real-time                         │  │
│  │  • Applies immediate fixes                             │  │
│  │  • Monitors system health                              │  │
│  └────────┬────────────────────────────────────┬──────────┘  │
│           │ Forwards metrics                   │              │
│           │ every 60s                          │ Reports      │
│           ↓                                    │ health       │
│  ┌────────────────────────────────────────────┴──────────┐  │
│  │         SELF-IMPROVEMENT ENGINE                        │  │
│  │  • Analyzes performance patterns                       │  │
│  │  • Identifies optimization opportunities               │  │
│  │  • Generates improvement proposals                     │  │
│  │  • Tracks trends and anomalies                         │  │
│  └────────┬───────────────────────────────────────────────┘  │
│           │ Sends proposals                                   │
│           │ for evaluation                                    │
│           ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SELF-INCORPORATION SERVICE                     │  │
│  │  • Discovers code in project                          │  │
│  │  • Classifies by type and risk                        │  │
│  │  • Evaluates safety and ethics                        │  │
│  │  • Integrates approved capabilities                   │  │
│  │  • Night cycle learning during idle                   │  │
│  └────────┬───────────────────────────────────────────────┘  │
│           │ Forwards insights                                 │
│           │ and integration metrics                           │
│           ↓                                                   │
│         (Back to Homeostasis)                                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Boot sequence

The Maintenance System is initialized during OS startup in a coordinated sequence:

**Phase 2: System Loading**

1. Self-Improvement Engine loads and starts analysis cycle
2. Self-Incorporation Service loads with configuration
3. Self-Repair Service loads (legacy support)
4. Homeostasis System loads all 8 phases

**Phase 3: System Injection**

1. Kernel loop initialized with core systems
2. HMR controller wired for hot-swap capabilities
3. Self-Incorporation receives references to service registry, kernel, plugin manager, and agent orchestrator

**Phase 4: System Activation**

1. Memory and plugin systems activate
2. Homeostasis starts all 8 phases (including error correction and metrics bridge)
3. Self-Incorporation starts and triggers initial code discovery scan
4. All systems mark themselves as healthy in service registry

## Core components

### 1) Homeostasis System (Stability Layer)

File: `Aetherra/homeostasis/homeostasis_integration.py`

The Homeostasis System maintains system stability through 8 coordinated phases:

**Phase 1: Stability Metrics Collection**

- Continuous gathering of health signals from all Aetherra components
- Plugin load success rates, memory RTT, task latency, hub connectivity
- Exception rates, queue depths, service availability
- Collects 15+ metric types every monitoring cycle

**Phase 2: Adaptive Controller**

- PID-based control decisions for corrective actions
- Calculates deviation from target setpoints
- Determines appropriate response magnitudes
- Rate-limits actions to prevent oscillation

**Phase 3: Multi-Level Actuators**

- Executes corrective actions across system components
- Plugin reload, memory cleanup, task prioritization
- Service restart, resource allocation adjustments
- Graceful degradation when actuators unavailable

**Phase 4: Supervisor & Health Monitoring**

- Maintains global system health score (0.0-1.0)
- Tracks OS runlevel and component states
- Aggregates health from all subsystems
- Provides unified health API for dashboards

**Phase 5: Feedback Loop**

- Validates effectiveness of corrective actions
- Adjusts controller parameters based on outcomes
- Learns optimal response strategies
- Tracks action success rates

**Phase 6: Validation & Observability**

- Comprehensive metrics export for monitoring
- Action effectiveness tracking
- Performance statistics and trends
- Integration with observability platforms

**Phase 7: Autonomous Error Correction**

File: `Aetherra/homeostasis/autonomous_error_corrector.py`

Real-time log monitoring and automatic error correction:

- Custom logging handler captures all WARNING+ messages
- Pattern-based detection for 6 error categories:
  - Service registration API mismatches
  - Deprecated module imports
  - Missing Python modules
  - Missing system capabilities
  - Plugin load failures
  - Expected data file missing
- Intelligent cooldown (5-10 minutes) prevents fix spam
- Automatic fix handlers for each error type
- Statistics tracking: detected, attempted, successful, failed

Key APIs:

- `start()`: Begin log monitoring and background processing
- `stop()`: Clean shutdown of monitoring
- `get_statistics()`: Retrieve correction statistics
- `process_log_message(record)`: Analyze log entry for errors

**Phase 8: Self-Improvement Metrics Bridge**

File: `Aetherra/homeostasis/self_improvement_metrics_bridge.py`

Data pipeline from homeostasis to self-improvement engine:

- Polls homeostasis metrics every 60 seconds
- Forwards 15+ metrics to self-improvement engine:
  - `plugin_load_success`: Plugin loading success rate
  - `memory_rtt`: Memory system response time
  - `task_latency`: Task processing latency
  - `hub_connection`: Hub connectivity health
  - `controller_active`: Controller operational state
  - `actions_executed`: Corrective actions taken
  - `system_health_score`: Overall system health (0.0-1.0)
  - `effectiveness_*`: 5 effectiveness metrics from validator
  - `errors_detected`: Error correction detections
  - `fixes_successful`: Successful auto-fixes
  - `fix_success_rate`: Fix effectiveness percentage
- Statistics tracking: metrics_forwarded, forward_failures, success_rate

Key APIs:

- `start()`: Begin metrics collection and forwarding
- `stop()`: Clean shutdown
- `get_status()`: Bridge health and statistics
- `_collect_homeostasis_metrics()`: Gather current metrics
- `_forward_metrics()`: Send to self-improvement engine

### 2) Self-Improvement Engine (Intelligence Layer)

File: `Aetherra/aetherra_core/engine/self_improvement_engine.py`

The Self-Improvement Engine provides continuous learning and optimization through pattern analysis:

**Metrics Collection**

- Receives performance metrics from homeostasis bridge every 60 seconds
- Stores metrics history with timestamps for trend analysis
- Maintains rolling window of recent performance data
- Tracks metric trends, anomalies, and patterns

**Pattern Analysis**

- Analyzes metrics every 5 minutes for patterns
- Identifies performance trends (improving, degrading, stable)
- Detects anomalies and outliers
- Correlates metrics to find relationships
- Calculates statistical measures (mean, variance, percentiles)

**Improvement Generation**

- Generates optimization proposals based on patterns:
  - `scale_up`: Increase resource allocation when performance degrading
  - `optimize`: Fine-tune parameters when inefficiencies detected
  - `degrade`: Reduce resource usage when overprovisioned
  - `change_strategy`: Switch approaches when current strategy suboptimal
- Includes rationale, confidence score, and supporting evidence
- Prioritizes proposals by impact and feasibility

**Strategy Library**

- Repository of proven improvement patterns
- Successful strategies learned from past actions
- Context-aware strategy selection
- Continuous refinement based on outcomes

Key APIs:

- `record_performance_metric(name, value, unit, context)`: Add metric
- `get_improvement_status()`: Current state and proposals
- `get_metric_trends(metric_name, time_window)`: Trend analysis
- `start_improvement_cycle(loop)`: Begin continuous analysis
- `stop_improvement_cycle()`: Clean shutdown

**Message API (Service Registry)**

- `selfimprovement.record_metric`: Receive metrics from other systems
- `selfimprovement.status`: Get engine state and proposals
- `selfimprovement.trends`: Retrieve metric trends

### 3) Self-Incorporation Service (Evolution Layer)

File: `aetherra_self_incorporation.py`

The Self-Incorporation Service provides autonomous code discovery, evaluation, and safe integration:

**Code Discovery**

Component: `CodeIndex`

- Scans project roots for Python files (configurable paths)
- Tracks file hash (SHA-256), size, modification time
- Identifies entry points and code structure
- Stores in dual format: SQLite database + JSONL backup
- Incremental scanning detects new/modified files

**Heuristic Classification**

Component: `HeuristicClassifier`

- Analyzes code to determine type and purpose
- Classification types:
  - `PLUGIN`: Aetherra plugin modules
  - `AGENT`: Agent implementations
  - `AETHER`: Aether script files
  - `WORKFLOW`: Workflow definitions
  - `UTILITY`: Helper/utility code
  - `DATASET`: Data files and datasets
  - `DOCS`: Documentation files
  - `UNKNOWN`: Unclassified items
- Confidence scoring (0.0-1.0) for classification quality
- Feature extraction: imports, classes, functions, patterns

**Policy & Safety Gate**

Components: `PolicyEngine`, `SecurityGate`, `SafetyIndex`

- Policy engine enforces integration policies from JSON configuration
- Security gate analyzes risk factors:
  - Dangerous imports (subprocess, eval, exec, network)
  - File system operations
  - Network access patterns
  - Code execution capabilities
  - External command invocation
- Trust tier assignment:
  - `VERIFIED`: Signed by Aetherra Labs, full trust
  - `TRUSTED`: Known good, reviewed and approved
  - `STANDARD`: Default trust, standard checks
  - `EXPERIMENTAL`: Unproven code, extra scrutiny
  - `QUARANTINED`: Suspicious or blocked
- Safety decisions stored with rationale and risk scores

**Integration Planning**

Component: `IntegrationPlanner`

- Creates integration plans from classified and approved code
- Conflict detection:
  - Duplicate capability names
  - Namespace collisions
  - Version incompatibilities
  - Dependency conflicts
- Generates integration actions:
  - `load_plugin`: Load plugin into plugin manager
  - `register_agent`: Register agent with orchestrator
  - `import_utility`: Import utility module
  - `execute_workflow`: Run aether workflow
  - `index_dataset`: Index data for retrieval
- Prioritizes actions by dependencies and risk

**Core Integration**

Component: `CoreIntegrator`

- Executes integration plans safely
- Hot-swap capabilities via HMR controller
- Rollback support with unique tokens
- Validates integration success
- Reports outcomes to audit ledger

**Ethics & Audit**

Components: `EthicsEngine`, `AuditLedger`

- Ethics evaluation using multiple frameworks:
  - Utilitarian: Maximum benefit, minimum harm
  - Deontological: Rule-based ethical principles
  - Virtue ethics: Character and excellence focus
  - Care ethics: Relationship and empathy focus
- Evaluates ethical implications of integrations
- Risk factor identification (privacy, security, autonomy)
- Benefit analysis (capability enhancement, performance)
- Complete audit trail in SQLite database
- Immutable record of all actions and decisions

**Quarantine Management**

Component: `QuarantineManager`

- Isolates suspicious or untrusted code
- Policy-based quarantine triggers
- Manual review interface for quarantined items
- Recovery and reintegration workflow
- Statistics tracking for quarantine events

**Night Cycle Learning**

Component: `NightCycleProcessor`

Autonomous learning during system idle periods:

- **7-Phase Night Cycle:**
  1. `INACTIVE`: Waiting for idle trigger
  2. `MONITORING`: Watching for user activity
  3. `DISCOVERY_ANALYSIS`: Analyzing discovered code
  4. `PATTERN_LEARNING`: Learning from code patterns
  5. `OPTIMIZATION`: Optimizing integrations
  6. `VALIDATION`: Validating learned patterns
  7. `REPORTING`: Generating insights report

- User activity detection:
  - Last interaction timestamp
  - CPU usage monitoring
  - Memory usage patterns
  - Network activity levels
  - Idle threshold: 30+ minutes no activity

- Learning insights generation:
  - Code quality patterns
  - Performance optimization opportunities
  - Security vulnerability patterns
  - Common integration conflicts
  - Best practices identification

Key APIs:

- `start()`: Start service and register with service registry
- `stop()`: Clean shutdown
- `inject_systems(registry, kernel, plugins, agents)`: Inject core systems
- `trigger_scan(root_filter)`: Discover code in project roots
- `trigger_classify(type_filter)`: Classify discovered items
- `trigger_security_eval(trust_filter)`: Evaluate code safety
- `trigger_planning(experimental)`: Create integration plan
- `trigger_integrate(plan_id)`: Execute integration plan
- `trigger_rollback(token)`: Rollback integration
- `get_status()`: Service health and metrics
- `health_check()`: Detailed health status

**Configuration**

Component: `SelfIncorporationConfig`

Default settings:

```python
enabled = True
roots = [Path("."), Path("Aetherra")]  # Project roots to scan
trust_mode = "standard"  # or "strict", "permissive"
index_db_path = Path("data/selfinc_index.db")
audit_db_path = Path("data/selfinc_audit.db")
```

Policy file: `config/self_incorporation_policy.json`

## Data flows

### Current operational flows

**Homeostasis → Self-Improvement**

- **Frequency**: Every 60 seconds
- **Method**: Phase 8 Metrics Bridge
- **Data**: 15+ metrics (stability, performance, health, errors)
- **Direction**: Homeostasis polls own metrics → forwards to SI Engine via service registry messages
- **Purpose**: Provides performance data for pattern analysis and improvement proposals

**Homeostasis → Error Correction**

- **Frequency**: Real-time (every log message)
- **Method**: Phase 7 Log Monitor (custom logging.Handler)
- **Data**: WARNING+ log messages
- **Direction**: Python logging system → Error Corrector → Fix handlers
- **Purpose**: Immediate error detection and automatic correction

### Planned flows (Phase 2)

**Self-Incorporation → Self-Improvement**

- **Frequency**: Every 60 seconds (planned)
- **Method**: Phase 9 Metrics Bridge (to be implemented)
- **Data**: Discovery metrics, classification success, integration stats, night cycle insights
- **Direction**: Self-Incorporation → SI Engine via service registry messages
- **Purpose**: Inform SI Engine about code evolution and integration effectiveness

**Self-Improvement → Self-Incorporation**

- **Frequency**: On proposal generation (as needed)
- **Method**: Proposal consumer in Self-Incorporation (to be implemented)
- **Data**: Improvement proposals (scale_up, optimize, integrate_capability, etc.)
- **Direction**: SI Engine → Self-Incorporation via service registry messages
- **Purpose**: Execute optimization proposals safely through integration pipeline

**Self-Incorporation → Homeostasis**

- **Frequency**: Every 60 seconds (planned)
- **Method**: Extended Phase 8 Bridge
- **Data**: Self-Incorporation health metrics, quarantine status, integration success rate
- **Direction**: Self-Incorporation → Homeostasis metrics
- **Purpose**: Include Self-Incorporation health in overall system health score

## Operational modes

The Maintenance System operates in coordinated modes across all three subsystems:

### Normal mode (default)

- Homeostasis monitors continuously with standard thresholds
- Self-Improvement analyzes every 5 minutes
- Self-Incorporation performs daily scheduled scans
- Night cycle learning during detected idle periods
- Full audit trail enabled
- Standard safety policies enforced

### Quiet mode (`AETHERRA_QUIET=1`)

- Reduced logging verbosity
- Faster stabilization delays (0.5s vs 2.0s)
- Error correction continues silently
- Metrics bridge operates normally
- Suitable for automated testing and CI/CD

### Strict mode (`AETHERRA_PROFILE=prod`)

- Enhanced security policies
- All integrations require manual approval
- Trust mode set to "strict"
- Network allowlisting enforced
- Audit ledger required for all actions
- Suitable for production environments

### Test mode (`AETHERRA_PROFILE=test`)

- Relaxed thresholds for faster testing
- Mock fallbacks for unavailable services
- Shorter collection intervals
- Suitable for development and testing

## Health monitoring

The Maintenance System provides comprehensive health monitoring through multiple interfaces:

### Service registry health

All three subsystems register with the service registry and report health status:

```python
# Query health via service registry
status = service_registry.get_service_info("homeostasis_system")
# Returns: {status: "HEALTHY", uptime: 3600, ...}

status = service_registry.get_service_info("self_improvement_engine")
# Returns: {status: "HEALTHY", proposals: 5, ...}

status = service_registry.get_service_info("self_incorporation")
# Returns: {status: "HEALTHY", files_discovered: 150, ...}
```

### Metrics endpoints

Each subsystem exposes metrics for observability platforms:

**Homeostasis metrics:**

- `system_health_score`: Overall health (0.0-1.0)
- `controller_active`: Controller operational (true/false)
- `actions_executed`: Count of corrective actions
- `errors_detected`: Count of detected errors
- `fixes_successful`: Count of successful fixes
- `metrics_collected`: Total metrics collected

**Self-Improvement metrics:**

- `metrics_recorded`: Total metrics received
- `patterns_detected`: Patterns identified
- `proposals_generated`: Improvement proposals created
- `trends_analyzed`: Trend analysis operations
- `analysis_cycles`: Total analysis cycles completed

**Self-Incorporation metrics:**

- `files_discovered`: Total files found
- `files_classified`: Files classified by type
- `files_integrated`: Successfully integrated
- `files_quarantined`: Quarantined for review
- `night_cycles_completed`: Learning cycles completed
- `insights_generated`: Learning insights created

### Health check APIs

Direct health check endpoints for detailed status:

```python
# Homeostasis health
health = await homeostasis.get_status()
# Returns: {status, uptime, phases: {phase1: {...}, ...}, metrics: {...}}

# Self-Improvement health
health = await self_improvement.handle_message("status", {})
# Returns: {status: "active", proposals: [...], trends: {...}}

# Self-Incorporation health
health = await self_incorporation.health_check()
# Returns: {status: "HEALTHY", running: true, metrics: {...}}
```

## Configuration

### Homeostasis configuration

File: `Aetherra/homeostasis/configs/setpoints.yaml`

```yaml
setpoints:
  plugin_load_success:
    target: 0.95
    min_acceptable: 0.85
  memory_rtt:
    target: 50.0
    max_acceptable: 120.0
  task_latency_p95:
    target: 100.0
    max_acceptable: 250.0

controller:
  pid_gains:
    kp: 1.0
    ki: 0.1
    kd: 0.05
  collection_interval: 60  # seconds

error_correction:
  enabled: true
  cooldown_min: 300  # 5 minutes
  cooldown_max: 600  # 10 minutes
```

### Self-Improvement configuration

File: `config.json` (section: `self_improvement`)

```json
{
  "self_improvement": {
    "enabled": true,
    "db_path": "self_improvement.db",
    "analysis_interval": 300,
    "confidence_threshold": 0.6,
    "max_proposals": 10
  }
}
```

### Self-Incorporation configuration

File: `config.json` (section: `self_incorporation`)

```json
{
  "self_incorporation": {
    "enabled": true,
    "roots": [".", "Aetherra"],
    "trust_mode": "standard",
    "night_cycle_enabled": true,
    "idle_threshold_minutes": 30,
    "auto_integrate": false
  }
}
```

Policy file: `config/self_incorporation_policy.json`

```json
{
  "trust_tiers": {
    "verified": {
      "auto_approve": true,
      "require_review": false
    },
    "trusted": {
      "auto_approve": true,
    ### Health check APIs

    ```
      "require_review": false
    },
    "standard": {
      "auto_approve": false,
      "require_review": true
    }
  },
  "risk_thresholds": {
    The Hub exposes a unified, best-effort maintenance status endpoint that aggregates Homeostasis, Self-Improvement, and Self-Incorporation.

    - Route: `GET /api/maintenance/status`
    - Behavior: Always returns HTTP 200 with availability flags; missing subsystems are reported as `available: false` and do not fail the endpoint.
    - Headline fields:
      - `overall.runlevel` — OS runlevel from supervisor if available, else `"UNKNOWN"`
      - `overall.health_percent` — Global health percent if reported by Homeostasis supervisor
      - `overall.critical_health_percent` — Critical health percent if reported
      - `homeostasis.si_health_contribution` — SI health contribution via Phase 9 bridge (if available)

    Example response:

    ```json
    {
      "ok": true,
      "ts": "2025-10-23T12:34:56.789123",
      "overall": {
        "runlevel": "ONLINE",
        "health_percent": 92.5,
        "critical_health_percent": 98.0,
        "overall_running": true
      },
      "homeostasis": {
        "available": true,
        "running": true,
        "orchestrator": {"running": true, "initialized": true},
        "health": {"supervisor": {"runlevel": "ONLINE"}},
        "si_health_contribution": {"score": 0.12}
      },
      "self_improvement": {
        "available": true,
        "status": {"improvement_active": true, "total_proposals": 0}
      },
      "self_incorporation": {
        "available": true,
        "status": {"status": "ok", "running": true}
      }
    }
    ```

    Quick check (with Hub running on 3001):

    ```powershell
    # Optional: start via VS Code task "Run Hub (AI API 3001)"
    Invoke-RestMethod -Uri "http://localhost:3001/api/maintenance/status" -Method GET | ConvertTo-Json -Depth 6
    ```
    "network_access": 0.7,
    "file_operations": 0.6,
    "code_execution": 0.8
  }
}
```

## Maintenance system lifecycle

### Startup sequence

1. **Phase 2: System Loading**
   - Self-Improvement Engine: Load and register with service registry
   - Self-Incorporation Service: Load with configuration, register with service registry
   - Homeostasis System: Load all 8 phases, register with service registry

2. **Phase 3: System Injection**
   - Self-Incorporation: Receive references to service registry, kernel loop, plugin manager, agent orchestrator
   - Homeostasis: Initialize all phase components (metrics collector, controller, actuators, supervisor, validator, error corrector, metrics bridge)

3. **Phase 4: System Activation**
   - Homeostasis: Start all 8 phases in sequence
     - Phase 7 (Error Correction): Install log handler, start background processing
     - Phase 8 (Metrics Bridge): Start 60-second polling loop
   - Self-Incorporation: Start service, trigger initial code discovery scan
   - All systems: Mark as HEALTHY in service registry

### Runtime operation

**Continuous monitoring (Homeostasis Phase 1)**

- Collects metrics every 60 seconds from all system components
- Stores in time-series for trend analysis
- Provides current snapshot on demand

**Real-time error correction (Homeostasis Phase 7)**

- Monitors all Python logs (WARNING+) in real-time
- Matches against error patterns
- Attempts automatic fixes with intelligent cooldown
- Tracks statistics for effectiveness analysis

**Metrics forwarding (Homeostasis Phase 8)**

- Every 60 seconds, collects homeostasis metrics
- Formats for self-improvement engine consumption
- Sends via service registry message bus
- Tracks forwarding success rate

**Pattern analysis (Self-Improvement)**

- Every 5 minutes, analyzes accumulated metrics
- Identifies trends: improving, degrading, stable, anomalous
- Generates improvement proposals with rationale
- Stores proposals for future action

**Code discovery (Self-Incorporation)**

- Initial scan at boot (non-blocking background task)
- Periodic rescans detect new/modified files
- Night cycle during idle periods for deep analysis
- Maintains index of all discovered code

**Safety evaluation (Self-Incorporation)**

- Classifies discovered code by type
- Analyzes risk factors and assigns trust tier
- Ethics evaluation for integration decisions
- Quarantines suspicious code

### Shutdown sequence

1. **Stop metrics forwarding**
   - Homeostasis Phase 8: Stop bridge loop, final metrics flush

2. **Stop error correction**
   - Homeostasis Phase 7: Remove log handler, stop background processing

3. **Stop self-incorporation**
   - Save current discovery state
   - Flush audit ledger
   - Unregister from service registry

4. **Stop self-improvement**
   - Complete current analysis cycle
   - Save proposals and trends
   - Unregister from service registry

5. **Stop homeostasis**
   - Stop all 8 phases in reverse order
   - Final metrics snapshot
   - Unregister from service registry

## Observability and metrics

### Prometheus/OpenMetrics export

Homeostasis exposes metrics in Prometheus format:

```
# HELP aetherra_system_health System health score (0.0-1.0)
# TYPE aetherra_system_health gauge
aetherra_system_health 0.95

# HELP aetherra_errors_detected Total errors detected
# TYPE aetherra_errors_detected counter
aetherra_errors_detected 42

# HELP aetherra_fixes_successful Successful automatic fixes
# TYPE aetherra_fixes_successful counter
aetherra_fixes_successful 38

# HELP aetherra_metrics_forwarded Metrics forwarded to SI Engine
# TYPE aetherra_metrics_forwarded counter
aetherra_metrics_forwarded 1440
```

### Logging

All three subsystems log to standard Python logging:

- **Homeostasis**: `[HOMEOSTASIS]` prefix, logs phase transitions, actions, errors
- **Self-Improvement**: `[SI]` prefix, logs analysis cycles, proposals, trends
- **Self-Incorporation**: `[SELFINC]` prefix, logs discoveries, integrations, night cycles

Log levels:

- `INFO`: Normal operational events (starts, stops, routine actions)
- `WARNING`: Anomalies, degradations, non-critical failures
- `ERROR`: Critical failures, unable to perform core functions
- `DEBUG`: Detailed diagnostics (metric values, pattern details, decision rationale)

### Dashboards

Recommended dashboard panels:

1. **System Health Overview**
   - Overall health score (gauge)
   - Health by component (bar chart)
   - Health trend (time series)

2. **Error Correction**
   - Errors detected (counter)
   - Fixes attempted (counter)
   - Fix success rate (percentage)
   - Errors by category (pie chart)

3. **Self-Improvement**
   - Metrics received (counter)
   - Proposals generated (counter)
   - Active proposals (list)
   - Trend analysis results (table)

4. **Self-Incorporation**
   - Files discovered (counter)
   - Files by type (pie chart)
   - Files by trust tier (bar chart)
   - Integration success rate (percentage)
   - Night cycle status (indicator)

## Safety and security

### Safety constraints

**Homeostasis actuators:**

- Rate limiting: Maximum 1 action per component per minute
- Cooldown periods: 5-10 minutes between repeated actions
- Policy validation: All actions checked against safety policies
- Rollback capability: All actuator actions reversible
- Human override: Manual intervention can disable actuators

**Self-Improvement proposals:**

- Confidence thresholds: Proposals require >60% confidence
- Impact assessment: High-impact proposals flagged for review
- Simulation mode: Test proposals before applying
- Audit trail: All proposals logged with rationale

**Self-Incorporation integrations:**

- Multi-tier trust model: Unverified code requires approval
- Risk analysis: Dangerous operations flagged
- Ethics evaluation: Ethical implications assessed
- Quarantine system: Suspicious code isolated
- Rollback tokens: All integrations reversible
- Audit ledger: Immutable record of all integrations

### Security policies

**Network access:**

- Self-Incorporation analyzes network imports
- Risk score increases for socket, urllib, requests usage
- Network allowlisting in strict mode
- Audit trail for all network-accessing code

**Code execution:**

- `eval()`, `exec()`, `subprocess` flagged as high risk
- Trust tier downgrade for dangerous operations
- Sandboxing for experimental code (future)
- Requires manual approval in strict mode

**File operations:**

- File I/O operations tracked and audited
- Path validation prevents directory traversal
- Sensitive file paths protected
- Audit trail for all file operations

**Data privacy:**

- No sensitive data logged to audit trail
- Policy-aware anonymization
- Configurable data retention periods
- GDPR-compliant by design

## Troubleshooting

### Common issues

**Issue: Homeostasis not starting**

Symptoms: No `[HOMEOSTASIS]` log messages, service not in registry

Diagnosis:

```python
# Check if homeostasis is registered
status = service_registry.get_service_info("homeostasis_system")
if status is None:
    # Not registered - check OS launcher logs for exceptions
```

Solutions:

- Check OS launcher startup logs for exceptions during Phase 2 loading
- Verify `Aetherra/homeostasis/` directory exists and has required files
- Check Python environment has required dependencies

**Issue: Metrics not forwarding to Self-Improvement**

Symptoms: Self-Improvement shows 0 metrics received, no proposals generated

Diagnosis:

```python
# Check metrics bridge status
bridge_status = homeostasis.metrics_bridge.get_status()
# Check forward_failures > 0 or success_rate < 100%
```

Solutions:

- Verify Self-Improvement Engine is registered: `service_registry.get_service_info("self_improvement_engine")`
- Check service registry is operational and routing messages
- Review homeostasis logs for `[BRIDGE]` messages indicating failures

**Issue: Error correction not detecting errors**

Symptoms: Errors in logs but no fix attempts, statistics show 0 detections

Diagnosis:

```python
# Check error corrector is running
stats = homeostasis.error_corrector.get_statistics()
# If errors_detected == 0, log handler may not be installed
```

Solutions:

- Verify Phase 7 started: Check for `[ERRCORR]` log messages
- Confirm logging.Handler installed: `logging.root.handlers` includes `LogMonitorHandler`
- Check error patterns match actual log messages

**Issue: Self-Incorporation not discovering files**

Symptoms: No files discovered after boot, `files_discovered` metric shows 0

Diagnosis:

```python
# Check initial scan was triggered
status = await self_incorporation.get_status()
# Check last_scan_timestamp > 0
```

Solutions:

- Verify service started: `service_registry.get_service_info("self_incorporation")`
- Check configured roots are valid paths: `self_incorporation.config.roots`
- Review logs for `[SELFINC]` messages about scan completion
- Manually trigger scan: `await self_incorporation.trigger_scan()`

**Issue: Night cycle not running**

Symptoms: `night_cycles_completed` remains 0, no learning insights

Diagnosis:

```python
# Check night cycle configuration
config = self_incorporation.config
if not config.night_cycle_enabled:
    # Disabled in configuration
```

Solutions:

- Enable night cycle in config: `"night_cycle_enabled": true`
- Ensure system detects idle: User activity must be low for 30+ minutes
- Check logs for night cycle phase transitions
- Verify CPU/memory usage is low (night cycle waits for low resource usage)

### Debug mode

Enable verbose debug logging:

```python
import logging
logging.getLogger("Aetherra.homeostasis").setLevel(logging.DEBUG)
logging.getLogger("Aetherra.aetherra_core.engine").setLevel(logging.DEBUG)
logging.getLogger("aetherra_self_incorporation").setLevel(logging.DEBUG)
```

Or via environment variable:

```bash
export AETHERRA_LOG_LEVEL=DEBUG
python aetherra_os_launcher.py --mode full -v
```

### Performance tuning

**Reduce metrics collection overhead:**

```yaml
# In setpoints.yaml
controller:
  collection_interval: 120  # Increase from 60 to 120 seconds
```

**Reduce self-improvement analysis frequency:**

```json
{
  "self_improvement": {
    "analysis_interval": 600  // Increase from 300 to 600 seconds (10 minutes)
  }
}
```

**Disable night cycle learning:**

```json
{
  "self_incorporation": {
    "night_cycle_enabled": false
  }
}
```

**Disable error correction:**

```yaml
# In setpoints.yaml
error_correction:
  enabled: false
```

## Future enhancements

### Phase 2: Complete data flows

**Priority 2: Self-Incorporation Metrics Bridge**

- Forward discovery and integration metrics to Self-Improvement Engine
- Include Self-Incorporation health in Homeostasis system health score
- Enable Self-Improvement to learn from code evolution patterns

**Priority 3: Proposal Consumer**

- Implement message handler in Self-Incorporation for improvement proposals
- Evaluate proposals against safety policies
- Execute safe proposals through integration pipeline
- Report outcomes back to Self-Improvement Engine

**Priority 4: Coordinated Night Cycle**

- Homeostasis broadcasts system-wide idle state
- Self-Incorporation synchronizes night cycle with system idle
- Optimal resource utilization for learning activities

### Phase 3: Advanced capabilities

**Predictive maintenance:**

- Self-Improvement predicts failures before they occur
- Proactive corrective actions prevent issues
- Statistical anomaly detection for early warning

**A/B testing framework:**

- Self-Improvement proposes multiple strategies
- Self-Incorporation tests strategies in parallel
- Homeostasis monitors outcomes and selects winner

**Automated rollback:**

- Homeostasis detects degraded health after integration
- Self-Incorporation automatically rolls back recent changes
- Self-Improvement learns from failed integrations

**Distributed maintenance:**

- Maintenance System coordinates across multiple Aetherra instances
- Shared learning and proposal exchange
- Federated pattern analysis

**Explainability interface:**

- Visual dashboard showing maintenance decisions
- Rationale and evidence for all actions
- Human-in-the-loop for complex decisions

## Related documentation

- [Aetherra Homeostasis System](./AETHERRA_HOMEOSTASIS_SYSTEM.md) - Detailed homeostasis documentation
- [Aetherra Kernel System](./AETHERRA_KERNEL_SYSTEM.md) - OS kernel and lifecycle
- [Aetherra Security System](./AETHERRA_SECURITY_SYSTEM.md) - Security policies and enforcement
- [Autonomous Error Correction](../AUTONOMOUS_ERROR_CORRECTION.md) - Error correction system details
- [Self-Incorporation Integration](../SELF_INCORPORATION_INTEGRATION_COMPLETE.md) - Integration implementation

## API reference

### Homeostasis System API

```python
from Aetherra.homeostasis.homeostasis_integration import HomeostasisOrchestrator

# Create and initialize
homeostasis = HomeostasisOrchestrator()
await homeostasis.initialize()

# Start all phases
await homeostasis.start()

# Get system status
status = homeostasis.get_status()
# Returns: {status: "active", health_score: 0.95, phases: {...}}

# Stop all phases
await homeostasis.stop()
```

### Self-Improvement Engine API

```python
from Aetherra.aetherra_core.engine.self_improvement_engine import SelfImprovementEngine

# Create and start
engine = SelfImprovementEngine(db_path="self_improvement.db")
await engine.start_improvement_cycle(loop=asyncio.get_running_loop())

# Record metric
engine.record_performance_metric(
    name="plugin_load_success",
    value=0.95,
    unit="percentage",
    context={"component": "plugin_manager"}
)

# Get improvement status
status = engine.get_improvement_status()
# Returns: {proposals: [...], metrics_count: 1440, last_analysis: ...}

# Get metric trends
trends = engine.get_metric_trends("plugin_load_success", time_window=3600)
# Returns: {trend: "improving", values: [...], statistics: {...}}

# Stop engine
await engine.stop_improvement_cycle()
```

### Self-Incorporation Service API

```python
from aetherra_self_incorporation import SelfIncorporationService, SelfIncorporationConfig

# Create with configuration
config = SelfIncorporationConfig(
    enabled=True,
    roots=[Path("."), Path("Aetherra")],
    trust_mode="standard"
)
service = SelfIncorporationService(config)

# Inject core systems
service.inject_systems(
    service_registry,
    kernel_loop,
    plugin_manager,
    agent_orchestrator
)

# Start service
await service.start()

# Trigger code discovery
result = await service.trigger_scan(root_filter=None)
# Returns: {ok: true, discovered: 150, duration: 2.3, timestamp: ...}

# Classify discovered files
result = await service.trigger_classify(type_filter=None)
# Returns: {ok: true, classified: 150, duration: 1.5, timestamp: ...}

# Security evaluation
result = await service.trigger_security_eval(trust_filter=None)
# Returns: {ok: true, evaluated: 150, duration: 1.2, timestamp: ...}

# Create integration plan
result = await service.trigger_planning(include_experimental=False)
# Returns: {ok: true, plan_id: "abc123", total_components: 25, ...}

# Execute integration
result = await service.trigger_integrate(plan_id="abc123")
# Returns: {ok: true, integrated: 25, rollback_token: "xyz789", ...}

# Get service status
status = await service.get_status()
# Returns: {status: "HEALTHY", files_discovered: 150, ...}

# Health check
health = await service.health_check()
# Returns: {status: "HEALTHY", running: true, config_enabled: true, ...}

# Stop service
await service.stop()
```

## Production hardening

### SLO promotion and guardrails

**Elevate setpoints to OS-level SLOs**

Homeostasis already defines target operating parameters. Promote these to formal SLOs with automated enforcement:

```yaml
# Aetherra/homeostasis/configs/slos.yaml
slos:
  plugin_load_success:
    target: 0.95
    minimum: 0.85
    breach_action: "alert_and_degrade"
    grace_period: 300  # seconds before enforcement

  memory_rtt_p95:
    target: 50.0
    maximum: 120.0
    breach_action: "trigger_maintenance"
    grace_period: 120

  task_latency_p95:
    target: 100.0
    maximum: 250.0
    breach_action: "auto_rollback"
    grace_period: 60

breach_policies:
  alert_and_degrade:
    - log_breach_event
    - notify_hub_dashboard
    - reduce_task_concurrency

  trigger_maintenance:
    - log_breach_event
    - trigger_memory_cleanup
    - notify_admin_if_persistent

  auto_rollback:
    - log_breach_event
    - identify_recent_changes
    - execute_automatic_rollback
    - notify_hub_dashboard
```

**Guard policies for autonomous actions**

```yaml
# Aetherra/homeostasis/configs/guard_policies.yaml
guards:
  integration_velocity:
    max_integrations_per_hour: 5
    max_quarantines_per_hour: 2
    breach_action: "pause_self_incorporation"

  actuator_frequency:
    max_actions_per_component: 1
    cooldown_minutes: 5
    breach_action: "disable_actuator"

  rollback_cascade:
    max_rollbacks_per_hour: 3
    breach_action: "require_human_approval"

escalation:
  persistent_slo_breach:
    threshold_minutes: 15
    action: "notify_chat_agents"
    message: "System health degraded, manual review required"
```

### Security system integration

**Wire Self-Incorporation through Security System**

All autonomous integrations must pass through existing security controls:

```python
# In aetherra_self_incorporation.py
async def _validate_integration_security(self, file_item: FileItem, plan: dict) -> bool:
    """
    Validate integration against Security System policies.
    Deny-by-default: requires explicit approval.
    """
    from Aetherra.security.security_policy import SecurityPolicy

    # 1. Check signature requirement (VERIFIED/TRUSTED tiers only)
    if self.config.trust_mode == "strict":
        if not await self._verify_code_signature(file_item):
            logger.warning(f"[SELFINC] Integration blocked: no valid signature for {file_item.path}")
            return False

    # 2. Check capability grants
    required_caps = plan.get("required_capabilities", [])
    for cap in required_caps:
        if not await SecurityPolicy.check_capability_grant(cap):
            logger.warning(f"[SELFINC] Integration blocked: capability '{cap}' not granted")
            return False

    # 3. Check network policy compliance
    if self._requires_network_access(file_item):
        if not await SecurityPolicy.check_network_policy(file_item.path):
            logger.warning(f"[SELFINC] Integration blocked: network policy violation")
            return False

    # 4. Policy drift detection
    drift = await SecurityPolicy.detect_policy_drift(file_item)
    if drift.severity == "critical":
        logger.error(f"[SELFINC] Integration blocked: critical policy drift detected")
        await self.quarantine_file(file_item.id, "critical_policy_drift", drift.details)
        return False

    return True
```

**Strict mode enforcement**

```python
# Environment-based security escalation
if os.getenv("AETHERRA_PROFILE") == "prod":
    # Production mode: strictest policies
    - require_signatures = True
    - auto_integrate = False  # Manual approval required
    - trust_mode = "strict"
    - capability_checks = "mandatory"

elif os.getenv("AETHERRA_NET_STRICT") == "1":
    # Network strict mode
    - network_allowlist_required = True
    - block_unsigned_network_code = True
    - audit_all_network_ops = True
```

### Kernel-native action safety

**Adopt kernel action envelopes for all actuator operations**

```python
# Aetherra/homeostasis/actuators.py
from Aetherra.kernel.action_envelope import ActionEnvelope, ActionPriority

async def execute_actuator_action(self, action_type: str, target: str, params: dict) -> bool:
    """
    Execute actuator action using kernel-native action envelope.
    Provides: trace_id, deadline, timeout, priority, DLQ on failure.
    """
    # Create action envelope
    envelope = ActionEnvelope(
        action_type=action_type,
        target=target,
        params=params,
        trace_id=self._generate_trace_id(),
        deadline_ts=time.time() + 30.0,  # 30-second deadline
        timeout_sec=25.0,  # 25-second timeout (< deadline)
        priority=ActionPriority.MAINTENANCE,
        retry_policy={
            "max_attempts": 2,
            "backoff_sec": 5.0,
            "exponential": False
        }
    )

    # Submit to kernel action queue
    try:
        result = await self.kernel_loop.submit_action(envelope)

        if result.success:
            self.metrics["actions_successful"] += 1
            return True
        else:
            self.metrics["actions_failed"] += 1
            logger.warning(f"[ACTUATOR] Action failed: {result.error}")
            return False

    except ActionExpiredError:
        # Action exceeded deadline, moved to DLQ
        self.metrics["actions_expired"] += 1
        logger.error(f"[ACTUATOR] Action expired and moved to DLQ: {envelope.trace_id}")
        return False

    except ActionQueueFullError:
        # Backpressure detected
        self.metrics["actions_dropped"] += 1
        logger.warning(f"[ACTUATOR] Action dropped due to queue backpressure")
        return False
```

**DLQ monitoring and recovery**

```python
async def monitor_dlq(self):
    """Monitor Dead Letter Queue for failed actions."""
    dlq_items = await self.kernel_loop.get_dlq_items(limit=100)

    if len(dlq_items) > 10:
        logger.error(f"[ACTUATOR] DLQ depth high: {len(dlq_items)} items")

        # Analyze failure patterns
        failure_patterns = self._analyze_dlq_patterns(dlq_items)

        # Disable problematic actuators
        for actuator_type, failure_rate in failure_patterns.items():
            if failure_rate > 0.5:  # 50% failure rate
                logger.error(f"[ACTUATOR] Disabling {actuator_type} due to high failure rate")
                await self.disable_actuator(actuator_type)
```

### Memory and STORM integration

**Feed memory health into Homeostasis**

```python
# Aetherra/homeostasis/stability_metrics.py
async def collect_memory_health_metrics(self) -> dict[str, float]:
    """Collect health metrics from Memory System including STORM."""
    from Aetherra.memory.memory_advanced import AetherraMemoryEngineAdvanced

    memory = AetherraMemoryEngineAdvanced.get_instance()

    metrics = {}

    # Core memory health
    health = await memory.get_health_snapshot()
    metrics["memory_recall_latency_p95"] = health.get("recall_latency_p95", 0.0)
    metrics["memory_store_success_rate"] = health.get("store_success_rate", 1.0)
    metrics["memory_index_size"] = health.get("index_size", 0)

    # STORM health (if enabled)
    if memory.storm_enabled:
        storm_health = await memory.storm.get_health_metrics()
        metrics["storm_sheaf_inconsistency"] = storm_health.get("sheaf_inconsistency", 0.0)
        metrics["storm_tt_rank_avg"] = storm_health.get("tt_rank_avg", 0.0)
        metrics["storm_ot_cost_avg"] = storm_health.get("ot_cost_avg", 0.0)
        metrics["storm_coherence_score"] = storm_health.get("coherence_score", 1.0)

    # Pulse health
    pulse = await memory.get_pulse_status()
    metrics["memory_pulse_healthy"] = 1.0 if pulse.get("status") == "healthy" else 0.0

    # Narrative health
    narrative_health = await memory.get_narrative_health()
    metrics["memory_narrative_completeness"] = narrative_health.get("completeness", 1.0)

    return metrics
```

**STORM maintenance triggers**

```yaml
# In setpoints.yaml
memory_slos:
  storm_sheaf_inconsistency:
    target: 0.0
    maximum: 0.1
    breach_action: "trigger_storm_maintenance"

  storm_coherence_score:
    target: 1.0
    minimum: 0.9
    breach_action: "trigger_storm_reindex"

storm_maintenance:
  inconsistency_threshold: 0.1
  actions:
    - recompute_sheaf_topology
    - rebuild_transport_maps
    - validate_tt_decompositions

  cooldown_minutes: 60  # Prevent excessive maintenance
```

### Canary deployments and HMR integration

**Default canary strategy for new capabilities**

```python
# In aetherra_self_incorporation.py
async def integrate_with_canary(self, plan_id: str, canary_percent: float = 0.1) -> dict:
    """
    Integrate new capability using canary deployment.

    Flow:
    1. Deploy to canary_percent of traffic
    2. Monitor health for canary_duration
    3. Auto-rollback if health degrades
    4. Full rollout if health stable
    """
    plan = self.integration_planner.get_plan(plan_id)

    # Generate rollback token before integration
    rollback_token = self._generate_rollback_token()

    # Create HMR canary configuration
    hmr_config = {
        "canary_percent": canary_percent,
        "canary_duration": 300,  # 5 minutes
        "health_check_interval": 10,  # 10 seconds
        "rollback_threshold": 0.9,  # Rollback if health < 0.9
        "rollback_token": rollback_token
    }

    # Execute canary deployment via HMR
    canary_result = await self.core_integrator.integrate_canary(
        plan=plan,
        hmr_config=hmr_config,
        kernel_loop=self.kernel_loop
    )

    if canary_result["status"] == "canary_stable":
        # Health stable during canary, proceed to full rollout
        logger.info(f"[SELFINC] Canary stable, proceeding to full rollout")
        full_result = await self.core_integrator.integrate_full(plan)

        return {
            "ok": True,
            "deployment": "canary_promoted",
            "rollback_token": rollback_token,
            "health_delta": canary_result["health_delta"]
        }

    elif canary_result["status"] == "auto_rollback":
        # Health degraded, automatic rollback executed
        logger.warning(f"[SELFINC] Canary failed, automatic rollback executed")

        return {
            "ok": False,
            "deployment": "canary_failed",
            "rollback_token": rollback_token,
            "rollback_reason": canary_result["rollback_reason"],
            "health_delta": canary_result["health_delta"]
        }
```

### Golden path testing

**Acceptance tests for autonomous error correction**

```python
# tests/acceptance/test_autonomous_error_correction.py
import pytest
from Aetherra.homeostasis.autonomous_error_corrector import AutonomousErrorCorrector

@pytest.mark.acceptance
async def test_service_registration_error_detection_and_fix():
    """
    Test: Service registration API mismatch error is detected and fixed.

    Golden path:
    1. Error appears in logs (service registration API mismatch)
    2. Error corrector detects pattern
    3. Cooldown respected (no immediate retry)
    4. Fix handler applies correction
    5. Metrics increment: errors_detected, fixes_attempted, fixes_successful
    """
    corrector = AutonomousErrorCorrector()
    await corrector.start()

    # Inject error into logs
    logger.warning("Service 'test_service' failed to register: API mismatch")

    # Wait for detection
    await asyncio.sleep(0.5)

    stats = corrector.get_statistics()
    assert stats["errors_detected"] >= 1, "Error should be detected"
    assert stats["fixes_attempted"] >= 1, "Fix should be attempted"

    # Inject same error immediately (should be blocked by cooldown)
    logger.warning("Service 'test_service' failed to register: API mismatch")
    await asyncio.sleep(0.5)

    stats_after = corrector.get_statistics()
    assert stats_after["fixes_attempted"] == stats["fixes_attempted"], \
        "Second fix should be blocked by cooldown"

    # Verify fix was successful
    assert stats["fixes_successful"] >= 1, "Fix should succeed"

    await corrector.stop()

# Similar tests for all 6 error categories:
# - test_deprecated_import_detection_and_fix()
# - test_missing_module_detection_and_fix()
# - test_missing_capability_detection_and_fix()
# - test_plugin_load_failure_detection_and_fix()
# - test_missing_data_detection_and_fix()
```

## Concrete implementation roadmap

 > **STATUS UPDATE (2025-10-23)**: Phases 2A, 2B, 2C, 2D, 2E, and 2F Complete! ✅
>
> - **Phase 2A**: Metrics triangle closed with Self-Incorporation bridge, proposal consumer, and unified status API
> - **Phase 2B**: Security hardening complete with trust modes, guard policies, audit immutability, and strict-mode enforcement
> - **Phase 2C**: Kernel integration complete with actuator action envelopes, DLQ monitoring, and backpressure handling
> - **Phase 2D**: Memory and STORM integration complete with health metrics collection and maintenance triggers
> - **Phase 2E**: Canary deployment strategy implemented with health monitoring and automatic rollback
> - **Phase 2F**: Testing and validation complete (golden paths, canary E2E, load + security)
>
> See `docs/PHASE_2A_IMPLEMENTATION.md` for Phase 2A details.

### Phase 2A: Close the metrics triangle (1-2 weeks)

**Week 1: Bridge implementation** ✅ **COMPLETE**

- [x] Implement Phase 9: Self-Incorporation Metrics Bridge
  - File: `Aetherra/homeostasis/self_incorporation_metrics_bridge.py` (453 lines)
  - Forward discovery/integration metrics to SI Engine (9+ metrics)
  - Include Self-Incorporation health in Homeostasis health score
  - Statistics: metrics_forwarded, forward_failures, success_rate
  - **Status:** ✅ Implemented, tested, integrated

- [x] Implement Proposal Consumer in Self-Incorporation
  - Message handler: `handle_improvement_proposal(proposal)` in `aetherra_self_incorporation.py`
  - Validates proposal type (scale_up, optimize, degrade, change_strategy)
  - Adjusts runtime knobs: processing_velocity, optimization_hints
  - Optional integration execution: accepts actions or integration_plan in params
  - Executes via core_integrator with HMR support where applicable
  - Records proposals_executed and proposals_accepted metrics
  - Appends to audit ledger with trace_id for observability
  - Reports results back to SI Engine via service registry ("selfimprovement.proposal_result")
  - Unit test: `tests/unit/test_selfinc_proposal_consumer.py`
  - **Status:** ✅ Implemented, tested, integrated

- [x] Unified Maintenance Status API
  - Endpoint: `/api/maintenance/status` in `aetherra_hub/blueprints/maintenance.py`
  - Aggregates: system_health_score, actions_executed, proposals_generated, proposals_executed, proposals_accepted, files_integrated, files_quarantined, last_rollback_token
  - Best-effort: returns HTTP 200 with availability flags; missing subsystems reported as available: false
  - KPIs extraction: reads from Homeostasis health, SIE status/metrics, Self-Inc status/metrics
  - OpenAPI schema: `aetherra_hub/blueprints/openapi.py` includes MaintenanceStatus and kpis
  - Unit tests: `tests/unit/test_hub_maintenance_status.py`, `tests/unit/test_openapi_maintenance_spec.py`
  - **Status:** ✅ Implemented and tested

**Week 2: Testing and validation** ✅ **COMPLETE**

- [x] End-to-end flow testing
  - Homeostasis detects performance issue → SI Engine generates proposal → Self-Incorporation evaluates → Integration executed → Health improves
  - Acceptance tests: `tests/acceptance/test_maintenance_e2e_flow.py`
  - Golden path test: proposal consumption → metrics increment → audit trail → feedback
  - Integration test: proposal with actions → dry-run execution → metrics tracking
  - **Status:** ✅ 2/2 tests passing in 19.24s

- [x] Metrics validation
  - Tool: `tools/validate_maintenance_metrics.py`
  - Validates: metrics increment, audit trail trace_ids, API extraction consistency
  - Checks: proposals_executed, proposals_accepted, last_rollback_token
  - **Status:** ✅ All validation checks passed

**Phase 2A Overall:** ✅ **COMPLETE**

Comprehensive completion summary: `docs/PHASE_2A_COMPLETION_SUMMARY.md`

**Optional Enhancements (deferred to Phase 2C):**

- [ ] Dashboard deployment
  - Unified maintenance status on Hub
  - Real-time metrics visualization

### Phase 2B: Security hardening (1 week) ✅ **COMPLETE**

- [x] Security System integration
  - Wire Self-Incorporation through Security System checks
  - File: `Aetherra/homeostasis/self_incorporation_security.py` (413 lines)
  - Signature verification for code integration (strict vs permissive modes)
  - Capability grant validation for integration plans
  - Network policy compliance checks (detects network imports, requires capability grants)
  - Policy drift detection (30% risk threshold)
  - **Status:** ✅ Implemented with 18/18 unit tests passing

- [x] Proposal authentication and authorization
  - Authenticate proposal sender (required in strict mode)
  - Authorize based on capability grants (maintenance:proposal:type)
  - Rate limiting: 10 proposals per minute per sender
  - Window-based rate limiting with automatic reset
  - **Status:** ✅ Implemented and tested

- [x] Strict mode enforcement
  - Production profile with mandatory security (`AETHERRA_PROFILE=prod`)
  - Network strict mode (`AETHERRA_NET_STRICT=1`)
  - trust_mode configuration: "strict" (prod), "standard" (default), "permissive" (dev)
  - Signature requirements enforced in strict mode
  - Anonymous proposals rejected in strict mode
  - **Status:** ✅ Implemented with environment-based activation

- [x] Guard policy implementation (foundation)
  - Define SLOs with breach actions
  - Integration velocity limits (env-overridable)
  - Actuator frequency guards per component
  - Rollback cascade prevention baseline
  - Config: `Aetherra/homeostasis/configs/guard_policies.yaml`
  - Runtime: `GuardPolicyEnforcer` wired into proposal flow (pre-check + record)
  - Tests: unit + acceptance for velocity enforcement

- [x] Guard policy metrics exposure
  - Status surfaces guard policy snapshot: policies (thresholds+windows), windows (accepted/rollbacks/components), and rejection counters
  - Available via `Self-Incorporation.get_status()` under `guards`
  - Included in Hub Maintenance Status aggregation (best-effort)
  - Tests: unit coverage for metrics presence and rejection increments

- [x] Audit trail immutability (hash chain)
  - Enhance audit ledger with tamper detection via SHA-256 hash chaining
  - New columns: `prev_hash`, `entry_hash` with automatic migration
  - Method: `AuditLedger.verify_integrity()` to validate chain
  - Tests: unit test detects tampering

- [x] Strict-mode and rate limit acceptance
  - Strict profile rejects unknown senders end-to-end
  - Proposal rate limiting enforced per-sender (10/min)
  - Tests: acceptance tests for strict-mode auth and rate limiting

### Phase 2C: Kernel integration (1 week) ✅ **COMPLETE**

- [x] Action envelope adoption
  - Kernel-native `actuator_action` task type with trace_id, deadline_ts, timeout_sec, priority
  - File: `aetherra_kernel_loop.py` - Added actuator_action handler in `_execute_task`
  - Submission helpers: `submit_actuator_action()` and `submit_actuator_action_and_wait()`
  - DLQ support: Failed actions written to `.aetherra/kernel_dlq.jsonl`
  - Priority mapping: ActionPriority (EMERGENCY/CRITICAL/HIGH → high queue, MEDIUM → normal, LOW → background)
  - Retry policy: Exponential backoff with jitter; timeout triggers retry; structural failure → DLQ
  - Actuators integration: `execute_action_via_kernel()` method submits via kernel with fallback to direct execution
  - Controller routing: `execute_pending_actions()` prefers kernel-aware path with backward compatibility
  - **Status:** ✅ Implemented, tested via smoke tests

- [x] DLQ monitoring
  - File: `Aetherra/homeostasis/homeostasis_integration.py` - Added `DLQMonitor` class
  - Periodic polling: `get_dlq_items(limit=100)` every 60 seconds
  - Failure pattern analysis: Groups by action_type, reason; calculates failure rates
  - Auto-disable: Quarantines actuator types with ≥5 failures (configurable threshold)
  - Metrics exposure: `dlq_count`, `top_failure_reasons`, `quarantined_actuators` via `get_system_health_status()`
  - Background task integration: Started with homeostasis background tasks; kernel reference injected dynamically
  - **Status:** ✅ Implemented, integrated, tested

- [x] Backpressure handling
  - Kernel queue limits enforced: high_priority, normal_priority, background queues
  - Drop to DLQ: Actions dropped when queue full; metrics track `drops_high`, `drops_normal`, `drops_background`
  - Graceful degradation: DLQ monitor detects high failure rates and quarantines problematic actuators
  - Metrics tracking: DLQ depth, failure patterns, quarantine events exposed in homeostasis status
  - **Status:** ✅ Implemented via kernel task queue infrastructure

**Phase 2C Overall:** ✅ **COMPLETE**

All actuator actions now flow through kernel-native envelopes with:

- Full observability (trace_id, timestamps, DLQ entries)
- Safety (timeout enforcement, retry logic, failure isolation)
- Resilience (auto-disable failing actuators, backpressure handling)
- Backward compatibility (fallback to direct execution if kernel unavailable)

**Remaining work (optional enhancements):**

- Unit/acceptance tests for DLQ monitoring and actuator quarantine behavior
- Per-actuator retry policy configuration (currently uses kernel defaults)
- DLQ analysis dashboard UI

### Phase 2D: STORM and memory integration (3-5 days) ✅ **COMPLETE**

- [x] Memory health metrics collection
  - File: `Aetherra/homeostasis/stability_metrics.py` - Added `_collect_memory_health_metrics()`
  - Recall latency p95: Extracted from STORM metrics (`storm_recall_latency_ms_p95`)
  - STORM sheaf inconsistency: Tracked via `aetherra_storm_sheaf_inconsistency` metric
  - STORM coherence score: Calculated as `1.0 / (1.0 + sheaf_inconsistency)`
  - STORM OT cost average: Tracked via `aetherra_storm_ot_cost_avg` metric
  - STORM TT rank: Tracked via `aetherra_storm_tt_rank` metric
  - Pulse health status: Coherence score, contradiction count, orphaned fragments from `get_memory_health()`
  - Narrative completeness: Optional from memory engine's narrative cache
  - Shadow mode metrics: Agreement rate, divergences, comparison count
  - **Status:** ✅ Implemented, integrated into metrics collection cycle

- [x] STORM maintenance triggers
  - File: `Aetherra/homeostasis/configs/setpoints.yaml` - Added memory/STORM SLOs and maintenance config
  - STORM setpoints: `storm_sheaf_inconsistency` (target: 0.0, max: 0.1), `storm_coherence_score` (target: 1.0, min: 0.9), `storm_ot_cost_avg` (max: 5.0), `storm_recall_latency_ms_p95` (target: 50ms, max: 150ms)
  - Memory pulse setpoints: `memory_coherence_score` (target: 0.9, min: 0.7), `memory_contradiction_count` (max: 5), `memory_orphaned_fragments` (max: 10)
  - Narrative setpoint: `narrative_completeness` (target: 1.0, min: 0.8)
  - Maintenance actions: STORM (recompute sheaf topology, rebuild transport maps, validate TT decompositions), Memory (resolve contradictions, cleanup orphaned fragments, rebuild concept clusters), Narrative (regenerate narrative, fill gaps, validate temporal consistency)
  - Cooldown periods: STORM (60 min), Memory (30 min), Narrative (120 min)
  - Rate limits: Max 2 STORM actions/hour, 3 memory actions/hour, 1 narrative action/hour
  - Emergency thresholds: STORM coherence < 0.75, Memory coherence < 0.5
  - **Status:** ✅ Configured with safety limits and cooldowns

**Phase 2D Overall:** ✅ **COMPLETE**

Memory and STORM health now integrated into Homeostasis monitoring with:

- Full observability of STORM sheaf coherence, optimal transport costs, and recall performance
- Memory pulse tracking (coherence, contradictions, orphaned fragments)
- Narrative completeness monitoring
- Automated maintenance triggers with safety limits (cooldowns, rate limits, emergency thresholds)
- Ready for Phase 2E canary deployments and Phase 2F testing

### Phase 2E: Canary deployments (1 week) ✅ **COMPLETE**

- [x] Canary integration strategy
  - File: `aetherra_self_incorporation.py` - Added `integrate_with_canary()` method
  - Default 10% canary rollout (configurable via `canary_percent` parameter)
  - Baseline health recording before deployment
  - Health monitoring during canary period (default 5 minutes, configurable)
  - Periodic health checks at configurable intervals (default 10 seconds)
  - Automatic rollback on health degradation below threshold (default 0.9)
  - Canary promotion when all health checks pass
  - Comprehensive result tracking: baseline/min/max/avg health, health delta, rollback reason
  - Metrics: `canary_deployments_successful`, `canary_deployments_failed`
  - **Status:** ✅ Implemented with configurable parameters and metrics tracking

- [x] HMR integration
  - Uses existing HMR controller from service registry
  - Integrates with CoreIntegrator's HMR-aware execution path
  - Rollback tokens generated automatically during integration
  - Automatic rollback via `trigger_rollback()` when health degrades
  - Leverages kernel HMR lifecycle (quiesce → swap → verify → rollback)
  - **Status:** ✅ Integrated with existing HMR infrastructure

- [x] Canary deployment tests
  - File: `tests/unit/test_canary_deployment.py` - 7 unit tests covering all canary logic paths
  - Test coverage: HMR disabled, plan not ready, baseline health too low, stable dry-run, auto-rollback on health drop, configurable parameters, metrics tracking
  - Mock-based tests for integration scenarios (real end-to-end tests deferred to Phase 2F)
  - **Status:** ✅ Unit tests passing (7/7)

**Phase 2E Overall:** ✅ **COMPLETE**

Canary deployment infrastructure is fully implemented and tested:

- Configurable canary strategy with health-based rollback
- Seamless HMR integration for hot-swapping
- Comprehensive unit test coverage
- Validated by Phase 2F end-to-end acceptance testing

### Phase 2F: Testing and validation (1 week) ✅ **COMPLETE**

- [x] Golden path tests
  - Acceptance tests for all 6 error correction categories
  - File: `tests/acceptance/test_autonomous_error_correction_golden_paths.py`
  - Status: ✅ 8/8 passing (cooldown semantics validated; regex-aligned messages)

- [x] Canary E2E acceptance tests (promotion + rollback)
  - File: `tests/acceptance/test_canary_e2e.py`
  - Scenarios: canary promotion on stable health; auto-rollback on health degradation below threshold
  - Health monitoring: exercised via Homeostasis health API path used by `integrate_with_canary()`
    (service registry stubs supply dynamic health sequences)
  - HMR: rollback_token generation validated through HMR path (register_plugin action)
  - Status: ✅ 2/2 passing (fast checks with patched sleep; no external services required)

- [x] Load testing
  - Stress test with high error rates
  - Validate actuator rate limiting (via DLQMonitor quarantine path)
  - Test DLQ behavior under load
  - File: `tests/acceptance/test_load_and_security_phase2f.py::test_dlq_monitor_quarantines_actuator_on_high_failure_rate`
  - Status: ✅ Pass — repeated actuator_action failures in DLQ trigger auto-quarantine; metrics (dlq_count, top_failure_reasons) exposed

- [x] Security testing
  - Verify strict mode enforcement (prod profile, deny-by-default without grants)
  - Test policy drift detection (critical drift blocks)
  - Validate capability grant checks
  - File: `tests/acceptance/test_load_and_security_phase2f.py`
    - `test_security_capability_grant_required_strict_mode`
    - `test_security_policy_drift_detection_critical`
  - Status: ✅ 2/2 passing — strict capability denial and critical drift detection

### Maintenance Guardrail Pack

Create `.aether` scripts for common maintenance scenarios:

```aether
// maintenance_guardrails.aether
// Policy enforcement and safety checks

metadata:
  name: "Maintenance Guardrails"
  version: "1.0.0"
  requires: ["homeostasis", "self_incorporation", "security"]

policy:
  max_integrations_per_hour: 5
  require_signatures_strict: true
  auto_rollback_on_health_drop: true

action check_slo_compliance:
  inputs: [slo_name, current_value]

  let target = homeostasis.get_slo(slo_name).target
  let breach = current_value < target

  if breach:
    emit "slo_breach" {slo: slo_name, value: current_value}
    trigger homeostasis.actuate_breach_policy(slo_name)

  return breach

action validate_integration_security:
  inputs: [file_item, plan]

  let signature_valid = security.verify_signature(file_item)
  let capabilities_granted = security.check_capabilities(plan.required_capabilities)
  let network_allowed = security.check_network_policy(file_item)

  return signature_valid && capabilities_granted && network_allowed
```

```aether
// maintenance_canary.aether
// Canary deployment with automatic rollback

metadata:
  name: "Maintenance Canary Deployment"
  version: "1.0.0"
  requires: ["self_incorporation", "homeostasis", "kernel"]

action deploy_canary:
  inputs: [plan_id, canary_percent = 0.1]

  // Capture baseline health
  let baseline_health = homeostasis.get_health_score()

  // Generate rollback token
  let rollback_token = self_incorporation.generate_rollback_token()

  // Deploy to canary percent
  let canary_result = self_incorporation.integrate_canary(plan_id, canary_percent)

  // Monitor health for 5 minutes
  sleep 300

  let canary_health = homeostasis.get_health_score()
  let health_delta = canary_health - baseline_health

  if health_delta < -0.1:  // Health dropped by 10%+
    emit "canary_failed" {health_delta: health_delta}
    trigger self_incorporation.rollback(rollback_token)
    return {success: false, reason: "health_degradation"}

  // Health stable, promote to full
  let full_result = self_incorporation.integrate_full(plan_id)

  return {success: true, rollback_token: rollback_token, health_delta: health_delta}
```

```aether
// maintenance_rollback.aether
// Trace-driven automatic rollback

metadata:
  name: "Maintenance Rollback"
  version: "1.0.0"
  requires: ["self_incorporation", "homeostasis", "kernel"]

action auto_rollback_on_breach:
  inputs: [slo_name, breach_severity]

  if breach_severity != "critical":
    return {action: "none", reason: "breach not critical"}

  // Find recent integrations (last hour)
  let recent_integrations = self_incorporation.get_recent_integrations(time_window = 3600)

  if recent_integrations.count == 0:
    return {action: "none", reason: "no recent integrations"}

  // Correlate breach with integrations using kernel trace_ids
  let suspected_integration = kernel.correlate_traces(breach_event, recent_integrations)

  if suspected_integration:
    emit "auto_rollback_triggered" {integration: suspected_integration, slo: slo_name}

    let rollback_result = self_incorporation.rollback(suspected_integration.rollback_token)

    // Verify health recovery
    sleep 60
    let health_recovered = homeostasis.check_slo(slo_name)

    return {
      action: "rollback",
      integration: suspected_integration.id,
      health_recovered: health_recovered
    }

  return {action: "none", reason: "no integration correlated with breach"}
```

## Hub dashboard KPIs

**System Health Panel**

- Global health score (0.0-1.0) with trend sparkline
- Task latency p95 with SLO threshold
- Plugin load success rate with target line
- Memory RTT with acceptable range

**Autonomy Quality Panel**

- Error correction effectiveness: `fixes_successful / fixes_attempted`
- Quarantine rate: `files_quarantined / files_discovered`
- Rollback count (last 24 hours)
- Auto-fix category breakdown (pie chart)

**Evolution Velocity Panel**

- Proposals generated (counter)
- Proposals accepted (counter)
- Time-to-canary average (seconds)
- Time-to-rollback average (seconds)
- Integration success rate

**Memory Integrity Panel**

- STORM OT cost average
- STORM sheaf coherence score
- Recall latency p95
- Pulse health indicator

**Risk Indicators**

- SLO breaches (last 24 hours)
- DLQ depth (actionable threshold)
- Policy drift alerts
- Actuator disable events

## Risk mitigation strategies

### Runaway auto-integration

**Risk**: Self-Incorporation integrates too many capabilities too quickly, destabilizing system.

**Mitigations**:

1. **Velocity limits**: Maximum 5 integrations per hour (configurable)
2. **Strict capability checks**: All integrations validated against Security System
3. **Signed manifests**: Require valid signatures in strict mode
4. **Canary rollouts**: Default 10% canary with health gates
5. **Automatic rollback**: Trigger on SLO breach within 5 minutes of integration
6. **Human-in-the-loop**: Chat/Agents API approval in strict mode

**Detection**:

```python
if metrics["integrations_last_hour"] > config["max_integrations_per_hour"]:
    logger.error("[GUARD] Integration velocity limit exceeded")
    await self_incorporation.pause(duration=3600)  # Pause for 1 hour
    await chat_agents.notify("Integration velocity limit exceeded, paused for 1 hour")
```

### Oscillation from aggressive actuators

**Risk**: Controller oscillates between corrective actions, causing instability.

**Mitigations**:

1. **PID tuning**: Properly tuned gains (Kp=1.0, Ki=0.1, Kd=0.05)
2. **Rate limiting**: Maximum 1 action per component per minute
3. **Cooldown periods**: 5-10 minute cooldown between repeated actions
4. **Effectiveness learning**: Controller learns optimal dampening gains over time
5. **Oscillation detection**: Detect rapid state changes and increase dampening

**Detection**:

```python
action_history = actuator.get_action_history(time_window=600)  # Last 10 minutes
if self._detect_oscillation(action_history):
    logger.warning("[ACTUATOR] Oscillation detected, increasing dampening")
    controller.increase_dampening(factor=2.0)
    actuator.extend_cooldown(minutes=5)
```

**Adaptive dampening**:

```python
# Track effectiveness of each action
for action in action_history:
    if action.effectiveness < 0.5:  # Action not effective
        controller.adjust_gain(action.type, factor=0.9)  # Reduce gain by 10%
    elif action.effectiveness > 0.9:  # Action very effective
        controller.adjust_gain(action.type, factor=1.05)  # Increase gain by 5%
```

## Conclusion

The Aetherra Maintenance System represents a paradigm shift in operating system design: from reactive manual maintenance to proactive autonomous self-management. By integrating the Homeostasis System (stability), Self-Improvement Engine (intelligence), and Self-Incorporation Service (evolution), Aetherra achieves:

- **Zero-touch operation**: System maintains itself without human intervention
- **Continuous learning**: Performance improves autonomously over time
- **Self-healing**: Errors detected and corrected in real-time
- **Safe evolution**: New capabilities integrated with safety guarantees
- **Complete auditability**: All decisions and actions fully traceable

**Production hardening complete**: With SLO promotion, security integration, kernel-native safety, STORM monitoring, canary deployments, and comprehensive testing, the Maintenance System is production-ready and auditable.

This autonomous maintenance architecture ensures Aetherra remains stable, performant, and continuously evolving to meet user needs and adapt to changing conditions.

The Maintenance System operates continuously in Aetherra OS installations worldwide.

---

For technical support or questions about the Maintenance System:

- GitHub Issues: <https://github.com/AetherraLabs/Aetherra>
- Documentation: <https://docs.aetherra.ai>
- Email: <support@aetherraalabs.com>
