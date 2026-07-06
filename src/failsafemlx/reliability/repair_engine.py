from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


REPAIR_CATALOG: dict[str, dict[str, str]] = {
    "R1_RECALIBRATE_MODEL": {
        "name": "Recalibrate model",
        "description": "Fit or apply probability calibration before relying on predicted confidence.",
    },
    "R2_APPLY_CONFORMAL_PREDICTION": {
        "name": "Apply conformal prediction",
        "description": "Use prediction sets or intervals instead of naked point predictions.",
    },
    "R3_ABSTAIN_FROM_AUTO_DECISION": {
        "name": "Abstain from auto decision",
        "description": "Do not automate cases that violate reliability guards.",
    },
    "R4_ROUTE_TO_HUMAN_REVIEW": {
        "name": "Route to human review",
        "description": "Send risky cases to a reviewer instead of executing automatically.",
    },
    "R5_TRIGGER_ACTIVE_LEARNING": {
        "name": "Trigger active learning",
        "description": "Create a queue of uncertain, drifted, or OOD cases for labeling.",
    },
    "R6_RETRAIN_WITH_REVIEWED_SAMPLES": {
        "name": "Retrain with reviewed samples",
        "description": "Schedule a retraining benchmark once reviewed labels are available.",
    },
    "R7_SWITCH_TO_BACKUP_MODEL": {
        "name": "Switch to backup model",
        "description": "Evaluate a simpler or alternate model before continuing automation.",
    },
    "R8_FLAG_DATA_PIPELINE_DRIFT": {
        "name": "Flag data pipeline drift",
        "description": "Escalate feature distribution changes to data quality monitoring.",
    },
    "R9_ADJUST_DECISION_THRESHOLD": {
        "name": "Adjust decision threshold",
        "description": "Make automation thresholds stricter under uncertainty or drift.",
    },
    "R10_REQUEST_MORE_FEATURES": {
        "name": "Request more features",
        "description": "Defer when available evidence is insufficient for safe action.",
    },
}

FAILURE_TO_REPAIRS: dict[str, list[str]] = {
    "F1_DATA_DRIFT": ["R8_FLAG_DATA_PIPELINE_DRIFT", "R4_ROUTE_TO_HUMAN_REVIEW", "R6_RETRAIN_WITH_REVIEWED_SAMPLES"],
    "F2_MODEL_OVERCONFIDENCE": ["R1_RECALIBRATE_MODEL", "R9_ADJUST_DECISION_THRESHOLD"],
    "F3_LOW_CONFIDENCE_PREDICTION": ["R3_ABSTAIN_FROM_AUTO_DECISION", "R4_ROUTE_TO_HUMAN_REVIEW", "R10_REQUEST_MORE_FEATURES"],
    "F4_OUT_OF_DISTRIBUTION_INPUT": ["R3_ABSTAIN_FROM_AUTO_DECISION", "R4_ROUTE_TO_HUMAN_REVIEW", "R5_TRIGGER_ACTIVE_LEARNING"],
    "F5_LABEL_NOISE_SUSPECTED": ["R5_TRIGGER_ACTIVE_LEARNING", "R6_RETRAIN_WITH_REVIEWED_SAMPLES"],
    "F6_CLASS_IMBALANCE_FAILURE": ["R9_ADJUST_DECISION_THRESHOLD", "R7_SWITCH_TO_BACKUP_MODEL"],
    "F7_CALIBRATION_FAILURE": ["R1_RECALIBRATE_MODEL", "R2_APPLY_CONFORMAL_PREDICTION"],
    "F8_WIDE_PREDICTION_INTERVAL": ["R2_APPLY_CONFORMAL_PREDICTION", "R3_ABSTAIN_FROM_AUTO_DECISION"],
    "F9_MODEL_DECAY_OVER_TIME": ["R7_SWITCH_TO_BACKUP_MODEL", "R6_RETRAIN_WITH_REVIEWED_SAMPLES"],
    "F10_UNSAFE_AUTO_DECISION": ["R3_ABSTAIN_FROM_AUTO_DECISION", "R4_ROUTE_TO_HUMAN_REVIEW", "R5_TRIGGER_ACTIVE_LEARNING"],
}

