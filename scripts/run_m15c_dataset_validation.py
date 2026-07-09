from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.data.loaders import load_csv_dataset
from failsafemlx.data.schema import load_dataset_schema
from failsafemlx.data.validators import validate_dataset

RESULT_PATH = PROJECT_ROOT / "experiments/results/m15c_dataset_validation.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_15c_dataset_validation.md"
DATASETS = [
    (
        PROJECT_ROOT / "data/samples/healthcare_sample.csv",
        PROJECT_ROOT / "data/schemas/healthcare_schema.json",
    ),
    (
        PROJECT_ROOT / "data/samples/energy_sample.csv",
        PROJECT_ROOT / "data/schemas/energy_schema.json",
    ),
]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Milestone 15C — Dataset Loader and Validator Layer",
        "",
        "## Objective",
        "",
        "Add a lightweight, dependency-minimal dataset ingestion and validation layer so FailSafeML-X can evaluate CSV datasets before reliability scoring.",
        "",
        "## Validation Summary",
        "",
        f"- Passed: {payload['passed']}",
        f"- Datasets checked: {payload['dataset_count']}",
        f"- Total errors: {payload['total_errors']}",
        f"- Total warnings: {payload['total_warnings']}",
        "",
        "## Dataset Results",
        "",
    ]
    for result in payload["dataset_results"]:
        lines.extend(
            [
                f"### {result['dataset_name']}",
                "",
                f"- Rows: {result['row_count']}",
                f"- Columns: {result['column_count']}",
                f"- Passed: {result['passed']}",
                f"- Errors: {len(result['errors'])}",
                f"- Warnings: {len(result['warnings'])}",
                "",
            ]
        )
        if result["errors"]:
            lines.append("Errors:")
            lines.extend(f"- {error}" for error in result["errors"])
            lines.append("")
        if result["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in result["warnings"])
            lines.append("")
    lines.extend(
        [
            "## Checks Implemented",
            "",
            "- CSV loading",
            "- JSON schema loading",
            "- required-column validation",
            "- numeric-column validation",
            "- categorical-column validation",
            "- target-column validation",
            "- missing-value detection",
            "- duplicate-row detection",
            "- class-imbalance warning",
            "- leakage-like column detection",
            "- timestamp parsing and ordering checks",
            "",
            "## Honest Limitation",
            "",
            "This milestone adds lightweight local dataset validation. It does not claim full data-quality governance, production data contracts, Great Expectations integration, or live feature-store validation.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_m15c() -> dict[str, Any]:
    dataset_results = []
    aggregate_warning_terms: Counter[str] = Counter()
    for dataset_path, schema_path in DATASETS:
        df = load_csv_dataset(dataset_path)
        schema = load_dataset_schema(schema_path)
        result = validate_dataset(df, schema).to_dict()
        result["dataset_path"] = str(dataset_path.relative_to(PROJECT_ROOT))
        result["schema_path"] = str(schema_path.relative_to(PROJECT_ROOT))
        dataset_results.append(result)
        for warning in result["warnings"]:
            aggregate_warning_terms[warning.split(":", 1)[0]] += 1

    total_errors = sum(len(result["errors"]) for result in dataset_results)
    total_warnings = sum(len(result["warnings"]) for result in dataset_results)
    payload: dict[str, Any] = {
        "project": "FailSafeML-X",
        "milestone": "M15C_DATASET_LOADER_VALIDATOR",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": total_errors == 0 and len(dataset_results) == len(DATASETS),
        "dataset_count": len(dataset_results),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "warning_categories": dict(aggregate_warning_terms),
        "dataset_results": dataset_results,
        "generated_outputs": [
            str(RESULT_PATH.relative_to(PROJECT_ROOT)),
            str(REPORT_PATH.relative_to(PROJECT_ROOT)),
        ],
        "honest_claim": "Added a lightweight dataset loader and validation layer for schema, missingness, duplicates, imbalance, leakage indicators, and time-series ordering checks before reliability evaluation.",
    }
    _write_json(RESULT_PATH, payload)
    _write_report(REPORT_PATH, payload)
    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    if not payload["passed"]:
        raise SystemExit(1)
    print("M15C completed successfully.")
    return payload


def main() -> None:
    run_m15c()


if __name__ == "__main__":
    main()
