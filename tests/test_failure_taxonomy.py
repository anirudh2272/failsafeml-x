from __future__ import annotations

from failsafemlx.reliability.failure_taxonomy import (
    FailureSignal,
    build_failure_profile,
    compute_trust_score,
    routing_decision_from_score,
)


def test_compute_trust_score_decreases_with_failures():
    failures = [
        FailureSignal("F1_DATA_DRIFT", "high", "drift", "review"),
        FailureSignal("F4_OUT_OF_DISTRIBUTION_INPUT", "high", "ood", "block"),
        FailureSignal("F10_UNSAFE_AUTO_DECISION", "critical", "multiple", "escalate"),
    ]
    summary = compute_trust_score(failures)
    assert summary["trust_score"] < 50
    assert summary["routing_decision"] == "ESCALATE_AND_BLOCK_AUTOMATION"


def test_routing_decision_thresholds():
    assert routing_decision_from_score(90) == "AUTO_ACCEPT"
    assert routing_decision_from_score(70) == "HUMAN_REVIEW"
    assert routing_decision_from_score(50) == "DEFER_OR_REQUEST_MORE_FEATURES"
    assert routing_decision_from_score(20) == "ESCALATE_AND_BLOCK_AUTOMATION"


def test_build_classification_failure_profile_flags_major_signals():
    m2 = {
        "task": "binary_classification",
        "metrics": {"expected_calibration_error": 0.12},
        "calibration_summary": {"calibration_warning": True, "expected_calibration_error": 0.12, "low_confidence_rate": 0.15, "overconfidence_gap": 0.0},
        "conformal_prediction_sets": {"average_set_size": 1.05},
    }
    m3 = {
        "dataset": "demo",
        "task": "binary_classification",
        "model": "rf",
        "feature_drift_report": {"num_features_drifted": 3},
        "drift_summary": {"feature_drift_detected": True, "ood_warning": True},
        "ood_report": {"ood_warning": True, "ood_rate": 0.25, "mahalanobis_threshold": 3.0},
        "reference_metrics": {"accuracy": 0.9},
        "current_shifted_metrics": {"accuracy": 0.82},
    }
    profile = build_failure_profile("healthcare_classification", m2, m3)
    ids = {f["failure_id"] for f in profile["failure_signals"]}
    assert "F1_DATA_DRIFT" in ids
    assert "F4_OUT_OF_DISTRIBUTION_INPUT" in ids
    assert "F7_CALIBRATION_FAILURE" in ids
    assert "F10_UNSAFE_AUTO_DECISION" in ids


def test_build_regression_failure_profile_flags_interval_and_drift():
    m2 = {
        "task": "time_series_regression",
        "metrics": {"rmse": 4.0},
        "conformal_prediction_intervals": {"mean_interval_width": 14.0},
    }
    m3 = {
        "dataset": "demo",
        "task": "time_series_regression",
        "model": "gbr",
        "feature_drift_report": {"num_features_drifted": 4},
        "prediction_drift_report": {"psi": 0.4},
        "drift_summary": {"feature_drift_detected": True, "prediction_drift_detected": True, "ood_warning": True},
        "ood_report": {"ood_warning": True, "ood_rate": 0.31, "mahalanobis_threshold": 4.0},
        "reference_metrics": {"mae": 3.0},
        "current_shifted_metrics": {"mae": 5.0},
    }
    profile = build_failure_profile("energy_timeseries", m2, m3)
    ids = [f["failure_id"] for f in profile["failure_signals"]]
    assert "F8_WIDE_PREDICTION_INTERVAL" in ids
    assert "F1_DATA_DRIFT" in ids
    assert "F10_UNSAFE_AUTO_DECISION" in ids
