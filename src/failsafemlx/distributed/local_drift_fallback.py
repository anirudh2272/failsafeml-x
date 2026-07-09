from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DriftFeatureSummary:
    """Feature-level drift summary for a reference/current batch pair."""

    feature: str
    reference_mean: float
    current_mean: float
    mean_shift: float
    reference_std: float
    current_std: float
    std_shift: float
    psi: float
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriftPipelineResult:
    """Dataset-level drift result."""

    engine: str
    row_count_reference: int
    row_count_current: int
    feature_count: int
    mean_psi: float
    max_psi: float
    overall_severity: str
    top_drifted_features: list[dict[str, Any]]
    feature_summaries: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_synthetic_drift_batches(
    n_reference: int = 1500,
    n_current: int = 1500,
    n_features: int = 8,
    drift_strength: float = 0.65,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate deterministic reference/current batches with controlled drift.

    The first two features receive a mean/variance shift. Remaining features stay
    close to the reference distribution. This keeps the test lightweight while
    creating a real measurable drift signal.
    """

    rng = np.random.default_rng(random_state)
    columns = [f"feature_{idx}" for idx in range(n_features)]

    reference = rng.normal(loc=0.0, scale=1.0, size=(n_reference, n_features))
    current = rng.normal(loc=0.0, scale=1.0, size=(n_current, n_features))

    if n_features >= 1:
        current[:, 0] += drift_strength
    if n_features >= 2:
        current[:, 1] = current[:, 1] * (1.0 + drift_strength / 2.0) + drift_strength / 2.0
    if n_features >= 3:
        current[:, 2] += drift_strength / 4.0

    return pd.DataFrame(reference, columns=columns), pd.DataFrame(current, columns=columns)


def _safe_std(values: pd.Series) -> float:
    std = float(values.std(ddof=0))
    return std if std > 1e-12 else 1e-12


def _psi_for_feature(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    """Compute a PSI-style distribution drift score.

    PSI is computed from quantile bins estimated on the reference batch. Small
    epsilons keep the score finite for sparse bins.
    """

    ref_values = pd.to_numeric(reference, errors="coerce").dropna().to_numpy(dtype=float)
    cur_values = pd.to_numeric(current, errors="coerce").dropna().to_numpy(dtype=float)
    if ref_values.size == 0 or cur_values.size == 0:
        return 0.0

    quantiles = np.linspace(0.0, 1.0, bins + 1)
    edges = np.quantile(ref_values, quantiles)
    edges = np.unique(edges)
    if edges.size < 3:
        low = float(np.min(ref_values)) - 1e-6
        high = float(np.max(ref_values)) + 1e-6
        edges = np.linspace(low, high, min(bins + 1, 4))

    edges[0] = -np.inf
    edges[-1] = np.inf

    ref_counts, _ = np.histogram(ref_values, bins=edges)
    cur_counts, _ = np.histogram(cur_values, bins=edges)

    eps = 1e-6
    ref_pct = np.maximum(ref_counts / max(ref_counts.sum(), 1), eps)
    cur_pct = np.maximum(cur_counts / max(cur_counts.sum(), 1), eps)

    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return float(max(psi, 0.0))


def severity_from_psi(psi: float) -> str:
    if psi >= 0.25:
        return "high"
    if psi >= 0.10:
        return "moderate"
    if psi >= 0.05:
        return "low"
    return "stable"


def overall_severity(feature_summaries: list[DriftFeatureSummary]) -> str:
    if not feature_summaries:
        return "stable"
    max_psi = max(item.psi for item in feature_summaries)
    return severity_from_psi(max_psi)


def analyze_drift_local(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    top_k: int = 5,
    bins: int = 10,
) -> DriftPipelineResult:
    """Analyze large-batch drift with Pandas/NumPy fallback logic."""

    if reference.empty or current.empty:
        raise ValueError("reference and current batches must be non-empty")

    common_features = [col for col in reference.columns if col in current.columns]
    if not common_features:
        raise ValueError("reference and current batches must share at least one feature")

    summaries: list[DriftFeatureSummary] = []
    for feature in common_features:
        ref_series = pd.to_numeric(reference[feature], errors="coerce").dropna()
        cur_series = pd.to_numeric(current[feature], errors="coerce").dropna()
        if ref_series.empty or cur_series.empty:
            continue

        ref_mean = float(ref_series.mean())
        cur_mean = float(cur_series.mean())
        ref_std = _safe_std(ref_series)
        cur_std = _safe_std(cur_series)
        mean_shift = abs(cur_mean - ref_mean) / ref_std
        std_shift = abs(cur_std - ref_std) / ref_std
        psi = _psi_for_feature(ref_series, cur_series, bins=bins)
        summaries.append(
            DriftFeatureSummary(
                feature=feature,
                reference_mean=round(ref_mean, 6),
                current_mean=round(cur_mean, 6),
                mean_shift=round(float(mean_shift), 6),
                reference_std=round(ref_std, 6),
                current_std=round(cur_std, 6),
                std_shift=round(float(std_shift), 6),
                psi=round(psi, 6),
                severity=severity_from_psi(psi),
            )
        )

    if not summaries:
        raise ValueError("no numeric features were available for drift analysis")

    summaries_sorted = sorted(summaries, key=lambda item: item.psi, reverse=True)
    top = [item.to_dict() for item in summaries_sorted[:top_k]]
    psi_values = [item.psi for item in summaries]

    return DriftPipelineResult(
        engine="local_pandas_numpy_fallback",
        row_count_reference=int(len(reference)),
        row_count_current=int(len(current)),
        feature_count=len(summaries),
        mean_psi=round(float(np.mean(psi_values)), 6),
        max_psi=round(float(np.max(psi_values)), 6),
        overall_severity=overall_severity(summaries),
        top_drifted_features=top,
        feature_summaries=[item.to_dict() for item in summaries_sorted],
    )
