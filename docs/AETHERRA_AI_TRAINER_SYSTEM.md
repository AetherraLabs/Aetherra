# Aetherra AI Trainer System

Updated: 2026-06-20

This document defines the Aetherra AI Trainer System: the training and evaluation layer that will enable Aetherra OS to fine-tune models, run structured experiments, and evolve capabilities safely over time. The current implementation is a guarded foundation, not a real training backend.

Status: Functional foundation complete.

Current foundation:

- `GET /api/trainer/status` exposes a read-only Trainer readiness contract and
  legacy metrics fields.
- Guarded in-memory job and evaluation queues exist behind Hub control auth,
  Guardian review, and capability checks.
- Real model training, dataset ingestion/export, model registry writes,
  artifact publishing, and artifact signing are explicitly disabled at this
  foundation stage.
- Disabled-by-default is the safe posture. A disabled trainer still exposes
  status and metrics, but rejects submissions.

## Understanding Rule

Before this system is considered complete, it must be explainable without
looking at the code:

- What it does: exposes a governed trainer scaffold for status, metrics,
  training request intake, and evaluation request intake.
- Why it exists: gives Aetherra a controlled path for future model and policy
  improvement without allowing unreviewed training, dataset use, or model
  promotion.
- Authority it owns: trainer readiness reporting, trainer metrics snapshots,
  and guarded in-memory job/eval queue state.
- Authority it does not own: dataset consent, model promotion, real backend
  training execution, artifact signing, Guardian approval, Security
  enforcement, or Self-Incorporation application.
- How it fails: disabled mode rejects submissions while status remains
  available; Guardian denial returns 403 without queue mutation; auth failures
  stop before payload handling; invalid payloads are rejected before mutation;
  missing real backend support is reported as scaffold-only.
- How it interacts with other systems: Guardian decides whether queue mutation
  is allowed, Security enforces capabilities, Hub exposes status and submit
  routes, future Maintenance can observe outcomes, and future Self-Improvement
  can propose training/evaluation work without directly starting it.

## Purpose and scope

- Provide a reproducible training/evaluation pipeline for models and policies used by Aetherra (LLMs, adapters, classifiers, rerankers)
- Manage datasets, experiment tracking, model registry, and artifact/version lifecycle
- Offer safe tuning methods (SFT, preference optimization, policy shaping) with privacy and security controls
- Integrate with Engine, Memory, Security, and Hub for orchestration and observability

## At‑a‑glance status

- Core trainer services: Functional foundation complete for guarded in-memory
  job/eval queue scaffolding.
- Datasets and curation: Planned; no ingestion/export authority yet.
- Training backends: Planned; real backend execution disabled.
- Evaluation harness: Foundation queue scaffolding only; real benchmark suites
  planned.
- Model registry: Planned; writes disabled.
- Hub/metrics: Functional foundation complete for status and metrics exposure.

## Core components (design)

### 1) Trainer Orchestrator

- Plan, schedule, and monitor training/eval jobs
- Coordinate resources (CPU/GPU), enforce budgets/timeouts, and retry policies

### 2) Dataset Manager

- Dataset registry with metadata (provenance, license, privacy level)
- Curation ops (dedupe, split, filter, redact PII)

### 3) Training Backends

- Local adapters (PyTorch/Transformers) and optional cloud/Hugging Face integrations
- Supports SFT, supervised adapters (LoRA/PEFT), preference optimization (DPO/IPO), and alignment techniques

### 4) Evaluation Harness

- Task/regression suites (accuracy, robustness), safety scores (toxicity, jailbreak resistance), and qualitative inspections
- Report aggregator (JSON + markdown summaries)

### 5) Model Registry

- Versioned models with lineage (base → fine-tuned → adapters) and artifacts (weights, configs, metrics)
- Rollback and staged rollout hooks

### 6) Safety & Privacy Controls

- Data redaction, consent tags, policy gating for sensitive domains
- Differential privacy (optional) and audit trails

## Minimal contracts (draft)

- Training job (input):
  - `{ job_id: str, task: "sft"|"ppo"|"dpo"|"lora", base_model: str, dataset_id: str|list, params?: dict, resources?: { gpus?: int, mem_gb?: int }, tags?: list[str] }`
