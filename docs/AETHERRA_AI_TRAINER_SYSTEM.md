# Aetherra AI Trainer System

Updated: 2025-08-27

This document defines the Aetherra AI Trainer System: the training and evaluation layer that will enable Aetherra OS to fine-tune models, run structured experiments, and evolve capabilities safely over time. It is forward-looking; core training functionality is not yet implemented. This doc establishes contracts and a roadmap so we can build iteratively.

## Purpose and scope

- Provide a reproducible training/evaluation pipeline for models and policies used by Aetherra (LLMs, adapters, classifiers, rerankers)
- Manage datasets, experiment tracking, model registry, and artifact/version lifecycle
- Offer safe tuning methods (SFT, preference optimization, policy shaping) with privacy and security controls
- Integrate with Engine, Memory, Security, and Hub for orchestration and observability

## At‑a‑glance status

- Core trainer services: Planned (orchestrator, job runner, dataset manager)
- Datasets and curation: Planned (dataset registry, curation policies, redaction)
- Training backends: Planned (local adapters + pluggable cloud/HF backends)
- Evaluation harness: Planned (benchmarks, regression suites, safety evals)
- Model registry: Planned (versioning, lineage, rollback)
- Hub/metrics: Planned (training/eval Prometheus series, Hub surfaces)

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

Hub surfaces (planned):

- `/api/trainer/jobs` (list/submit/status), `/api/trainer/evals`, and `/metrics` integration

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

## Roadmap (phased)

1. Scaffolding (this doc + stubs): trainer orchestrator, dataset registry (read-only), model registry (local)
2. Local SFT/LoRA adapter path with a tiny demo dataset and eval harness
3. Safety eval suite + basic scores in `/metrics`
4. Preference optimization (DPO/IPO) and staged rollout hooks
5. Cloud/HF backend adapters and larger-scale orchestration

---

Status: 🔮 Planned — This system is a design blueprint to guide upcoming implementation work.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

