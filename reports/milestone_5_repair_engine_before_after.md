# Milestone 5 — Repair Engine and Before/After Benchmark

## Objective

Turn M4 failure-taxonomy outputs into executable repair policies and measure before/after safety tradeoffs on labeled synthetic evaluation data.

## Dataset A — Healthcare-Style Risk Classification

- Repair policy: stricter_threshold_abstention
- Unsafe auto-decision rate before repair: 0.045
- Unsafe auto-decision rate after repair: 0.0109
- Automation rate before repair: 0.6529
- Automation rate after repair: 0.2706
- Active-learning queue size: 248

### Healthcare Repair Actions
- R3_ABSTAIN_FROM_AUTO_DECISION — Abstain from auto decision (execute_now)
  - Priority: 1
  - Trigger failures: F10_UNSAFE_AUTO_DECISION, F3_LOW_CONFIDENCE_PREDICTION
  - Rationale: Triggered by 2 active failure signal(s): F10_UNSAFE_AUTO_DECISION, F3_LOW_CONFIDENCE_PREDICTION.
- R4_ROUTE_TO_HUMAN_REVIEW — Route to human review (execute_now)
  - Priority: 2
  - Trigger failures: F10_UNSAFE_AUTO_DECISION, F1_DATA_DRIFT, F3_LOW_CONFIDENCE_PREDICTION
  - Rationale: Triggered by 3 active failure signal(s): F10_UNSAFE_AUTO_DECISION, F1_DATA_DRIFT, F3_LOW_CONFIDENCE_PREDICTION.
- R8_FLAG_DATA_PIPELINE_DRIFT — Flag data pipeline drift (execute_now)
  - Priority: 3
  - Trigger failures: F1_DATA_DRIFT
  - Rationale: Triggered by 1 active failure signal(s): F1_DATA_DRIFT.
- R1_RECALIBRATE_MODEL — Recalibrate model (apply_policy_guard)
  - Priority: 4
  - Trigger failures: F7_CALIBRATION_FAILURE
  - Rationale: Triggered by 1 active failure signal(s): F7_CALIBRATION_FAILURE.
- R2_APPLY_CONFORMAL_PREDICTION — Apply conformal prediction (apply_policy_guard)
  - Priority: 5
  - Trigger failures: F7_CALIBRATION_FAILURE
  - Rationale: Triggered by 1 active failure signal(s): F7_CALIBRATION_FAILURE.
- R5_TRIGGER_ACTIVE_LEARNING — Trigger active learning (schedule_follow_up)
  - Priority: 7
  - Trigger failures: F10_UNSAFE_AUTO_DECISION
  - Rationale: Triggered by 1 active failure signal(s): F10_UNSAFE_AUTO_DECISION.
- R6_RETRAIN_WITH_REVIEWED_SAMPLES — Retrain with reviewed samples (schedule_follow_up)
  - Priority: 9
  - Trigger failures: F1_DATA_DRIFT
  - Rationale: Triggered by 1 active failure signal(s): F1_DATA_DRIFT.
- R10_REQUEST_MORE_FEATURES — Request more features (schedule_follow_up)
  - Priority: 10
  - Trigger failures: F3_LOW_CONFIDENCE_PREDICTION
  - Rationale: Triggered by 1 active failure signal(s): F3_LOW_CONFIDENCE_PREDICTION.

## Dataset B — Energy-Style Time-Series Regression

- Repair policy: conformal_interval_abstention_under_drift
- Unsafe auto-decision rate before repair: 0.1266
- Unsafe auto-decision rate after repair: 0.0
- Automation rate before repair: 1.0
- Automation rate after repair: 0.0
- Active-learning queue size: 237

### Energy Repair Actions
- R3_ABSTAIN_FROM_AUTO_DECISION — Abstain from auto decision (execute_now)
  - Priority: 1
  - Trigger failures: F10_UNSAFE_AUTO_DECISION, F4_OUT_OF_DISTRIBUTION_INPUT, F8_WIDE_PREDICTION_INTERVAL
  - Rationale: Triggered by 3 active failure signal(s): F10_UNSAFE_AUTO_DECISION, F4_OUT_OF_DISTRIBUTION_INPUT, F8_WIDE_PREDICTION_INTERVAL.
- R4_ROUTE_TO_HUMAN_REVIEW — Route to human review (execute_now)
  - Priority: 2
  - Trigger failures: F10_UNSAFE_AUTO_DECISION, F1_DATA_DRIFT, F4_OUT_OF_DISTRIBUTION_INPUT
  - Rationale: Triggered by 3 active failure signal(s): F10_UNSAFE_AUTO_DECISION, F1_DATA_DRIFT, F4_OUT_OF_DISTRIBUTION_INPUT.
- R8_FLAG_DATA_PIPELINE_DRIFT — Flag data pipeline drift (execute_now)
  - Priority: 3
  - Trigger failures: F1_DATA_DRIFT
  - Rationale: Triggered by 1 active failure signal(s): F1_DATA_DRIFT.
- R2_APPLY_CONFORMAL_PREDICTION — Apply conformal prediction (apply_policy_guard)
  - Priority: 5
  - Trigger failures: F8_WIDE_PREDICTION_INTERVAL
  - Rationale: Triggered by 1 active failure signal(s): F8_WIDE_PREDICTION_INTERVAL.
- R5_TRIGGER_ACTIVE_LEARNING — Trigger active learning (schedule_follow_up)
  - Priority: 7
  - Trigger failures: F10_UNSAFE_AUTO_DECISION, F4_OUT_OF_DISTRIBUTION_INPUT
  - Rationale: Triggered by 2 active failure signal(s): F10_UNSAFE_AUTO_DECISION, F4_OUT_OF_DISTRIBUTION_INPUT.
- R7_SWITCH_TO_BACKUP_MODEL — Switch to backup model (schedule_follow_up)
  - Priority: 8
  - Trigger failures: F9_MODEL_DECAY_OVER_TIME
  - Rationale: Triggered by 1 active failure signal(s): F9_MODEL_DECAY_OVER_TIME.
- R6_RETRAIN_WITH_REVIEWED_SAMPLES — Retrain with reviewed samples (schedule_follow_up)
  - Priority: 9
  - Trigger failures: F1_DATA_DRIFT, F9_MODEL_DECAY_OVER_TIME
  - Rationale: Triggered by 2 active failure signal(s): F1_DATA_DRIFT, F9_MODEL_DECAY_OVER_TIME.

## Generated Figures

- `reports/figures/m5_unsafe_auto_decision_rate.png`
- `reports/figures/m5_automation_tradeoff.png`

## Honest Limitation

Milestone 5 implements repair policies as engineering guardrails and evaluates them on labeled synthetic data. The repair engine reduces unsafe automation primarily through abstention, stricter thresholds, conformal guardrails, and human-review routing. It is not a production safety certification and it does not yet perform online retraining.

## Next Milestone

Milestone 6 should add an RL-style repair router that learns when to accept, abstain, defer, request review, or trigger retraining using a cost-sensitive reward function.
