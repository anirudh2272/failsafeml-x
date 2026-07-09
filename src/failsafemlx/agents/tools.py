from __future__ import annotations

from typing import Any

FAILURE_CATALOG: dict[str, dict[str, str]] = {
    "F1_DATA_DRIFT": {
        "name": "Data drift",
        "severity": "high",
        "description": "Current feature distribution differs from the reference/training distribution.",
        "primary_repair": "R8_FLAG_DATA_PIPELINE_DRIFT",
    },
    "F2_MODEL_OVERCONFIDENCE": {
        "name": "Model overconfidence",
        "severity": "high",
        "description": "The model is highly confident while calibration or empirical reliability is weak.",
        "primary_repair": "R1_RECALIBRATE_MODEL",
    },
    "F3_LOW_CONFIDENCE_PREDICTION": {
        "name": "Low-confidence prediction",
        "severity": "medium",
        "description": "Prediction confidence is insufficient for automatic decisioning.",
        "primary_repair": "R3_ABSTAIN_FROM_AUTO_DECISION",
    },
    "F4_OUT_OF_DISTRIBUTION_INPUT": {
        "name": "Out-of-distribution input",
        "severity": "critical",
        "description": "The input appears far from the model's known reference distribution.",
        "primary_repair": "R4_ROUTE_TO_HUMAN_REVIEW",
    },
    "F5_LABEL_NOISE_SUSPECTED": {
        "name": "Label noise suspected",
        "severity": "medium",
        "description": "The sample or region may contain unreliable labels or inconsistent supervision.",
        "primary_repair": "R5_TRIGGER_ACTIVE_LEARNING",
    },
    "F6_CLASS_IMBALANCE_FAILURE": {
        "name": "Class imbalance failure",
        "severity": "medium",
        "description": "Reliability may be weaker for minority or underrepresented classes.",
        "primary_repair": "R9_ADJUST_DECISION_THRESHOLD",
    },
    "F7_CALIBRATION_FAILURE": {
        "name": "Calibration failure",
        "severity": "high",
        "description": "Predicted probabilities do not align well with empirical outcome frequencies.",
        "primary_repair": "R1_RECALIBRATE_MODEL",
    },
    "F8_WIDE_PREDICTION_INTERVAL": {
        "name": "Wide prediction interval",
        "severity": "medium",
        "description": "Conformal or uncertainty interval is too wide for confident automated action.",
        "primary_repair": "R2_APPLY_CONFORMAL_PREDICTION",
    },
    "F9_MODEL_DECAY_OVER_TIME": {
        "name": "Model decay over time",
        "severity": "high",
        "description": "Recent reliability metrics suggest model performance degradation.",
        "primary_repair": "R6_RETRAIN_WITH_REVIEWED_SAMPLES",
    },
    "F10_UNSAFE_AUTO_DECISION": {
        "name": "Unsafe automatic decision",
        "severity": "critical",
        "description": "The case is too risky for automatic action under the current reliability envelope.",
        "primary_repair": "R4_ROUTE_TO_HUMAN_REVIEW",
    },
}

REPAIR_ACTIONS: dict[str, dict[str, str]] = {
    "R1_RECALIBRATE_MODEL": {"decision": "recalibrate", "label": "Recalibrate model"},
    "R2_APPLY_CONFORMAL_PREDICTION": {"decision": "abstain", "label": "Apply conformal prediction"},
    "R3_ABSTAIN_FROM_AUTO_DECISION": {"decision": "abstain", "label": "Abstain from auto decision"},
    "R4_ROUTE_TO_HUMAN_REVIEW": {"decision": "human_review", "label": "Route to human review"},
    "R5_TRIGGER_ACTIVE_LEARNING": {"decision": "active_learning", "label": "Trigger active learning"},
    "R6_RETRAIN_WITH_REVIEWED_SAMPLES": {"decision": "active_learning", "label": "Retrain with reviewed samples"},
    "R7_SWITCH_TO_BACKUP_MODEL": {"decision": "abstain", "label": "Switch to backup model"},
    "R8_FLAG_DATA_PIPELINE_DRIFT": {"decision": "flag_drift", "label": "Flag data pipeline drift"},
    "R9_ADJUST_DECISION_THRESHOLD": {"decision": "abstain", "label": "Adjust decision threshold"},
    "R10_REQUEST_MORE_FEATURES": {"decision": "abstain", "label": "Request more features"},
}


def _clip_score(value: float | None, default: float = 0.0) -> float:
    if value is None:
        value = default
    return max(0.0, min(1.0, float(value)))


def explain_failure_ids(failure_ids: list[str]) -> list[dict[str, Any]]:
    """Explain FailSafeML-X failure IDs using a local deterministic catalog."""
    explanations: list[dict[str, Any]] = []
    for failure_id in failure_ids:
        item = FAILURE_CATALOG.get(failure_id)
        if item is None:
            explanations.append(
                {
                    "failure_id": failure_id,
                    "name": "Unknown failure ID",
                    "severity": "unknown",
                    "description": "This failure ID is not in the local FailSafeML-X catalog.",
                    "primary_repair": "R4_ROUTE_TO_HUMAN_REVIEW",
                }
            )
        else:
            explanations.append({"failure_id": failure_id, **item})
    return explanations


