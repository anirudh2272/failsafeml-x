from __future__ import annotations

from pathlib import Path

from scripts.run_m11_airflow_orchestration import run_m11
from scripts.validate_airflow_dag import EXPECTED_TASK_IDS, validate_airflow_dag


def test_airflow_dag_static_validation_passes_without_airflow():
    result = validate_airflow_dag()

    assert result["passed"] is True, result["errors"]
    assert result["airflow_required_for_validation"] is False
    assert result["task_count"] == len(EXPECTED_TASK_IDS)


def test_airflow_dag_contains_all_milestone_tasks():
    result = validate_airflow_dag()

    assert result["task_ids_found"] == EXPECTED_TASK_IDS


def test_airflow_dag_file_uses_optional_import_fallback():
    dag_path = Path("infra/airflow/dags/failsafeml_nightly_reliability_dag.py")
    content = dag_path.read_text(encoding="utf-8")

    assert "try:" in content
    assert "from airflow" in content
    assert "DAG_SPEC" in content
    assert "build_dag" in content


def test_m11_runner_generates_json_and_report():
    result = run_m11()

    assert result["passed"] is True
    assert Path("experiments/results/m11_airflow_orchestration.json").exists()
    assert Path("reports/milestone_11_airflow_orchestration.md").exists()


def test_airflow_requirements_are_optional_not_core():
    core_requirements = Path("requirements.txt").read_text(encoding="utf-8").lower()
    airflow_requirements = Path("requirements-airflow.txt").read_text(encoding="utf-8").lower()

    assert "apache-airflow" not in core_requirements
    assert "apache-airflow" in airflow_requirements


def test_airflow_docs_exist():
    assert Path("infra/airflow/README.md").exists()
    assert Path("docs/airflow_orchestration.md").exists()
