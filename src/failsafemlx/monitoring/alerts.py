from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .metrics_exporter import ReliabilityMetric


@dataclass(frozen=True)
class AlertRecommendation:
    alert_id: str
    severity: str
    metric: str
    condition: str
    recommendation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "metric": self.metric,
            "condition": self.condition,
            "recommendation": self.recommendation,
        }


def recommend_alerts(metrics: list[ReliabilityMetric]) -> list[AlertRecommendation]:
    values = {metric.safe_name(): metric.value for metric in metrics}
    alerts: list[AlertRecommendation] = []

    if values.get("failsafemlx_unsafe_auto_decision_rate", 0.0) > 0.05:
        alerts.append(
            AlertRecommendation(
                "ALERT_UNSAFE_AUTO_DECISION_RATE",
                "CRITICAL",
                "failsafemlx_unsafe_auto_decision_rate",
                "> 0.05",
                "Stop auto-accept routing for affected segments and require human review until repair validation passes.",
            )
        )

    if values.get("failsafemlx_average_trust_score", 1.0) < 0.60:
        alerts.append(
            AlertRecommendation(
                "ALERT_LOW_AVERAGE_TRUST_SCORE",
                "HIGH",
                "failsafemlx_average_trust_score",
                "< 0.60",
                "Review failure taxonomy outputs and inspect drift/OOD or RAG evidence quality before expanding automation.",
            )
        )

    if values.get("failsafemlx_dataset_validation_error_count", 0.0) > 0:
        alerts.append(
            AlertRecommendation(
                "ALERT_DATASET_VALIDATION_ERRORS",
                "HIGH",
                "failsafemlx_dataset_validation_error_count",
                "> 0",
                "Block reliability evaluation for invalid datasets until schema and data-quality errors are resolved.",
            )
        )

    if values.get("failsafemlx_provider_external_api_call_used_count", 0.0) > 0:
        alerts.append(
            AlertRecommendation(
                "ALERT_EXTERNAL_PROVIDER_USED_IN_LOCAL_CI",
                "MEDIUM",
                "failsafemlx_provider_external_api_call_used_count",
                "> 0",
                "Verify environment flags and secrets policy; local CI should remain offline by default.",
            )
        )

    if values.get("failsafemlx_rag_failure_count", 0.0) > 3:
        alerts.append(
            AlertRecommendation(
                "ALERT_RAG_RELIABILITY_FAILURES",
                "MEDIUM",
                "failsafemlx_rag_failure_count",
                "> 3",
                "Filter stale or untrusted context, require citations, and rerun retrieval repair checks.",
            )
        )

    return alerts


def alerts_to_markdown(alerts: list[AlertRecommendation]) -> str:
    if not alerts:
        return "No alert recommendations were triggered for the local validation sample.\n"
    lines = ["| Alert | Severity | Metric | Condition | Recommendation |", "|---|---:|---|---|---|"]
    for alert in alerts:
        lines.append(
            f"| {alert.alert_id} | {alert.severity} | `{alert.metric}` | `{alert.condition}` | {alert.recommendation} |"
        )
    return "\n".join(lines) + "\n"
