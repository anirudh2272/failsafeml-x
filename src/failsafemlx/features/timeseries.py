from __future__ import annotations

import pandas as pd


def make_lag_features(
    df: pd.DataFrame,
    target_col: str = "demand",
    lags: tuple[int, ...] = (1, 2, 3, 24, 48, 168),
) -> tuple[pd.DataFrame, pd.Series]:
    work = df.copy()
    work["hour"] = work["timestamp"].dt.hour
    work["dayofweek"] = work["timestamp"].dt.dayofweek
    for lag in lags:
        work[f"{target_col}_lag_{lag}"] = work[target_col].shift(lag)

    work["rolling_mean_24"] = work[target_col].shift(1).rolling(24).mean()
    work["rolling_std_24"] = work[target_col].shift(1).rolling(24).std()
    work = work.dropna().reset_index(drop=True)

    y = work[target_col]
    X = work.drop(columns=["timestamp", target_col])
    return X, y
