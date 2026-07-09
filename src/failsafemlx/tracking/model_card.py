from __future__ import annotations

from .experiment_registry import ExperimentRecord


def _bullet_lines(items: list[str]) -> str:
    if not items:
        return "- None recorded."
    return "\n".join(f"- {item}" for item in items)


def generate_model_card(record: ExperimentRecord) -> str:
    """Generate a concise Markdown model card from a registry record."""

    metrics = record.metrics
    reliability = record.reliability_summary
    return f"""# FailSafeML-X Model Card

## Model / System

- **Project:** {record.project}
- **Model name:** {record.model_name}
- **Milestone:** {record.milestone}
- **Run ID:** {record.run_id}
- **Created:** {record.created_at_utc}

## Intended Use

FailSafeML-X is intended to audit ML prediction reliability, assign failure IDs, recommend repair actions, and route risky predictions to safer handling paths such as human review or abstention.

## Data Used in This Prototype Run

- **Datasets:** {record.dataset_name}
- **Dataset count:** {metrics.get('dataset_count', 0)}
- **Dataset validation errors:** {metrics.get('dataset_validation_errors', 0)}
- **Dataset validation warnings:** {metrics.get('dataset_validation_warnings', 0)}

## Reliability Capabilities Covered

- Dataset validation passed: {reliability.get('dataset_validation_passed')}
- RAGOps reliability passed: {reliability.get('ragops_passed')}
- Provider-aware agent passed: {reliability.get('provider_agent_passed')}
- External providers disabled by default: {reliability.get('external_providers_disabled_by_default')}

## Trust Score Summary

- Minimum: {record.trust_score_summary.get('min', 0.0)}
- Mean: {record.trust_score_summary.get('mean', 0.0)}
- Maximum: {record.trust_score_summary.get('max', 0.0)}

## Known Warnings

{_bullet_lines(record.warnings)}

## Limitations

{_bullet_lines(record.limitations)}

## Safe Claim

This run records a locally validated FailSafeML-X reliability evaluation with local JSON tracking and generated model-risk documentation. It does not claim production certification, live cloud deployment, or a live MLflow/DVC tracking backend.
"""
