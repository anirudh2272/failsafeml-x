# Experiment Registry and Model Risk Card

Milestone 15E adds a lightweight local experiment registry for FailSafeML-X.

The goal is to make reliability experiments reproducible without requiring a live MLflow server, DVC remote, cloud storage, or credentials. The registry captures JSON-compatible metadata from existing milestone outputs and generates model-risk documentation for engineering review.

## What is tracked

- project and milestone name
- dataset names
- model/system name
- dataset validation error and warning counts
- RAGOps reliability status
- provider-aware agent status
- failure counts
- repair action counts
- trust score summary
- best-effort git metadata
- generated artifact paths
- honest limitations

## Why this belongs in FailSafeML-X

FailSafeML-X is a reliability layer. A reliability layer should not only detect failures; it should also leave behind an auditable record of what was evaluated, what failed, how it was routed, and what artifacts were generated.

## Generated files

- `experiments/results/m15e_experiment_registry.json`
- `reports/model_risk_card.md`
- `reports/model_card.md`
- `reports/milestone_15e_experiment_registry.md`

## How to run

```bash
python scripts/run_m15e_experiment_registry.py
python scripts/local_ci.py
```

## Honest limitations

This is a local JSON tracking layer. It is MLflow/DVC-style in structure, but it is not a live MLflow Tracking Server, not a DVC remote pipeline, and not a formal compliance system.
