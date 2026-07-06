import numpy as np

from failsafemlx.reliability.repair_engine import (
    build_repair_plan,
    classification_repair_benchmark,
    regression_repair_benchmark,
    summarize_repair_effect,
)


def test_build_repair_plan_maps_failures_to_actions():
    profile = {
        "dataset_key": "demo",
        "task": "binary_classification",
        "trust_summary": {"trust_score": 35, "routing_decision": "ESCALATE_AND_BLOCK_AUTOMATION"},
        "failure_signals": [
            {"failure_id": "F1_DATA_DRIFT"},
            {"failure_id": "F7_CALIBRATION_FAILURE"},
            {"failure_id": "F10_UNSAFE_AUTO_DECISION"},
        ],
    }
    plan = build_repair_plan(profile)
    repair_ids = {action["repair_id"] for action in plan["repair_actions"]}
    assert "R3_ABSTAIN_FROM_AUTO_DECISION" in repair_ids
    assert "R4_ROUTE_TO_HUMAN_REVIEW" in repair_ids
    assert "R8_FLAG_DATA_PIPELINE_DRIFT" in repair_ids
    assert "R1_RECALIBRATE_MODEL" in repair_ids
    assert plan["num_repair_actions"] >= 4


def test_classification_repair_reduces_automation_and_does_not_increase_unsafe_rate():
    y_true = np.array([0, 0, 0, 1, 1, 1, 1, 0])
    y_prob = np.array([0.05, 0.20, 0.82, 0.55, 0.91, 0.76, 0.48, 0.30])
    benchmark = classification_repair_benchmark(y_true, y_prob)
    assert benchmark["after"]["auto_decision_rate"] <= benchmark["before"]["auto_decision_rate"]
    assert benchmark["after"]["unsafe_auto_decision_rate"] <= benchmark["before"]["unsafe_auto_decision_rate"]
    assert benchmark["active_learning_queue_size"] > 0


def test_regression_repair_blocks_automation_under_critical_drift():
    y_true = np.array([100, 110, 120, 130], dtype=float)
    y_pred = np.array([95, 130, 118, 160], dtype=float)
    benchmark = regression_repair_benchmark(y_true, y_pred, qhat=10.0, critical_drift=True)
    assert benchmark["before"]["auto_decision_rate"] == 1.0
    assert benchmark["after"]["auto_decision_rate"] == 0.0
    assert benchmark["after"]["unsafe_auto_decision_rate"] == 0.0


def test_summarize_repair_effect_reports_reductions():
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.9, 0.95, 0.4])
    benchmark = classification_repair_benchmark(y_true, y_prob)
    summary = summarize_repair_effect(benchmark)
    assert "unsafe_auto_decision_rate_reduction" in summary
    assert "automation_rate_reduction" in summary
    assert summary["automation_rate_before"] >= summary["automation_rate_after"]
