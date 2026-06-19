# Aether Script Language Tutorial

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This tutorial provides a progressive introduction to the Aether Script language (`.aether`), the declarative-intent language for orchestrating workflows in Aetherra OS.

## Purpose and scope

- Learn Aether Script syntax from basics to advanced
- Write your first `.aether` workflows
- Understand plugin coordination and memory operations
- Implement error handling and parallel execution
- Follow best practices for script authoring
- Debug and troubleshoot scripts

## What is Aether Script?

**Aether Script** is a declarative, human-readable language designed for:

- **Cognitive workflows** - Express intentions, not just instructions
- **Plugin orchestration** - Chain and coordinate plugin operations
- **Memory-driven execution** - Query and store in persistent memory
- **AI agent coordination** - Enable autonomous execution and reasoning

### Key Features

- **Whitespace-sensitive** - Python-like indentation
- **Intent-focused** - Emphasize "why" not just "what"
- **Plugin-native** - First-class plugin support
- **Self-documenting** - Scripts are readable by humans and AI
- **Signature-verified** - Cryptographic verification for trust

---

## Hello, Aetherra

### Your First Script

Create `hello.aether`:

```aether
# My first Aether script

meta:
  name: "hello_aetherra"
  purpose: "Learn Aether Script basics"

# Declare the goal
goal: "Say hello to Aetherra"

# Execute a plugin
greeting: run_plugin("echo", message="Hello, Aetherra!")

# Store the result
store(greeting, tag="tutorial")
```

### Running the Script

```bash
python aether.py hello.aether
```

**Expected output:**

```
[Aether] Loaded: hello_aetherra
[Aether] Executing goal: Say hello to Aetherra
[Plugin] echo: Hello, Aetherra!
[Memory] Stored with tag: tutorial
[Aether] Completed successfully
```

---

## Basic Syntax

### Comments

```aether
# This is a single-line comment
# Comments are ignored during execution

# Use comments to explain intent and document your workflow
```

### Meta Section

Every script should declare metadata:

```aether
meta:
  name: "my_script"
  purpose: "Brief description of what this script does"
  author: "Your Name"
  version: "1.0"
```

### Goal Declaration

The `goal:` statement declares the script's primary intention:

```aether
goal: "Summarize today's system health"
```

**Good goals:**

- "Analyze memory for patterns"
- "Generate daily system report"
- "Clean up old logs and optimize storage"

**Avoid:**

- "Do stuff" (too vague)
- "Run plugins" (not intent-focused)

### Assignments

Store values in variables using `:` syntax:

```aether
# Simple assignment
message: "Hello, World!"

# Function result
summary: summarize(logs)

# Plugin output
data: run_plugin("fetch_data")

# Numbers
count: 42
threshold: 0.95

# Lists
items: ["apple", "banana", "cherry"]

# Dictionaries
config: {
  timeout: 30,
  retry: 3
}
```

---

## Working with Plugins

### Running Plugins

The `run_plugin()` function executes registered plugins:

```aether
# Simple plugin call
result: run_plugin("hello_world")

# With arguments
processed: run_plugin("text_processor", input="sample text", mode="clean")

# Using previous results
step1: run_plugin("fetch_data")
step2: run_plugin("analyze_data", data=step1)
```

### Plugin Chaining

Chain plugins by passing outputs as inputs:

```aether
meta:
  name: "data_pipeline"
  purpose: "Process data through multiple stages"

# Stage 1: Fetch
raw_data: run_plugin("data_fetcher", source="api")

# Stage 2: Transform
cleaned: run_plugin("data_cleaner", input=raw_data)

# Stage 3: Analyze
insights: run_plugin("data_analyzer", input=cleaned)

# Stage 4: Store
store(insights, tag="pipeline_results")
```

### Available Plugins

Check available plugins at runtime:

```aether
# List plugins
plugins: available_plugins()

# Check specific plugin
has_summarizer: plugin_exists("summarizer")
```

---

## Memory Operations

### Loading from Memory

```aether
# Load recent events
events: load_logs(hours=24)

# Load by tag
daily_reports: load_memory(tag="daily_report")

# Query memory
patterns: query_memory("SELECT * FROM events WHERE type='anomaly'")
```

