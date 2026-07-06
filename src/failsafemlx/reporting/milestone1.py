from __future__ import annotations

from pathlib import Path
from typing import Any

from failsafemlx.utils.io import ensure_dir


def write_m1_report(results: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)

    hc = results["datasets"]["healthcare_classification"]
    ts = results["datasets"]["energy_timeseries"]
    rel = results["initial_reliability_summary"]

    content = f"""# Milestone 1 — Baseline Multi-Domain Reliability Benchmark

## Objective

Establish a reproducible baseline for FailSafeML-X before adding uncertainty, drift, failure diagnosis, and repair policies.

## Dataset A — Healthcare-Style Risk Classification

- Dataset type: synthetic binary classification
- Best model: {hc["best_model"]}
- Accuracy: {hc["metrics"]["accuracy"]}
- F1: {hc["metrics"]["f1"]}
- AUROC: {hc["metrics"]["auroc"]}
- Brier score: {hc["metrics"]["brier_score"]}
- Expected Calibration Error: {hc["metrics"]["expected_calibration_error"]}

## Dataset B — Energy-Style Time-Series Regression

- Dataset type: synthetic time-series regression
- Best model: {ts["best_model"]}
- MAE: {ts["metrics"]["mae"]}
- RMSE: {ts["metrics"]["rmse"]}
- MAPE: {ts["metrics"]["mape"]}
- R2: {ts["metrics"]["r2"]}

## Initial Reliability Warnings

- Classification calibration warning: {rel["classification_calibration_warning"]}
- Regression error warning: {rel["regression_error_warning"]}

## Honest Limitation

{rel["m1_limitation"]}

## Next Milestone

Milestone 2 should add calibration curves, conformal prediction, prediction sets/intervals, and reliability-aware confidence reporting.
"""
    path.write_text(content, encoding="utf-8")
    return path
