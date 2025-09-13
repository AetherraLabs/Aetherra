# Aetherra Metrics Reference

> Consolidated catalog of Prometheus metrics exposed by the Hub / Kernel / Orchestrator / Memory (QFAC) subsystems.
>
> Format: `metric_name` — TYPE — Description (Key related env or notes)

## Chat / Streaming

| Metric                                                | Type              | Description                                                  | Key Env / Notes                        |
| ----------------------------------------------------- | ----------------- | ------------------------------------------------------------ | -------------------------------------- |
| aetherra_chat_requests_total                          | counter           | Total chat (ask + stream) requests processed                 | Incremented at request ingress         |
| aetherra_chat_streams_current                         | gauge             | Active SSE streaming connections                             | Decremented on stream close            |
| aetherra_chat_streams_current_by_principal{principal} | gauge             | Active streams per principal                                 | Cardinality bounded by active users    |
| aetherra_chat_latency_ms_sum / _count / _bucket{le}   | counter/histogram | Response latency distribution (ask path & finalization time) | Buckets: 50…5000 ms                    |
| aetherra_chat_ttft_ms_sum / _count / _bucket{le}      | counter/histogram | Time-to-first-token (TTFT) distribution (future expansion)   | Buckets: 50…2000 ms                    |
| aetherra_chat_chars_in_total                          | counter           | Cumulative input characters                                  | Heuristic length of prompt             |
| aetherra_chat_chars_out_total                         | counter           | Cumulative output characters                                 |                                        |
| aetherra_chat_tokens_in_total                         | counter           | Approximate input tokens                                     | Heuristic tokenizer; non-authoritative |
| aetherra_chat_tokens_out_total                        | counter           | Approximate output tokens                                    |                                        |
| aetherra_chat_chunks_total                            | counter           | SSE chunk events emitted                                     | Excludes status/policy/usage/final     |
| aetherra_chat_fallback_total{path}                    | counter           | Model fallback path counts (mock\|cached\|engine)            | Mock path also tracked via delta logic |
| aetherra_chat_resume_gaps_total                       | counter           | SSE resume gap detections (missed events replayed)           | Driven by Last-Event-ID replay scan    |
| aetherra_chat_soft_timeouts_total                     | counter           | Streams terminated by soft timeout window                    | AETHERRA_STREAM_SOFT_TIMEOUT_S         |
| aetherra_chat_breaker_open_total                      | counter           | Circuit breaker / timeout error finalizations                | Engine-level faults/latency guards     |
| aetherra_chat_auth_missing_token_total                | counter           | Requests lacking required token (prod)                       | AETHERRA_AI_API_REQUIRE_TOKEN=1        |
| aetherra_chat_auth_invalid_token_total                | counter           | Provided token rejected                                      | Future enforcement                     |
| aetherra_hmr_denied_total                             | counter           | HMR enable attempts denied                                   | Production safety guard                |
| aetherra_hmr_denied_reasons_total{reason}             | counter           | HMR deny counts by reason                                    | reason label (configuration cause)     |
| aetherra_chat_fallback_mock_total                     | counter           | Aggregate mock fallback counter (stable baseline)            | Derived from internal delta            |
| aetherra_chat_latency_count                           | counter           | Latency observations (paired with latency_ms_sum)            | Histogram aggregate                    |
| aetherra_chat_ttft_count                              | counter           | TTFT observations (paired with ttft_ms_sum)                  | Histogram aggregate                    |
| aetherra_chat_hmr_denied_total                        | counter           | (Alias) HMR denied attempts (chat export naming)             | Mirrors aetherra_hmr_denied_total      |

## Kernel / Scheduling

| Metric                                                   | Type      | Description                                          | Key Env / Notes                           |
| -------------------------------------------------------- | --------- | ---------------------------------------------------- | ----------------------------------------- |
| aetherra_kernel_uptime_seconds                           | gauge     | Kernel uptime (best-effort)                          | Derived from status snapshot              |
| aetherra_kernel_cycle_time_ms_bucket{le}                 | histogram | Rolling kernel loop iteration time                   | Buckets: 10..1000ms +Inf                  |
| aetherra_kernel_queue_size{queue}                        | gauge     | Pending tasks per priority queue                     | Values: high / normal / background        |
| aetherra_kernel_plugin_invoke_timeout_sec                | gauge     | Effective per-plugin invocation timeout (post clamp) | Guard rails enforce max                   |
| aetherra_kernel_backpressure_guard_pass                  | gauge     | 1 if backpressure guard passed                       | Fails when queue thresholds exceeded      |
| aetherra_kernel_backpressure_guard_violations{violation} | gauge     | Backpressure violation types (value=1)               | Low-cardinality flags                     |
| aetherra_kernel_night_schedule_guard_pass                | gauge     | 1 if explicit night TZ configured (prod/staging)     | AETHERRA_NIGHT_TZ or AETHERRA_NIGHT_UTC=1 |

## Orchestrator / Agents

