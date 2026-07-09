# Milestone 11 — Airflow Orchestration

## Objective

Add optional Apache Airflow-style orchestration for scheduled FailSafeML-X reliability evaluation while keeping the core project lightweight and testable without Airflow installed.

## What M11 Adds

- Optional Airflow DAG template at `infra/airflow/dags/failsafeml_nightly_reliability_dag.py`
- Static DAG validator at `scripts/validate_airflow_dag.py`
- M11 milestone runner at `scripts/run_m11_airflow_orchestration.py`
- Optional dependency file: `requirements-airflow.txt`
- Airflow documentation under `infra/airflow/README.md` and `docs/airflow_orchestration.md`

## DAG Scope

The DAG orchestrates milestone scripts from M1 through M10 in a linear reliability workflow:

1. M1 baseline benchmark
2. M2 uncertainty and calibration
3. M3 drift and OOD detection
4. M4 failure taxonomy and trust score
5. M5 repair engine
6. M6 RL-style repair router
7. M7 API/dashboard demo artifact generation
8. M8 final packaging
9. M9 CI/CD software-quality validation
10. M10 agentic reliability explanation

## Validation Summary

- Passed: True
- DAG task count: 10
- Airflow required for validation: False

## Missing Required Paths

- None

## Warnings

- None

## Errors

- None

## Generated Outputs

- `experiments/results/m11_airflow_orchestration.json`
- `reports/milestone_11_airflow_orchestration.md`

## Honest Limitation

M11 adds an optional orchestration template and static validation. It does not claim a production Airflow deployment, managed scheduler, SLA monitoring, secret backend integration, or cloud-hosted orchestration.
