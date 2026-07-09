from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable


_METRIC_NAME_RE = re.compile(r"[^a-zA-Z0-9_:]")


@dataclass(frozen=True)
class ReliabilityMetric:
    """A small Prometheus-compatible metric representation."""

    name: str
    value: float
    help: str
    metric_type: str = "gauge"
    labels: dict[str, str] | None = None

    def safe_name(self) -> str:
        name = _METRIC_NAME_RE.sub("_", self.name.strip())
        if not name:
            return "failsafemlx_unknown_metric"
        if not name.startswith("failsafemlx_"):
            name = f"failsafemlx_{name}"
        return name


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _count(mapping: Any) -> float:
    if isinstance(mapping, dict):
        return float(sum(_float(v) for v in mapping.values()))
    return 0.0


def _failure_count(results: dict[str, Any], *paths: str) -> float:
    total = 0.0
    for path in paths:
        cursor: Any = results
        for part in path.split("."):
            if isinstance(cursor, dict):
                cursor = cursor.get(part, {})
            else:
                cursor = {}
                break
        total += _count(cursor)
    return total


def build_reliability_metrics(results: dict[str, Any]) -> list[ReliabilityMetric]:
    """Build monitoring metrics from milestone result dictionaries.

    The function accepts a compact dictionary of previously generated milestone
    results. It is intentionally dependency-free and tolerant of missing keys so
    the monitoring layer can run in local CI without requiring live services.
    """

    m5 = results.get("m5", {}) if isinstance(results, dict) else {}
    m15b = results.get("m15b", {}) if isinstance(results, dict) else {}
    m15c = results.get("m15c", {}) if isinstance(results, dict) else {}
    m15d = results.get("m15d", {}) if isinstance(results, dict) else {}

    rag_aggregate = m15b.get("aggregate", {}) if isinstance(m15b, dict) else {}

    unsafe_rate = _float(
        m5.get("after", {}).get("unsafe_auto_decision_rate")
        if isinstance(m5.get("after"), dict)
        else m5.get("unsafe_auto_decision_rate"),
        default=0.0,
    )
    average_trust = _float(
        m15d.get("average_trust_score")
        if isinstance(m15d, dict)
        else None,
        default=_float(rag_aggregate.get("average_trust_score"), default=0.0),
    )
    dataset_errors = _float(m15c.get("total_errors"), default=0.0) if isinstance(m15c, dict) else 0.0
    dataset_warnings = _float(m15c.get("total_warnings"), default=0.0) if isinstance(m15c, dict) else 0.0
    provider_blocked = 1.0 if isinstance(m15d, dict) and m15d.get("external_provider_blocked_by_default") else 0.0
    external_calls_used = 1.0 if isinstance(m15d, dict) and m15d.get("external_api_calls_used") else 0.0

    failure_count = _failure_count(results, "m15b.aggregate.failure_counts", "m15d.failure_counts")
    repair_count = _failure_count(results, "m15b.aggregate.repair_action_counts", "m15d.repair_action_counts")

    human_review_rate = _float(m15d.get("human_review_rate"), default=0.0) if isinstance(m15d, dict) else 0.0
    drift_warnings = _float(m15d.get("failure_counts", {}).get("F1_DATA_DRIFT"), default=0.0) if isinstance(m15d, dict) else 0.0
    ood_warnings = _float(m15d.get("failure_counts", {}).get("F4_OUT_OF_DISTRIBUTION_INPUT"), default=0.0) if isinstance(m15d, dict) else 0.0

    return [
        ReliabilityMetric(
            "unsafe_auto_decision_rate",
            unsafe_rate,
            "Fraction of high-risk predictions that were incorrectly auto-accepted.",
        ),
        ReliabilityMetric(
            "average_trust_score",
            average_trust,
            "Average reliability trust score across audited cases.",
        ),
        ReliabilityMetric("drift_warning_count", drift_warnings, "Count of drift-related warnings."),
        ReliabilityMetric("ood_warning_count", ood_warnings, "Count of out-of-distribution warnings."),
        ReliabilityMetric("human_review_rate", human_review_rate, "Fraction of audited cases routed to human review."),
        ReliabilityMetric("repair_action_count", repair_count, "Total recommended repair actions."),
        ReliabilityMetric(
            "provider_external_call_blocked_count",
            provider_blocked,
            "Whether external LLM providers were blocked by default in local validation.",
        ),
        ReliabilityMetric(
            "provider_external_api_call_used_count",
            external_calls_used,
            "Whether external API calls were used during local validation.",
        ),
        ReliabilityMetric(
            "dataset_validation_error_count",
            dataset_errors,
            "Dataset validation errors detected before reliability evaluation.",
        ),
        ReliabilityMetric(
            "dataset_validation_warning_count",
            dataset_warnings,
            "Dataset validation warnings detected before reliability evaluation.",
        ),
        ReliabilityMetric("rag_failure_count", failure_count, "Total RAG/provider reliability failures detected."),
    ]


def _labels_to_text(labels: dict[str, str] | None) -> str:
    if not labels:
        return ""
    parts = [f'{key}="{str(value).replace(chr(34), "_")}"' for key, value in sorted(labels.items())]
    return "{" + ",".join(parts) + "}"


def export_prometheus_metrics(metrics: Iterable[ReliabilityMetric]) -> str:
    """Export metrics in Prometheus text exposition format."""

    lines: list[str] = []
    seen: set[str] = set()
    for metric in metrics:
        name = metric.safe_name()
        if name not in seen:
            lines.append(f"# HELP {name} {metric.help}")
            lines.append(f"# TYPE {name} {metric.metric_type}")
            seen.add(name)
        lines.append(f"{name}{_labels_to_text(metric.labels)} {metric.value:.6g}")
    return "\n".join(lines) + "\n"


def write_prometheus_metrics(metrics: Iterable[ReliabilityMetric], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(export_prometheus_metrics(metrics), encoding="utf-8")
    return target


def build_grafana_dashboard_spec(metrics: Iterable[ReliabilityMetric]) -> dict[str, Any]:
    """Build a simple Grafana dashboard JSON skeleton for reliability metrics."""

    panels: list[dict[str, Any]] = []
    for idx, metric in enumerate(metrics, start=1):
        name = metric.safe_name()
        panels.append(
            {
                "id": idx,
                "title": name,
                "type": "stat",
                "targets": [{"expr": name, "legendFormat": name}],
                "description": metric.help,
                "gridPos": {"h": 4, "w": 6, "x": ((idx - 1) % 4) * 6, "y": ((idx - 1) // 4) * 4},
            }
        )

    return {
        "title": "FailSafeML-X Reliability Monitoring",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "30s",
        "tags": ["failsafeml-x", "ml-reliability", "local-template"],
        "panels": panels,
        "templating": {"list": []},
        "annotations": {"list": []},
        "timezone": "browser",
        "honest_limitations": [
            "Dashboard JSON is a template and was not deployed to a live Grafana server.",
            "Metrics are generated from local milestone outputs, not a production Prometheus scrape target.",
        ],
    }