REPAIR_PRIORITIES: dict[str, int] = {
    "R3_ABSTAIN_FROM_AUTO_DECISION": 1,
    "R4_ROUTE_TO_HUMAN_REVIEW": 2,
    "R8_FLAG_DATA_PIPELINE_DRIFT": 3,
    "R1_RECALIBRATE_MODEL": 4,
    "R2_APPLY_CONFORMAL_PREDICTION": 5,
    "R9_ADJUST_DECISION_THRESHOLD": 6,
    "R5_TRIGGER_ACTIVE_LEARNING": 7,
    "R7_SWITCH_TO_BACKUP_MODEL": 8,
    "R6_RETRAIN_WITH_REVIEWED_SAMPLES": 9,
    "R10_REQUEST_MORE_FEATURES": 10,
}


@dataclass(frozen=True)
class RepairAction:
    repair_id: str
    priority: int
    trigger_failures: list[str]
    execution_mode: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        meta = REPAIR_CATALOG.get(self.repair_id, {})
        payload["name"] = meta.get("name", self.repair_id)
        payload["description"] = meta.get("description", "")
        return payload


def build_repair_plan(failure_profile: dict[str, Any]) -> dict[str, Any]:
    """Convert a M4 failure profile into an ordered repair plan."""
    failure_signals = failure_profile.get("failure_signals", [])
    repair_to_failures: dict[str, list[str]] = {}
    for failure in failure_signals:
        failure_id = failure.get("failure_id")
        for repair_id in FAILURE_TO_REPAIRS.get(failure_id, []):
            repair_to_failures.setdefault(repair_id, []).append(failure_id)

    actions: list[RepairAction] = []
    for repair_id, triggers in repair_to_failures.items():
        if repair_id in {"R3_ABSTAIN_FROM_AUTO_DECISION", "R4_ROUTE_TO_HUMAN_REVIEW", "R8_FLAG_DATA_PIPELINE_DRIFT"}:
            mode = "execute_now"
        elif repair_id in {"R1_RECALIBRATE_MODEL", "R2_APPLY_CONFORMAL_PREDICTION", "R9_ADJUST_DECISION_THRESHOLD"}:
            mode = "apply_policy_guard"
        else:
            mode = "schedule_follow_up"
        actions.append(
            RepairAction(
                repair_id=repair_id,
                priority=REPAIR_PRIORITIES.get(repair_id, 99),
                trigger_failures=sorted(set(triggers)),
                execution_mode=mode,
                rationale=f"Triggered by {len(set(triggers))} active failure signal(s): {', '.join(sorted(set(triggers)))}.",
            )
        )
    actions = sorted(actions, key=lambda item: (item.priority, item.repair_id))
    return {
        "dataset_key": failure_profile.get("dataset_key"),
        "task": failure_profile.get("task"),
        "routing_before_repair": failure_profile.get("trust_summary", {}).get("routing_decision"),
        "trust_score_before_repair": failure_profile.get("trust_summary", {}).get("trust_score"),
        "repair_actions": [action.to_dict() for action in actions],
        "num_repair_actions": len(actions),
    }


def _safe_rate(mask: np.ndarray) -> float:
    return float(np.mean(mask)) if mask.size else 0.0


def _auto_metrics(y_true: np.ndarray, y_pred: np.ndarray, auto_mask: np.ndarray) -> dict[str, Any]:
    auto_count = int(np.sum(auto_mask))
    n = int(len(y_true))
    if auto_count == 0:
        return {
            "auto_decision_rate": 0.0,
            "human_review_rate": 1.0,
            "auto_accuracy": None,
            "unsafe_auto_decision_rate": 0.0,
            "unsafe_auto_decision_count": 0,
            "auto_decision_count": 0,
            "human_review_count": n,
        }
    wrong = y_pred[auto_mask] != y_true[auto_mask]
    unsafe_count = int(np.sum(wrong))
    return {
        "auto_decision_rate": round(auto_count / n, 4),
        "human_review_rate": round(1.0 - auto_count / n, 4),
        "auto_accuracy": round(float(np.mean(~wrong)), 4),
        "unsafe_auto_decision_rate": round(unsafe_count / auto_count, 4),
        "unsafe_auto_decision_count": unsafe_count,
        "auto_decision_count": auto_count,
        "human_review_count": n - auto_count,
    }


