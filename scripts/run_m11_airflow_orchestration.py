from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from validate_airflow_dag import validate_airflow_dag
except ModuleNotFoundError:  # allows pytest imports from repository root
    from scripts.validate_airflow_dag import validate_airflow_dag

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = PROJECT_ROOT / "experiments/results/m11_airflow_orchestration.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_11_airflow_orchestration.md"

REQUIRED_PATHS = [
    "scripts/run_m11_airflow_orchestration.py",
    "scripts/validate_airflow_dag.py",
    "infra/airflow/dags/failsafeml_nightly_reliability_dag.py",
    "infra/airflow/README.md",
    "requirements-airflow.txt",
    "tests/test_airflow_orchestration.py",
    "docs/airflow_orchestration.md",
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    warnings = result.get("warnings", [])
    errors = result.get("errors", [])
    missing_paths = result.get("missing_required_paths", [])
    warning_lines = "\n".join(f"- {w}" for w in warnings) if warnings else "- None"
    error_lines = "\n".join(f"- {e}" for e in errors) if errors else "- None"
    missing_lines = "\n".join(f"- {p}" for p in missing_paths) if missing_paths else "- None"

    content = f"""# Milestone 11 — Airflow Orchestration

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

- Passed: {result['passed']}
- DAG task count: {result.get('dag_validation', {}).get('task_count')}
- Airflow required for validation: {result.get('dag_validation', {}).get('airflow_required_for_validation')}

## Missing Required Paths

{missing_lines}

## Warnings

{warning_lines}

## Errors

{error_lines}

## Generated Outputs

- `experiments/results/m11_airflow_orchestration.json`
- `reports/milestone_11_airflow_orchestration.md`

## Honest Limitation

M11 adds an optional orchestration template and static validation. It does not claim a production Airflow deployment, managed scheduler, SLA monitoring, secret backend integration, or cloud-hosted orchestration.
"""
    path.write_text(content, encoding="utf-8")


def run_m11() -> dict[str, Any]:
    missing_paths = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]
    dag_validation = validate_airflow_dag()

    errors: list[str] = []
    warnings: list[str] = []
    errors.extend(f"Missing required path: {path}" for path in missing_paths)
    errors.extend(dag_validation.get("errors", []))
    warnings.extend(dag_validation.get("warnings", []))

    result: dict[str, Any] = {
        "project": "FailSafeML-X",
        "milestone": "M11_AIRFLOW_ORCHESTRATION",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dag_validation": dag_validation,
        "required_paths_checked": len(REQUIRED_PATHS),
        "missing_required_paths": missing_paths,
        "errors": errors,
        "warnings": warnings,
        "generated_outputs": [
            str(RESULT_PATH.relative_to(PROJECT_ROOT)),
            str(REPORT_PATH.relative_to(PROJECT_ROOT)),
        ],
        "honest_claim": "Added optional Apache Airflow DAG orchestration for scheduled ML reliability benchmarking, repair evaluation, and artifact generation. No production Airflow deployment is claimed.",
        "next_milestone": "M12_SPARK_DISTRIBUTED_DRIFT_PIPELINE",
    }

    write_json(RESULT_PATH, result)
    write_report(REPORT_PATH, result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if not result["passed"]:
        print("M11 validation failed. Review errors above.")
        raise SystemExit(1)

    print("M11 completed successfully.")
    return result


def main() -> None:
    run_m11()


if __name__ == "__main__":
    main()
