from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from scripts.validate_infra_templates import validate_infra_templates

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"


def generate_report(payload: dict[str, Any]) -> str:
    summary = payload["template_summary"]
    lines = [
        "# Milestone 17 — Terraform and Helm Deployment Templates",
        "",
        "## Objective",
        "Add static Terraform and Helm templates for packaging the FailSafeML-X FastAPI reliability service while preserving safe local/offline provider defaults.",
        "",
        "## Validation Summary",
        f"- Passed: `{payload['passed']}`",
        f"- Checked files: `{len(payload['checked_files'])}`",
        f"- Terraform files: `{summary['terraform_files']}`",
        f"- Helm files: `{summary['helm_files']}`",
        f"- Service target: `{summary['service_target']}`",
        f"- Provider default: `{summary['provider_default']}`",
        f"- External LLM default enabled: `{summary['external_llm_default_enabled']}`",
        f"- External vector DB default enabled: `{summary['external_vector_db_default_enabled']}`",
        "",
        "## Template Files",
        "| File | Purpose |",
        "|---|---|",
        "| `infra/terraform/main.tf` | Kubernetes namespace, deployment, and service template |",
        "| `infra/terraform/variables.tf` | Configurable image, replica, service, and resource parameters |",
        "| `infra/terraform/outputs.tf` | Static output references for namespace and service |",
        "| `charts/failsafeml-x/Chart.yaml` | Helm chart metadata |",
        "| `charts/failsafeml-x/values.yaml` | Safe local/offline defaults |",
        "| `charts/failsafeml-x/templates/deployment.yaml` | FastAPI deployment template |",
        "| `charts/failsafeml-x/templates/service.yaml` | Kubernetes service template |",
        "| `charts/failsafeml-x/templates/ingress.yaml` | Optional ingress template |",
        "",
        "## Safety Defaults",
        "```text",
        "FAILSAFEMLX_PROVIDER_MODE=local",
        "FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false",
        "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false",
        "```",
        "",
        "## Honest Limitations",
    ]
    lines.extend(f"- {item}" for item in payload["honest_limitations"])
    if payload["warnings"]:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = validate_infra_templates()
    result_path = RESULTS_DIR / "m17_infra_templates.json"
    report_path = REPORTS_DIR / "milestone_17_infra_templates.md"

    payload["artifacts"] = {
        "result": str(result_path.relative_to(PROJECT_ROOT)),
        "report": str(report_path.relative_to(PROJECT_ROOT)),
        "terraform_dir": "infra/terraform",
        "helm_chart_dir": "charts/failsafeml-x",
        "docs": "docs/deployment_templates.md",
    }

    result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(generate_report(payload), encoding="utf-8")

    print(f"Wrote {result_path}")
    print(f"Wrote {report_path}")

    if not payload["passed"]:
        raise SystemExit(1)

    print("M17 completed successfully.")


if __name__ == "__main__":
    main()