- Training job status (output):
  - `{ job_id: str, state: "queued"|"running"|"failed"|"completed", progress?: number, metrics?: dict, started_at?: iso8601, finished_at?: iso8601, artifacts?: dict }`
- Evaluation request (input):
  - `{ eval_id: str, model_ref: str, suite: str|list[str], params?: dict }`
- Evaluation report (output):
  - `{ eval_id: str, status: "pending"|"running"|"failed"|"completed", results: { benchmarks: dict, safety: dict, regressions: dict }, summary: string }`
- Model registry entry:
  - `{ id: str, kind: "base"|"adapter"|"merged", version: string, source_model?: string, artifacts: dict, metrics?: dict, created_at: iso8601, lineage?: list[str] }`

Error modes (representative):

- Invalid dataset or missing consent → reject with `error: dataset_invalid`
- Resource limit exceeded → `error: resource_exceeded`
- Backend error (compile/runtime) → `error: backend_failure` with log refs

## Observability (planned)

Prometheus metrics (planned series):

- `aetherra_trainer_jobs_total{state}` — counters per job state
- `aetherra_trainer_jobs_running` — gauge of concurrent running jobs
- `aetherra_trainer_job_duration_seconds` — histogram per task type
- `aetherra_trainer_eval_scores{suite,metric}` — gauges for key eval metrics
- `aetherra_trainer_data_records_total{dataset}` — counters for ingested/filtered records

Hub surfaces:

- `GET /api/trainer/status` - read-only readiness and metrics contract.
- `/api/trainer/jobs` and `/api/trainer/evals` - guarded in-memory queue
  scaffolding when `AETHERRA_TRAINER_ENABLED=1`.
- `/metrics` integration exposes trainer metric series.

## Configuration and environment (draft)

Examples (subject to change as implementation lands):

- `AETHERRA_TRAINER_ENABLED=1` — enable trainer services
- `AETHERRA_TRAINER_BACKEND=local|hf|custom` — select backend
- `AETHERRA_TRAINER_DATA_ROOT=...` — dataset storage root
- `AETHERRA_TRAINER_REGISTRY=...` — model registry path or URL
- `AETHERRA_TRAINER_MAX_JOBS=...` — concurrency limits

## Security & privacy

- PII scrubbing, consent tagging, and policy-enforced dataset usage
- Optional differential privacy during training/eval logging
- Signed model artifacts and provenance records

## Guardian enforcement

Current active trainer surfaces are guarded at the service layer:

- `aetherra_hub.services.trainer.submit_job` declares `trainer.submit_job` before creating job IDs, mutating the in-memory job queue, or starting background transition threads.
- `aetherra_hub.services.trainer.submit_eval` declares `trainer.submit_eval` before creating eval IDs, mutating the in-memory eval queue, or starting background transition threads.
- Hub `/api/trainer/jobs` and `/api/trainer/evals` return HTTP 403 on Guardian denial.
- Audit metadata uses task names, payload shape, parameter/resource keys, tag counts, and hashes for model and dataset references instead of raw model names, dataset IDs, parameter values, resource values, or tags.
- Strict capability mode requires explicit external callers to hold trainer, model, and dataset capabilities before trainer queue mutation.

Remaining Guardian scope:

- Dataset ingestion/export, real backend training start, fine-tune execution, evaluation promotion, adapter deployment, model registry writes, artifact signing, and policy/model replacement must receive Guardian preflight before implementation moves beyond the in-memory scaffold.

## Roadmap (phased)

1. Scaffolding (this doc + stubs): trainer orchestrator, dataset registry (read-only), model registry (local)
2. Local SFT/LoRA adapter path with a tiny demo dataset and eval harness
3. Safety eval suite + basic scores in `/metrics`
4. Preference optimization (DPO/IPO) and staged rollout hooks
5. Cloud/HF backend adapters and larger-scale orchestration

---

Status: Functional foundation complete. Real training backends, dataset
pipelines, model registry writes, artifact signing, and promotion remain future
work and must be added behind Guardian, Security, and explicit approval gates.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

