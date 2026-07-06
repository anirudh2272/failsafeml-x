# Milestone 3 — Drift and Out-of-Distribution Detection

## Objective

Add reliability monitoring that detects when current inference inputs or predictions no longer resemble the reference training/evaluation distribution.

## Dataset A — Healthcare-Style Risk Classification

- Model: random_forest
- Reference accuracy: 0.8941
- Current shifted accuracy: 0.8765
- Feature drift detected: True
- Prediction drift detected: False
- OOD warning: False
- Risk level: medium

### Top Healthcare Drifted Features
- age_like: PSI=1.2952, KS=0.4559, p=0.0
- bp_like: PSI=0.8068, KS=0.3588, p=0.0
- activity_score: PSI=0.3523, KS=0.2471, p=0.0
- glucose_like: PSI=0.3114, KS=0.2265, p=0.0
- lab_marker_1: PSI=0.1428, KS=0.1706, p=9.8e-05

## Dataset B — Energy-Style Time-Series Regression

- Model: gradient_boosting_regressor
- Reference MAE: 2.7868
- Current shifted MAE: 3.8468
- Feature drift detected: True
- Prediction drift detected: True
- OOD warning: True
- Risk level: high

### Top Energy Drifted Features
- temperature_proxy: PSI=11.1412, KS=0.7205, p=0.0
- rolling_mean_24: PSI=0.927, KS=0.3364, p=0.0
- demand_lag_2: PSI=0.3758, KS=0.2602, p=0.0
- demand_lag_24: PSI=0.3729, KS=0.2556, p=0.0
- demand_lag_1: PSI=0.372, KS=0.2687, p=0.0

## Generated Figures

- `reports/figures/m3_healthcare_feature_drift.png`
- `reports/figures/m3_energy_feature_drift.png`

## Honest Limitation

Milestone 3 detects drift and OOD conditions, but it still does not automatically repair the model or change deployment decisions. Those actions begin in Milestone 4 and Milestone 5.

## Next Milestone

Milestone 4 should convert reliability signals into a failure taxonomy and trust score so the system can explain why a prediction should be trusted, deferred, or escalated.
