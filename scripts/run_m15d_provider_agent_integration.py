from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.agents.provider_agent import analyze_with_provider
from failsafemlx.providers.base import ExternalProviderDisabledError
from failsafemlx.providers.router import get_provider

RESULT_PATH = PROJECT_ROOT / "experiments/results/m15d_provider_agent_integration.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_15d_provider_agent_integration.md"


SAMPLE_CASES: list[dict[str, Any]] = [
    {
        "sample_id": "m15d_safe_case",
        "prediction": "approve_low_risk",
        "trust_score": 0.91,
        "failure_ids": [],
        "uncertainty": 0.08,
        "calibration_error": 0.02,
        "drift_score": 0.05,
        "ood_score": 0.03,
        "domain": "healthcare_risk",
    },
    {
        "sample_id": "m15d_drift_case",
        "prediction": "approve_high_risk",
        "trust_score": 0.52,
        "failure_ids": ["F1_DATA_DRIFT", "F7_CALIBRATION_FAILURE"],
        "uncertainty": 0.48,
        "calibration_error": 0.18,
        "drift_score": 0.73,
        "ood_score": 0.27,
        "domain": "healthcare_risk",
    },
    {
        "sample_id": "m15d_critical_case",
        "prediction": "auto_decision_requested",
        "trust_score": 0.31,
        "failure_ids": ["F4_OUT_OF_DISTRIBUTION_INPUT", "F10_UNSAFE_AUTO_DECISION"],
        "uncertainty": 0.81,
        "calibration_error": 0.16,
        "drift_score": 0.62,
        "ood_score": 0.91,
        "domain": "energy_timeseries",
    },
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Milestone 15D — Provider-Aware Agent Integration",
        "",
        "## Objective",
        "",
        "Connect the local deterministic reliability agent to the optional provider abstraction while keeping local/offline behavior as the default.",
        "",
        "## Validation Summary",
        "",
        f"- Passed: {payload['passed']}",
        f"- Cases evaluated: {payload['case_count']}",
        f"- Providers used: {', '.join(payload['providers_used'])}",
        f"- External provider blocked by default: {payload['external_provider_blocked_by_default']}",
        f"- External API calls used: {payload['external_api_calls_used']}",
        f"- Average trust score: {payload['average_trust_score']}",
        "",
        "## Risk-Level Counts",
        "",
    ]
    for risk, count in payload["risk_level_counts"].items():
        lines.append(f"- {risk}: {count}")
    lines.extend(["", "## Case Summaries", ""])
    for item in payload["case_summaries"]:
        lines.extend(
            [
                f"### {item['case_id']}",
                "",
                f"- Provider requested: {item['provider_requested']}",
                f"- Provider used: {item['provider_used']}",
                f"- Used external API: {item['used_external_api']}",
                f"- Risk level: {item['risk_level']}",
                f"- Recommended action: {item['recommended_action_id']}",
                f"- Recommended decision: {item['recommended_decision']}",
                f"- Warning count: {item['warning_count']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Honest Limitation",
            "",
            "M15D integrates provider-aware reliability explanations but does not call OpenAI, AWS Bedrock, or any paid provider during tests/local CI. External providers remain disabled by default and require explicit opt-in.",
            "",
            "## Resume-Safe Claim",
            "",
            "Integrated provider-aware reliability explanations with a local default provider and optional OpenAI-compatible/AWS Bedrock-style adapters disabled by default.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _assert_external_blocked_by_default() -> bool:
    try:
        get_provider("openai_compatible", allow_external=False)
    except ExternalProviderDisabledError:
        return True
    return False


def run_m15d() -> dict[str, Any]:
    analyses = [analyze_with_provider(case, provider_name="local") for case in SAMPLE_CASES]
    blocked_result = analyze_with_provider(SAMPLE_CASES[1], provider_name="bedrock", allow_external=False)

    providers_used = sorted({str(item["provider_used"]) for item in analyses + [blocked_result]})
    external_api_calls = [item for item in analyses + [blocked_result] if item["used_external_api"]]
    risk_levels = Counter(str(item["risk_summary"].get("risk_level", "unknown")) for item in analyses)
    actions = Counter(str(item["repair_recommendation"].get("action_id", "unknown")) for item in analyses)
    trust_scores = [float(item["risk_summary"].get("trust_score") or 0.0) for item in analyses]

    errors: list[str] = []
    if external_api_calls:
        errors.append("External API calls were used during M15D local validation.")
    if not _assert_external_blocked_by_default():
        errors.append("OpenAI-compatible provider was not blocked by default.")
    if blocked_result["provider_used"] != "local":
        errors.append("Blocked external provider request did not fall back to local provider.")
    if not any(item["risk_summary"].get("risk_level") == "critical" for item in analyses):
        errors.append("Expected at least one critical-risk provider-aware analysis case.")
    if not all(item["provider_metadata"].get("used_external_api") is False for item in analyses + [blocked_result]):
        errors.append("Provider metadata did not clearly report local/offline execution.")

    payload = {
        "project": "FailSafeML-X",
        "milestone": "M15D_PROVIDER_AWARE_AGENT_INTEGRATION",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_count": len(analyses),
        "providers_used": providers_used,
        "external_provider_blocked_by_default": blocked_result["provider_used"] == "local" and bool(blocked_result["warnings"]),
        "external_api_calls_used": bool(external_api_calls),
        "average_trust_score": round(sum(trust_scores) / len(trust_scores), 4),
        "risk_level_counts": dict(sorted(risk_levels.items())),
        "repair_action_counts": dict(sorted(actions.items())),
        "case_summaries": [
            {
                "case_id": item["case_id"],
                "provider_requested": item["provider_requested"],
                "provider_used": item["provider_used"],
                "used_external_api": item["used_external_api"],
                "risk_level": item["risk_summary"].get("risk_level"),
                "recommended_action_id": item["repair_recommendation"].get("action_id"),
                "recommended_decision": item["repair_recommendation"].get("decision"),
                "warning_count": len(item["warnings"]),
            }
            for item in analyses + [blocked_result]
        ],
        "sample_outputs": analyses,
        "blocked_external_provider_output": blocked_result,
        "errors": errors,
        "warnings": [
            "External providers are adapter-ready but disabled by default.",
            "Provider-aware explanations are advisory and do not override reliability routing.",
        ],
        "generated_outputs": [
            "experiments/results/m15d_provider_agent_integration.json",
            "reports/milestone_15d_provider_agent_integration.md",
        ],
        "honest_claim": "Integrated provider-aware reliability explanations with a local default provider and optional OpenAI-compatible/AWS Bedrock-style adapters disabled by default.",
    }

    _write_json(RESULT_PATH, payload)
    _write_report(REPORT_PATH, payload)
    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    if not payload["passed"]:
        raise SystemExit(1)
    print("M15D completed successfully.")
    return payload


def main() -> None:
    run_m15d()


if __name__ == "__main__":
    main()
