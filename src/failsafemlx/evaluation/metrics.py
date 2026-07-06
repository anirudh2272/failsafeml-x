from __future__ import annotations

import math
from typing import Any

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute binary Expected Calibration Error using equal-width bins."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (y_prob > lo) & (y_prob <= hi)
        if not np.any(mask):
            continue
        bin_confidence = float(np.mean(y_prob[mask]))
        bin_accuracy = float(np.mean(y_true[mask]))
        bin_weight = float(np.mean(mask))
        ece += bin_weight * abs(bin_accuracy - bin_confidence)
    return float(ece)


def classification_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    y_true = np.asarray(y_true)
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1": round(float(f1_score(y_true, y_pred)), 4),
        "auroc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob)), 4),
        "expected_calibration_error": round(expected_calibration_error(y_true, y_prob), 4),
    }


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    denom = np.maximum(np.abs(y_true), 1e-8)
    mape = np.mean(np.abs((y_true - y_pred) / denom)) * 100.0
    return {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "mape": round(float(mape), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def initial_reliability_summary(classification: dict[str, Any], regression: dict[str, Any]) -> dict[str, Any]:
    """Milestone-1 reliability summary.

    This is intentionally simple. Later milestones replace this with real
    conformal uncertainty, drift scoring, OOD detection, and repair policies.
    """
    ece = classification["metrics"]["expected_calibration_error"]
    brier = classification["metrics"]["brier_score"]
    rmse = regression["metrics"]["rmse"]

    return {
        "classification_calibration_warning": bool(ece > 0.08 or brier > 0.20),
        "regression_error_warning": bool(rmse > 10.0),
        "m1_limitation": "No repair policy yet. Milestone 1 only establishes baseline reliability metrics.",
    }
