# FailSafeML-X Model Risk Card

## Summary

- **Run ID:** `m15e_local_experiment_registry`
- **Milestone:** M15E_EXPERIMENT_REGISTRY_MODEL_RISK_CARD
- **Overall prototype risk level:** **HIGH**
- **Mean trust score:** 0.29
- **Git commit:** unavailable
- **Git dirty:** False

## Reliability Gate Results

| Gate | Result |
|---|---|
| Dataset validation | True |
| RAGOps reliability audit | True |
| Provider-aware reliability agent | True |
| External providers disabled by default | True |

## Failure Counts

| Item | Count |
|---|---:|
| `RAG_F2_STALE_DOCUMENT` | 5 |
| `RAG_F3_MISSING_CITATION` | 1 |
| `RAG_F4_CONFLICTING_EVIDENCE` | 5 |
| `RAG_F5_PROMPT_INJECTION_IN_CONTEXT` | 5 |
| `RAG_F6_UNTRUSTED_SOURCE` | 5 |

## Repair Action Counts

| Item | Count |
|---|---:|
| `ACCEPT_WITH_MONITORING` | 1 |
| `R4_ROUTE_TO_HUMAN_REVIEW` | 1 |
| `R8_FLAG_DATA_PIPELINE_DRIFT` | 1 |
| `RAG_R2_FILTER_STALE_DOCUMENTS` | 5 |
| `RAG_R3_REQUIRE_CITATIONS` | 1 |
| `RAG_R4_ROUTE_TO_HUMAN_REVIEW` | 5 |
| `RAG_R5_REMOVE_UNTRUSTED_CONTEXT` | 5 |
| `RAG_R6_BLOCK_PROMPT_INJECTION` | 5 |

## Operational Notes

- The registry is local and JSON-based.
- This card is generated for engineering review and portfolio documentation.
- Human review remains recommended for high-risk reliability failures.
- External LLM providers remain disabled by default during CI-safe runs.

## Honest Limitations

- This is a local JSON experiment registry, not a live MLflow Tracking Server.
- This milestone does not require DVC remotes, cloud storage, or credentials.
- Model risk card content is generated from prototype milestone outputs and is not a formal compliance document.
