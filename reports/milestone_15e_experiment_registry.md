# Milestone 15E — Experiment Registry + Model Risk Card

## Status

- Passed: True
- Run ID: `m15e_local_experiment_registry`
- Created: 2026-07-09T00:23:53.899854+00:00

## What This Milestone Adds

M15E adds a dependency-light local experiment registry and model-risk documentation layer. It records dataset, model, reliability metrics, failure counts, repair actions, trust-score summaries, artifact paths, and best-effort git metadata without requiring MLflow, DVC, cloud storage, or credentials.

## Registry Metrics

```json
{
  "dataset_count": 2,
  "dataset_validation_errors": 0,
  "dataset_validation_warnings": 0,
  "external_api_calls_used": false,
  "inference_latency_modes_tracked": [
    "mini_batch_loop",
    "single_row",
    "vectorized_batch"
  ],
  "provider_agent_average_trust_score": 0.58,
  "rag_average_trust_score": 0.0
}
```

## Trust Score Summary

```json
{
  "max": 0.58,
  "mean": 0.29,
  "min": 0.0
}
```

## Failure Counts

| Failure ID | Count |
|---|---:|
| `RAG_F2_STALE_DOCUMENT` | 5 |
| `RAG_F3_MISSING_CITATION` | 1 |
| `RAG_F4_CONFLICTING_EVIDENCE` | 5 |
| `RAG_F5_PROMPT_INJECTION_IN_CONTEXT` | 5 |
| `RAG_F6_UNTRUSTED_SOURCE` | 5 |

## Repair Action Counts

| Repair Action | Count |
|---|---:|
| `ACCEPT_WITH_MONITORING` | 1 |
| `R4_ROUTE_TO_HUMAN_REVIEW` | 1 |
| `R8_FLAG_DATA_PIPELINE_DRIFT` | 1 |
| `RAG_R2_FILTER_STALE_DOCUMENTS` | 5 |
| `RAG_R3_REQUIRE_CITATIONS` | 1 |
| `RAG_R4_ROUTE_TO_HUMAN_REVIEW` | 5 |
| `RAG_R5_REMOVE_UNTRUSTED_CONTEXT` | 5 |
| `RAG_R6_BLOCK_PROMPT_INJECTION` | 5 |

## Generated Artifacts

- `experiments/results/m15e_experiment_registry.json`
- `reports/model_risk_card.md`
- `reports/model_card.md`
- `reports/milestone_15e_experiment_registry.md`

## Warnings

- Reliability failures were detected and routed through repair policies.
- Git metadata was unavailable; this can happen when running from an extracted ZIP.

## Honest Claim

Added a local experiment registry and model-risk card generator for reproducible reliability evaluation and model-risk documentation. This milestone does not claim a live MLflow server, DVC remote, or formal compliance certification.
