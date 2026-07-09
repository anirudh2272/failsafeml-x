from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "infra/terraform/README.md",
    "infra/terraform/main.tf",
    "infra/terraform/variables.tf",
    "infra/terraform/outputs.tf",
    "charts/failsafeml-x/Chart.yaml",
    "charts/failsafeml-x/values.yaml",
    "charts/failsafeml-x/templates/deployment.yaml",
    "charts/failsafeml-x/templates/service.yaml",
    "charts/failsafeml-x/templates/ingress.yaml",
    "docs/deployment_templates.md",
]

FORBIDDEN_SECRET_MARKERS = [
    "OPENAI_API_KEY=sk-",
    "AWS_SECRET_ACCESS_KEY=",
    "AWS_ACCESS_KEY_ID=AKIA",
    "BEGIN PRIVATE KEY",
    "password =",
]

REQUIRED_MARKERS = {
    "infra/terraform/main.tf": [
        "kubernetes_deployment",
        "failsafeml-x-api",
        "FAILSAFEMLX_PROVIDER_MODE",
        "FAILSAFEMLX_ENABLE_EXTERNAL_LLM",
        "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB",
        "/health",
    ],
    "infra/terraform/variables.tf": [
        "variable \"image\"",
        "variable \"replica_count\"",
        "variable \"enable_prometheus_scrape\"",
        "variable \"prometheus_path\"",
    ],
    "charts/failsafeml-x/Chart.yaml": [
        "apiVersion: v2",
        "name: failsafeml-x",
        "version: 0.17.0",
    ],
    "charts/failsafeml-x/values.yaml": [
        "FAILSAFEMLX_PROVIDER_MODE: local",
        "FAILSAFEMLX_ENABLE_EXTERNAL_LLM: \"false\"",
        "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB: \"false\"",
        "prometheusScrape: false",
    ],
    "charts/failsafeml-x/templates/deployment.yaml": [
        "kind: Deployment",
        "readinessProbe",
        "livenessProbe",
        "prometheus.io/scrape",
        "FAILSAFEMLX_PROVIDER_MODE",
    ],
    "charts/failsafeml-x/templates/service.yaml": [
        "kind: Service",
        "targetPort: http",
    ],
    "charts/failsafeml-x/templates/ingress.yaml": [
        "kind: Ingress",
        "ingress.enabled",
    ],
}


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def validate_infra_templates() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for file_name in REQUIRED_FILES:
        if not (PROJECT_ROOT / file_name).exists():
            errors.append(f"Missing required file: {file_name}")

    checked_files: list[str] = []
    if not errors:
        for file_name in REQUIRED_FILES:
            text = _read(file_name)
            checked_files.append(file_name)
            for marker in FORBIDDEN_SECRET_MARKERS:
                if marker in text:
                    errors.append(f"Potential secret marker found in {file_name}: {marker}")

        for file_name, markers in REQUIRED_MARKERS.items():
            text = _read(file_name)
            for marker in markers:
                if marker not in text:
                    errors.append(f"Required marker {marker!r} missing from {file_name}")

        terraform_text = "\n".join(_read(path) for path in [
            "infra/terraform/main.tf",
            "infra/terraform/variables.tf",
            "infra/terraform/outputs.tf",
        ])
        helm_text = "\n".join(_read(path) for path in [
            "charts/failsafeml-x/Chart.yaml",
            "charts/failsafeml-x/values.yaml",
            "charts/failsafeml-x/templates/deployment.yaml",
            "charts/failsafeml-x/templates/service.yaml",
            "charts/failsafeml-x/templates/ingress.yaml",
        ])

        if "terraform apply" in terraform_text.lower():
            warnings.append("Terraform docs mention apply; ensure users understand execution is optional.")
        if "OpenAI API key" in terraform_text or "AWS secret" in terraform_text:
            errors.append("Terraform templates must not request live provider secrets.")
        if "FAILSAFEMLX_ENABLE_EXTERNAL_LLM: \"true\"" in helm_text:
            errors.append("Helm values must not enable external LLM providers by default.")

    return {
        "milestone": "M17_INFRA_TEMPLATES",
        "passed": not errors,
        "checked_files": checked_files,
        "required_files": REQUIRED_FILES,
        "template_summary": {
            "terraform_files": 4,
            "helm_files": 5,
            "service_target": "FailSafeML-X FastAPI API service on port 8000",
            "provider_default": "local/offline",
            "external_llm_default_enabled": False,
            "external_vector_db_default_enabled": False,
            "terraform_executed": False,
            "helm_executed": False,
            "kubernetes_cluster_required_for_tests": False,
        },
        "errors": errors,
        "warnings": warnings,
        "honest_limitations": [
            "Validation is static and does not run terraform plan/apply.",
            "Validation is static and does not run helm template/install.",
            "No Kubernetes cluster or cloud deployment is created by this milestone.",
            "Production deployment requires real cluster, image registry, networking, authentication, and security review.",
        ],
    }


def main() -> None:
    result = validate_infra_templates()
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
