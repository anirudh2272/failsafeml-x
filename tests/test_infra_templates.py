from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.validate_infra_templates import validate_infra_templates


def test_infra_required_files_exist():
    result = validate_infra_templates()
    assert result["passed"] is True
    for file_name in result["required_files"]:
        assert Path(file_name).exists()


def test_terraform_templates_have_safe_provider_defaults():
    text = Path("infra/terraform/main.tf").read_text(encoding="utf-8")
    assert "FAILSAFEMLX_PROVIDER_MODE" in text
    assert "local" in text
    assert "FAILSAFEMLX_ENABLE_EXTERNAL_LLM" in text
    assert "false" in text
    assert "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB" in text
    assert "/health" in text


def test_helm_values_have_safe_offline_defaults():
    text = Path("charts/failsafeml-x/values.yaml").read_text(encoding="utf-8")
    assert "FAILSAFEMLX_PROVIDER_MODE: local" in text
    assert 'FAILSAFEMLX_ENABLE_EXTERNAL_LLM: "false"' in text
    assert 'FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB: "false"' in text
    assert "prometheusScrape: false" in text


def test_helm_templates_target_fastapi_service():
    deployment = Path("charts/failsafeml-x/templates/deployment.yaml").read_text(encoding="utf-8")
    service = Path("charts/failsafeml-x/templates/service.yaml").read_text(encoding="utf-8")
    assert "kind: Deployment" in deployment
    assert "readinessProbe" in deployment
    assert "livenessProbe" in deployment
    assert "containerPort" in deployment
    assert "kind: Service" in service
    assert "targetPort: http" in service


def test_no_real_secrets_in_infra_templates():
    joined = "\n".join(path.read_text(encoding="utf-8") for path in [
        Path("infra/terraform/main.tf"),
        Path("infra/terraform/variables.tf"),
        Path("charts/failsafeml-x/values.yaml"),
        Path("charts/failsafeml-x/templates/deployment.yaml"),
    ])
    forbidden = ["sk-", "AKIA", "BEGIN PRIVATE KEY", "AWS_SECRET_ACCESS_KEY"]
    assert not any(marker in joined for marker in forbidden)


def test_m17_runner_writes_result_and_report():
    subprocess.run([sys.executable, "scripts/run_m17_infra_templates.py"], check=True)
    result_path = Path("experiments/results/m17_infra_templates.json")
    report_path = Path("reports/milestone_17_infra_templates.md")
    assert result_path.exists()
    assert report_path.exists()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["milestone"] == "M17_INFRA_TEMPLATES"
    assert payload["passed"] is True
    assert payload["template_summary"]["terraform_executed"] is False
    assert payload["template_summary"]["helm_executed"] is False
