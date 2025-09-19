# Expose /api/selfinc/status + Prom metrics

Labels: phase:1, area:observability, type:feature
Milestone: Self-Incorporation v1

## Description

Expose an HTTP endpoint to surface Self-Incorporation status and Prometheus metrics.

## Acceptance Criteria

- GET /api/selfinc/status returns JSON with counts:
	{found, classified, planned, applied, quarantined}
- Prometheus counters/gauges for the same are exported on /metrics
- Basic error handling documented; 200 OK with payload or clear 5xx on failure
- Minimal unit tests for the endpoint and metrics registry updates

## Notes

- Wire into the existing hub/Flask app if available
- Document env flags in PROJECT_OVERVIEW.md
