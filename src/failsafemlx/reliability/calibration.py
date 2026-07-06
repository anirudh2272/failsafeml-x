from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from failsafemlx.evaluation.metrics import expected_calibration_error


@dataclass(frozen=True)
class CalibrationSummary:
    ece: float
    mean_confidence: float
    high_confidence_rate: float
    low_confidence_rate: float
    overconfidence_gap: float


def confidence_from_binary_probability(y_prob: np.ndarray) -> np.ndarray:
    """Return model confidence for binary probabilities.

    Confidence is the probability assigned to the predicted class, so it is
    max(p, 1-p). This is different from positive-class probability.
    """
    y_prob = np.asarray(y_prob, dtype=float)
    return np.maximum(y_prob, 1.0 - y_prob)


def calibration_bins(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> list[dict[str, float]]:
    """Compute equal-width calibration bins for binary classification."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    rows: list[dict[str, float]] = []
    for idx, (lo, hi) in enumerate(zip(bins[:-1], bins[1:])):
        if idx == 0:
            mask = (y_prob >= lo) & (y_prob <= hi)
        else:
            mask = (y_prob > lo) & (y_prob <= hi)
        count = int(np.sum(mask))
        if count == 0:
            rows.append(
                {
                    "bin_lower": round(float(lo), 4),
                    "bin_upper": round(float(hi), 4),
                    "count": 0,
                    "mean_probability": None,
                    "empirical_positive_rate": None,
                    "abs_gap": None,
                }
            )
            continue
        mean_probability = float(np.mean(y_prob[mask]))
        empirical_positive_rate = float(np.mean(y_true[mask]))
        rows.append(
            {
                "bin_lower": round(float(lo), 4),
                "bin_upper": round(float(hi), 4),
                "count": count,
                "mean_probability": round(mean_probability, 4),
                "empirical_positive_rate": round(empirical_positive_rate, 4),
                "abs_gap": round(abs(mean_probability - empirical_positive_rate), 4),
            }
        )
    return rows


def calibration_summary(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> dict[str, float | bool]:
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)
    confidence = confidence_from_binary_probability(y_prob)
    accuracy = float(np.mean(y_pred == y_true))
    mean_confidence = float(np.mean(confidence))
    ece = expected_calibration_error(y_true, y_prob, n_bins=n_bins)
    overconfidence_gap = max(0.0, mean_confidence - accuracy)
    return {
        "expected_calibration_error": round(float(ece), 4),
        "mean_confidence": round(mean_confidence, 4),
        "empirical_accuracy": round(accuracy, 4),
        "overconfidence_gap": round(float(overconfidence_gap), 4),
        "high_confidence_rate": round(float(np.mean(confidence >= 0.85)), 4),
        "low_confidence_rate": round(float(np.mean(confidence < 0.60)), 4),
        "calibration_warning": bool(ece > 0.08 or overconfidence_gap > 0.05),
    }
