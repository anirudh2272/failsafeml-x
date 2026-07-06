from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


FAILURE_CATALOG: dict[str, dict[str, str]] = {
    "F1_DATA_DRIFT": {
        "name": "Data drift",
        "description": "Current input features no longer resemble the reference distribution.",
    },
    "F2_MODEL_OVERCONFIDENCE": {
        "name": "Model overconfidence",
        "description": "The model is more confident than its observed correctness supports.",
    },
    "F3_LOW_CONFIDENCE_PREDICTION": {
        "name": "Low-confidence prediction",
        "description": "A meaningful fraction of decisions are made with weak model confidence.",
    },
    "F4_OUT_OF_DISTRIBUTION_INPUT": {
        "name": "Out-of-distribution input",
        "description": "Distance-based OOD scoring indicates current inputs are far from the training/reference region.",
    },
    "F5_LABEL_NOISE_SUSPECTED": {
        "name": "Label-noise suspected",
        "description": "Metric and calibration behavior suggests possible noisy labels or unstable supervision.",
    },
    "F6_CLASS_IMBALANCE_FAILURE": {
        "name": "Class-imbalance failure",
        "description": "Classification reliability may be harmed by imbalance-sensitive decision behavior.",
    },
    "F7_CALIBRATION_FAILURE": {
        "name": "Calibration failure",
        "description": "Predicted probabilities are not well aligned with empirical frequencies.",
    },
    "F8_WIDE_PREDICTION_INTERVAL": {
        "name": "Wide prediction interval",
        "description": "Conformal intervals or sets indicate high uncertainty around the model output.",
    },
    "F9_MODEL_DECAY_OVER_TIME": {
        "name": "Model decay over time",
        "description": "Current shifted data produces worse metrics than the reference data.",
    },
    "F10_UNSAFE_AUTO_DECISION": {
        "name": "Unsafe auto decision",
        "description": "The model should not automatically act because multiple reliability warnings are active.",
    },
}

SEVERITY_WEIGHTS = {
    "low": 8,
    "medium": 15,
    "high": 25,
    "critical": 35,
}


@dataclass(frozen=True)
class FailureSignal:
    failure_id: str
    severity: str
    evidence: str
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        meta = FAILURE_CATALOG.get(self.failure_id, {})
        payload["name"] = meta.get("name", self.failure_id)
        payload["description"] = meta.get("description", "")
        payload["penalty"] = SEVERITY_WEIGHTS[self.severity]
        return payload


def routing_decision_from_score(trust_score: float) -> str:
    """Convert a 0-100 trust score into a deployment decision."""
    if trust_score >= 80:
        return "AUTO_ACCEPT"
    if trust_score >= 60:
        return "HUMAN_REVIEW"
    if trust_score >= 40:
        return "DEFER_OR_REQUEST_MORE_FEATURES"
    return "ESCALATE_AND_BLOCK_AUTOMATION"


def risk_level_from_score(trust_score: float) -> str:
    if trust_score >= 80:
        return "low"
    if trust_score >= 60:
        return "medium"
    if trust_score >= 40:
        return "high"
    return "critical"


def compute_trust_score(failures: list[FailureSignal]) -> dict[str, Any]:
    raw_penalty = sum(SEVERITY_WEIGHTS[f.severity] for f in failures)
    # Cap penalty so many correlated warnings do not push below zero in a misleading way.
    score = max(0.0, 100.0 - min(raw_penalty, 100))
    return {
        "trust_score": round(score, 2),
        "risk_level": risk_level_from_score(score),
        "routing_decision": routing_decision_from_score(score),
        "num_failures": len(failures),
        "total_penalty": int(min(raw_penalty, 100)),
    }


