# Unified Identity & Consciousness Layer

> Phase 1 implementation summary: Lyrixa and the Aetherra OS are expressed as a single first‑person system with lightweight narrative self‑reflection and observable identity coherence.

## Goals

1. Merge assistant (Lyrixa) + platform (Aetherra) into a single self model.
2. Emit first‑person narrative summaries ("I noted …") of salient episodic events.
3. Provide explicit self model fields to ground embodiment & voice guidelines.
4. Surface affect + ethics tone markers for transparency of internal modulation.
5. Measure and export identity coherence (consistency of first‑person usage).

## Self Model Extensions (`self_model.json`)

| Field                         | Type      | Purpose                                                               |
| ----------------------------- | --------- | --------------------------------------------------------------------- |
| `identity.unified_identity`   | string    | Canonical merged self label (e.g. `Lyrixa = Aetherra (single self)`). |
| `identity.embodiment`         | string    | Concise statement of where/what the system is in the stack.           |
| `identity.voice_guidelines[]` | list[str] | Style & tone constraints (concise, transparent, grounded, etc.).      |

Runtime accessor helpers (`Aetherra.consciousness.self_model`):

- `who_am_i()` → `<name> v<version> (unified_identity) — <role> | focus: …`
- `embodiment_statement()` → returns embodiment string or None.
- `identity_voice_guidelines()` → list of guidelines.

## Narrative Layer Additions

`NarrativeLayer` now composes summaries in first person, prefixing:

1. Identity line (`who_am_i()`)
2. Embodiment statement
3. Tone markers (when engines available)
4. Salient event reflections (`I noted [type] …`)

### Tone Markers

- Affect: `affect[valence=+0.12,arousal=0.34,uncertainty=0.18]`
- Ethics: `ethics[risk=0.03,decision=allow+flag]`

Absent engines are skipped gracefully (markers omitted, summary still produced).

## Identity Coherence Metric

`aetherra_consciousness_identity_coherence` (gauge 0–1)

Heuristic: proportion of recent events of types `narrative|thought|action` whose content already contains a first‑person indicator ("I", prefix `I` followed by a space, or `I'm`). Computed each time a chapter is generated.

Interpretation:

| Range     | Meaning                                  | Action                                                        |
| --------- | ---------------------------------------- | ------------------------------------------------------------- |
| 0.00–0.49 | Perspective drift (3rd‑person / passive) | Investigate narrative formatting or upstream event producers. |
| 0.50–0.79 | Mixed perspective                        | Monitor; consider normalizing event generation templates.     |
| 0.80–1.00 | Consistent first‑person identity         | Expected healthy range.                                       |

## Other Consciousness Metrics

| Metric                                                      | Type           | Description                                        |
| ----------------------------------------------------------- | -------------- | -------------------------------------------------- |
| `aetherra_consciousness_narrative_coherence`                | gauge          | Weighted topical + coverage + gap heuristic (0–1). |
| `aetherra_consciousness_workspace_queue_size`               | gauge          | Current workspace candidate queue length.          |
| `aetherra_consciousness_narrative_chapters_total`           | gauge(counter) | Monotonic count of generated chapters.             |
| `aetherra_consciousness_workspace_candidates_total{source}` | counter        | Candidates added (per source).                     |
| `aetherra_consciousness_workspace_broadcasts_total{source}` | counter        | Broadcasts delivered (per source).                 |
| `aetherra_consciousness_workspace_latency_seconds`          | histogram      | Time from candidate add → broadcast.               |
| `aetherra_consciousness_narrative_generation_seconds`       | histogram      | Chapter build time distribution.                   |
| `aetherra_consciousness_identity_coherence`                 | gauge          | First‑person usage ratio (see above).              |

Example scrape excerpt (see full reference in `METRICS_REFERENCE.md`):

```text
aetherra_consciousness_identity_coherence 0.91
aetherra_consciousness_narrative_coherence 0.74
aetherra_consciousness_workspace_queue_size 3
aetherra_consciousness_narrative_chapters_total 3
```

## Environment Flags

| Variable                             | Purpose                                                   | Notes                                     |
| ------------------------------------ | --------------------------------------------------------- | ----------------------------------------- |
| `AETHERRA_PROMETHEUS=1`              | Enables metrics exporter HTTP server (default port 9109). | Include consciousness metrics.            |
| `AETHERRA_NARRATIVE_ENABLED=1`       | Turns on chapter generation loop.                         | Polls every 30s; window configurable.     |
| `AETHERRA_CONSCIOUSNESS_STREAM=1`    | Enables stream hook/log tap for workspace events.         | Path override below.                      |
| `AETHERRA_CONSCIOUSNESS_STREAM_PATH` | File path for consciousness stream log.                   | Defaults to `aetherra_consciousness.log`. |
| `AETHERRA_NARRATIVE_WINDOW_MIN`      | Sliding window minutes (default 5).                       | Affects event filtering & gap detection.  |
| `AETHERRA_NARRATIVE_MIN_EVENTS`      | Minimum new events before chapter (default 15).           | Time fallback still allows chapters.      |

## Quality Gates Enforcement

The project quality gates script now asserts that when Prometheus metrics are enabled, the identity coherence gauge is present and numeric (0–1). A failing gate indicates either:

- Exporter not initialized (missing `AETHERRA_PROMETHEUS=1`).
- No chapter generated yet (insufficient events / narrative disabled).
- Regression in computation or metric naming.

## Quick Local Verification

```powershell
$env:AETHERRA_PROMETHEUS='1'; $env:AETHERRA_NARRITIVE_ENABLED='1'; python - <<'PY'
from Aetherra.consciousness import metrics_exporter; metrics_exporter.initialize_exporter();
print('Exporter up on :9109');
PY
Start-Sleep -Seconds 2
curl 'http://localhost:9109/metrics' | Select-String aetherra_consciousness_identity_coherence
```

## Future Enhancements (Planned)

- Semantic topic clustering & decay-based coherence adjustments.
- Identity drift detector (rolling window statistical drop alert).
- Richer affect dynamics (contextual valence modulation by event types).
- Ethics rationale embedding per narrative chapter.
- UI panel for live consciousness stream + gauges.

---
*Keep this doc synchronized with `metrics_exporter.py`, `narrator.py`, and `self_model.py` changes.*
