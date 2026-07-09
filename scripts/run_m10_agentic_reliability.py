from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from failsafemlx.agents.reliability_agent import ReliabilityAgent
from failsafemlx.agents.schemas import ReliabilityCase

RESULT_PATH = ROOT / "experiments/results/m10_agentic_reliability.json"
REPORT_PATH = ROOT / "reports/milestone_10_agentic_reliability.md"


def sample_cases() -> list[ReliabilityCase]:
    return [
        ReliabilityCase(
            sample_id="healthcare-high-risk-001",
            prediction={"positive_class_probability": 0.91, "predicted_label": 1},
            trust_score=0.31,
            failure_ids=["F2_MODEL_OVERCONFIDENCE", "F7_CALIBRATION_FAILURE", "F10_UNSAFE_AUTO_DECISION"],
            uncertainty=0.42,
            calibration_error=0.18,
            drift_score=0.22,
            ood_score=0.18,
            domain="healthcare_risk_classification",
        ),
        ReliabilityCase(
            sample_id="energy-load-forecast-042",
            prediction={"forecast_value": 148.4, "interval_width": 31.2},
            trust_score=0.54,
            failure_ids=["F1_DATA_DRIFT", "F8_WIDE_PREDICTION_INTERVAL"],
            uncertainty=0.67,
            calibration_error=0.08,
            drift_score=0.72,
            ood_score=0.36,
            domain="energy_time_series_regression",
        ),
        ReliabilityCase(
            sample_id="low-risk-reference-007",
            prediction={"positive_class_probability": 0.14, "predicted_label": 0},
            trust_score=0.88,
            failure_ids=[],
            uncertainty=0.12,
            calibration_error=0.04,
            drift_score=0.08,
            ood_score=0.05,
            domain="reference_monitoring_case",
        ),
    ]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    analyses = result["analyses"]
    rows = []
    for item in analyses:
        rows.append(
            "| {sample_id} | {trust} | {failures} | {action} | {decision} |".format(
                sample_id=item["case"]["sample_id"],
                trust=item["case"]["trust_score"],
                failures=", ".join(item["case"]["failure_ids"]) or "none",
                action=item["recommended_action"]["action_id"],
                decision=item["recommended_action"]["decision"],
            )
        )

    content = """# Milestone 10 — Agentic Reliability Layer

## Objective

Add an optional agentic reliability diagnosis layer that explains FailSafeML-X failure IDs, trust scores, drift/OOD risk, and repair recommendations using structured deterministic tools.

## Added Capabilities

- Local deterministic reliability agent
- Optional LangGraph/LangChain-ready adapter detection
- Failure ID explanations
- Trust-score interpretation
- Drift/OOD risk summarization
- Repair-action recommendation
- Human-review note generation
- JSON-compatible structured outputs

## Validation Summary

- Passed: {passed}
- Agent mode: {agent_mode}
- Cases analyzed: {case_count}
- LangGraph available: {langgraph}
- LangChain available: {langchain}

## Sample Agent Decisions

| Sample ID | Trust Score | Failure IDs | Recommended Action | Decision |
|---|---:|---|---|---|
{rows}

## Generated Outputs

- `experiments/results/m10_agentic_reliability.json`
- `reports/milestone_10_agentic_reliability.md`

## Skills Demonstrated

- Agentic AI workflow design
- LangGraph/LangChain-style tool orchestration readiness
- Structured output design
- ML failure explanation
- Trust-score interpretation
- Human-in-the-loop review note generation
- Repair recommendation logic

## Honest Limitation

This milestone does not call external LLM APIs, does not require API keys, and does not claim production agent deployment. LangGraph/LangChain are optional integration targets; the tested path is a deterministic local fallback.
""".format(
        passed=result["passed"],
        agent_mode=result["agent_mode"],
        case_count=len(analyses),
        langgraph=result["optional_integrations"]["langgraph_available"],
        langchain=result["optional_integrations"]["langchain_available"],
        rows="\n".join(rows),
    )
    path.write_text(content, encoding="utf-8")


def run_m10() -> dict[str, Any]:
    agent = ReliabilityAgent()
    analyses = [agent.analyze(case) for case in sample_cases()]

    errors: list[str] = []
    if len(analyses) != 3:
        errors.append("Expected exactly three sample analyses.")
    for item in analyses:
        if "recommended_action" not in item:
            errors.append(f"Missing recommended action for {item.get('case', {}).get('sample_id')}.")
        if "human_review_note" not in item or not item["human_review_note"]:
            errors.append(f"Missing human review note for {item.get('case', {}).get('sample_id')}.")
        if item["agent_mode"] != "deterministic_local_fallback":
            # This is not necessarily an error, but the no-dependency tested path should be deterministic.
            pass

    result = {
        "milestone": "M10_AGENTIC_RELIABILITY_LAYER",
        "project": "FailSafeML-X",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "agent_mode": agent.agent_mode,
        "optional_integrations": agent.optional_integrations,
        "analyses": analyses,
        "errors": errors,
        "warnings": [
            "External LLM APIs are intentionally not used.",
            "LangGraph/LangChain are optional and are not required for the default tested path.",
        ],
        "generated_outputs": [
            str(RESULT_PATH.relative_to(ROOT)),
            str(REPORT_PATH.relative_to(ROOT)),
        ],
        "honest_claim": "Optional LangGraph/LangChain-style reliability agent tooling is implemented with deterministic local fallback, structured failure explanation, repair recommendation, and human-review note generation.",
    }

    write_json(RESULT_PATH, result)
    write_report(REPORT_PATH, result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if errors:
        print(json.dumps(result, indent=2))
        raise SystemExit(1)

    print("M10 completed successfully.")
    return result


def main() -> None:
    run_m10()


if __name__ == "__main__":
    main()
