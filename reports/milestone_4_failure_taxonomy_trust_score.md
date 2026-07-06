# Milestone 4 — Failure Taxonomy and Trust Score

## Objective

Convert M2 uncertainty/calibration signals and M3 drift/OOD signals into an explainable failure taxonomy, trust score, and deployment routing decision.

## Dataset A — Healthcare-Style Risk Classification

- Model: random_forest
- Trust score: 17.0
- Risk level: critical
- Routing decision: ESCALATE_AND_BLOCK_AUTOMATION
- Number of active failure signals: 4

### Active Healthcare Failure Signals
- F1_DATA_DRIFT — Data drift (high)
  - Evidence: 5 features crossed drift thresholds.
  - Recommended action: Flag data pipeline drift and evaluate current cohort before automatic decisions.
- F7_CALIBRATION_FAILURE — Calibration failure (medium)
  - Evidence: ECE=0.1058 and calibration_warning=True.
  - Recommended action: Apply recalibration or require calibrated probability reporting before deployment.
- F3_LOW_CONFIDENCE_PREDICTION — Low-confidence prediction (low)
  - Evidence: Low-confidence rate=0.1094.
  - Recommended action: Route low-confidence cases to human review or request more features.
- F10_UNSAFE_AUTO_DECISION — Unsafe auto decision (critical)
  - Evidence: 2 major reliability conditions are active simultaneously.
  - Recommended action: Disable automatic decisioning for affected slices and require human review.

## Dataset B — Energy-Style Time-Series Regression

- Model: gradient_boosting_regressor
- Trust score: 0.0
- Risk level: critical
- Routing decision: ESCALATE_AND_BLOCK_AUTOMATION
- Number of active failure signals: 6

### Active Energy Failure Signals
- F1_DATA_DRIFT — Data drift (high)
  - Evidence: 9 features crossed drift thresholds.
  - Recommended action: Flag data pipeline drift and pause automatic forecast-based actions.
- F9_MODEL_DECAY_OVER_TIME — Model decay over time (medium)
  - Evidence: Prediction PSI=0.1577.
  - Recommended action: Compare forecast residuals against current-distribution labels and retrain if confirmed.
- F4_OUT_OF_DISTRIBUTION_INPUT — Out-of-distribution input (high)
  - Evidence: OOD rate=0.9916 using Mahalanobis threshold=19.0555.
  - Recommended action: Block automation for OOD forecast contexts and request analyst review.
- F8_WIDE_PREDICTION_INTERVAL — Wide prediction interval (medium)
  - Evidence: Mean conformal interval width=14.4399; M2 RMSE=4.03.
  - Recommended action: Report interval forecasts and avoid point-estimate-only automation.
- F9_MODEL_DECAY_OVER_TIME — Model decay over time (medium)
  - Evidence: MAE changed from 2.7868 to 3.8468 under shifted current data.
  - Recommended action: Run retraining benchmark on current data before production use.
- F10_UNSAFE_AUTO_DECISION — Unsafe auto decision (critical)
  - Evidence: 4 major reliability conditions are active simultaneously.
  - Recommended action: Disable automatic forecast-triggered actions and escalate for review.

## Generated Figures

- `reports/figures/m4_trust_scores.png`
- `reports/figures/m4_failure_counts.png`

## Honest Limitation

Milestone 4 explains failures and recommends routing decisions, but it still does not execute repairs. The trust score should be treated as a transparent engineering heuristic, not as a safety certification.

## Next Milestone

Milestone 5 should implement the repair engine: recalibration, abstention, threshold adjustment, backup-model switching, active-learning queue creation, and before/after reliability benchmarks.
