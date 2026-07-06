from __future__ import annotations

import numpy as np

from failsafemlx.reliability.calibration import calibration_bins, calibration_summary, confidence_from_binary_probability


def test_confidence_from_probability_uses_predicted_class_probability():
    probs = np.array([0.1, 0.5, 0.9])
    confidence = confidence_from_binary_probability(probs)
    assert np.allclose(confidence, np.array([0.9, 0.5, 0.9]))


def test_calibration_bins_account_for_all_examples():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.2, 0.8, 0.9])
    bins = calibration_bins(y, p, n_bins=5)
    assert sum(row["count"] for row in bins) == 4


def test_calibration_summary_has_warning_key():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.2, 0.8, 0.9])
    summary = calibration_summary(y, p)
    assert "expected_calibration_error" in summary
    assert "calibration_warning" in summary
