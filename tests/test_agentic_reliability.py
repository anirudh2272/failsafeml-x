from __future__ import annotations

from pathlib import Path

from failsafemlx.agents.reliability_agent import ReliabilityAgent, analyze_reliability_case
from failsafemlx.agents.schemas import ReliabilityCase
from failsafemlx.agents.tools import (
    explain_failure_ids,
    generate_human_review_note,
    recommend_repair_action,
    summarize_drift_ood_risk,
    summarize_trust_score,
)
from scripts.run_m10_agentic_reliability import run_m10


def test_failure_id_explanations_are_structured():
    explanations = explain_failure_ids(["F1_DATA_DRIFT", "F4_OUT_OF_DISTRIBUTION_INPUT"])

    assert len(explanations) == 2
    assert explanations[0]["failure_id"] == "F1_DATA_DRIFT"
    assert explanations[1]["severity"] == "critical"
    assert "primary_repair" in explanations[0]


def test_trust_score_summary_routes_low_trust_to_review():
    summary = summarize_trust_score(0.22)

    assert summary["trust_band"] == "very_low"
    assert summary["default_decision"] == "human_review"


def test_drift_ood_summary_detects_critical_risk():
    summary = summarize_drift_ood_risk(drift_score=0.3, ood_score=0.91)

    assert summary["severity"] == "critical"
    assert summary["recommended_drift_action"] == "human_review"


def test_repair_recommendation_blocks_unsafe_auto_decision():
    recommendation = recommend_repair_action(
        failure_ids=["F10_UNSAFE_AUTO_DECISION"],
        trust_score=0.35,
        calibration_error=0.2,
    )

    assert recommendation["action_id"] == "R4_ROUTE_TO_HUMAN_REVIEW"
    assert recommendation["auto_decision_allowed"] is False


def test_human_review_note_is_deterministic():
    recommendation = recommend_repair_action(["F7_CALIBRATION_FAILURE"], trust_score=0.55, calibration_error=0.2)
    note = generate_human_review_note("case-1", ["F7_CALIBRATION_FAILURE"], 0.55, recommendation)

    assert "case-1" in note
    assert "F7_CALIBRATION_FAILURE" in note
    assert recommendation["action_id"] in note


def test_reliability_agent_outputs_json_compatible_payload():
    case = ReliabilityCase(
        sample_id="test-case",
        prediction={"probability": 0.93},
        trust_score=0.33,
        failure_ids=["F2_MODEL_OVERCONFIDENCE", "F7_CALIBRATION_FAILURE"],
        calibration_error=0.19,
    )
    result = ReliabilityAgent().analyze(case)

    assert result["project"] == "FailSafeML-X"
    assert result["agent_mode"] == "deterministic_local_fallback"
    assert result["recommended_action"]["action_id"] in {
        "R1_RECALIBRATE_MODEL",
        "R4_ROUTE_TO_HUMAN_REVIEW",
    }
    assert result["human_review_note"]


def test_convenience_wrapper_accepts_dict_input():
    result = analyze_reliability_case(
        {
            "sample_id": "dict-case",
            "prediction": {"label": 1},
            "trust_score": 0.84,
            "failure_ids": [],
            "uncertainty": 0.1,
            "calibration_error": 0.03,
            "drift_score": 0.02,
            "ood_score": 0.01,
        }
    )

    assert result["recommended_action"]["decision"] == "accept"


def test_m10_runner_generates_json_and_report():
    result = run_m10()

    assert result["passed"] is True
    assert Path("experiments/results/m10_agentic_reliability.json").exists()
    assert Path("reports/milestone_10_agentic_reliability.md").exists()
