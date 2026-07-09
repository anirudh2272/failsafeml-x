# M11 — Airflow Orchestration

Milestone 11 adds an optional orchestration layer for FailSafeML-X.

## Purpose

The goal is to show how the reliability pipeline can be scheduled as a repeatable workflow without making Airflow a required dependency for normal development, testing, or portfolio review.

## DAG Location

```text
infra/airflow/dags/failsafeml_nightly_reliability_dag.py
```

## Workflow

The DAG runs the milestone scripts from M1 through M10 in order. This turns the project into a scheduled reliability-evaluation workflow:

```text
M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9 → M10
```

## Lightweight Validation

Run:

```bash
python scripts/validate_airflow_dag.py
python scripts/run_m11_airflow_orchestration.py
```

These checks do not require Apache Airflow to be installed.

## Optional Airflow Dependency

Airflow dependencies are isolated in:

```text
requirements-airflow.txt
```

This keeps the core environment lightweight.

## What This Does Not Claim

M11 does not claim production Airflow deployment, managed Airflow service usage, credential storage, alerting, SLA monitoring, or cloud scheduling. It is an orchestration template and validation layer.
