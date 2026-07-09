from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from failsafemlx.distributed.local_drift_fallback import generate_synthetic_drift_batches
from failsafemlx.distributed.spark_drift import analyze_drift_spark_compatible

RESULT_PATH = PROJECT_ROOT / "experiments/results/m12_spark_drift_pipeline.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_12_spark_drift_pipeline.md"

REQUIRED_PATHS = [
    "scripts/run_m12_spark_drift_pipeline.py",
    "src/failsafemlx/distributed/__init__.py",
    "src/failsafemlx/distributed/spark_drift.py",
    "src/failsafemlx/distributed/local_drift_fallback.py",
    "notebooks/databricks_drift_demo.md",
    "tests/test_spark_drift_pipeline.py",
    "requirements-spark.txt",
    "docs/distributed_drift_pipeline.md",
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    analysis = result["drift_analysis"]
    top_lines = "\n".join(
        f"- `{item['feature']}`: PSI={item['psi']}, severity={item['severity']}, "
        f"mean_shift={item['mean_shift']}, std_shift={item['std_shift']}"
        for item in analysis["top_drifted_features"]
    )

    content = f"""# Milestone 12 — PySpark / Databricks-Style Drift Pipeline

## Objective

Add a distributed-style drift monitoring layer for large-batch feature reliability checks. The implementation exposes a PySpark-compatible adapter while keeping a deterministic Pandas/NumPy fallback for local tests.

## What M12 Adds

- `src/failsafemlx/distributed/local_drift_fallback.py`
- `src/failsafemlx/distributed/spark_drift.py`
- `scripts/run_m12_spark_drift_pipeline.py`
- `notebooks/databricks_drift_demo.md`
- `docs/distributed_drift_pipeline.md`
- `requirements-spark.txt`

## Drift Metrics

The pipeline computes:

- feature mean shift
- feature standard-deviation shift
- PSI-style distribution drift score
- top drifted features
- feature-level severity labels
- overall batch drift severity

## Validation Summary

- Passed: {result['passed']}
- Engine: {analysis['engine']}
- Spark available locally: {analysis['spark_available']}
- Reference rows: {analysis['row_count_reference']}
- Current rows: {analysis['row_count_current']}
- Feature count: {analysis['feature_count']}
- Mean PSI: {analysis['mean_psi']}
- Max PSI: {analysis['max_psi']}
- Overall severity: {analysis['overall_severity']}

## Top Drifted Features

{top_lines}

## Generated Outputs

- `experiments/results/m12_spark_drift_pipeline.json`
- `reports/milestone_12_spark_drift_pipeline.md`

## Honest Limitation

M12 provides a PySpark-compatible interface and Databricks-style workflow documentation. It does not claim that a Databricks cluster or production Spark job has been deployed.
"""
    path.write_text(content, encoding="utf-8")


def run_m12() -> dict[str, Any]:
    missing_paths = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]
    errors = [f"Missing required path: {path}" for path in missing_paths]
    warnings: list[str] = []

    reference, current = generate_synthetic_drift_batches()
    drift_analysis = analyze_drift_spark_compatible(reference, current, top_k=5)

    if drift_analysis["feature_count"] < 3:
        errors.append("Drift analysis should evaluate at least three features.")
    if not drift_analysis["top_drifted_features"]:
        errors.append("Drift analysis did not return top drifted features.")
    if drift_analysis["overall_severity"] == "stable":
        warnings.append("Synthetic drift pipeline returned stable overall severity; expected measurable drift.")

    result: dict[str, Any] = {
        "project": "FailSafeML-X",
        "milestone": "M12_SPARK_DISTRIBUTED_DRIFT_PIPELINE",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "required_paths_checked": len(REQUIRED_PATHS),
        "missing_required_paths": missing_paths,
        "drift_analysis": drift_analysis,
        "errors": errors,
        "warnings": warnings,
        "generated_outputs": [
            str(RESULT_PATH.relative_to(PROJECT_ROOT)),
            str(REPORT_PATH.relative_to(PROJECT_ROOT)),
        ],
        "honest_claim": "Added PySpark-compatible distributed drift analysis with local fallback for large-batch feature monitoring and Databricks-style workflow documentation. No live Databricks deployment is claimed.",
        "next_milestone": "M13_AI_SECURITY_GUARDRAILS",
    }

    write_json(RESULT_PATH, result)
    write_report(REPORT_PATH, result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if not result["passed"]:
        print("M12 validation failed. Review errors above.")
        raise SystemExit(1)

    print("M12 completed successfully.")
    return result


def main() -> None:
    run_m12()


if __name__ == "__main__":
    main()