### Storing to Memory

```aether
# Simple store
store(result, tag="analysis")

# With metadata
store(summary, tag="daily", metadata={
  date: "2025-11-01",
  type: "health_check",
  priority: "high"
})

# Store multiple items
for item in results:
  store(item, tag="batch_results")
```

### Memory-Driven Logic

```aether
# Load and process
events: load_logs(hours=24)
anomalies: detect_anomalies(events)

if anomalies:
  # Investigate anomalies
  analysis: reflect_on(anomalies)
  escalate_to("Lyrixa", priority="high")
else:
  # Normal day
  summary: summarize(events)
  store(summary, tag="normal_day")
```

---

## Control Flow

### Conditionals

```aether
# Simple if
if health_score > 0.9:
  status: "healthy"

# If-else
if error_count > threshold:
  escalate_to("admin")
else:
  log("All systems normal")

# Nested conditions
if health_score > 0.9:
  if uptime > 86400:
    status: "excellent"
  else:
    status: "good"
else:
  status: "degraded"
```

### Loops

**For loops:**

```aether
# Iterate over list
for plugin in ["summarizer", "analyzer", "reporter"]:
  result: run_plugin(plugin)
  store(result, tag=plugin)

# Iterate over memory results
events: load_logs(hours=24)
for event in events:
  if event.severity == "high":
    process(event)

# Range iteration
for i in range(5):
  log("Iteration:", i)
```

**While loops (planned):**

```aether
# Not yet implemented
# while condition:
#   do_something()
```

---

## Error Handling

### Policy Declaration

Define error handling policy at the script level:

```aether
meta:
  name: "resilient_workflow"

policy:
  on_error: "continue"     # continue, rollback, or stop
  timeout_default: "30s"
  max_retries: 3
```

**Policy options:**

| Policy                 | Behavior                        |
| ---------------------- | ------------------------------- |
| `on_error: "continue"` | Continue execution after errors |
| `on_error: "rollback"` | Revert changes on error         |
| `on_error: "stop"`     | Halt execution immediately      |

### Try-Fallback Pattern

```aether
meta:
  name: "error_handling_demo"

policy:
  on_error: "continue"

# Try risky operation
risky_result: run_plugin("external_api", source="untrusted")

# Fallback if risky failed
if not risky_result:
  fallback: "Using cached data instead"
  result: load_memory(tag="cached_data")
else:
  result: risky_result

store(result, tag="final_output")
```

### Escalation

```aether
# Escalate on critical errors
if critical_failure:
  escalate_to("Lyrixa", message="System degraded", priority="high")
  escalate_to("ops@aetherraalabs.com", alert=true)
```

---

## Parallel Execution

### Parallel Branches

Execute multiple operations in parallel:

```aether
meta:
  name: "parallel_demo"
  purpose: "Parallel execution with join"

policy:
  on_error: "rollback"

# Branch A: Fetch recent events
A: run_plugin("fetch_recent_events")

# Branch B: Check system health
B: run_plugin("summarize_memory_health")

# Branch C: Load configurations
C: load_memory(tag="config")

# Join: Combine results
combined: summarize(A, B, C)

# Store final result
store(combined, tag="parallel_results")
```

**How it works:**

- Assignments `A`, `B`, `C` execute in parallel
- `summarize()` waits for all inputs to complete
- Execution continues after join point

### Dependency Resolution

Aether automatically resolves dependencies:

```aether
# Step 1 (independent)
data: fetch_data()

# Step 2 (depends on data)
cleaned: clean_data(data)

# Step 3 (depends on cleaned)
analyzed: analyze_data(cleaned)

# Steps 1, 2, 3 execute in sequence
# But independent steps can run in parallel
```

---

## Advanced Features

### Workflow Blocks

Define structured workflows:

```aether
workflow:
  input: "design.json"
  output: "game.rbxmx"
  steps:
    - parse_input
    - generate_assets
    - assemble_scene
    - export_game

# Each step is a plugin that receives previous output
```

### Function Definitions (Planned)

```aether
# Not yet implemented
function analyze_health(events):
  anomalies: detect_anomalies(events)
  if anomalies:
    return reflect_on(anomalies)
  else:
    return "healthy"
```

