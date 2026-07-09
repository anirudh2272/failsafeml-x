from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DAG_PATH = PROJECT_ROOT / "infra/airflow/dags/failsafeml_nightly_reliability_dag.py"

EXPECTED_TASK_IDS = [
    "run_m1_baseline",
    "run_m2_uncertainty_calibration",
    "run_m3_drift_ood",
    "run_m4_failure_taxonomy",
    "run_m5_repair_engine",
    "run_m6_rl_router",
    "run_m7_api_dashboard_demo",
    "run_m8_final_packaging",
    "run_m9_cicd_software_quality",
    "run_m10_agentic_reliability",
]

EXPECTED_SCRIPT_COMMANDS = [
    "python scripts/run_m1_baseline.py",
    "python scripts/run_m2_uncertainty_calibration.py",
    "python scripts/run_m3_drift_ood.py",
    "python scripts/run_m4_failure_taxonomy.py",
    "python scripts/run_m5_repair_engine.py",
    "python scripts/run_m6_rl_router.py",
    "python scripts/run_m7_api_dashboard_demo.py",
    "python scripts/run_m8_final_packaging.py",
    "python scripts/run_m9_cicd_software_quality.py",
    "python scripts/run_m10_agentic_reliability.py",
]

FORBIDDEN_SECRET_PATTERNS = [
    "AWS_SECRET_ACCESS_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "password=",
    "secret=",
]


def validate_airflow_dag(dag_path: Path | None = None) -> dict[str, Any]:
    dag_path = dag_path or DAG_PATH
    errors: list[str] = []
    warnings: list[str] = []

    if not dag_path.exists():
        return {
            "passed": False,
            "dag_path": str(dag_path.relative_to(PROJECT_ROOT)),
            "errors": [f"Missing DAG file: {dag_path}"],
            "warnings": [],
            "task_ids_found": [],
            "tasks_expected": EXPECTED_TASK_IDS,
        }

    content = dag_path.read_text(encoding="utf-8", errors="ignore")

    try:
        ast.parse(content)
    except SyntaxError as exc:
        errors.append(f"DAG file has invalid Python syntax: {exc}")

    if "failsafeml_nightly_reliability" not in content:
        errors.append("DAG ID failsafeml_nightly_reliability not found.")

    if "DAG_SPEC" not in content:
        errors.append("DAG_SPEC fallback not found; static validation should not require Airflow.")

    if "try:" not in content or "from airflow" not in content:
        warnings.append("DAG does not appear to use optional Airflow imports.")

    task_ids_found = [task_id for task_id in EXPECTED_TASK_IDS if task_id in content]
    for task_id in EXPECTED_TASK_IDS:
        if task_id not in content:
            errors.append(f"Missing expected DAG task ID: {task_id}")

    for command in EXPECTED_SCRIPT_COMMANDS:
        if command not in content:
            errors.append(f"Missing expected milestone command: {command}")

    if "schedule" not in content and "schedule_interval" not in content:
        errors.append("No schedule or schedule_interval found in DAG file.")

    if ">>" not in content and "dependency_style" not in content:
        warnings.append("No explicit dependency chain marker found.")

    for forbidden in FORBIDDEN_SECRET_PATTERNS:
        if forbidden.lower() in content.lower():
            errors.append(f"Potential secret/config leak pattern found in DAG: {forbidden}")

    return {
        "passed": not errors,
        "dag_path": str(dag_path.relative_to(PROJECT_ROOT)),
        "dag_id": "failsafeml_nightly_reliability",
        "tasks_expected": EXPECTED_TASK_IDS,
        "task_ids_found": task_ids_found,
        "task_count": len(task_ids_found),
        "airflow_required_for_validation": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    result = validate_airflow_dag()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
