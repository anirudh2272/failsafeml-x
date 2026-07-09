from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.monitoring.alerts import alerts_to_markdown, recommend_alerts
from failsafemlx.monitoring.metrics_exporter import (
    build_grafana_dashboard_spec,
    build_reliability_metrics,
    export_prometheus_metrics,
)

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"
MONITORING_DIR = PROJECT_ROOT / "monitoring"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def collect_milestone_results() -> dict[str, Any]:
    return {
        "m5": _load_json(RESULTS_DIR / "m5_repair_engine_before_after.json"),
        "m15b": _load_json(RESULTS_DIR / "m15b_ragops_reliability.json"),
        "m15c": _load_json(RESULTS_DIR / "m15c_dataset_validation.json"),
        "m15d": _load_json(RESULTS_DIR / "m15d_provider_agent_integration.json"),
        "m15e": _load_json(RESULTS_DIR / "m15e_experiment_registry.json"),
    }


def generate_report(payload: dict[str, Any], prometheus_text: str, alerts_md: str) -> str:
    metrics = payload["metrics"]
    lines = [
        "# Milestone 16 — Monitoring Metrics Export",
        "",
        "## Objective",
        "Export FailSafeML-X reliability metrics in Prometheus text format and generate a Grafana dashboard specification without requiring live Prometheus or Grafana services.",
        "",
        "## Validation Summary",
        f"- Passed: `{payload['passed']}`",
        f"- Metric count: `{len(metrics)}`",
        f"- Alert recommendation count: `{len(payload['alert_recommendations'])}`",
        f"- Prometheus file: `{payload['artifacts']['prometheus_metrics']}`",
        f"- Grafana dashboard spec: `{payload['artifacts']['grafana_dashboard_spec']}`",
        "",
        "## Exported Metrics",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for item in metrics:
        lines.append(f"| `{item['name']}` | {item['value']} |")
    lines.extend(
        [
            "",
            "## Alert Recommendations",
            alerts_md,
            "",
            "## Prometheus Preview",
            "```text",
            "\n".join(prometheus_text.splitlines()[:20]),
            "```",
            "",
            "## Honest Limitations",
            "- This milestone creates monitoring-ready artifacts, not a live Prometheus/Grafana deployment.",
            "- Metrics are generated from local milestone outputs and sample validations.",
            "- Production alert thresholds would require calibration against real traffic and business risk tolerance.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MONITORING_DIR.mkdir(parents=True, exist_ok=True)

    milestone_results = collect_milestone_results()
    metrics = build_reliability_metrics(milestone_results)
    prometheus_text = export_prometheus_metrics(metrics)
    alerts = recommend_alerts(metrics)
    dashboard_spec = build_grafana_dashboard_spec(metrics)

    prometheus_path = MONITORING_DIR / "prometheus_metrics_example.txt"
    grafana_path = MONITORING_DIR / "grafana_dashboard_spec.json"
    result_path = RESULTS_DIR / "m16_monitoring_metrics.json"
    report_path = REPORTS_DIR / "milestone_16_monitoring_metrics.md"

    prometheus_path.write_text(prometheus_text, encoding="utf-8")
    grafana_path.write_text(json.dumps(dashboard_spec, indent=2), encoding="utf-8")

    payload = {
        "milestone": "M16_MONITORING_METRICS_EXPORT",
        "passed": True,
        "metric_count": len(metrics),
        "metrics": [
            {
                "name": metric.safe_name(),
                "value": metric.value,
                "help": metric.help,
                "type": metric.metric_type,
            }
            for metric in metrics
        ],
        "alert_recommendations": [alert.to_dict() for alert in alerts],
        "artifacts": {
            "prometheus_metrics": str(prometheus_path.relative_to(PROJECT_ROOT)),
            "grafana_dashboard_spec": str(grafana_path.relative_to(PROJECT_ROOT)),
            "report": str(report_path.relative_to(PROJECT_ROOT)),
        },
        "honest_limitations": [
            "Prometheus and Grafana were not started during local CI.",
            "The dashboard JSON is a template suitable for later import, not evidence of live monitoring.",
            "Alert thresholds are demonstration defaults and must be tuned for production use.",
        ],
    }

    if len(metrics) < 8 or "failsafemlx_average_trust_score" not in prometheus_text:
        payload["passed"] = False

    result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(generate_report(payload, prometheus_text, alerts_to_markdown(alerts)), encoding="utf-8")

    print(f"Wrote {result_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {prometheus_path}")
    print(f"Wrote {grafana_path}")

    if not payload["passed"]:
        raise SystemExit(1)

    print("M16 completed successfully.")


if __name__ == "__main__":
    main()
