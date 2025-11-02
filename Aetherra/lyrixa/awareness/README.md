# Awareness Module - Lyrixa System Intelligence

This module provides Lyrixa with deep awareness of Aetherra OS capabilities.

## Components

### `context_analyzer.py`
Analyzes user messages to detect intent patterns and map them to relevant Aetherra systems.

**Key Features:**
- Intent detection across 8 categories (coding, memory ops, plugins, system queries, etc.)
- Pattern matching with confidence scoring
- System capability mapping
- Contextual hint generation for AI prompts

**Intent Categories:**
- `coding`: Code generation, debugging, refactoring
- `memory_ops`: Memory storage, retrieval, recall
- `plugin_request`: Plugin discovery and execution
- `system_query`: System status and health checks
- `consciousness_query`: Consciousness and quantum state queries
- `learning_request`: Self-improvement and adaptation
- `workspace_ops`: File and workspace operations
- `aether_workflow`: Workflow and pipeline execution

### `system_monitor.py`
Tracks real-time Aetherra OS status by querying the service registry.

**Key Features:**
- Comprehensive service status snapshots
- Health aggregation (healthy/degraded/critical)
- Capability extraction from registered services
- Cached status with configurable TTL (default 10s)

**Usage:**
```python
monitor = SystemMonitor(service_registry)
status = await monitor.get_comprehensive_status()
context = await monitor.build_awareness_context()
```

## Integration

These modules are integrated into `LyrixaChatService` to:
1. Analyze every message for contextual intent
2. Retrieve current system status
3. Inject awareness context into AI prompts
4. Surface relevant capabilities proactively

This makes Lyrixa naturally aware of what systems are available and what she can do, allowing her to be a truly intelligent interface to Aetherra OS.
