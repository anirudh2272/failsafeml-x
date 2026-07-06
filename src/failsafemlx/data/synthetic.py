from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification


def make_healthcare_risk_dataset(
    n_samples: int = 1500,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.Series]:
    """Create a healthcare-style binary risk dataset.

    This is synthetic by design so Milestone 1 is reproducible and does not depend
    on external downloads. It is not medical data and must not be presented as a
    clinical model.
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=14,
        n_informative=8,
        n_redundant=3,
        n_repeated=0,
        n_classes=2,
        weights=[0.68, 0.32],
        class_sep=1.15,
        flip_y=0.035,
        random_state=random_state,
    )
    columns = [
        "age_like",
        "bmi_like",
        "glucose_like",
        "bp_like",
        "cholesterol_like",
        "activity_score",
        "prior_visit_count",
        "medication_count",
        "sleep_score",
        "smoking_proxy",
        "family_history_proxy",
        "lab_marker_1",
        "lab_marker_2",
        "lab_marker_3",
    ]
    return pd.DataFrame(X, columns=columns), pd.Series(y, name="risk_label")


def make_energy_timeseries(
    n_points: int = 1200,
    random_state: int = 42,
) -> pd.DataFrame:
    """Create synthetic energy-demand-like time series with seasonality and drift."""
    rng = np.random.default_rng(random_state)
    t = np.arange(n_points)
    daily = 8.0 * np.sin(2 * np.pi * t / 24)
    weekly = 4.0 * np.sin(2 * np.pi * t / (24 * 7))
    trend = 0.01 * t
    temperature_proxy = 20 + 10 * np.sin(2 * np.pi * t / (24 * 30)) + rng.normal(0, 1.2, n_points)
    demand = 100 + trend + daily + weekly + 0.8 * temperature_proxy + rng.normal(0, 2.5, n_points)

    # Simulate mild distribution shift near the end.
    demand[-200:] += 8.0
    temperature_proxy[-200:] += 2.5

    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=n_points, freq="h"),
            "temperature_proxy": temperature_proxy,
            "demand": demand,
        }
    )
