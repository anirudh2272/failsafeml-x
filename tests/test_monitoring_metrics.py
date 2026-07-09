from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from failsafemlx.monitoring.alerts import recommend_alerts
from failsafemlx.monitoring.metrics_exporter import (
    ReliabilityMetric,
    build_grafana_dashboard_spec,
    build_reliability_metrics,
    export_prometheus_metrics,
)


def sample_results() -> dict:
    return {
        "m5": {"after": {"unsafe_auto_decision_rate": 0.08}},
        "m15b": {
            "aggregate": {
                "average_trust_score": 0.72,
                "failure_counts": {"RAG_F3_MISSING_CITATION": 2},
                "repair_action_counts": {"RAG_R3_REQUIRE_CITATIONS": 2},
            }
        },
        "m15c": {"total_errors": 1, "total_warnings": 2},
        "m15d": {
            "average_trust_score": 0.55,
            "external_provider_blocked_by_default": True,
            "external_api_calls_used": False,
            "failure_counts": {"F1_DATA_DRIFT": 1, "F4_OUT_OF_DISTRIBUTION_INPUT": 1},
            "repair_action_counts": {"R8_FLAG_DATA_PIPELINE_DRIFT": 1},
            "human_review_rate": 0.25,
        },
    }


def test_build_reliability_metrics_contains_core_names():
    metrics = build_reliability_metrics(sample_results())
    names = {metric.safe_name() for metric in metrics}
    assert "failsafemlx_unsafe_auto_decision_rate" in names
    assert "failsafemlx_average_trust_score" in names
    assert "failsafemlx_dataset_validation_error_count" in names
    assert "failsafemlx_provider_external_call_blocked_count" in names
    assert len(metrics) >= 8


def test_prometheus_export_is_text_format():
    metrics = build_reliability_metrics(sample_results())
    text = export_prometheus_metrics(metrics)
    assert "# HELP failsafemlx_average_trust_score" in text
    assert "# TYPE failsafemlx_average_trust_score gauge" in text
    assert "failsafemlx_human_review_rate" in text


def test_alerts_trigger_for_risky_metrics():
    metrics = build_reliability_metrics(sample_results())
    alerts = recommend_alerts(metrics)
    alert_ids = {alert.alert_id for alert in alerts}
    assert "ALERT_UNSAFE_AUTO_DECISION_RATE" in alert_ids
    assert "ALERT_LOW_AVERAGE_TRUST_SCORE" in alert_ids
    assert "ALERT_DATASET_VALIDATION_ERRORS" in alert_ids


def test_grafana_dashboard_spec_is_json_compatible():
    metrics = build_reliability_metrics(sample_results())
    dashboard = build_grafana_dashboard_spec(metrics)
    encoded = json.dumps(dashboard)
    assert "FailSafeML-X Reliability Monitoring" in encoded
    assert dashboard["panels"]
    assert dashboard["honest_limitations"]


def test_metric_name_sanitization():
    metric = ReliabilityMetric("bad metric-name", 1, "help")
    assert metric.safe_name() == "failsafemlx_bad_metric_name"


def test_m16_runner_writes_monitoring_outputs():
    subprocess.run([sys.executable, "scripts/run_m16_monitoring_metrics.py"], check=True)
    result_path = Path("experiments/results/m16_monitoring_metrics.json")
    report_path = Path("reports/milestone_16_monitoring_metrics.md")
    prometheus_path = Path("monitoring/prometheus_metrics_example.txt")
    grafana_path = Path("monitoring/grafana_dashboard_spec.json")

    assert result_path.exists()
    assert report_path.exists()
    assert prometheus_path.exists()
    assert grafana_path.exists()

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M16_MONITORING_METRICS_EXPORT"
    assert payload["passed"] is True
    assert payload["metric_count"] >= 8
