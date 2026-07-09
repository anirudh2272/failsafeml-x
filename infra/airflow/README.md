# Optional Airflow Orchestration

Milestone 11 adds an optional Apache Airflow DAG for scheduled FailSafeML-X reliability evaluation.

The DAG is located at:

```text
infra/airflow/dags/failsafeml_nightly_reliability_dag.py
```

It orchestrates the milestone runners from M1 through M10 in a linear reliability-evaluation workflow.

## Lightweight Validation

Core project tests do not require Airflow. Static validation can be run with:

```bash
python scripts/validate_airflow_dag.py
python scripts/run_m11_airflow_orchestration.py
```

## Optional Airflow Install

Airflow is intentionally not part of `requirements.txt`. To experiment with a real Airflow environment, install optional dependencies separately:

```bash
pip install -r requirements-airflow.txt
```

## Scope

This is an orchestration template and validation layer. It does not claim production Airflow deployment, cloud scheduling, authentication, secret management, SLA monitoring, or production incident response.
