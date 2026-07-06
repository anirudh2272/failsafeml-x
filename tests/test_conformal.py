from __future__ import annotations

import numpy as np

from failsafemlx.reliability.conformal import (
    binary_conformal_prediction_sets,
    conformal_quantile,
    regression_conformal_interval,
    summarize_intervals,
    summarize_prediction_sets,
)


def test_conformal_quantile_returns_valid_score():
    scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    qhat = conformal_quantile(scores, alpha=0.2)
    assert 0.1 <= qhat <= 0.5


def test_binary_prediction_sets_cover_high_confidence_examples():
    y_cal = np.array([0, 1, 0, 1, 1, 0])
    prob_cal = np.array([0.05, 0.95, 0.10, 0.90, 0.85, 0.20])
    prob_test = np.array([0.03, 0.97, 0.52])
    sets, qhat = binary_conformal_prediction_sets(y_cal, prob_cal, prob_test, alpha=0.1)
    summary = summarize_prediction_sets(np.array([0, 1, 1]), sets)
    assert qhat >= 0.0
    assert sets[0] == [0]
    assert sets[1] == [1]
    assert summary["coverage"] >= 0.66


def test_regression_intervals_have_positive_width():
    y_cal = np.array([10.0, 12.0, 14.0, 16.0])
    pred_cal = np.array([9.5, 12.5, 13.5, 16.2])
    pred_test = np.array([11.0, 15.0])
    lower, upper, qhat = regression_conformal_interval(y_cal, pred_cal, pred_test, alpha=0.1)
    summary = summarize_intervals(np.array([10.8, 15.4]), lower, upper)
    assert qhat > 0
    assert np.all(upper > lower)
    assert summary["mean_interval_width"] > 0
