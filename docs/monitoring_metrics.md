# Monitoring Metrics Export

Milestone 16 adds monitoring-ready artifacts for FailSafeML-X reliability metrics.
It exports a dependency-free Prometheus text-format example and a Grafana dashboard JSON skeleton.

## Why this belongs in FailSafeML-X

A reliability layer is only useful if its warnings can be observed over time. This milestone prepares metrics for tracking unsafe auto-decision risk, trust score trends, drift/OOD warnings, dataset validation errors, RAG reliability failures, repair actions, and external-provider safety status.

## Metrics

The local exporter includes:

- `failsafemlx_unsafe_auto_decision_rate`
- `failsafemlx_average_trust_score`
- `failsafemlx_drift_warning_count`
- `failsafemlx_ood_warning_count`
- `failsafemlx_human_review_rate`
- `failsafemlx_repair_action_count`
- `failsafemlx_provider_external_call_blocked_count`
- `failsafemlx_provider_external_api_call_used_count`
- `failsafemlx_dataset_validation_error_count`
- `failsafemlx_dataset_validation_warning_count`
- `failsafemlx_rag_failure_count`

## Artifacts

- `monitoring/prometheus_metrics_example.txt`
- `monitoring/grafana_dashboard_spec.json`
- `reports/milestone_16_monitoring_metrics.md`
- `experiments/results/m16_monitoring_metrics.json`

## Run

```bash
python scripts/run_m16_monitoring_metrics.py
python scripts/local_ci.py
```

## Honest limitations

This milestone does not start a live Prometheus server, Grafana server, Kubernetes service monitor, or production alerting stack. It creates locally validated monitoring-ready artifacts that can later be wired into real infrastructure.
