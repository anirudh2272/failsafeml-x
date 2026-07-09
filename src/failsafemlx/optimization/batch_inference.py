from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BatchPredictionResult:
    """Container for batch prediction outputs."""

    predictions: list[int]
    probabilities: list[float] | None
    batch_size: int


def predict_in_batches(model: Any, X: pd.DataFrame | np.ndarray, batch_size: int = 128) -> BatchPredictionResult:
    """Run model inference in deterministic mini-batches.

    This function intentionally uses a lightweight sklearn-compatible interface so
    it remains usable without ONNX Runtime, Triton, vLLM, or GPU dependencies.
    """
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    n_rows = len(X)
    predictions: list[int] = []
    probabilities: list[float] | None = [] if hasattr(model, "predict_proba") else None

    for start in range(0, n_rows, batch_size):
        stop = min(start + batch_size, n_rows)
        batch = X.iloc[start:stop] if hasattr(X, "iloc") else X[start:stop]

        batch_predictions = model.predict(batch)
        predictions.extend(int(value) for value in np.asarray(batch_predictions).tolist())

        if probabilities is not None:
            batch_probabilities = model.predict_proba(batch)[:, 1]
            probabilities.extend(float(value) for value in np.asarray(batch_probabilities).tolist())

    return BatchPredictionResult(
        predictions=predictions,
        probabilities=probabilities,
        batch_size=batch_size,
    )


def summarize_prediction_distribution(result: BatchPredictionResult) -> dict[str, float | int | None]:
    """Summarize prediction outputs without exposing raw records."""
    predictions = np.asarray(result.predictions)
    positive_rate = float(np.mean(predictions)) if len(predictions) else 0.0

    mean_probability = None
    if result.probabilities is not None and len(result.probabilities) > 0:
        mean_probability = float(np.mean(result.probabilities))

    return {
        "num_predictions": int(len(result.predictions)),
        "batch_size": int(result.batch_size),
        "positive_prediction_rate": round(positive_rate, 6),
        "mean_positive_probability": None if mean_probability is None else round(mean_probability, 6),
    }
