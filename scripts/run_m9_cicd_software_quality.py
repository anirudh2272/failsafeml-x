from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.validate_project_structure import validate_project_structure
except ImportError:  # Allows `python scripts/run_m9...` execution.
    from validate_project_structure import validate_project_structure

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = PROJECT_ROOT / "experiments/results/m9_cicd_software_quality.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_9_cicd_software_quality.md"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    warnings = result.get("warnings", [])
    errors = result.get("errors", [])

    warning_lines = "\n".join(f"- {w}" for w in warnings) if warnings else "- None"
    error_lines = "\n".join(f"- {e}" for e in errors) if errors else "- None"

    content = f"""# Milestone 9 — CI/CD and Software Engineering Hardening

## Objective

Add a professional software-engineering validation layer around FailSafeML-X so the project is easier to test, review, reproduce, and extend.

## Added Capabilities

- GitHub Actions CI workflow
- Local CI runner
- Project-structure validation
- Repository hygiene checks
- Docker build validation readiness
- Pytest automation integration
- Software engineering documentation
- M9 JSON and Markdown reporting

## Validation Summary

- Passed: {result["passed"]}
- Required paths checked: {result["required_paths_checked"]}
- Tracked Git files checked: {result["tracked_files_checked"]}

## Warnings

{warning_lines}

## Errors

{error_lines}

## Generated Outputs

- `experiments/results/m9_cicd_software_quality.json`
- `reports/milestone_9_cicd_software_quality.md`

## Skills Demonstrated

- GitHub Actions
- CI/CD
- Pytest automation
- Docker build validation readiness
- Local CI validation
- Repository hygiene checks
- Reproducible ML project validation
- Production-style software engineering practices

## Honest Limitation

This milestone adds CI/CD and software engineering hardening. It does not claim production deployment, cloud hosting, production monitoring, or safety certification.
"""
    path.write_text(content, encoding="utf-8")


def run_m9() -> dict[str, Any]:
    result = validate_project_structure()
    result["project"] = "FailSafeML-X"
    result["status"] = "completed" if result["passed"] else "failed"
    result["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["generated_outputs"] = [
        str(RESULT_PATH.relative_to(PROJECT_ROOT)),
        str(REPORT_PATH.relative_to(PROJECT_ROOT)),
    ]

    write_json(RESULT_PATH, result)
    write_report(REPORT_PATH, result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if not result["passed"]:
        print("M9 validation failed. Review errors above.")
        raise SystemExit(1)

    print("M9 completed successfully.")
    return result


def main() -> None:
    run_m9()


if __name__ == "__main__":
    main()