def classification_repair_benchmark(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    before_low: float = 0.25,
    before_high: float = 0.75,
    after_low: float = 0.10,
    after_high: float = 0.90,
) -> dict[str, Any]:
    """Evaluate stricter automation thresholds after M4 reliability warnings.

    Before repair, high-confidence probabilities are automatically accepted. After
    repair, only very high-confidence probabilities are automated; the remaining
    cases are routed to review/active learning.
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)
    before_auto = (y_prob <= before_low) | (y_prob >= before_high)
    after_auto = (y_prob <= after_low) | (y_prob >= after_high)
    uncertainty = np.abs(y_prob - 0.5)
    queue_size = int(np.sum(~after_auto))
    return {
        "repair_policy": "stricter_threshold_abstention",
        "before_thresholds": {"low": before_low, "high": before_high},
        "after_thresholds": {"low": after_low, "high": after_high},
        "before": _auto_metrics(y_true, y_pred, before_auto),
        "after": _auto_metrics(y_true, y_pred, after_auto),
        "active_learning_queue_size": queue_size,
        "active_learning_queue_rule": "probability outside strict auto-accept bands or near decision boundary",
        "mean_uncertainty_distance_from_boundary": round(float(np.mean(uncertainty)), 4),
    }


def regression_repair_benchmark(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    qhat: float,
    critical_drift: bool,
) -> dict[str, Any]:
    """Evaluate abstention + conformal guardrails for regression actions.

    The labeled benchmark treats a point forecast as unsafe when its absolute
    error is larger than the split-conformal residual threshold qhat. Under
    critical drift/OOD, the repair engine blocks point-estimate automation and
    routes cases to human review while still reporting conformal intervals.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    abs_error = np.abs(y_true - y_pred)
    before_auto = np.ones_like(abs_error, dtype=bool)
    after_auto = np.zeros_like(abs_error, dtype=bool) if critical_drift else abs_error <= qhat

    def metrics(auto_mask: np.ndarray) -> dict[str, Any]:
        auto_count = int(np.sum(auto_mask))
        n = int(len(abs_error))
        unsafe = abs_error[auto_mask] > qhat
        unsafe_count = int(np.sum(unsafe))
        accepted_mae = None if auto_count == 0 else round(float(np.mean(abs_error[auto_mask])), 4)
        return {
            "auto_decision_rate": round(auto_count / n, 4),
            "human_review_rate": round(1.0 - auto_count / n, 4),
            "accepted_forecast_mae": accepted_mae,
            "unsafe_auto_decision_rate": 0.0 if auto_count == 0 else round(unsafe_count / auto_count, 4),
            "unsafe_auto_decision_count": unsafe_count,
            "auto_decision_count": auto_count,
            "human_review_count": n - auto_count,
        }

    return {
        "repair_policy": "conformal_interval_abstention_under_drift",
        "qhat_residual_threshold": round(float(qhat), 4),
        "critical_drift_or_ood": bool(critical_drift),
        "before": metrics(before_auto),
        "after": metrics(after_auto),
        "active_learning_queue_size": int(np.sum(~after_auto)),
        "active_learning_queue_rule": "forecast contexts blocked by drift/OOD or outside conformal safety guard",
    }


def summarize_repair_effect(benchmark: dict[str, Any]) -> dict[str, Any]:
    before = benchmark["before"]
    after = benchmark["after"]
    unsafe_delta = before["unsafe_auto_decision_rate"] - after["unsafe_auto_decision_rate"]
    automation_delta = before["auto_decision_rate"] - after["auto_decision_rate"]
    return {
        "unsafe_auto_decision_rate_before": before["unsafe_auto_decision_rate"],
        "unsafe_auto_decision_rate_after": after["unsafe_auto_decision_rate"],
        "unsafe_auto_decision_rate_reduction": round(float(unsafe_delta), 4),
        "automation_rate_before": before["auto_decision_rate"],
        "automation_rate_after": after["auto_decision_rate"],
        "automation_rate_reduction": round(float(automation_delta), 4),
        "safety_tradeoff": "reduced unsafe automation by routing more cases to review",
    }
