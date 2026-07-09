from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    ".env.example",
    ".gitignore",
    ".github/workflows/ci.yml",
    "apps/streamlit_dashboard.py",
    "configs/tabular_healthcare.yaml",
    "configs/timeseries_energy.yaml",
    "docs/architecture.md",
    "docs/demo_script.md",
    "docs/github_release_checklist.md",
    "docs/patent_screening_memo.md",
    "docs/software_engineering.md",
    "reports/final_project_card.md",
    "reports/milestone_8_final_packaging.md",
    "reports/figures/failsafeml_architecture.svg",
    "reports/milestone_9_cicd_software_quality.md",
    "reports/milestone_10_agentic_reliability.md",
    "reports/milestone_11_airflow_orchestration.md",
    "reports/milestone_12_spark_drift_pipeline.md",
    "experiments/results/m9_cicd_software_quality.json",
    "experiments/results/m10_agentic_reliability.json",
    "experiments/results/m11_airflow_orchestration.json",
    "experiments/results/m12_spark_drift_pipeline.json",
    "tests/test_ai_security.py",
    "scripts/run_m13_ai_security.py",
    "src/failsafemlx/security/tool_safety.py",
    "src/failsafemlx/security/prompt_injection.py",
    "src/failsafemlx/security/guardrails.py",
    "security/ai_security_checklist.md",
    "docs/ai_security.md",
    "experiments/results/m13_ai_security.json",
    "reports/milestone_13_ai_security.md",
    "docs/agentic_reliability.md",
    "docs/airflow_orchestration.md",
    "infra/airflow/README.md",
    "infra/airflow/dags/failsafeml_nightly_reliability_dag.py",
    "requirements-airflow.txt",
    "requirements-spark.txt",
    "docs/distributed_drift_pipeline.md",
    "notebooks/databricks_drift_demo.md",
    "src/failsafemlx/distributed/local_drift_fallback.py",
    "src/failsafemlx/distributed/spark_drift.py",
    "scripts/run_m12_spark_drift_pipeline.py",
    "tests/test_spark_drift_pipeline.py",
    "scripts/validate_airflow_dag.py",
    "scripts/run_m11_airflow_orchestration.py",
    "tests/test_airflow_orchestration.py",
    "scripts/run_m1_baseline.py",
    "scripts/run_m2_uncertainty_calibration.py",
    "scripts/run_m3_drift_ood.py",
    "scripts/run_m4_failure_taxonomy.py",
    "scripts/run_m5_repair_engine.py",
    "scripts/run_m6_rl_router.py",
    "scripts/run_m7_api_dashboard_demo.py",
    "scripts/run_m8_final_packaging.py",
    "scripts/run_m9_cicd_software_quality.py",
    "scripts/local_ci.py",
    "src/failsafemlx/data/synthetic.py",
    "src/failsafemlx/evaluation/metrics.py",
    "src/failsafemlx/models/baselines.py",
    "src/failsafemlx/reliability/calibration.py",
    "src/failsafemlx/reliability/conformal.py",
    "src/failsafemlx/reliability/drift.py",
    "src/failsafemlx/reliability/ood.py",
    "src/failsafemlx/reliability/failure_taxonomy.py",
    "src/failsafemlx/reliability/repair_engine.py",
    "src/failsafemlx/reliability/rl_router.py",
    "src/failsafemlx/serving/fastapi_app.py",
    "src/failsafemlx/serving/gateway.py",
    "tests/test_project_structure.py",
    "scripts/run_m14_inference_optimization.py",
    "src/failsafemlx/optimization/inference_benchmark.py",
    "src/failsafemlx/optimization/batch_inference.py",
    "tests/test_inference_optimization.py",
    "docs/inference_optimization.md",
]

README_EXPECTED_TERMS = [
    "FailSafeML-X",
    "model-agnostic",
    "calibration",
    "conformal",
    "drift",
    "OOD",
    "FastAPI",
    "Streamlit",
    "Docker",
    "Airflow",
    "PySpark",
    "Databricks",
    "guardrails",
    "security",
]

README_FORBIDDEN_TERMS = [
    "Suggested Resume Bullet",
    "Built FailSafeML-X, a model-agnostic ML reliability layer",
    "resume_bullets",
    "resume bullets",
]

FORBIDDEN_TRACKED_PREFIXES = [
    ".venv/",
    ".agents/",
    ".claude/",
    ".pytest_cache/",
]

FORBIDDEN_TRACKED_FRAGMENTS = [
    "__pycache__",
    ".DS_Store",
]


def tracked_files() -> list[str]:
    """Return Git-tracked files. If Git is unavailable, return an empty list."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def validate_project_structure() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for rel_path in REQUIRED_PATHS:
        if not (PROJECT_ROOT / rel_path).exists():
            errors.append(f"Missing required path: {rel_path}")

    readme_path = PROJECT_ROOT / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8", errors="ignore")

        for term in README_EXPECTED_TERMS:
            if term not in readme:
                warnings.append(f"README does not mention expected term: {term}")

        readme_lower = readme.lower()
        for term in README_FORBIDDEN_TERMS:
            if term.lower() in readme_lower:
                errors.append(f"README still contains forbidden resume/reference term: {term}")

        if "reports/figures/m8_system_architecture.png" in readme:
            errors.append("README points to old m8_system_architecture.png instead of the labeled SVG.")

    requirements_path = PROJECT_ROOT / "requirements.txt"
    if requirements_path.exists():
        requirements = requirements_path.read_text(encoding="utf-8", errors="ignore")
        if "streamlit" not in requirements.lower():
            warnings.append("requirements.txt does not include streamlit, although the dashboard uses it.")

    gitignore_path = PROJECT_ROOT / ".gitignore"
    if gitignore_path.exists():
        gitignore = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        for expected in [".venv", ".agents", ".claude", ".pytest_cache", "__pycache__", ".DS_Store"]:
            if expected not in gitignore:
                warnings.append(f".gitignore may not ignore: {expected}")

    git_files = tracked_files()
    for file in git_files:
        for prefix in FORBIDDEN_TRACKED_PREFIXES:
            if file.startswith(prefix):
                errors.append(f"Local/environment file is tracked by git: {file}")
        for fragment in FORBIDDEN_TRACKED_FRAGMENTS:
            if fragment in file:
                errors.append(f"Generated/cache file is tracked by git: {file}")

    return {
        "milestone": "M9_CICD_SOFTWARE_ENGINEERING",
        "passed": not errors,
        "required_paths_checked": len(REQUIRED_PATHS),
        "tracked_files_checked": len(git_files),
        "warnings": warnings,
        "errors": errors,
    }


def main() -> None:
    result = validate_project_structure()
    print(json.dumps(result, indent=2))

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
