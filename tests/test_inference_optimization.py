from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from failsafemlx.optimization.batch_inference import predict_in_batches, summarize_prediction_distribution
from failsafemlx.optimization.inference_benchmark import (
    build_benchmark_model,
    measure_latency,
    run_local_inference_benchmark,
)
from scripts.run_m14_inference_optimization import run_m14


def test_predict_in_batches_returns_all_rows():
    model, X_test, _ = build_benchmark_model(random_state=7)
    X_batch = X_test.iloc[:64]

    result = predict_in_batches(model, X_batch, batch_size=16)

    assert len(result.predictions) == len(X_batch)
    assert result.probabilities is not None
    assert len(result.probabilities) == len(X_batch)
    assert set(result.predictions).issubset({0, 1})


def test_predict_in_batches_rejects_invalid_batch_size():
    model, X_test, _ = build_benchmark_model(random_state=7)

    with pytest.raises(ValueError):
        predict_in_batches(model, X_test.iloc[:10], batch_size=0)


def test_prediction_summary_is_safe_and_aggregate_only():
    model, X_test, _ = build_benchmark_model(random_state=11)
    result = predict_in_batches(model, X_test.iloc[:32], batch_size=8)
    summary = summarize_prediction_distribution(result)

    assert summary["num_predictions"] == 32
    assert 0.0 <= summary["positive_prediction_rate"] <= 1.0
    assert summary["mean_positive_probability"] is not None
    assert 0.0 <= summary["mean_positive_probability"] <= 1.0


def test_measure_latency_returns_positive_stats():
    stats = measure_latency(lambda: np.arange(10).sum(), mode="toy", num_rows=10, repeats=3, warmup=1)

    assert stats.mean_latency_ms > 0
    assert stats.p50_latency_ms > 0
    assert stats.p95_latency_ms >= stats.p50_latency_ms
    assert stats.throughput_rows_per_second > 0


def test_local_inference_benchmark_outputs_expected_sections():
    result = run_local_inference_benchmark(random_state=13, batch_size=32, repeats=3)

    assert result["benchmark_name"] == "local_sklearn_inference_benchmark"
    assert result["num_benchmark_rows"] > 0
    assert set(result["latency"].keys()) == {
        "single_row",
        "vectorized_batch",
        "mini_batch_loop",
    }
    assert result["prediction_summary"]["num_predictions"] == result["num_benchmark_rows"]
    assert "available" in result["optional_onnx_runtime"]


def test_m14_runner_generates_outputs():
    result = run_m14()

    assert result["passed"] is True
    assert Path("experiments/results/m14_inference_optimization.json").exists()
    assert Path("reports/milestone_14_inference_optimization.md").exists()
