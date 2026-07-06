from __future__ import annotations

import math

import numpy as np


def conformal_quantile(scores: np.ndarray, alpha: float = 0.1) -> float:
    """Finite-sample split-conformal quantile.

    Uses the standard ceil((n + 1) * (1 - alpha)) / n order statistic with
    clipping for tiny calibration sets. Scores should be nonconformity scores.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 1 or len(scores) == 0:
        raise ValueError("scores must be a non-empty 1D array")
    sorted_scores = np.sort(scores)
    n = len(sorted_scores)
    rank = int(math.ceil((n + 1) * (1.0 - alpha)))
    rank = min(max(rank, 1), n)
    return float(sorted_scores[rank - 1])


def binary_conformal_prediction_sets(
    y_cal: np.ndarray,
    prob_cal: np.ndarray,
    prob_test: np.ndarray,
    alpha: float = 0.1,
) -> tuple[list[list[int]], float]:
    """Return split-conformal prediction sets for binary classifiers.

    Nonconformity score is 1 - probability assigned to the true class.
    A test label is included when its class probability is >= 1 - qhat.
    """
    y_cal = np.asarray(y_cal).astype(int)
    prob_cal = np.asarray(prob_cal, dtype=float)
    prob_test = np.asarray(prob_test, dtype=float)
    true_class_probs = np.where(y_cal == 1, prob_cal, 1.0 - prob_cal)
    scores = 1.0 - true_class_probs
    qhat = conformal_quantile(scores, alpha=alpha)
    threshold = 1.0 - qhat
    sets: list[list[int]] = []
    for p in prob_test:
        label_set = []
        if 1.0 - p >= threshold:
            label_set.append(0)
        if p >= threshold:
            label_set.append(1)
        sets.append(label_set)
    return sets, qhat


def summarize_prediction_sets(y_true: np.ndarray, prediction_sets: list[list[int]]) -> dict[str, float]:
    y_true = np.asarray(y_true).astype(int)
    if len(y_true) != len(prediction_sets):
        raise ValueError("y_true and prediction_sets must have the same length")
    contains = [int(y in s) for y, s in zip(y_true, prediction_sets)]
    sizes = [len(s) for s in prediction_sets]
    return {
        "coverage": round(float(np.mean(contains)), 4),
        "average_set_size": round(float(np.mean(sizes)), 4),
        "singleton_rate": round(float(np.mean([size == 1 for size in sizes])), 4),
        "empty_set_rate": round(float(np.mean([size == 0 for size in sizes])), 4),
    }


def regression_conformal_interval(
    y_cal: np.ndarray,
    pred_cal: np.ndarray,
    pred_test: np.ndarray,
    alpha: float = 0.1,
) -> tuple[np.ndarray, np.ndarray, float]:
    y_cal = np.asarray(y_cal, dtype=float)
    pred_cal = np.asarray(pred_cal, dtype=float)
    pred_test = np.asarray(pred_test, dtype=float)
    residual_scores = np.abs(y_cal - pred_cal)
    qhat = conformal_quantile(residual_scores, alpha=alpha)
    lower = pred_test - qhat
    upper = pred_test + qhat
    return lower, upper, qhat


def summarize_intervals(y_true: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    if not (len(y_true) == len(lower) == len(upper)):
        raise ValueError("y_true, lower, and upper must have the same length")
    covered = (y_true >= lower) & (y_true <= upper)
    widths = upper - lower
    return {
        "coverage": round(float(np.mean(covered)), 4),
        "mean_interval_width": round(float(np.mean(widths)), 4),
        "median_interval_width": round(float(np.median(widths)), 4),
        "min_interval_width": round(float(np.min(widths)), 4),
        "max_interval_width": round(float(np.max(widths)), 4),
    }