def _safe_get(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def classification_failures(m2: dict[str, Any], m3: dict[str, Any]) -> list[FailureSignal]:
    failures: list[FailureSignal] = []
    cal = m2.get("calibration_summary", {})
    conf = m2.get("conformal_prediction_sets", {})
    drift = m3.get("drift_summary", {})
    ref_metrics = m3.get("reference_metrics", {})
    cur_metrics = m3.get("current_shifted_metrics", {})
    ood = m3.get("ood_report", {})

    if drift.get("feature_drift_detected"):
        failures.append(FailureSignal(
            "F1_DATA_DRIFT", "high",
            f"{_safe_get(m3, 'feature_drift_report', 'num_features_drifted', default=0)} features crossed drift thresholds.",
            "Flag data pipeline drift and evaluate current cohort before automatic decisions.",
        ))
    if cal.get("calibration_warning") or cal.get("expected_calibration_error", 0.0) > 0.08:
        failures.append(FailureSignal(
            "F7_CALIBRATION_FAILURE", "medium",
            f"ECE={cal.get('expected_calibration_error', 'unknown')} and calibration_warning={cal.get('calibration_warning')}.",
            "Apply recalibration or require calibrated probability reporting before deployment.",
        ))
    if cal.get("low_confidence_rate", 0.0) >= 0.10:
        failures.append(FailureSignal(
            "F3_LOW_CONFIDENCE_PREDICTION", "low",
            f"Low-confidence rate={cal.get('low_confidence_rate')}.",
            "Route low-confidence cases to human review or request more features.",
        ))
    if cal.get("overconfidence_gap", 0.0) > 0.05:
        failures.append(FailureSignal(
            "F2_MODEL_OVERCONFIDENCE", "medium",
            f"Overconfidence gap={cal.get('overconfidence_gap')}.",
            "Reduce automation threshold and recalibrate probability outputs.",
        ))
    if ood.get("ood_warning"):
        failures.append(FailureSignal(
            "F4_OUT_OF_DISTRIBUTION_INPUT", "high",
            f"OOD rate={ood.get('ood_rate')} using Mahalanobis threshold={ood.get('mahalanobis_threshold')}.",
            "Block automatic action for OOD inputs and collect review labels.",
        ))
    ref_acc = ref_metrics.get("accuracy")
    cur_acc = cur_metrics.get("accuracy")
    if ref_acc is not None and cur_acc is not None and (ref_acc - cur_acc) >= 0.05:
        failures.append(FailureSignal(
            "F9_MODEL_DECAY_OVER_TIME", "medium",
            f"Accuracy changed from {ref_acc} to {cur_acc} under shifted current data.",
            "Schedule retraining evaluation with current-distribution samples.",
        ))
    if conf.get("average_set_size", 1.0) > 1.20:
        failures.append(FailureSignal(
            "F8_WIDE_PREDICTION_INTERVAL", "medium",
            f"Average conformal set size={conf.get('average_set_size')}.",
            "Use prediction sets rather than single-class automation.",
        ))
    critical_conditions = sum([
        bool(drift.get("feature_drift_detected")),
        bool(ood.get("ood_warning")),
        bool(cal.get("calibration_warning")),
        bool(ref_acc is not None and cur_acc is not None and (ref_acc - cur_acc) >= 0.05),
    ])
    if critical_conditions >= 2:
        failures.append(FailureSignal(
            "F10_UNSAFE_AUTO_DECISION", "critical",
            f"{critical_conditions} major reliability conditions are active simultaneously.",
            "Disable automatic decisioning for affected slices and require human review.",
        ))
    return failures


def regression_failures(m2: dict[str, Any], m3: dict[str, Any]) -> list[FailureSignal]:
    failures: list[FailureSignal] = []
    intervals = m2.get("conformal_prediction_intervals", {})
    drift = m3.get("drift_summary", {})
    ref_metrics = m3.get("reference_metrics", {})
    cur_metrics = m3.get("current_shifted_metrics", {})
    ood = m3.get("ood_report", {})

    if drift.get("feature_drift_detected"):
        failures.append(FailureSignal(
            "F1_DATA_DRIFT", "high",
            f"{_safe_get(m3, 'feature_drift_report', 'num_features_drifted', default=0)} features crossed drift thresholds.",
            "Flag data pipeline drift and pause automatic forecast-based actions.",
        ))
    if drift.get("prediction_drift_detected"):
        failures.append(FailureSignal(
            "F9_MODEL_DECAY_OVER_TIME", "medium",
            f"Prediction PSI={_safe_get(m3, 'prediction_drift_report', 'psi', default='unknown')}.",
            "Compare forecast residuals against current-distribution labels and retrain if confirmed.",
        ))
    if ood.get("ood_warning"):
        failures.append(FailureSignal(
            "F4_OUT_OF_DISTRIBUTION_INPUT", "high",
            f"OOD rate={ood.get('ood_rate')} using Mahalanobis threshold={ood.get('mahalanobis_threshold')}.",
            "Block automation for OOD forecast contexts and request analyst review.",
        ))
    mean_width = intervals.get("mean_interval_width", 0.0)
    rmse = m2.get("metrics", {}).get("rmse", 0.0)
    if rmse and mean_width / max(rmse, 1e-8) >= 3.0:
        failures.append(FailureSignal(
            "F8_WIDE_PREDICTION_INTERVAL", "medium",
            f"Mean conformal interval width={mean_width}; M2 RMSE={rmse}.",
            "Report interval forecasts and avoid point-estimate-only automation.",
        ))
    ref_mae = ref_metrics.get("mae")
    cur_mae = cur_metrics.get("mae")
    if ref_mae is not None and cur_mae is not None and cur_mae >= 1.25 * max(ref_mae, 1e-8):
        failures.append(FailureSignal(
            "F9_MODEL_DECAY_OVER_TIME", "medium",
            f"MAE changed from {ref_mae} to {cur_mae} under shifted current data.",
            "Run retraining benchmark on current data before production use.",
        ))
    critical_conditions = sum([
        bool(drift.get("feature_drift_detected")),
        bool(drift.get("prediction_drift_detected")),
        bool(ood.get("ood_warning")),
        bool(rmse and mean_width / max(rmse, 1e-8) >= 3.0),
    ])
    if critical_conditions >= 2:
        failures.append(FailureSignal(
            "F10_UNSAFE_AUTO_DECISION", "critical",
            f"{critical_conditions} major reliability conditions are active simultaneously.",
            "Disable automatic forecast-triggered actions and escalate for review.",
        ))
    return failures


def build_failure_profile(dataset_key: str, m2_dataset: dict[str, Any], m3_dataset: dict[str, Any]) -> dict[str, Any]:
    if m3_dataset.get("task") == "binary_classification":
        failures = classification_failures(m2_dataset, m3_dataset)
    elif m3_dataset.get("task") == "time_series_regression":
        failures = regression_failures(m2_dataset, m3_dataset)
    else:
        raise ValueError(f"Unsupported task for failure taxonomy: {m3_dataset.get('task')}")

    score_summary = compute_trust_score(failures)
    return {
        "dataset_key": dataset_key,
        "dataset": m3_dataset.get("dataset"),
        "task": m3_dataset.get("task"),
        "model": m3_dataset.get("model"),
        "failure_signals": [f.to_dict() for f in failures],
        "trust_summary": score_summary,
        "honest_scope": "This profile explains reliability risk. It still does not execute repairs.",
    }
