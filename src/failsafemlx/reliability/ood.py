from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.covariance import EmpiricalCovariance
from sklearn.preprocessing import StandardScaler


def _as_numeric_frame(X: pd.DataFrame | np.ndarray) -> pd.DataFrame:
    if isinstance(X, pd.DataFrame):
        frame = X.select_dtypes(include=["number"]).copy()
    else:
        frame = pd.DataFrame(np.asarray(X, dtype=float))
    if frame.empty:
        raise ValueError("OOD detection requires at least one numeric feature")
    return frame


class MahalanobisOODDetector:
    """Simple distance-based OOD detector for tabular reliability monitoring."""

    def __init__(self, threshold_quantile: float = 0.95):
        if not 0.5 <= threshold_quantile < 1.0:
            raise ValueError("threshold_quantile must be in [0.5, 1.0)")
        self.threshold_quantile = threshold_quantile
        self.scaler = StandardScaler()
        self.cov = EmpiricalCovariance(assume_centered=False)
        self.threshold_: float | None = None
        self.reference_mean_score_: float | None = None
        self.feature_names_: list[str] | None = None

    def fit(self, X_reference: pd.DataFrame | np.ndarray) -> "MahalanobisOODDetector":
        frame = _as_numeric_frame(X_reference)
        self.feature_names_ = list(frame.columns.astype(str))
        X_scaled = self.scaler.fit_transform(frame)
        self.cov.fit(X_scaled)
        scores = self.cov.mahalanobis(X_scaled)
        self.threshold_ = float(np.quantile(scores, self.threshold_quantile))
        self.reference_mean_score_ = float(np.mean(scores))
        return self

    def score(self, X_current: pd.DataFrame | np.ndarray) -> np.ndarray:
        if self.threshold_ is None:
            raise RuntimeError("Detector must be fitted before scoring")
        frame = _as_numeric_frame(X_current)
        X_scaled = self.scaler.transform(frame)
        return self.cov.mahalanobis(X_scaled)

    def report(self, X_current: pd.DataFrame | np.ndarray, *, ood_rate_warning_threshold: float = 0.15) -> dict:
        scores = self.score(X_current)
        threshold = float(self.threshold_)
        ood_mask = scores > threshold
        ood_rate = float(np.mean(ood_mask))
        return {
            "threshold_quantile": self.threshold_quantile,
            "mahalanobis_threshold": round(threshold, 4),
            "reference_mean_score": round(float(self.reference_mean_score_), 4),
            "current_mean_score": round(float(np.mean(scores)), 4),
            "current_median_score": round(float(np.median(scores)), 4),
            "max_score": round(float(np.max(scores)), 4),
            "ood_rate": round(ood_rate, 4),
            "ood_rate_warning_threshold": ood_rate_warning_threshold,
            "ood_warning": bool(ood_rate >= ood_rate_warning_threshold),
        }
