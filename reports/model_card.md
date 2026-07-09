# FailSafeML-X Model Card

## Model / System

- **Project:** FailSafeML-X
- **Model name:** FailSafeML-X reliability envelope prototype
- **Milestone:** M15E_EXPERIMENT_REGISTRY_MODEL_RISK_CARD
- **Run ID:** m15e_local_experiment_registry
- **Created:** 2026-07-09T00:23:53.899854+00:00

## Intended Use

FailSafeML-X is intended to audit ML prediction reliability, assign failure IDs, recommend repair actions, and route risky predictions to safer handling paths such as human review or abstention.

## Data Used in This Prototype Run

- **Datasets:** healthcare_sample + energy_sample + ragops_eval_queries
- **Dataset count:** 2
- **Dataset validation errors:** 0
- **Dataset validation warnings:** 0

## Reliability Capabilities Covered

- Dataset validation passed: True
- RAGOps reliability passed: True
- Provider-aware agent passed: True
- External providers disabled by default: True

## Trust Score Summary

- Minimum: 0.0
- Mean: 0.29
- Maximum: 0.58

## Known Warnings

- Reliability failures were detected and routed through repair policies.
- Git metadata was unavailable; this can happen when running from an extracted ZIP.

## Limitations

- This is a local JSON experiment registry, not a live MLflow Tracking Server.
- This milestone does not require DVC remotes, cloud storage, or credentials.
- Model risk card content is generated from prototype milestone outputs and is not a formal compliance document.

## Safe Claim

This run records a locally validated FailSafeML-X reliability evaluation with local JSON tracking and generated model-risk documentation. It does not claim production certification, live cloud deployment, or a live MLflow/DVC tracking backend.