### Reflection and Self-Modification

```aether
# Trigger system introspection
reflection: reflect()

# Analyze own performance
performance: evaluate_confidence(reflection)

# Self-heal if needed
if performance < 0.8:
  self_heal()
```

### Narration

Generate human-readable explanations:

```aether
# Execute workflow
result: run_plugin("data_processor")

# Narrate what happened
story: narrate()

# Store narration
store(story, tag="execution_log")
```

---

## Real-World Examples

### Example 1: Daily Health Check

```aether
meta:
  name: "daily_health_check"
  purpose: "Comprehensive daily system health analysis"
  schedule: "daily at 06:00"

goal: "Analyze system health and generate report"

policy:
  on_error: "continue"
  timeout_default: "60s"

# Load 24 hours of events
events: load_logs(hours=24)

# Analyze health
health_score: calculate_health(events)
anomalies: detect_anomalies(events)

# Generate report
if health_score > 0.9 and not anomalies:
  report: summarize("System healthy. No anomalies detected.", events)
  priority: "normal"
else:
  report: summarize("System issues detected. Investigating.", events, anomalies)
  priority: "high"
  escalate_to("Lyrixa", message=report, priority=priority)

# Store report
store(report, tag="daily_health", metadata={
  health_score: health_score,
  priority: priority,
  date: today()
})
```

### Example 2: Memory Cleanup

```aether
meta:
  name: "memory_cleanup"
  purpose: "Clean old logs and optimize memory"
  schedule: "weekly on Sunday at 02:00"

goal: "Clean up old memory and optimize storage"

policy:
  on_error: "rollback"

# Find old logs (older than 90 days)
old_logs: query_memory("SELECT * FROM events WHERE age_days > 90")

# Archive important events
important: filter(old_logs, importance="high")
store(important, tag="archived")

# Delete old logs
deleted_count: delete_memory(old_logs)

# Optimize memory
optimize_memory()

# Generate report
report: summarize("Cleaned", deleted_count, "old logs. Archived", len(important), "important events.")
store(report, tag="cleanup_report")
```

### Example 3: Data Pipeline

```aether
meta:
  name: "data_processing_pipeline"
  purpose: "Multi-stage data processing workflow"

goal: "Process incoming data through validation, transformation, and analysis"

policy:
  on_error: "stop"
  timeout_default: "120s"

# Stage 1: Fetch
raw_data: run_plugin("data_fetcher", source="api", limit=1000)

# Stage 2: Validate
validation: run_plugin("data_validator", input=raw_data)

if not validation.passed:
  escalate_to("data_team", message="Validation failed", data=validation.errors)
  stop_execution()

# Stage 3: Transform
transformed: run_plugin("data_transformer", input=raw_data, mode="normalize")

# Stage 4: Analyze
insights: run_plugin("data_analyzer", input=transformed, algorithm="ml")

# Stage 5: Store results
store(insights, tag="pipeline_results", metadata={
  records_processed: len(raw_data),
  timestamp: now(),
  confidence: insights.confidence
})

# Generate summary
summary: narrate()
store(summary, tag="pipeline_log")
```

### Example 4: Plugin Chain with Error Handling

```aether
meta:
  name: "robust_plugin_chain"
  purpose: "Chain plugins with comprehensive error handling"

policy:
  on_error: "continue"
  max_retries: 3

# Step 1: Try external fetch with fallback
external_data: run_plugin("external_fetcher", source="api")

if not external_data:
  log("External fetch failed, using cache")
  external_data: load_memory(tag="cached_external_data")

# Step 2: Process data
processed: run_plugin("data_processor", input=external_data)

if not processed:
  escalate_to("Lyrixa", message="Processing failed")
  stop_execution()

# Step 3: Analyze
analysis: run_plugin("analyzer", input=processed)

# Step 4: Store with confidence check
if analysis.confidence > 0.8:
  store(analysis, tag="high_confidence")
else:
  store(analysis, tag="low_confidence")
  escalate_to("review_team", message="Low confidence analysis", data=analysis)
```

---

## Best Practices

### Script Organization

✅ **Always include meta section:**

