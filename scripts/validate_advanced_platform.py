from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MILESTONE_SCRIPTS = [
    "scripts/run_m1_baseline.py",
    "scripts/run_m2_uncertainty_calibration.py",
    "scripts/run_m3_drift_ood.py",
    "scripts/run_m4_failure_taxonomy.py",
    "scripts/run_m5_repair_engine.py",
    "scripts/run_m6_rl_router.py",
    "scripts/run_m7_api_dashboard_demo.py",
    "scripts/run_m8_final_packaging.py",
    "scripts/run_m9_cicd_software_quality.py",
    "scripts/run_m10_agentic_reliability.py",
    "scripts/run_m11_airflow_orchestration.py",
    "scripts/run_m12_spark_drift_pipeline.py",
    "scripts/run_m13_ai_security.py",
    "scripts/run_m14_inference_optimization.py",
    "scripts/run_m15a_provider_abstraction.py",
    "scripts/run_m15b_ragops_reliability.py",
    "scripts/run_m15c_dataset_validation.py",
    "scripts/run_m15d_provider_agent_integration.py",
    "scripts/run_m15e_experiment_registry.py",
    "scripts/run_m16_monitoring_metrics.py",
    "scripts/run_m17_infra_templates.py",
    "scripts/run_m18_cloud_ai_templates.py",
    "scripts/run_m19_finetuning_scaffold.py",
    "scripts/run_m20_final_advanced_packaging.py",
]

REQUIRED_CORE_PATHS = [
    "README.md",
    "requirements.txt",
    "scripts/local_ci.py",
    "docs/ragops_reliability.md",
    "docs/dataset_validation.md",
    "docs/provider_agent_integration.md",
    "docs/experiment_registry.md",
    "docs/monitoring_metrics.md",
    "docs/deployment_templates.md",
    "docs/managed_cloud_ai.md",
    "docs/finetuning_scaffold.md",
    "docs/advanced_platform_architecture.md",
    "docs/recruiter_walkthrough.md",
    "docs/research_summary.md",
    "reports/final_project_card.md",
    "reports/model_card.md",
    "reports/model_risk_card.md",
    "reports/advanced_project_card.md",
    "reports/figures/advanced_platform_architecture.svg",
    "experiments/results/m15b_ragops_reliability.json",
    "experiments/results/m15c_dataset_validation.json",
    "experiments/results/m15d_provider_agent_integration.json",
    "experiments/results/m15e_experiment_registry.json",
    "experiments/results/m16_monitoring_metrics.json",
    "experiments/results/m17_infra_templates.json",
    "experiments/results/m18_cloud_ai_templates.json",
    "experiments/results/m19_finetuning_scaffold.json",
    "monitoring/prometheus_metrics_example.txt",
    "monitoring/grafana_dashboard_spec.json",
    "infra/terraform/main.tf",
    "charts/failsafeml-x/Chart.yaml",
    "cloud/aws/sagemaker/inference.py",
    "cloud/gcp/vertex_ai/predictor.py",
    "data/fine_tuning/reliability_explanations_sample.jsonl",
]

REQUIRED_MODULE_DIRS = [
    "src/failsafemlx/ragops",
    "src/failsafemlx/data",
    "src/failsafemlx/providers",
    "src/failsafemlx/agents",
    "src/failsafemlx/tracking",
    "src/failsafemlx/monitoring",
    "src/failsafemlx/finetuning",
]

EXPECTED_RESULT_FILES = [
    "experiments/results/m8_final_packaging.json",
    "experiments/results/m9_cicd_software_quality.json",
    "experiments/results/m10_agentic_reliability.json",
    "experiments/results/m11_airflow_orchestration.json",
    "experiments/results/m12_spark_drift_pipeline.json",
    "experiments/results/m13_ai_security.json",
    "experiments/results/m14_inference_optimization.json",
    "experiments/results/m15a_provider_abstraction.json",
    "experiments/results/m15b_ragops_reliability.json",
    "experiments/results/m15c_dataset_validation.json",
    "experiments/results/m15d_provider_agent_integration.json",
    "experiments/results/m15e_experiment_registry.json",
    "experiments/results/m16_monitoring_metrics.json",
    "experiments/results/m17_infra_templates.json",
    "experiments/results/m18_cloud_ai_templates.json",
    "experiments/results/m19_finetuning_scaffold.json",
]


def _exists(rel_path: str) -> bool:
    return (PROJECT_ROOT / rel_path).exists()