def summarize_trust_score(trust_score: float) -> dict[str, Any]:
    """Convert a numerical trust score into a deployment-facing summary."""
    score = _clip_score(trust_score)
    if score >= 0.80:
        band = "high"
        decision = "accept"
        explanation = "Trust score is high enough for low-risk automation if no critical failures are present."
    elif score >= 0.60:
        band = "moderate"
        decision = "accept_with_monitoring"
        explanation = "Trust score is usable but should be monitored, especially for sensitive decisions."
    elif score >= 0.40:
        band = "low"
        decision = "abstain"
        explanation = "Trust score is weak; automatic decisioning should be avoided."
    else:
        band = "very_low"
        decision = "human_review"
        explanation = "Trust score is too low for automatic decisioning."

    return {
        "trust_score": round(score, 4),
        "trust_band": band,
        "default_decision": decision,
        "explanation": explanation,
    }


def summarize_drift_ood_risk(
    drift_score: float | None = None,
    ood_score: float | None = None,
) -> dict[str, Any]:
    """Summarize combined drift and OOD risk."""
    drift = _clip_score(drift_score)
    ood = _clip_score(ood_score)
    combined = max(drift, ood)

    if combined >= 0.75:
        severity = "critical"
        action = "human_review"
    elif combined >= 0.50:
        severity = "high"
        action = "flag_drift"
    elif combined >= 0.25:
        severity = "medium"
        action = "monitor"
    else:
        severity = "low"
        action = "no_drift_action"

    return {
        "drift_score": round(drift, 4),
        "ood_score": round(ood, 4),
        "combined_risk": round(combined, 4),
        "severity": severity,
        "recommended_drift_action": action,
    }


def recommend_repair_action(
    failure_ids: list[str],
    trust_score: float,
    drift_score: float | None = None,
    ood_score: float | None = None,
    calibration_error: float | None = None,
    uncertainty: float | None = None,
) -> dict[str, Any]:
    """Recommend a deterministic repair action from reliability signals."""
    failures = set(failure_ids)
    trust = _clip_score(trust_score)
    drift = _clip_score(drift_score)
    ood = _clip_score(ood_score)
    ece = _clip_score(calibration_error)
    unc = _clip_score(uncertainty)

    if "F10_UNSAFE_AUTO_DECISION" in failures or "F4_OUT_OF_DISTRIBUTION_INPUT" in failures or trust < 0.40:
        action_id = "R4_ROUTE_TO_HUMAN_REVIEW"
        reason = "Critical safety/OOD/low-trust condition blocks automatic decisioning."
    elif drift >= 0.65 or "F1_DATA_DRIFT" in failures:
        action_id = "R8_FLAG_DATA_PIPELINE_DRIFT"
        reason = "Drift risk is high enough to flag the input/data pipeline before automation."
    elif ece >= 0.12 or "F7_CALIBRATION_FAILURE" in failures or "F2_MODEL_OVERCONFIDENCE" in failures:
        action_id = "R1_RECALIBRATE_MODEL"
        reason = "Calibration or overconfidence risk suggests probability recalibration."
    elif unc >= 0.60 or "F3_LOW_CONFIDENCE_PREDICTION" in failures or "F8_WIDE_PREDICTION_INTERVAL" in failures:
        action_id = "R3_ABSTAIN_FROM_AUTO_DECISION"
        reason = "Uncertainty is too high for automatic action."
    elif "F5_LABEL_NOISE_SUSPECTED" in failures:
        action_id = "R5_TRIGGER_ACTIVE_LEARNING"
        reason = "Potential label-noise region should be routed into review/active learning."
    elif "F6_CLASS_IMBALANCE_FAILURE" in failures:
        action_id = "R9_ADJUST_DECISION_THRESHOLD"
        reason = "Class imbalance risk suggests threshold review before automation."
    elif "F9_MODEL_DECAY_OVER_TIME" in failures:
        action_id = "R6_RETRAIN_WITH_REVIEWED_SAMPLES"
        reason = "Model decay signal suggests retraining with reviewed recent samples."
    else:
        return {
            "action_id": "ACCEPT_WITH_MONITORING",
            "decision": "accept",
            "label": "Accept with monitoring",
            "reason": "No high-severity reliability failures were detected.",
            "auto_decision_allowed": True,
        }

    action = REPAIR_ACTIONS[action_id]
    return {
        "action_id": action_id,
        "decision": action["decision"],
        "label": action["label"],
        "reason": reason,
        "auto_decision_allowed": action["decision"] == "accept",
    }


def generate_human_review_note(
    sample_id: str,
    failure_ids: list[str],
    trust_score: float,
    recommended_action: dict[str, Any],
) -> str:
    """Generate a concise review note without using an external LLM."""
    failures = ", ".join(failure_ids) if failure_ids else "none"
    return (
        f"Sample {sample_id} should be handled with action "
        f"{recommended_action.get('action_id')} ({recommended_action.get('label')}). "
        f"Trust score: {round(_clip_score(trust_score), 4)}. "
        f"Detected failure IDs: {failures}. "
        f"Reason: {recommended_action.get('reason')}"
    )
