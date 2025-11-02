# Aetherra Metrics and Monitoring Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide covers comprehensive monitoring and observability for Aetherra OS deployments. Learn how to instrument, collect, visualize, and alert on system metrics.

## Purpose and Scope

- Set up Prometheus metrics collection
- Create Grafana dashboards for visualization
- Configure alerts and notifications
- Monitor system health and performance
- Analyze trends and capacity planning
- Implement observability best practices

## What is Monitoring in Aetherra?

**Monitoring** provides real-time visibility into Aetherra OS operations:

- **Metrics Collection** - Gather quantitative measurements
- **Visualization** - Display metrics in dashboards
- **Alerting** - Notify teams of anomalies
- **Diagnostics** - Investigate performance issues
- **Capacity Planning** - Predict future resource needs

### Key Monitoring Areas

| Area                 | Metrics                     | Purpose                   |
| -------------------- | --------------------------- | ------------------------- |
| **System Health**    | CPU, memory, disk           | Infrastructure monitoring |
| **API Performance**  | Latency, throughput, errors | Service quality           |
| **Memory System**    | Events, queries, size       | Memory health             |
| **Self-Improvement** | Tasks, success rate         | Learning progress         |
| **Homeostasis**      | Status, interventions       | System stability          |
| **Plugins**          | Executions, failures        | Plugin health             |

---

## Quick Start

### Minimal Monitoring Setup (5 Minutes)

**1. Enable metrics in config.json:**

```json
{
  "monitoring": {
    "enabled": true,
    "prometheus_port": 9090,
    "metrics_path": "/metrics"
  }
}
```

**2. Start Aetherra with metrics:**

```bash
python aetherra_os_launcher.py --mode full
```

**3. View metrics:**

```bash
curl http://localhost:9090/metrics
```

**4. Check metric availability:**

```bash
# Test metrics endpoint
curl -s http://localhost:9090/metrics | grep aetherra_

# Sample output:
# aetherra_api_requests_total{method="GET",endpoint="/health"} 42
# aetherra_memory_events_total{type="user_interaction"} 128
# aetherra_homeostasis_status{status="active"} 1
```

---

## Metrics Architecture

### Metrics Flow

```
┌──────────────────────────────────────────────────────────┐
│                   Metrics Pipeline                        │
└──────────────────────────────────────────────────────────┘

1. INSTRUMENTATION
   ├─ Code instruments operations
   ├─ Metrics emitted to collectors
   └─ Local aggregation

2. COLLECTION
   ├─ Prometheus scrapes endpoints
   ├─ Time-series storage
   └─ Data retention policies

3. QUERYING
   ├─ PromQL queries
   ├─ Aggregations and functions
   └─ API access

4. VISUALIZATION
   ├─ Grafana dashboards
   ├─ Real-time graphs
   └─ Custom panels

5. ALERTING
   ├─ Alert rule evaluation
   ├─ Notification routing
   └─ Incident tracking
```

### Metric Types

**Counter** - Monotonically increasing value:
```python
# Example: Total API requests
aetherra_api_requests_total{endpoint="/chat"} 1542
```

**Gauge** - Value that can increase or decrease:
```python
# Example: Current memory usage
aetherra_memory_bytes{type="events"} 134217728
```

**Histogram** - Distribution of values:
```python
# Example: Request latencies
aetherra_request_duration_seconds_bucket{le="0.1"} 450
aetherra_request_duration_seconds_bucket{le="0.5"} 890
aetherra_request_duration_seconds_sum 245.3
aetherra_request_duration_seconds_count 1000
```

**Summary** - Similar to histogram with quantiles:
```python
# Example: Response time quantiles
aetherra_response_time{quantile="0.5"} 0.12
aetherra_response_time{quantile="0.95"} 0.45
aetherra_response_time{quantile="0.99"} 1.2
```

---

## Prometheus Setup

### Installation

**Docker:**