| Metric                                           | Type      | Description                        | Key Env / Notes      |
| ------------------------------------------------ | --------- | ---------------------------------- | -------------------- |
| aetherra_orchestrator_task_latency_ms_bucket{le} | histogram | Observed task latency distribution | Buckets: 10..2000 ms |
| aetherra_orchestrator_agents_total               | gauge     | Total registered agents            | Dynamic              |
| aetherra_orchestrator_tasks_pending_total        | gauge     | Pending orchestrator tasks         | Backlog indicator    |

## Memory / Quantum (QFAC) & Audit

| Metric                                  | Type  | Description                                          | Key Env / Notes                        |
| --------------------------------------- | ----- | ---------------------------------------------------- | -------------------------------------- |
| aetherra_memory_coherence_score         | gauge | Current coherence (EMA)                              | AETHERRA_QFAC_COHERENCE_EMA fallback   |
| aetherra_memory_branches_total          | gauge | Branch count                                         |                                        |
| aetherra_memory_fragments_total         | gauge | Fragment count                                       |                                        |
| aetherra_memory_branch_nodes_total      | gauge | Audit graph node count                               | From memory audit snapshot             |
| aetherra_memory_branch_edges_total      | gauge | Audit graph edge count                               |                                        |
| aetherra_qfac_policy_mode_current       | gauge | Effective QFAC mode (0=classical,1=hybrid,2=quantum) | AETHERRA_QFAC_MODE requested vs gating |
| aetherra_qfac_policy_allowed            | gauge | 1 if requested mode allowed; 0 if downgraded         | Policy enforce vs shadow               |
| aetherra_qfac_policy_info{key="reason"} | gauge | Downgrade / decision reason (value=1)                | Labels: reason, policy                 |
| aetherra_qfac_policy_info{key="policy"} | gauge | Active policy mode (enforce\|shadow\|off)            | AETHERRA_QFAC_POLICY                   |

## Trainer / Evaluation

| Metric                              | Type    | Description                                | Key Env / Notes                 |
| ----------------------------------- | ------- | ------------------------------------------ | ------------------------------- |
| aetherra_trainer_enabled            | gauge   | Trainer subsystem enabled                  | AETHERRA_TRAINER_ENABLED        |
| aetherra_trainer_jobs_total{state}  | counter | Cumulative trainer jobs by lifecycle state | queued/running/completed/failed |
| aetherra_trainer_jobs_running       | gauge   | Currently running jobs                     |                                 |
| aetherra_trainer_eval_runs_total    | counter | Total evaluation runs                      |                                 |
| aetherra_trainer_evals_total{state} | counter | Evaluation jobs by state                   | queued/running/completed/failed |
| aetherra_trainer_eval_last_score    | gauge   | Last evaluation score                      | 0 if none                       |

## Consciousness / Identity (New)

See `CONSCIOUSNESS_UNIFIED_IDENTITY.md` for conceptual context.

| Metric                                                         | Type        | Description                                                              | Notes / Alert Hints                                    |
| -------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------ |
| aetherra_consciousness_narrative_coherence                     | gauge       | Heuristic topical + coverage + gap composite (0–1)                       | Low (<0.4) may signal fragmented event flow            |
| aetherra_consciousness_identity_coherence                      | gauge       | First-person usage ratio in recent narrative/thought/action events (0–1) | Sustained <0.7 => perspective drift investigation      |
| aetherra_consciousness_workspace_queue_size                    | gauge       | Current workspace candidate queue size                                   | Sudden spikes + latency hist increase => backpressure  |
| aetherra_consciousness_narrative_chapters_total                | gauge(cntr) | Total narrative chapters generated (monotonic)                           | Growth halt while events continue => stalled generator |
| aetherra_consciousness_workspace_candidates_total{source}      | counter     | Workspace candidates added by source                                     | Unexpected source surge => noisy producer              |
| aetherra_consciousness_workspace_broadcasts_total{source}      | counter     | Broadcasts delivered by source                                           | Candidates >> broadcasts => latency/backpressure       |
| aetherra_consciousness_workspace_latency_seconds_bucket{le}    | histogram   | Time from candidate add → broadcast (s)                                  | 95th >0.5s sustained => investigate queue contention   |
| aetherra_consciousness_narrative_generation_seconds_bucket{le} | histogram   | Narrative chapter generation duration (s)                                | 95th >0.25s sustained => summarization inefficiency    |

Example alert sketches:

| Condition                     | Rule Sketch                                                                                                                                          |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Identity coherence drift      | `avg_over_time(aetherra_consciousness_identity_coherence[10m]) < 0.7`                                                                                |
| Narrative stalled             | `increase(aetherra_consciousness_narrative_chapters_total[15m]) == 0 and sum(increase(aetherra_consciousness_workspace_candidates_total[15m])) > 10` |
| Workspace latency spike       | `histogram_quantile(0.95, sum by (le) (rate(aetherra_consciousness_workspace_latency_seconds_bucket[5m]))) > 0.5`                                    |
| Narrative generation slowdown | `histogram_quantile(0.95, sum by (le) (rate(aetherra_consciousness_narrative_generation_seconds_bucket[5m]))) > 0.25`                                |

### Example Scrape Excerpt

