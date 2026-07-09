from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from failsafemlx.data.synthetic import make_healthcare_risk_dataset
from failsafemlx.models.baselines import build_healthcare_models
from failsafemlx.optimization.batch_inference import predict_in_batches, summarize_prediction_distribution


@dataclass(frozen=True)
class LatencyStats:
    """Latency and throughput summary for a measured inference mode."""

    mode: str
    repeats: int
    num_rows: int
    mean_latency_ms: float
    median_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    throughput_rows_per_second: float

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "mode": self.mode,
            "repeats": self.repeats,
            "num_rows": self.num_rows,
            "mean_latency_ms": round(self.mean_latency_ms, 6),
            "median_latency_ms": round(self.median_latency_ms, 6),
            "p50_latency_ms": round(self.p50_latency_ms, 6),
            "p95_latency_ms": round(self.p95_latency_ms, 6),
            "min_latency_ms": round(self.min_latency_ms, 6),
            "max_latency_ms": round(self.max_latency_ms, 6),
            "throughput_rows_per_second": round(self.throughput_rows_per_second, 6),
        }


def percentile(values: list[float], q: float) -> float:
    """Small dependency-free percentile helper."""
    if not values:
        raise ValueError("values must not be empty")
    return float(np.percentile(np.asarray(values, dtype=float), q))


def measure_latency(
    fn: Callable[[], Any],
    *,
    mode: str,
    num_rows: int,
    repeats: int = 20,
    warmup: int = 3,
) -> LatencyStats:
    """Measure wall-clock latency for a deterministic local inference call."""
    if repeats <= 0:
        raise ValueError("repeats must be positive")
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if num_rows <= 0:
        raise ValueError("num_rows must be positive")

    for _ in range(warmup):
        fn()

    latencies_ms: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        stop = time.perf_counter()
        latencies_ms.append((stop - start) * 1000.0)

    mean_ms = float(statistics.mean(latencies_ms))
    total_rows_per_call = float(num_rows)
    throughput = 1000.0 * total_rows_per_call / mean_ms if mean_ms > 0 else 0.0

    return LatencyStats(
        mode=mode,
        repeats=repeats,
        num_rows=num_rows,
        mean_latency_ms=mean_ms,
        median_latency_ms=float(statistics.median(latencies_ms)),
        p50_latency_ms=percentile(latencies_ms, 50),
        p95_latency_ms=percentile(latencies_ms, 95),
        min_latency_ms=float(min(latencies_ms)),
        max_latency_ms=float(max(latencies_ms)),
        throughput_rows_per_second=float(throughput),
    )


def build_benchmark_model(random_state: int = 42) -> tuple[Any, pd.DataFrame, pd.Series]:
    """Train a compact sklearn model for local inference benchmarking."""
    X, y = make_healthcare_risk_dataset(n_samples=600, random_state=random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=random_state,
    )
    model = build_healthcare_models(random_state=random_state)["logistic_regression"]
    model.fit(X_train, y_train)
    return model, X_test.reset_index(drop=True), y_test.reset_index(drop=True)


def check_optional_onnx_runtime() -> dict[str, Any]:
    """Return optional ONNX Runtime availability without requiring it."""
    try:
        import onnxruntime as ort  # type: ignore
    except Exception:
        return {
            "available": False,
            "package": "onnxruntime",
            "note": "ONNX Runtime is optional and was not required for this milestone.",
        }

    return {
        "available": True,
        "package": "onnxruntime",
        "version": getattr(ort, "__version__", "unknown"),
        "note": "ONNX Runtime is available, but the default benchmark remains sklearn-compatible for portability.",
    }


def run_local_inference_benchmark(
    *,
    random_state: int = 42,
    batch_size: int = 128,
    repeats: int = 12,
) -> dict[str, Any]:
    """Run a lightweight inference benchmark with honest, local-only results."""
    model, X_test, _ = build_benchmark_model(random_state=random_state)
    sample_one = X_test.iloc[[0]]
    batch = X_test.iloc[: min(256, len(X_test))]

    single_stats = measure_latency(
        lambda: model.predict_proba(sample_one),
        mode="single_row_predict_proba",
        num_rows=1,
        repeats=repeats,
    )
    full_batch_stats = measure_latency(
        lambda: model.predict_proba(batch),
        mode="vectorized_batch_predict_proba",
        num_rows=len(batch),
        repeats=repeats,
    )
    mini_batch_stats = measure_latency(
        lambda: predict_in_batches(model, batch, batch_size=batch_size),
        mode="mini_batch_prediction_loop",
        num_rows=len(batch),
        repeats=repeats,
    )

    batch_result = predict_in_batches(model, batch, batch_size=batch_size)
    prediction_summary = summarize_prediction_distribution(batch_result)

    single_throughput = single_stats.throughput_rows_per_second
    batch_throughput = full_batch_stats.throughput_rows_per_second
    throughput_ratio = batch_throughput / single_throughput if single_throughput > 0 else 0.0

    return {
        "benchmark_name": "local_sklearn_inference_benchmark",
        "model_family": "logistic_regression_classifier",
        "dataset": "synthetic_healthcare_risk",
        "num_benchmark_rows": int(len(batch)),
        "batch_size": int(batch_size),
        "repeats": int(repeats),
        "latency": {
            "single_row": single_stats.to_dict(),
            "vectorized_batch": full_batch_stats.to_dict(),
            "mini_batch_loop": mini_batch_stats.to_dict(),
        },
        "throughput_ratio_batch_vs_single": round(float(throughput_ratio), 6),
        "prediction_summary": prediction_summary,
        "optional_onnx_runtime": check_optional_onnx_runtime(),
        "optimization_notes": [
            "Vectorized sklearn inference is benchmarked as the portable default path.",
            "Mini-batch inference is implemented as a reusable utility for larger local batches.",
            "ONNX Runtime is treated as an optional extension and is not required for tests.",
            "No GPU, vLLM, Triton, or production-serving speedup is claimed.",
        ],
    }
