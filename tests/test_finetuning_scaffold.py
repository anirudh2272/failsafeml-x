from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from failsafemlx.finetuning.dataset_builder import (
    build_dataset_from_reliability_cases,
    generate_sample_reliability_records,
    load_jsonl,
    validate_instruction_dataset,
    write_jsonl,
)
from failsafemlx.finetuning.lora_config import default_lora_config, validate_lora_config
from failsafemlx.finetuning.training_stub import create_training_plan, validate_training_plan


def test_sample_reliability_records_are_valid(tmp_path):
    path = tmp_path / "sample.jsonl"
    records = generate_sample_reliability_records()
    write_jsonl(records, path)
    result = validate_instruction_dataset(path)
    assert result["passed"] is True
    assert result["record_count"] >= 10
    assert "RAG_F5_PROMPT_INJECTION_IN_CONTEXT" in result["unique_failure_ids"]
    assert "dataset_validation" in result["domains"]


def test_instruction_dataset_round_trip_jsonl(tmp_path):
    path = tmp_path / "records.jsonl"
    records = build_dataset_from_reliability_cases([
        {
            "failure_id": "F2_MODEL_OVERCONFIDENCE",
            "repair_action": "R1_RECALIBRATE_MODEL",
            "trust_score": 71,
            "routing_decision": "FILTER_AND_RETRY",
            "signal_summary": "High confidence with poor calibration.",
        }
    ] * 10)
    write_jsonl(records, path)
    loaded = load_jsonl(path)
    assert len(loaded) == 10
    assert loaded[0]["metadata"]["repair_action"] == "R1_RECALIBRATE_MODEL"


def test_invalid_instruction_dataset_fails(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"instruction": "missing required fields"}) + "\n", encoding="utf-8")
    result = validate_instruction_dataset(path, min_records=1)
    assert result["passed"] is False
    assert result["errors"]


def test_default_lora_config_is_valid_scaffold():
    config = default_lora_config()
    result = validate_lora_config(config)
    assert result["passed"] is True
    assert result["peft_config_preview"]["r"] == 8
    assert "target_modules" in result["peft_config_preview"]


def test_training_plan_is_ci_safe():
    plan = create_training_plan("data/fine_tuning/reliability_explanations_sample.jsonl")
    result = validate_training_plan(plan)
    assert result["passed"] is True
    assert result["plan"]["training_enabled_by_default"] is False
    assert result["plan"]["downloads_models_during_tests"] is False
    assert result["plan"]["requires_gpu_for_tests"] is False
    assert "peft" in result["plan"]["optional_packages"]


def test_m19_runner_writes_result_report_and_dataset():
    subprocess.run([sys.executable, "scripts/run_m19_finetuning_scaffold.py"], check=True)
    result_path = Path("experiments/results/m19_finetuning_scaffold.json")
    report_path = Path("reports/milestone_19_finetuning_scaffold.md")
    dataset_path = Path("data/fine_tuning/reliability_explanations_sample.jsonl")
    stub_path = Path("docs/optional_lora_training_stub.md")
    assert result_path.exists()
    assert report_path.exists()
    assert dataset_path.exists()
    assert stub_path.exists()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M19_LORA_PEFT_FINETUNING_SCAFFOLD"
    assert payload["passed"] is True
    assert payload["safety_summary"]["training_performed"] is False
    assert payload["safety_summary"]["model_download_performed"] is False


def test_finetuning_docs_are_honest_about_no_training_claim():
    text = Path("docs/finetuning_scaffold.md").read_text(encoding="utf-8")
    assert "No model is fine-tuned" in text
    assert "does not download" in text
    reqs = Path("requirements-finetuning.txt").read_text(encoding="utf-8")
    assert "peft" in reqs
    assert "not required for normal tests" in reqs
