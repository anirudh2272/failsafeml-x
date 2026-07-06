from __future__ import annotations

from pathlib import Path
from typing import Any


def write_m2_report(results: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    cls = results["datasets"]["healthcare_classification"]
    reg = results["datasets"]["energy_timeseries"]
    cls_conf = cls["conformal_prediction_sets"]
    reg_conf = reg["conformal_prediction_intervals"]
    cal = cls["calibration_summary"]

    text = f"""# Milestone 2 — Uncertainty and Calibration Engine

## Objective

Add uncertainty-aware reliability reporting on top of the Milestone 1 baseline. This milestone introduces calibration analysis and split-conformal uncertainty estimates for classification and regression.

## Dataset A — Healthcare-Style Risk Classification

- Model: {cls['model']}
- Accuracy: {cls['metrics']['accuracy']}
- F1: {cls['metrics']['f1']}
- AUROC: {cls['metrics']['auroc']}
- Brier score: {cls['metrics']['brier_score']}
- Expected Calibration Error: {cls['metrics']['expected_calibration_error']}

### Calibration Summary

- Mean confidence: {cal['mean_confidence']}
- Empirical accuracy: {cal['empirical_accuracy']}
- Overconfidence gap: {cal['overconfidence_gap']}
- High-confidence rate: {cal['high_confidence_rate']}
- Low-confidence rate: {cal['low_confidence_rate']}
- Calibration warning: {cal['calibration_warning']}

### Split-Conformal Classification Prediction Sets

- Target coverage: {cls_conf['target_coverage']}
- Empirical coverage: {cls_conf['coverage']}
- Average prediction-set size: {cls_conf['average_set_size']}
- Singleton rate: {cls_conf['singleton_rate']}
- Empty-set rate: {cls_conf['empty_set_rate']}
- qhat: {cls_conf['qhat']}

## Dataset B — Energy-Style Time-Series Regression

- Model: {reg['model']}
- MAE: {reg['metrics']['mae']}
- RMSE: {reg['metrics']['rmse']}
- MAPE: {reg['metrics']['mape']}
- R2: {reg['metrics']['r2']}

### Split-Conformal Regression Prediction Intervals

- Target coverage: {reg_conf['target_coverage']}
- Empirical coverage: {reg_conf['coverage']}
- Mean interval width: {reg_conf['mean_interval_width']}
- Median interval width: {reg_conf['median_interval_width']}
- qhat residual: {reg_conf['qhat']}

## Generated Figures

- `reports/figures/m2_healthcare_calibration.png`
- `reports/figures/m2_energy_prediction_intervals.png`

## Honest Limitation

Milestone 2 adds uncertainty and calibration reporting, but it still does not implement self-healing repair policies. Calibration warnings and conformal intervals are reliability signals, not repairs.

## Next Milestone

Milestone 3 should add drift and out-of-distribution detection so the system can identify when new inputs no longer resemble the training/calibration data.
"""
    path.write_text(text, encoding="utf-8")
    return path