```text
# HELP aetherra_consciousness_identity_coherence First-person usage ratio in recent narrative/thought/action events (0-1)
# TYPE aetherra_consciousness_identity_coherence gauge
aetherra_consciousness_identity_coherence 0.91
# HELP aetherra_consciousness_narrative_coherence Latest narrative coherence index (0-1)
# TYPE aetherra_consciousness_narrative_coherence gauge
aetherra_consciousness_narrative_coherence 0.74
# HELP aetherra_consciousness_workspace_queue_size Current workspace candidate queue size
# TYPE aetherra_consciousness_workspace_queue_size gauge
aetherra_consciousness_workspace_queue_size 3
# TYPE aetherra_consciousness_workspace_latency_seconds histogram
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.001"} 2
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.005"} 4
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.01"} 5
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.02"} 5
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.05"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.1"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.25"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="0.5"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="1"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="2"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="5"} 6
aetherra_consciousness_workspace_latency_seconds_bucket{le="+Inf"} 6
aetherra_consciousness_workspace_latency_seconds_count 6
aetherra_consciousness_workspace_latency_seconds_sum 0.013
# TYPE aetherra_consciousness_narrative_generation_seconds histogram
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.005"} 1
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.01"} 2
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.02"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.05"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.1"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.25"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="0.5"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="1"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="2"} 3
aetherra_consciousness_narrative_generation_seconds_bucket{le="+Inf"} 3
aetherra_consciousness_narrative_generation_seconds_count 3
aetherra_consciousness_narrative_generation_seconds_sum 0.017
# TYPE aetherra_consciousness_narrative_chapters_total gauge
aetherra_consciousness_narrative_chapters_total 3
# TYPE aetherra_consciousness_workspace_candidates_total counter
aetherra_consciousness_workspace_candidates_total{source="narrative_layer"} 9
# TYPE aetherra_consciousness_workspace_broadcasts_total counter
aetherra_consciousness_workspace_broadcasts_total{source="narrative_layer"} 9
```


## Security / Keys / Overrides

| Metric                                  | Type  | Description                                   | Key Env / Notes                                             |
| --------------------------------------- | ----- | --------------------------------------------- | ----------------------------------------------------------- |
| aetherra_keys_encrypted                 | gauge | 1 if `keys.json` in encrypted layout          | __encrypted__ flag present                                  |
| aetherra_master_key_present             | gauge | 1 if master key (env or file) present         | AETHERRA_KEYS_MASTER or file path                           |
| aetherra_unsafe_override_present        | gauge | 1 if any unsafe override is set               | Checks AETHERRA_PROD_UNSAFE_ALLOW, AETHERRA_ALLOW_UNBOUNDED |
| aetherra_unsafe_override_info{override} | gauge | Individual unsafe override presence (value=1) | override label                                              |

## Export / Meta

| Metric                                | Type  | Description                                 | Notes                             |
| ------------------------------------- | ----- | ------------------------------------------- | --------------------------------- |
| aetherra_hub_export_timestamp_seconds | gauge | Exporter UTC timestamp at scrape generation | Useful for stale scrape detection |

## Interpretation Notes

- All counters are monotonic within process lifetime; restarts reset to zero.
- Histogram `_bucket` series are cumulative as per Prometheus exposition format.
- Info series (e.g., `*_info`) use value=1 with key/value encoded as labels to keep cardinality bounded.
- Some metrics are *best-effort* (e.g., coherence score) and may be absent if the underlying subsystem is offline.

## Alerting Suggestions (Examples)

| Condition                         | Rule Sketch                                                                                             |
| --------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Frequent stream soft timeouts     | `increase(aetherra_chat_soft_timeouts_total[5m]) > 5`                                                   |
| QFAC downgrades sustained         | `avg_over_time(aetherra_qfac_policy_allowed[10m]) < 0.5 and ON() aetherra_qfac_policy_mode_current > 0` |
| Missing explicit night TZ in prod | `aetherra_kernel_night_schedule_guard_pass == 0 and on() (env:prod)` (env label added externally)       |
| Resume gaps spike                 | `increase(aetherra_chat_resume_gaps_total[1h]) > 10`                                                    |
| Unsafe override triggered         | `aetherra_unsafe_override_present == 1`                                                                 |

## Related Environment Variables (Quick Set)

```bash
# QFAC
AETHERRA_QFAC_MODE=hybrid
AETHERRA_QFAC_POLICY=enforce
AETHERRA_QFAC_BACKEND=qiskit
AETHERRA_QFAC_VALIDATED=1
AETHERRA_QFAC_COHERENCE_EMA=0.91

# Night cycle
AETHERRA_NIGHT_TZ=UTC
# or: AETHERRA_NIGHT_UTC=1

# SSE replay / soft timeout
AETHERRA_SSE_REPLAY_MAX_EVENTS=50
AETHERRA_SSE_REPLAY_MAX_AGE_S=120
AETHERRA_STREAM_SOFT_TIMEOUT_S=15

# Keys
AETHERRA_KEYS_MASTER=change_me_master_key_material
```

---
*This reference is generated manually; keep synchronized with code changes to `metrics_accum.py`.*
