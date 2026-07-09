from __future__ import annotations

from pathlib import Path
import json
import sys
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.tracking.experiment_registry import build_experiment_record
from failsafemlx.tracking.model_card import generate_model_card
from failsafemlx.tracking.risk_card import generate_risk_card

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"

SOURCE_RESULT_FILES = {
    "m14": RESULTS_DIR / "m14_inference_optimization.json",
    "m15b": RESULTS_DIR / "m15b_ragops_reliability.json",
    "m15c": RESULTS_DIR / "m15c_dataset_validation.json",
    "m15d": RESULTS_DIR / "m15d_provider_agent_integration.json",
}

OUTPUT_JSON = RESULTS_DIR / "m15e_experiment_registry.json"
OUTPUT_REPORT = REPORTS_DIR / "milestone_15e_experiment_registry.md"
OUTPUT_RISK_CARD = REPORTS_DIR / "model_risk_card.md"
OUTPUT_MODEL_CARD = REPORTS_DIR / "model_card.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"passed": False, "missing": True, "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def write_markdown_report(record, result: dict) -> None:
    failure_rows = "\n".join(
        f"| `{key}` | {value} |" for key, value in sorted(record.failure_counts.items())
    ) or "| None | 0 |"
    repair_rows = "\n".join(
        f"| `{key}` | {value} |" for key, value in sorted(record.repair_action_counts.items())
    ) or "| None | 0 |"
    warnings = "\n".join(f"- {warning}" for warning in record.warnings) or "- None."

    report = f"""# Milestone 15E — Experiment Registry + Model Risk Card

## Status

- Passed: {result['passed']}
- Run ID: `{record.run_id}`
- Created: {record.created_at_utc}

## What This Milestone Adds

M15E adds a dependency-light local experiment registry and model-risk documentation layer. It records dataset, model, reliability metrics, failure counts, repair actions, trust-score summaries, artifact paths, and best-effort git metadata without requiring MLflow, DVC, cloud storage, or credentials.

## Registry Metrics

```json
{json.dumps(record.metrics, indent=2, sort_keys=True)}
```

## Trust Score Summary

```json
{json.dumps(record.trust_score_summary, indent=2, sort_keys=True)}
```

## Failure Counts

| Failure ID | Count |
|---|---:|
{failure_rows}

## Repair Action Counts

| Repair Action | Count |
|---|---:|
{repair_rows}

## Generated Artifacts

- `experiments/results/m15e_experiment_registry.json`
- `reports/model_risk_card.md`
- `reports/model_card.md`
- `reports/milestone_15e_experiment_registry.md`

## Warnings

{warnings}

## Honest Claim

Added a local experiment registry and model-risk card generator for reproducible reliability evaluation and model-risk documentation. This milestone does not claim a live MLflow server, DVC remote, or formal compliance certification.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    milestone_results = {name: load_json(path) for name, path in SOURCE_RESULT_FILES.items()}
    missing_sources = [name for name, payload in milestone_results.items() if payload.get("missing")]

    record = build_experiment_record(
        milestone_results=milestone_results,
        project_root=PROJECT_ROOT,
        run_id="m15e_local_experiment_registry",
    )

    result = {
        "project": "FailSafeML-X",
        "milestone": "M15E_EXPERIMENT_REGISTRY_MODEL_RISK_CARD",
        "passed": not missing_sources and record.metrics["dataset_validation_errors"] == 0,
        "missing_sources": missing_sources,
        "registry_record": record.to_dict(),
        "generated_outputs": [
            str(OUTPUT_JSON.relative_to(PROJECT_ROOT)),
            str(OUTPUT_REPORT.relative_to(PROJECT_ROOT)),
            str(OUTPUT_RISK_CARD.relative_to(PROJECT_ROOT)),
            str(OUTPUT_MODEL_CARD.relative_to(PROJECT_ROOT)),
        ],
        "failure_count_total": sum(record.failure_counts.values()),
        "repair_action_total": sum(record.repair_action_counts.values()),
        "honest_claim": "Added a local experiment registry and model-risk card generator for reproducible reliability evaluation and model-risk documentation.",
        "honest_limitations": record.limitations,
    }

    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    OUTPUT_RISK_CARD.write_text(generate_risk_card(record), encoding="utf-8")
    OUTPUT_MODEL_CARD.write_text(generate_model_card(record), encoding="utf-8")
    write_markdown_report(record, result)

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_REPORT}")
    print(f"Wrote {OUTPUT_RISK_CARD}")
    print(f"Wrote {OUTPUT_MODEL_CARD}")

    if not result["passed"]:
        raise SystemExit(f"M15E failed validation: {result}")

    print("M15E completed successfully.")


if __name__ == "__main__":
    main()
