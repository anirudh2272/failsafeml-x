# Milestone 16 — Monitoring Metrics Export

## Objective
Export FailSafeML-X reliability metrics in Prometheus text format and generate a Grafana dashboard specification without requiring live Prometheus or Grafana services.

## Validation Summary
- Passed: `True`
- Metric count: `11`
- Alert recommendation count: `2`
- Prometheus file: `monitoring/prometheus_metrics_example.txt`
- Grafana dashboard spec: `monitoring/grafana_dashboard_spec.json`

## Exported Metrics
| Metric | Value |
|---|---:|
| `failsafemlx_unsafe_auto_decision_rate` | 0.0 |
| `failsafemlx_average_trust_score` | 0.58 |
| `failsafemlx_drift_warning_count` | 0.0 |
| `failsafemlx_ood_warning_count` | 0.0 |
| `failsafemlx_human_review_rate` | 0.0 |
| `failsafemlx_repair_action_count` | 24.0 |
| `failsafemlx_provider_external_call_blocked_count` | 1.0 |
| `failsafemlx_provider_external_api_call_used_count` | 0.0 |
| `failsafemlx_dataset_validation_error_count` | 0.0 |
| `failsafemlx_dataset_validation_warning_count` | 0.0 |
| `failsafemlx_rag_failure_count` | 21.0 |

## Alert Recommendations
| Alert | Severity | Metric | Condition | Recommendation |
|---|---:|---|---|---|
| ALERT_LOW_AVERAGE_TRUST_SCORE | HIGH | `failsafemlx_average_trust_score` | `< 0.60` | Review failure taxonomy outputs and inspect drift/OOD or RAG evidence quality before expanding automation. |
| ALERT_RAG_RELIABILITY_FAILURES | MEDIUM | `failsafemlx_rag_failure_count` | `> 3` | Filter stale or untrusted context, require citations, and rerun retrieval repair checks. |


## Prometheus Preview
```text
# HELP failsafemlx_unsafe_auto_decision_rate Fraction of high-risk predictions that were incorrectly auto-accepted.
# TYPE failsafemlx_unsafe_auto_decision_rate gauge
failsafemlx_unsafe_auto_decision_rate 0
# HELP failsafemlx_average_trust_score Average reliability trust score across audited cases.
# TYPE failsafemlx_average_trust_score gauge
failsafemlx_average_trust_score 0.58
# HELP failsafemlx_drift_warning_count Count of drift-related warnings.
# TYPE failsafemlx_drift_warning_count gauge
failsafemlx_drift_warning_count 0
# HELP failsafemlx_ood_warning_count Count of out-of-distribution warnings.
# TYPE failsafemlx_ood_warning_count gauge
failsafemlx_ood_warning_count 0
# HELP failsafemlx_human_review_rate Fraction of audited cases routed to human review.
# TYPE failsafemlx_human_review_rate gauge
failsafemlx_human_review_rate 0
# HELP failsafemlx_repair_action_count Total recommended repair actions.
# TYPE failsafemlx_repair_action_count gauge
failsafemlx_repair_action_count 24
# HELP failsafemlx_provider_external_call_blocked_count Whether external LLM providers were blocked by default in local validation.
# TYPE failsafemlx_provider_external_call_blocked_count gauge
```

## Honest Limitations
- This milestone creates monitoring-ready artifacts, not a live Prometheus/Grafana deployment.
- Metrics are generated from local milestone outputs and sample validations.
- Production alert thresholds would require calibration against real traffic and business risk tolerance.
