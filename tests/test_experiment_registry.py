from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from failsafemlx.tracking.experiment_registry import (
    ExperimentRecord,
    build_experiment_record,
    capture_git_snapshot,
    load_experiment_record,
    save_experiment_record,
)
from failsafemlx.tracking.model_card import generate_model_card
from failsafemlx.tracking.risk_card import generate_risk_card


def sample_milestone_results() -> dict:
    return {
        "m14": {"benchmark": {"latency": {"single_row": {}, "vectorized_batch": {}}}},
        "m15b": {
            "passed": True,
            "aggregate": {
                "average_trust_score": 0.72,
                "failure_counts": {"RAG_F3_MISSING_CITATION": 1},
                "repair_action_counts": {"RAG_R3_REQUIRE_CITATIONS": 1},
            },
        },
        "m15c": {
            "passed": True,
            "dataset_count": 2,
            "total_errors": 0,
            "total_warnings": 1,
            "dataset_results": [{"dataset_name": "healthcare_sample"}, {"dataset_name": "energy_sample"}],
        },
        "m15d": {
            "passed": True,
            "average_trust_score": 0.61,
            "external_api_calls_used": False,
            "external_provider_blocked_by_default": True,
            "failure_counts": {"F1_DATA_DRIFT": 2},
            "repair_action_counts": {"R8_FLAG_DATA_PIPELINE_DRIFT": 2},
            "case_summaries": [{"trust_score": 0.52}, {"trust_score": 0.7}],
        },
    }


def test_build_experiment_record_is_json_compatible(tmp_path: Path):
    record = build_experiment_record(milestone_results=sample_milestone_results(), project_root=tmp_path)
    payload = record.to_dict()
    json.dumps(payload)
    assert payload["project"] == "FailSafeML-X"
    assert payload["metrics"]["dataset_count"] == 2
    assert payload["metrics"]["external_api_calls_used"] is False
    assert payload["failure_counts"]["RAG_F3_MISSING_CITATION"] == 1
    assert payload["failure_counts"]["F1_DATA_DRIFT"] == 2


def test_save_and_load_experiment_record(tmp_path: Path):
    record = build_experiment_record(milestone_results=sample_milestone_results(), project_root=tmp_path)
    target = tmp_path / "registry.json"
    save_experiment_record(record, target)
    loaded = load_experiment_record(target)
    assert isinstance(loaded, ExperimentRecord)
    assert loaded.run_id == record.run_id
    assert loaded.trust_score_summary["mean"] > 0


def test_model_card_contains_safe_claims(tmp_path: Path):
    record = build_experiment_record(milestone_results=sample_milestone_results(), project_root=tmp_path)
    card = generate_model_card(record)
    assert "FailSafeML-X Model Card" in card
    assert "does not claim production certification" in card
    assert "live MLflow/DVC" in card


def test_risk_card_contains_failure_and_repair_tables(tmp_path: Path):
    record = build_experiment_record(milestone_results=sample_milestone_results(), project_root=tmp_path)
    card = generate_risk_card(record)
    assert "Model Risk Card" in card
    assert "RAG_F3_MISSING_CITATION" in card
    assert "RAG_R3_REQUIRE_CITATIONS" in card
    assert "External providers disabled by default" in card


def test_git_snapshot_is_safe_without_git_repo(tmp_path: Path):
    snapshot = capture_git_snapshot(tmp_path)
    assert snapshot.commit
    assert snapshot.branch
    assert isinstance(snapshot.dirty, bool)


def test_m15e_runner_writes_outputs():
    subprocess.run([sys.executable, "scripts/run_m15e_experiment_registry.py"], check=True)
    result_path = Path("experiments/results/m15e_experiment_registry.json")
    report_path = Path("reports/milestone_15e_experiment_registry.md")
    risk_card_path = Path("reports/model_risk_card.md")
    model_card_path = Path("reports/model_card.md")

    assert result_path.exists()
    assert report_path.exists()
    assert risk_card_path.exists()
    assert model_card_path.exists()

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M15E_EXPERIMENT_REGISTRY_MODEL_RISK_CARD"
    assert payload["passed"] is True
