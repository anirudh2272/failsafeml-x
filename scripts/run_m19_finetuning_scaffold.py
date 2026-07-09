from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.finetuning.dataset_builder import (  # noqa: E402
    generate_sample_reliability_records,
    validate_instruction_dataset,
    write_jsonl,
)
from failsafemlx.finetuning.lora_config import default_lora_config, validate_lora_config  # noqa: E402
from failsafemlx.finetuning.training_stub import (  # noqa: E402
    create_training_plan,
    render_training_stub,
    validate_training_plan,
)

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATASET_PATH = PROJECT_ROOT / "data" / "fine_tuning" / "reliability_explanations_sample.jsonl"
TRAINING_STUB_PATH = PROJECT_ROOT / "docs" / "optional_lora_training_stub.md"


def run_m19_finetuning_scaffold() -> dict[str, Any]:
    records = generate_sample_reliability_records()
    write_jsonl(records, DATASET_PATH)

    lora_config = default_lora_config()
    dataset_validation = validate_instruction_dataset(DATASET_PATH)
    lora_validation = validate_lora_config(lora_config)
    training_plan = create_training_plan(DATASET_PATH.relative_to(PROJECT_ROOT), config=lora_config)
    training_validation = validate_training_plan(training_plan)

    TRAINING_STUB_PATH.write_text(render_training_stub(training_plan, lora_config), encoding="utf-8")

    errors: list[str] = []
    for section_name, section in [
        ("dataset_validation", dataset_validation),
        ("lora_validation", lora_validation),
        ("training_validation", training_validation),
    ]:
        if not section.get("passed", False):
            errors.append(f"{section_name} failed: {section.get('errors', [])}")

    payload: dict[str, Any] = {
        "milestone": "M19_LORA_PEFT_FINETUNING_SCAFFOLD",
        "passed": not errors,
        "dataset_validation": dataset_validation,
        "lora_validation": lora_validation,
        "training_validation": training_validation,
        "training_plan": training_plan.to_dict(),
        "generated_files": [
            str(DATASET_PATH.relative_to(PROJECT_ROOT)),
            str(TRAINING_STUB_PATH.relative_to(PROJECT_ROOT)),
            "reports/milestone_19_finetuning_scaffold.md",
            "experiments/results/m19_finetuning_scaffold.json",
        ],
        "safety_summary": {
            "gpu_required_for_tests": False,
            "model_download_performed": False,
            "training_performed": False,
            "external_api_calls_performed": False,
            "adapter_weights_created": False,
        },
        "honest_limitations": [
            "This milestone creates a LoRA/PEFT scaffold only; no model is fine-tuned.",
            "The sample dataset is small and synthetic; real training requires a larger reviewed dataset.",
            "No GPU, model download, Hugging Face login, or external provider call is required for tests.",
            "Before real training, review privacy, licensing, evaluation quality, and model safety constraints.",
        ],
        "errors": errors,
        "warnings": dataset_validation.get("warnings", [])
        + lora_validation.get("warnings", [])
        + training_validation.get("warnings", []),
    }
    return payload


def generate_report(payload: dict[str, Any]) -> str:
    dataset = payload["dataset_validation"]
    safety = payload["safety_summary"]
    lines = [
        "# Milestone 19 — LoRA / PEFT Fine-Tuning Scaffold",
        "",
        "## Objective",
        "Add a CI-safe fine-tuning scaffold for reliability explanation and failure-routing examples.",
        "",
        "## Validation Summary",
        f"- Passed: `{payload['passed']}`",
        f"- Instruction records: `{dataset['record_count']}`",
        f"- Unique failure IDs: `{len(dataset['unique_failure_ids'])}`",
        f"- Domains covered: `{', '.join(dataset['domains'])}`",
        f"- Training performed: `{safety['training_performed']}`",
        f"- Model download performed: `{safety['model_download_performed']}`",
        f"- GPU required for tests: `{safety['gpu_required_for_tests']}`",
        f"- Adapter weights created: `{safety['adapter_weights_created']}`",
        "",
        "## Generated Files",
    ]
    for file_name in payload["generated_files"]:
        lines.append(f"- `{file_name}`")
    lines.extend([
        "",
        "## LoRA Configuration Preview",
        "```json",
        json.dumps(payload["lora_validation"]["config"], indent=2),
        "```",
        "",
        "## Honest Limitations",
    ])
    for item in payload["honest_limitations"]:
        lines.append(f"- {item}")
    if payload["warnings"]:
        lines.extend(["", "## Warnings"])
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = run_m19_finetuning_scaffold()
    result_path = RESULTS_DIR / "m19_finetuning_scaffold.json"
    report_path = REPORTS_DIR / "milestone_19_finetuning_scaffold.md"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(generate_report(payload), encoding="utf-8")

    print(f"Wrote {result_path}")
    print(f"Wrote {report_path}")
    if not payload["passed"]:
        raise SystemExit("M19 validation failed. See JSON result for details.")
    print("M19 completed successfully.")


if __name__ == "__main__":
    main()
