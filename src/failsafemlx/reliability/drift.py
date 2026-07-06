from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


EPS = 1e-8


def _to_float_array(values: Iterable[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError("values must contain at least one finite numeric value")
    return arr


def population_stability_index(
    reference: Iterable[float],
    current: Iterable[float],
    n_bins: int = 10,
) -> float:
    """Compute PSI using reference quantile bins.

    PSI is used here as an engineering drift score, not as a statistical proof.
    The bins are learned from the reference distribution and then applied to the
    current distribution.
    """
    ref = _to_float_array(reference)
    cur = _to_float_array(current)
    quantiles = np.linspace(0.0, 1.0, n_bins + 1)
    edges = np.quantile(ref, quantiles)
    edges = np.unique(edges)

    if edges.size < 3:
        lo = min(float(np.min(ref)), float(np.min(cur))) - EPS
        hi = max(float(np.max(ref)), float(np.max(cur))) + EPS
        edges = np.linspace(lo, hi, n_bins + 1)

    edges[0] = min(edges[0], float(np.min(cur)), float(np.min(ref))) - EPS
    edges[-1] = max(edges[-1], float(np.max(cur)), float(np.max(ref))) + EPS

    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)
    ref_pct = np.maximum(ref_counts / max(ref_counts.sum(), 1), EPS)
    cur_pct = np.maximum(cur_counts / max(cur_counts.sum(), 1), EPS)
    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return round(float(psi), 4)


def ks_drift_score(reference: Iterable[float], current: Iterable[float]) -> dict[str, float]:
    ref = _to_float_array(reference)
    cur = _to_float_array(current)
    stat, p_value = ks_2samp(ref, cur)
    return {"ks_statistic": round(float(stat), 4), "ks_p_value": round(float(p_value), 6)}


def feature_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    psi_warning_threshold: float = 0.20,
    ks_alpha: float = 0.01,
) -> dict:
    """Return per-feature drift diagnostics for numeric columns shared by two frames."""
    numeric_cols = [
        col for col in reference.columns
        if col in current.columns and pd.api.types.is_numeric_dtype(reference[col])
    ]
    features = []
    for col in numeric_cols:
        psi = population_stability_index(reference[col], current[col])
        ks = ks_drift_score(reference[col], current[col])
        drift_flag = bool(psi >= psi_warning_threshold or ks["ks_p_value"] < ks_alpha)
        features.append(
            {
                "feature": col,
                "psi": psi,
                **ks,
                "drift_flag": drift_flag,
            }
        )

    features_sorted = sorted(features, key=lambda row: (row["drift_flag"], row["psi"]), reverse=True)
    drifted = [row for row in features_sorted if row["drift_flag"]]
    return {
        "num_features_checked": len(features_sorted),
        "num_features_drifted": len(drifted),
        "drift_detected": bool(len(drifted) > 0),
        "psi_warning_threshold": psi_warning_threshold,
        "ks_alpha": ks_alpha,
        "top_drifted_features": drifted[:8],
        "feature_details": features_sorted,
    }


def prediction_drift_report(
    reference_predictions: Iterable[float],
    current_predictions: Iterable[float],
    *,
    psi_warning_threshold: float = 0.10,
    ks_alpha: float = 0.01,
) -> dict:
    psi = population_stability_index(reference_predictions, current_predictions)
    ks = ks_drift_score(reference_predictions, current_predictions)
    drift_flag = bool(psi >= psi_warning_threshold or ks["ks_p_value"] < ks_alpha)
    return {
        "psi": psi,
        **ks,
        "prediction_drift_detected": drift_flag,
        "psi_warning_threshold": psi_warning_threshold,
        "ks_alpha": ks_alpha,
    }


def summarize_drift(feature_report: dict, prediction_report: dict, ood_report: dict) -> dict:
    return {
        "feature_drift_detected": bool(feature_report["drift_detected"]),
        "prediction_drift_detected": bool(prediction_report["prediction_drift_detected"]),
        "ood_warning": bool(ood_report["ood_warning"]),
        "num_feature_warnings": int(feature_report["num_features_drifted"]),
        "risk_level": "high" if (
            feature_report["drift_detected"] and (prediction_report["prediction_drift_detected"] or ood_report["ood_warning"])
        ) else "medium" if (feature_report["drift_detected"] or prediction_report["prediction_drift_detected"] or ood_report["ood_warning"]) else "low",
    }
