# Milestone 2 — Uncertainty and Calibration Engine

## Objective

Add uncertainty-aware reliability reporting on top of the Milestone 1 baseline. This milestone introduces calibration analysis and split-conformal uncertainty estimates for classification and regression.

## Dataset A — Healthcare-Style Risk Classification

- Model: random_forest
- Accuracy: 0.8656
- F1: 0.8
- AUROC: 0.9468
- Brier score: 0.0963
- Expected Calibration Error: 0.1058

### Calibration Summary

- Mean confidence: 0.7916
- Empirical accuracy: 0.8656
- Overconfidence gap: 0.0
- High-confidence rate: 0.4188
- Low-confidence rate: 0.1094
- Calibration warning: True

### Split-Conformal Classification Prediction Sets

- Target coverage: 0.9
- Empirical coverage: 0.9
- Average prediction-set size: 1.0781
- Singleton rate: 0.9219
- Empty-set rate: 0.0
- qhat: 0.5604

## Dataset B — Energy-Style Time-Series Regression

- Model: gradient_boosting_regressor
- MAE: 3.2118
- RMSE: 4.03
- MAPE: 2.4548
- R2: 0.6137

### Split-Conformal Regression Prediction Intervals

- Target coverage: 0.9
- Empirical coverage: 0.9339
- Mean interval width: 14.4399
- Median interval width: 14.4399
- qhat residual: 7.2199

## Generated Figures

- `reports/figures/m2_healthcare_calibration.png`
- `reports/figures/m2_energy_prediction_intervals.png`

## Honest Limitation

Milestone 2 adds uncertainty and calibration reporting, but it still does not implement self-healing repair policies. Calibration warnings and conformal intervals are reliability signals, not repairs.

## Next Milestone

Milestone 3 should add drift and out-of-distribution detection so the system can identify when new inputs no longer resemble the training/calibration data.
