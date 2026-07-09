from __future__ import annotations

from pathlib import Path

from scripts.run_m9_cicd_software_quality import run_m9
from scripts.validate_project_structure import validate_project_structure


def test_project_structure_validation_passes():
    result = validate_project_structure()

    assert result["passed"] is True, result["errors"]


def test_required_project_paths_are_checked():
    result = validate_project_structure()

    assert result["required_paths_checked"] >= 30


def test_no_resume_bullet_references_in_readme():
    readme = Path("README.md").read_text(encoding="utf-8").lower()

    assert "suggested resume bullet" not in readme
    assert "resume_bullets" not in readme
    assert "resume bullets" not in readme
    assert "built failsafeml-x, a model-agnostic ml reliability layer" not in readme


def test_m9_runner_generates_json_and_report():
    result = run_m9()

    assert result["passed"] is True
    assert Path("experiments/results/m9_cicd_software_quality.json").exists()
    assert Path("reports/milestone_9_cicd_software_quality.md").exists()


def test_local_only_files_are_not_tracked():
    result = validate_project_structure()

    tracked_file_errors = [
        error for error in result["errors"] if "tracked by git" in error.lower()
    ]

    assert tracked_file_errors == []