```bash
docker run -d \
  --name prometheus \
  -p 9091:9090 \
  -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**Direct Install (Linux):**

```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Create config
cat > prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aetherra'
    static_configs:
      - targets: ['localhost:9090']
EOF

# Start Prometheus
./prometheus --config.file=prometheus.yml
```

### Prometheus Configuration

**prometheus.yml:**

```yaml
global:
  scrape_interval: 15s      # Scrape targets every 15 seconds
  evaluation_interval: 15s   # Evaluate rules every 15 seconds
  external_labels:
    cluster: 'aetherra-prod'
    environment: 'production'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

# Rule files
rule_files:
  - "rules/*.yml"

# Scrape configurations
scrape_configs:
  # Aetherra OS metrics
  - job_name: 'aetherra_os'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Aetherra Hub API
  - job_name: 'aetherra_hub'
    static_configs:
      - targets: ['localhost:3001']
    metrics_path: '/api/metrics'
    scrape_interval: 15s

  # Service Registry
  - job_name: 'service_registry'
    static_configs:
      - targets: ['localhost:3030']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

# Storage configuration
storage:
  tsdb:
    path: /prometheus/data
    retention.time: 30d
    retention.size: 10GB
```

### Alert Rules

**rules/aetherra_alerts.yml:**

```yaml
groups:
  - name: aetherra_critical
    interval: 30s
    rules:
      # API Error Rate Alert
      - alert: HighAPIErrorRate
        expr: |
          rate(aetherra_api_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate detected"
          description: "API error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      # Memory System Alert
      - alert: MemorySystemDown
        expr: |
          aetherra_memory_healthy{} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Memory system is unhealthy"
          description: "Memory system health check failing for 2 minutes"

      # Homeostasis Inactive Alert
      - alert: HomeostasisInactive
        expr: |
          aetherra_homeostasis_status{status="active"} == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Homeostasis system inactive"
          description: "Homeostasis has been inactive for 10 minutes"

      # Disk Space Alert
      - alert: LowDiskSpace
        expr: |
          (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space below 10% ({{ $value | humanizePercentage }} remaining)"

      # High Memory Usage Alert
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage above 90% for 10 minutes"

  - name: aetherra_performance
    interval: 1m
    rules:
      # Slow API Response Alert
      - alert: SlowAPIResponses
        expr: |
          histogram_quantile(0.95, rate(aetherra_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API responses detected"
          description: "P95 latency is {{ $value | humanizeDuration }} (threshold: 1s)"

      # Plugin Execution Failures
      - alert: PluginExecutionFailures
        expr: |
          rate(aetherra_plugin_executions_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High plugin failure rate"
          description: "Plugin failure rate: {{ $value | humanizePercentage }}"
```

### PromQL Query Examples

**API Request Rate:**
```promql
# Requests per second by endpoint
rate(aetherra_api_requests_total[5m])

# Requests per second by method
sum(rate(aetherra_api_requests_total[5m])) by (method)

# Top 5 endpoints by request count
topk(5, rate(aetherra_api_requests_total[5m]))
```

**Error Rates:**
```promql
# Overall error rate
rate(aetherra_api_errors_total[5m]) / rate(aetherra_api_requests_total[5m])

# Error rate by endpoint
sum(rate(aetherra_api_errors_total[5m])) by (endpoint)
  / sum(rate(aetherra_api_requests_total[5m])) by (endpoint)
```

**Latency Analysis:**
```promql
# P50, P95, P99 latencies
histogram_quantile(0.50, rate(aetherra_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(aetherra_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(aetherra_request_duration_seconds_bucket[5m]))

# Average latency
rate(aetherra_request_duration_seconds_sum[5m])
  / rate(aetherra_request_duration_seconds_count[5m])
```

**Memory System:**
```promql
# Memory events per second
rate(aetherra_memory_events_total[5m])

# Memory query latency
histogram_quantile(0.95, rate(aetherra_memory_query_duration_bucket[5m]))

# Memory storage size
aetherra_memory_storage_bytes
```

---

## Grafana Setup

### Installation

**Docker:**

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana
```

**Access Grafana:**
- URL: http://localhost:3000
- Default credentials: admin/admin

### Add Prometheus Data Source

1. **Navigate to Configuration → Data Sources**
2. **Click "Add data source"**
3. **Select "Prometheus"**
4. **Configure:**

```yaml
Name: Aetherra Prometheus
URL: http://localhost:9091
Access: Server (default)
Scrape interval: 15s
```

5. **Click "Save & Test"**

### Dashboard Examples

#### 1. System Overview Dashboard

**Dashboard JSON (partial):**

```json
{
  "dashboard": {
    "title": "Aetherra System Overview",
    "tags": ["aetherra", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(aetherra_api_requests_total[5m])",
            "legendFormat": "{{ endpoint }}"
          }
        ],
        "yaxes": [
          {"label": "Requests/sec"}
        ]
      },
      {
        "id": 2,
        "title": "System CPU Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ],
        "options": {
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {"value": 0, "color": "green"},
              {"value": 70, "color": "yellow"},
              {"value": 90, "color": "red"}
            ]
          }
        }
      },
      {
        "id": 3,
        "title": "Memory Events Timeline",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(aetherra_memory_events_total[5m])",
            "legendFormat": "{{ type }}"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Services",
        "type": "stat",
        "targets": [
          {
            "expr": "count(aetherra_service_healthy{status=\"active\"})"
          }
        ]
      }
    ]
  }
}
```

#### 2. API Performance Dashboard

**Key Panels:**

**Request Latency (Heatmap):**
```promql
sum(rate(aetherra_request_duration_seconds_bucket[5m])) by (le)
```

**Throughput (Graph):**
```promql
sum(rate(aetherra_api_requests_total[5m])) by (endpoint)
```

**Error Rate (Single Stat):**
```promql
sum(rate(aetherra_api_errors_total[5m]))
  / sum(rate(aetherra_api_requests_total[5m])) * 100
```

**Top Endpoints (Table):**
```promql
topk(10, sum(rate(aetherra_api_requests_total[5m])) by (endpoint))
```

#### 3. Memory System Dashboard

**Panels:**

```promql
# Event Storage Growth
aetherra_memory_storage_bytes

# Query Performance
histogram_quantile(0.95, rate(aetherra_memory_query_duration_bucket[5m]))

# Events by Type
sum(rate(aetherra_memory_events_total[5m])) by (type)

# Memory Health
aetherra_memory_healthy
```

#### 4. Self-Improvement Dashboard

```promql
# Task Success Rate
sum(rate(aetherra_self_improvement_tasks_total{status="success"}[5m]))
  / sum(rate(aetherra_self_improvement_tasks_total[5m]))

# Active Tasks
aetherra_self_improvement_active_tasks

# Task Duration
histogram_quantile(0.95, rate(aetherra_self_improvement_task_duration_bucket[5m]))

# Learning Progress
aetherra_self_improvement_learning_score
```

---

## Instrumentation Guide

### Adding Metrics to Your Code

**Python metrics instrumentation:**

```python
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# Define metrics
api_requests_total = Counter(
    'aetherra_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'aetherra_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

active_connections = Gauge(
    'aetherra_active_connections',
    'Number of active connections'
)

# Instrument functions
def handle_request(method: str, endpoint: str):
    """Handle API request with metrics."""

    # Track active connections
    active_connections.inc()

    # Measure duration
    start_time = time.time()

    try:
        # Process request
        result = process_request(method, endpoint)
        status = "success"

    except Exception as e:
        status = "error"
        raise

    finally:
        # Record metrics
        duration = time.time() - start_time
        request_duration.labels(endpoint=endpoint).observe(duration)
        api_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        active_connections.dec()

    return result
```

### Context Manager for Metrics

```python
from contextlib import contextmanager
import time

@contextmanager
def track_operation(operation_name: str):
    """Track operation duration and success."""

    operation_duration = Histogram(
        f'aetherra_{operation_name}_duration_seconds',
        f'Duration of {operation_name} operations'
    )

    operation_total = Counter(
        f'aetherra_{operation_name}_total',
        f'Total {operation_name} operations',
        ['status']
    )

    start = time.time()
    status = "success"

    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        duration = time.time() - start
        operation_duration.observe(duration)
        operation_total.labels(status=status).inc()

# Usage
with track_operation("memory_query"):
    results = memory.query(filters)
```

### Decorator for Automatic Instrumentation

```python
from functools import wraps
from prometheus_client import Counter, Histogram
import time

def instrument_function(metric_name: str):
    """Decorator to instrument function calls."""

    counter = Counter(
        f'{metric_name}_total',
        f'Total calls to {metric_name}',
        ['status']
    )

    duration = Histogram(
        f'{metric_name}_duration_seconds',
        f'Duration of {metric_name} calls'
    )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                counter.labels(status=status).inc()
                duration.observe(time.time() - start)

        return wrapper
    return decorator

# Usage
@instrument_function("aetherra_plugin_execute")
def execute_plugin(plugin_name: str, **kwargs):
    # Plugin execution logic
    pass
```

---

## Alerting Configuration

### Alertmanager Setup

**alertmanager.yml:**

```yaml
global:
  resolve_timeout: 5m

  # Email configuration
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@aetherra.example.com'
  smtp_auth_username: 'alerts@aetherra.example.com'
  smtp_auth_password: 'your_password'

  # Slack configuration
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

# Alert routing
route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  receiver: 'default'

  routes:
    # Critical alerts to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true

    # All alerts to Slack
    - match_re:
        severity: '.*'
      receiver: 'slack'

    # Warnings to email
    - match:
        severity: warning
      receiver: 'email'

# Notification receivers
receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'

  - name: 'slack'
    slack_configs:
      - channel: '#aetherra-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true

  - name: 'email'
    email_configs:
      - to: 'ops@example.com'
        headers:
          Subject: 'Aetherra Alert: {{ .GroupLabels.alertname }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        description: '{{ .GroupLabels.alertname }}'

# Alert inhibition (suppress redundant alerts)
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']
```

### Notification Templates

**Slack notification template:**

```yaml
slack_configs:
  - channel: '#aetherra-alerts'
    title: 'Alert: {{ .GroupLabels.alertname }}'
    text: |
      *Severity:* {{ .GroupLabels.severity }}
      *Summary:* {{ .CommonAnnotations.summary }}

      *Details:*
      {{ range .Alerts }}
      • {{ .Annotations.description }}
        _Instance:_ {{ .Labels.instance }}
        _Started:_ {{ .StartsAt }}
      {{ end }}
    actions:
      - type: button
        text: 'View in Prometheus'
        url: '{{ .ExternalURL }}'
      - type: button
        text: 'View in Grafana'
        url: 'http://grafana.example.com/d/alerts'
```

---

## Log Aggregation

### ELK Stack Integration

**Filebeat configuration (filebeat.yml):**

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/aetherra/*.log
    fields:
      service: aetherra_os
      environment: production
    multiline:
      pattern: '^\d{4}-\d{2}-\d{2}'
      negate: true
      match: after

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "aetherra-logs-%{+yyyy.MM.dd}"

setup.kibana:
  host: "localhost:5601"

logging.level: info
```

### Structured Logging for Metrics

```python
import logging
import json
from datetime import datetime

class MetricsLogger:
    """Logger with structured metrics output."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def log_metric(self, metric_name: str, value: float,
                   labels: dict = None, level: str = "info"):
        """Log structured metric."""

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "metric": metric_name,
            "value": value,
            "labels": labels or {},
            "type": "metric"
        }

        log_func = getattr(self.logger, level)
        log_func(json.dumps(entry))

# Usage
metrics_logger = MetricsLogger("aetherra_hub")
metrics_logger.log_metric(
    "api_request_duration",
    0.234,
    labels={"endpoint": "/chat", "method": "POST"}
)
```

---

## Monitoring Best Practices

### 1. The Four Golden Signals

Monitor these critical metrics:

**Latency** - How long requests take:
```promql
histogram_quantile(0.95, rate(aetherra_request_duration_seconds_bucket[5m]))
```

**Traffic** - How much demand on the system:
```promql
sum(rate(aetherra_api_requests_total[5m]))
```

**Errors** - Rate of failed requests:
```promql
sum(rate(aetherra_api_errors_total[5m])) / sum(rate(aetherra_api_requests_total[5m]))
```

**Saturation** - How "full" the service is:
```promql
aetherra_active_connections / aetherra_max_connections
```

### 2. SLI/SLO Tracking

**Define Service Level Indicators:**

```yaml
# SLI: API availability
- record: sli:aetherra_api:availability:5m
  expr: |
    sum(rate(aetherra_api_requests_total{status!~"5.."}[5m]))
    / sum(rate(aetherra_api_requests_total[5m]))

# SLI: API latency
- record: sli:aetherra_api:latency:5m
  expr: |
    histogram_quantile(0.95, rate(aetherra_request_duration_seconds_bucket[5m]))

# SLO: 99.9% availability
- alert: SLOViolation_Availability
  expr: sli:aetherra_api:availability:5m < 0.999
  for: 5m

# SLO: P95 latency < 500ms
- alert: SLOViolation_Latency
  expr: sli:aetherra_api:latency:5m > 0.5
  for: 5m
```

### 3. Metric Naming Conventions

Follow consistent naming:

```python
# Pattern: <namespace>_<subsystem>_<metric>_<unit>
aetherra_api_requests_total           # Counter
aetherra_memory_storage_bytes         # Gauge
aetherra_request_duration_seconds     # Histogram
aetherra_plugin_executions_total      # Counter

# Use labels for dimensions
aetherra_api_requests_total{method="GET", endpoint="/health", status="200"}
```

### 4. Alert Severity Levels

**Critical** - Immediate action required:
- Service down
- Data loss imminent
- Security breach

**Warning** - Investigate soon:
- High resource usage
- Elevated error rates
- Performance degradation

**Info** - For awareness:
- Deployment events
- Configuration changes
- Routine maintenance

---

## Troubleshooting Monitoring

### Metrics Not Appearing

**Check endpoint:**
```bash
curl http://localhost:9090/metrics
```

**Verify Prometheus scrape:**
```bash
# Check Prometheus targets
curl http://localhost:9091/api/v1/targets | jq '.data.activeTargets[] | {job, health, lastError}'
```

**Check logs:**
```bash
# Aetherra logs
tail -f logs/aetherra_os.log | grep -i metric

# Prometheus logs
docker logs prometheus
```

### High Cardinality Issues

**Problem:** Too many unique label combinations

**Solution:** Limit label values

```python
# Bad: Unbounded cardinality
counter.labels(user_id=user_id).inc()

# Good: Bounded cardinality
counter.labels(user_type=user_type).inc()
```

### Missing Historical Data

**Check retention:**
```yaml
# prometheus.yml
storage:
  tsdb:
    retention.time: 30d  # Increase if needed
```

---

## Related Documentation

- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Debug issues
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production setup
- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - API metrics
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Test monitoring
- [SECURITY_OPERATIONS_GUIDE.md](./SECURITY_OPERATIONS_GUIDE.md) - Security metrics

---

Status: ✅ Complete - Comprehensive monitoring and metrics guide with Prometheus, Grafana, and alerting

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