def _load_json_if_present(rel_path: str) -> dict[str, Any]:
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_json_error": True}
    return data if isinstance(data, dict) else {"_non_object_json": True}


def _collect_result_statuses() -> dict[str, Any]:
    statuses: dict[str, Any] = {}
    for rel_path in EXPECTED_RESULT_FILES:
        data = _load_json_if_present(rel_path)
        status = data.get("passed")
        if status is None and data:
            status = not bool(data.get("errors"))
        statuses[rel_path] = {
            "exists": _exists(rel_path),
            "passed": bool(status) if status is not None else None,
            "keys": sorted(data.keys())[:12] if data else [],
        }
    return statuses


def _summarize_capabilities() -> list[str]:
    return [
        "calibration and conformal uncertainty",
        "drift and OOD detection",
        "failure taxonomy and trust scoring",
        "repair routing and human-review routing",
        "agentic reliability explanations with local fallback",
        "optional RAGOps reliability auditing",
        "dataset loading and schema validation",
        "provider-aware reliability agent integration",
        "local experiment registry and model risk card",
        "Prometheus/Grafana-ready monitoring artifacts",
        "Terraform and Helm deployment templates",
        "managed-cloud AI inference templates",
        "LoRA/PEFT fine-tuning scaffold",
    ]


def validate_advanced_platform() -> dict[str, Any]:
    missing_scripts = [path for path in MILESTONE_SCRIPTS if not _exists(path)]
    missing_core_paths = [path for path in REQUIRED_CORE_PATHS if not _exists(path)]
    missing_module_dirs = [path for path in REQUIRED_MODULE_DIRS if not _exists(path)]
    result_statuses = _collect_result_statuses()

    failed_or_missing_results = []
    for rel_path, status in result_statuses.items():
        if not status["exists"] or status["passed"] is False:
            failed_or_missing_results.append(rel_path)

    docs_text = ""
    for rel_path in [
        "README.md",
        "docs/advanced_platform_architecture.md",
        "docs/recruiter_walkthrough.md",
        "docs/research_summary.md",
        "reports/advanced_project_card.md",
    ]:
        path = PROJECT_ROOT / rel_path
        if path.exists():
            docs_text += "\n" + path.read_text(encoding="utf-8", errors="ignore").lower()

    required_phrases = [
        "failSafeml-x".lower(),
        "model-agnostic",
        "ragops",
        "dataset validation",
        "provider abstraction",
        "monitoring",
        "terraform",
        "helm",
        "sagemaker",
        "vertex",
        "lora",
        "peft",
        "not a production",
        "no external api",
    ]
    missing_doc_phrases = [phrase for phrase in required_phrases if phrase not in docs_text]

    capability_tags = _summarize_capabilities()
    status_counter = Counter(
        "passed" if item.get("passed") is True else "unknown" if item.get("passed") is None else "failed"
        for item in result_statuses.values()
    )

    errors = []
    if missing_scripts:
        errors.append(f"Missing milestone scripts: {missing_scripts}")
    if missing_core_paths:
        errors.append(f"Missing core files: {missing_core_paths}")
    if missing_module_dirs:
        errors.append(f"Missing module directories: {missing_module_dirs}")
    if failed_or_missing_results:
        errors.append(f"Missing or failed result artifacts: {failed_or_missing_results}")
    if missing_doc_phrases:
        errors.append(f"Documentation missing expected phrases: {missing_doc_phrases}")

    return {
        "milestone": "M20_FINAL_ADVANCED_PACKAGING",
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": not errors,
        "errors": errors,
        "scripts_checked": len(MILESTONE_SCRIPTS),
        "core_paths_checked": len(REQUIRED_CORE_PATHS),
        "module_dirs_checked": len(REQUIRED_MODULE_DIRS),
        "result_status_summary": dict(status_counter),
        "result_statuses": result_statuses,
        "capability_tags": capability_tags,
        "honest_limitations": [
            "Prototype is locally validated but not production-certified.",
            "OpenAI-compatible and AWS Bedrock-style providers are optional and disabled by default.",
            "Terraform, Helm, SageMaker, Vertex AI, Prometheus, Grafana, Airflow, Spark, and fine-tuning paths are templates/scaffolds unless explicitly deployed or executed.",
            "No fine-tuned model or adapter weights are claimed by this milestone.",
            "No live cloud deployment, GPU training, external vector database, or paid API call is required for tests.",
        ],
    }


def main() -> None:
    result = validate_advanced_platform()
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