```aether
meta:
  name: "descriptive_name"
  purpose: "Clear description of intent"
  author: "Your Name"
  version: "1.0"
```

✅ **Declare goal explicitly:**

```aether
goal: "Clear statement of what this script accomplishes"
```

✅ **Use descriptive variable names:**

```aether
# Good
daily_health_report: summarize(events)
anomaly_count: count(anomalies)

# Bad
r: summarize(e)
x: count(a)
```

✅ **Add comments for complex logic:**

```aether
# Check if system health is below critical threshold
if health_score < 0.5:
  # Emergency protocol: escalate immediately
  escalate_to("emergency_team", priority="critical")
```

### Error Handling

✅ **Set appropriate error policies:**

```aether
# For critical operations
policy:
  on_error: "rollback"

# For data pipelines
policy:
  on_error: "continue"
```

✅ **Validate inputs:**

```aether
data: fetch_data()

if not data:
  log("No data available")
  stop_execution()

# Continue with validated data
process(data)
```

✅ **Use fallbacks:**

```aether
primary_result: run_plugin("primary")

if not primary_result:
  backup_result: run_plugin("backup")
  result: backup_result
else:
  result: primary_result
```

### Performance

✅ **Leverage parallel execution:**

```aether
# These execute in parallel
data_a: fetch_source_a()
data_b: fetch_source_b()
data_c: fetch_source_c()

# Join here
combined: merge(data_a, data_b, data_c)
```

✅ **Set appropriate timeouts:**

```aether
policy:
  timeout_default: "30s"  # Quick operations

# Or per-plugin
result: run_plugin("slow_operation", timeout="300s")
```

✅ **Query memory efficiently:**

```aether
# Good: Specific query with limit
recent: query_memory("SELECT * FROM events WHERE type='error' LIMIT 100")

# Bad: Load everything
all_events: query_memory("SELECT * FROM events")
```

### Security

✅ **Verify script signatures:**

```bash
# Scripts should include signature
# @signature: d8eb959fcec6ae177969f955c8a5242f...
```

✅ **Avoid hardcoded credentials:**

```aether
# Bad
password: "secret123"

# Good
credentials: load_secure_config("credentials")
```

✅ **Validate external inputs:**

```aether
external: fetch_external_data()

if not validate_schema(external):
  log("Invalid external data schema")
  stop_execution()
```

---

## Debugging

### Enable Verbose Logging

```bash
# Run with verbose output
python aether.py my_script.aether -v

# Or set environment variable
export AETHERRA_LOG_LEVEL=DEBUG
python aether.py my_script.aether
```

### Check Script Syntax

```bash
# Validate without executing
python tools/verify_aether_scripts.py my_script.aether
```

### Inspect Variable Values

```aether
# Add debug output
data: fetch_data()
log("Data received:", data)
log("Data length:", len(data))

# Continue processing
processed: process(data)
```

### Common Errors

**SyntaxError: Invalid indentation**

```aether
# Bad
if condition:
result: "yes"  # Wrong indentation

# Good
if condition:
  result: "yes"  # Correct indentation
```

**NameError: Undefined variable**

```aether
# Bad
result: process(undefined_var)  # Variable not defined

# Good
data: fetch_data()
result: process(data)  # Variable defined first
```

**PluginError: Plugin not found**

```bash
# Check available plugins
python -c "from aetherra_plugin_discovery import discover_plugins; print(discover_plugins())"
```

---

## Related Documentation

- [Aether Script Language System](Aether_Script_Language_System.md) - Complete language spec
- [PLUGIN_DEVELOPMENT_GUIDE.md](./PLUGIN_DEVELOPMENT_GUIDE.md) - Create custom plugins
- [AETHERRA_MEMORY_SYSTEM.md](./AETHERRA_MEMORY_SYSTEM.md) - Memory operations
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Script troubleshooting
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Test your scripts

---

## Next Steps

1. **Try the examples** - Run the example scripts in `workflows/`
2. **Write your first script** - Create a simple health check workflow
3. **Explore plugins** - Discover available plugins and their capabilities
4. **Read the spec** - Dive deeper into language features
5. **Join the community** - Share your scripts and learn from others

---

Status: ✅ Complete - Comprehensive Aether Script tutorial from basics to advanced

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
