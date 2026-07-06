# Milestone 1 — Baseline Multi-Domain Reliability Benchmark

## Objective

Establish a reproducible baseline for FailSafeML-X before adding uncertainty, drift, failure diagnosis, and repair policies.

## Dataset A — Healthcare-Style Risk Classification

- Dataset type: synthetic binary classification
- Best model: random_forest
- Accuracy: 0.9067
- F1: 0.8583
- AUROC: 0.9592
- Brier score: 0.0808
- Expected Calibration Error: 0.1029

## Dataset B — Energy-Style Time-Series Regression

- Dataset type: synthetic time-series regression
- Best model: gradient_boosting_regressor
- MAE: 3.9615
- RMSE: 4.9204
- MAPE: 2.913
- R2: 0.6289

## Initial Reliability Warnings

- Classification calibration warning: True
- Regression error warning: False

## Honest Limitation

No repair policy yet. Milestone 1 only establishes baseline reliability metrics.

## Next Milestone

Milestone 2 should add calibration curves, conformal prediction, prediction sets/intervals, and reliability-aware confidence reporting.
