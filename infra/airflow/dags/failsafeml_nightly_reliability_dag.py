"""Optional Airflow DAG for scheduled FailSafeML-X reliability evaluation.

This file is intentionally safe to import without Apache Airflow installed.
When Airflow is unavailable, it exposes a deterministic DAG_SPEC dictionary so
static validation and repository tests still work in lightweight environments.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

DAG_ID = "failsafeml_nightly_reliability"
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MILESTONE_TASKS = [
    ("run_m1_baseline", "python scripts/run_m1_baseline.py"),
    ("run_m2_uncertainty_calibration", "python scripts/run_m2_uncertainty_calibration.py"),
    ("run_m3_drift_ood", "python scripts/run_m3_drift_ood.py"),
    ("run_m4_failure_taxonomy", "python scripts/run_m4_failure_taxonomy.py"),
    ("run_m5_repair_engine", "python scripts/run_m5_repair_engine.py"),
    ("run_m6_rl_router", "python scripts/run_m6_rl_router.py"),
    ("run_m7_api_dashboard_demo", "python scripts/run_m7_api_dashboard_demo.py"),
    ("run_m8_final_packaging", "python scripts/run_m8_final_packaging.py"),
    ("run_m9_cicd_software_quality", "python scripts/run_m9_cicd_software_quality.py"),
    ("run_m10_agentic_reliability", "python scripts/run_m10_agentic_reliability.py"),
]

DAG_SPEC = {
    "dag_id": DAG_ID,
    "description": "Nightly FailSafeML-X reliability benchmarking and artifact generation.",
    "schedule": "@daily",
    "start_date": "2026-01-01",
    "catchup": False,
    "task_ids": [task_id for task_id, _ in MILESTONE_TASKS],
    "commands": {task_id: command for task_id, command in MILESTONE_TASKS},
    "dependency_style": "linear",
}

try:  # pragma: no cover - Airflow is optional in the core test environment.
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except Exception:  # pragma: no cover
    DAG = None
    BashOperator = None


def build_dag():
    """Build an Airflow DAG when Airflow is installed; otherwise return DAG_SPEC."""
    if DAG is None or BashOperator is None:
        return DAG_SPEC

    default_args = {
        "owner": "failsafeml-x",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        dag_id=DAG_ID,
        description=DAG_SPEC["description"],
        schedule=DAG_SPEC["schedule"],
        start_date=datetime(2026, 1, 1),
        catchup=False,
        default_args=default_args,
        tags=["ml-reliability", "failsafeml-x", "optional"],
    ) as dag:
        previous_task = None
        for task_id, command in MILESTONE_TASKS:
            task = BashOperator(
                task_id=task_id,
                bash_command=f"cd {PROJECT_ROOT} && {command}",
            )
            if previous_task is not None:
                previous_task >> task
            previous_task = task

    return dag


dag = build_dag()
