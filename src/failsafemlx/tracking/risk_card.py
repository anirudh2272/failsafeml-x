from __future__ import annotations

from .experiment_registry import ExperimentRecord


def _format_count_table(counts: dict[str, int], empty_label: str) -> str:
    if not counts:
        return f"| Item | Count |\n|---|---:|\n| {empty_label} | 0 |"
    rows = ["| Item | Count |", "|---|---:|"]
    for key, value in sorted(counts.items()):
        rows.append(f"| `{key}` | {value} |")
    return "\n".join(rows)


def _risk_level(record: ExperimentRecord) -> str:
    failure_total = sum(record.failure_counts.values())
    trust_mean = float(record.trust_score_summary.get("mean", 0.0))
    validation_errors = int(record.metrics.get("dataset_validation_errors", 0))
    if validation_errors > 0 or trust_mean < 0.35:
        return "HIGH"
    if failure_total > 0 or trust_mean < 0.7:
        return "MEDIUM"
    return "LOW"


def generate_risk_card(record: ExperimentRecord) -> str:
    """Generate a Markdown risk card for ML reliability review."""

    risk_level = _risk_level(record)
    return f"""# FailSafeML-X Model Risk Card

## Summary

- **Run ID:** `{record.run_id}`
- **Milestone:** {record.milestone}
- **Overall prototype risk level:** **{risk_level}**
- **Mean trust score:** {record.trust_score_summary.get('mean', 0.0)}
- **Git commit:** {record.git.get('commit', 'unavailable')}
- **Git dirty:** {record.git.get('dirty', False)}

## Reliability Gate Results

| Gate | Result |
|---|---|
| Dataset validation | {record.reliability_summary.get('dataset_validation_passed')} |
| RAGOps reliability audit | {record.reliability_summary.get('ragops_passed')} |
| Provider-aware reliability agent | {record.reliability_summary.get('provider_agent_passed')} |
| External providers disabled by default | {record.reliability_summary.get('external_providers_disabled_by_default')} |

## Failure Counts

{_format_count_table(record.failure_counts, 'No failures recorded')}

## Repair Action Counts

{_format_count_table(record.repair_action_counts, 'No repair actions recorded')}

## Operational Notes

- The registry is local and JSON-based.
- This card is generated for engineering review and portfolio documentation.
- Human review remains recommended for high-risk reliability failures.
- External LLM providers remain disabled by default during CI-safe runs.

## Honest Limitations

""" + "\n".join(f"- {item}" for item in record.limitations) + "\n"
