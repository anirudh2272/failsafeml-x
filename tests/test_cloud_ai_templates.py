from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from scripts.run_m18_cloud_ai_templates import validate_cloud_ai_templates


def _load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cloud_ai_required_files_exist():
    result = validate_cloud_ai_templates()
    assert result["passed"] is True
    for file_name in result["required_files"]:
        assert Path(file_name).exists()


def test_sagemaker_template_wraps_prediction_with_reliability_envelope():
    module = _load("cloud/aws/sagemaker/inference.py", "test_sagemaker_template")
    model = module.model_fn("/tmp/model")
    payload = module.input_fn(json.dumps({"features": {"age": 33, "income": None}, "prediction": 1}))
    result = module.predict_fn(payload, model)
    assert result["managed_cloud_target"] == "aws_sagemaker"
    assert "reliability_envelope" in result
    envelope = result["reliability_envelope"]
    assert envelope["trust_score"] < 100
    assert envelope["routing_decision"] in {"ACCEPT", "HUMAN_REVIEW"}
    assert envelope["provider_metadata"]["external_calls_performed"] is False
    rendered = module.output_fn(result)
    assert json.loads(rendered)["managed_cloud_target"] == "aws_sagemaker"


def test_vertex_template_wraps_predictions_with_reliability_envelope():
    module = _load("cloud/gcp/vertex_ai/predictor.py", "test_vertex_template")
    predictor = module.FailSafeMLXVertexPredictor()
    predictor.load("gs://placeholder/model")
    result = predictor.predict([{"features": {"temperature": None}, "prediction": 0.4}])
    assert result["managed_cloud_target"] == "gcp_vertex_ai"
    envelope = result["predictions"][0]["reliability_envelope"]
    assert envelope["trust_score"] < 100
    assert envelope["provider_metadata"]["external_calls_performed"] is False


def test_managed_cloud_templates_do_not_contain_real_secrets():
    joined = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in [
            "cloud/aws/sagemaker/inference.py",
            "cloud/gcp/vertex_ai/predictor.py",
            "cloud/aws/sagemaker/README.md",
            "cloud/gcp/vertex_ai/README.md",
        ]
    )
    forbidden = ["sk-", "AKIA", "BEGIN PRIVATE KEY", "private_key_id"]
    assert not any(marker in joined for marker in forbidden)


def test_m18_runner_writes_result_and_report():
    subprocess.run([sys.executable, "scripts/run_m18_cloud_ai_templates.py"], check=True)
    result_path = Path("experiments/results/m18_cloud_ai_templates.json")
    report_path = Path("reports/milestone_18_cloud_ai_templates.md")
    assert result_path.exists()
    assert report_path.exists()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M18_CLOUD_AI_TEMPLATES"
    assert payload["passed"] is True
    assert payload["template_summary"]["cloud_credentials_required_for_tests"] is False
    assert payload["template_summary"]["live_cloud_deployment_performed"] is False


def test_m18_docs_are_honest_about_no_live_deployment():
    text = Path("docs/managed_cloud_ai.md").read_text(encoding="utf-8")
    assert "does not deploy" in text
    assert "No Google Cloud credentials" in Path("cloud/gcp/vertex_ai/README.md").read_text(encoding="utf-8")
    assert "No AWS credentials" in Path("cloud/aws/sagemaker/README.md").read_text(encoding="utf-8")
