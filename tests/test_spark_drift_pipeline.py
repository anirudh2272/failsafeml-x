from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from failsafemlx.distributed.local_drift_fallback import (
    analyze_drift_local,
    generate_synthetic_drift_batches,
    severity_from_psi,
)
from failsafemlx.distributed.spark_drift import analyze_drift_spark_compatible
from scripts.run_m12_spark_drift_pipeline import run_m12


def test_generate_synthetic_batches_are_deterministic_and_shape_safe():
    reference, current = generate_synthetic_drift_batches(n_reference=100, n_current=120, n_features=5)

    assert reference.shape == (100, 5)
    assert current.shape == (120, 5)
    assert list(reference.columns) == list(current.columns)


def test_local_drift_pipeline_returns_top_drifted_features():
    reference, current = generate_synthetic_drift_batches(n_reference=300, n_current=300, n_features=6)
    result = analyze_drift_local(reference, current, top_k=3).to_dict()

    assert result["engine"] == "local_pandas_numpy_fallback"
    assert result["feature_count"] == 6
    assert len(result["top_drifted_features"]) == 3
    assert result["top_drifted_features"][0]["psi"] >= result["top_drifted_features"][-1]["psi"]
    assert result["overall_severity"] in {"stable", "low", "moderate", "high"}


def test_spark_compatible_adapter_works_without_pyspark():
    reference, current = generate_synthetic_drift_batches(n_reference=200, n_current=200, n_features=4)
    result = analyze_drift_spark_compatible(reference, current, top_k=2)

    assert result["spark_execution_mode"] == "pandas_input_adapter"
    assert result["feature_count"] == 4
    assert len(result["top_drifted_features"]) == 2
    assert "No Databricks deployment" not in result["claim_scope"]


def test_severity_thresholds_are_stable():
    assert severity_from_psi(0.01) == "stable"
    assert severity_from_psi(0.06) == "low"
    assert severity_from_psi(0.12) == "moderate"
    assert severity_from_psi(0.30) == "high"


def test_empty_batches_raise_clear_error():
    with pytest.raises(ValueError, match="non-empty"):
        analyze_drift_local(pd.DataFrame(), pd.DataFrame())


def test_m12_runner_generates_json_and_report():
    result = run_m12()

    assert result["passed"] is True
    assert result["drift_analysis"]["feature_count"] >= 3
    assert Path("experiments/results/m12_spark_drift_pipeline.json").exists()
    assert Path("reports/milestone_12_spark_drift_pipeline.md").exists()
