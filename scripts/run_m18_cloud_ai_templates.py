from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

RESULTS_DIR = PROJECT_ROOT / "experiments" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"

REQUIRED_FILES = [
    "cloud/aws/sagemaker/README.md",
    "cloud/aws/sagemaker/inference.py",
    "cloud/aws/sagemaker/model.tar.gz.placeholder.md",
    "cloud/gcp/vertex_ai/README.md",
    "cloud/gcp/vertex_ai/predictor.py",
    "docs/managed_cloud_ai.md",
]

FORBIDDEN_SECRET_MARKERS = [
    "OPENAI_API_KEY=sk-",
    "AWS_SECRET_ACCESS_KEY=",
    "AWS_ACCESS_KEY_ID=AKIA",
    "BEGIN PRIVATE KEY",
    "GOOGLE_APPLICATION_CREDENTIALS=/",
    "private_key_id",
]

REQUIRED_MARKERS = {
    "cloud/aws/sagemaker/inference.py": [
        "model_fn",
        "input_fn",
        "predict_fn",
        "output_fn",
        "reliability_envelope",
        "FAILSAFEMLX_PROVIDER_MODE",
        "FAILSAFEMLX_ENABLE_EXTERNAL_LLM",
        "external_calls_performed",
    ],
    "cloud/gcp/vertex_ai/predictor.py": [
        "FailSafeMLXVertexPredictor",
        "predict",
        "reliability_envelope",
        "FAILSAFEMLX_PROVIDER_MODE",
        "external_calls_performed",
    ],
    "docs/managed_cloud_ai.md": [
        "AWS SageMaker",
        "Google Vertex AI",
        "not deploy",
        "local/offline",
    ],
}


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exercise_sagemaker_template() -> dict[str, Any]:
    module = _load_module(PROJECT_ROOT / "cloud/aws/sagemaker/inference.py", "m18_sagemaker_inference")
    model = module.model_fn("/opt/ml/model")
    payload = module.input_fn(json.dumps({"features": {"age": 42, "risk_score": None}, "prediction": 1}))
    prediction = module.predict_fn(payload, model)
    rendered = module.output_fn(prediction)
    parsed = json.loads(rendered)
    envelope = parsed["reliability_envelope"]
    return {
        "target": "aws_sagemaker",
        "entrypoints_present": all(hasattr(module, name) for name in ["model_fn", "input_fn", "predict_fn", "output_fn"]),
        "trust_score": envelope["trust_score"],
        "routing_decision": envelope["routing_decision"],
        "external_calls_performed": envelope["provider_metadata"]["external_calls_performed"],
        "has_failure_for_missing_features": bool(envelope["failures"]),
    }


def _exercise_vertex_template() -> dict[str, Any]:
    module = _load_module(PROJECT_ROOT / "cloud/gcp/vertex_ai/predictor.py", "m18_vertex_predictor")
    predictor = module.FailSafeMLXVertexPredictor()
    predictor.load("gs://placeholder/failsafeml-x")
    result = predictor.predict([{"features": {"temperature": 91.2, "load": None}, "prediction": 0.73}])
    envelope = result["predictions"][0]["reliability_envelope"]
    return {
        "target": "gcp_vertex_ai",
        "entrypoint_present": hasattr(module, "FailSafeMLXVertexPredictor"),
        "trust_score": envelope["trust_score"],
        "routing_decision": envelope["routing_decision"],
        "external_calls_performed": envelope["provider_metadata"]["external_calls_performed"],
        "has_failure_for_missing_features": bool(envelope["failures"]),
    }


def validate_cloud_ai_templates() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked_files: list[str] = []

    for file_name in REQUIRED_FILES:
        if not (PROJECT_ROOT / file_name).exists():
            errors.append(f"Missing required file: {file_name}")

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

    template_exercises: list[dict[str, Any]] = []
    if not errors:
        try:
            template_exercises.append(_exercise_sagemaker_template())
            template_exercises.append(_exercise_vertex_template())
        except Exception as exc:  # pragma: no cover - reported through validation payload
            errors.append(f"Template execution failed: {exc}")

    for exercise in template_exercises:
        if exercise.get("external_calls_performed") is not False:
            errors.append(f"External calls were unexpectedly performed for {exercise['target']}")
        if exercise.get("trust_score", 100) >= 100:
            warnings.append(f"{exercise['target']} demo did not reduce trust score; sample may be too clean.")

    return {
        "milestone": "M18_CLOUD_AI_TEMPLATES",
        "passed": not errors,
        "checked_files": checked_files,
        "required_files": REQUIRED_FILES,
        "template_exercises": template_exercises,
        "template_summary": {
            "aws_sagemaker_template": True,
            "gcp_vertex_ai_template": True,
            "cloud_sdks_required_for_tests": False,
            "cloud_credentials_required_for_tests": False,
            "live_cloud_deployment_performed": False,
            "external_provider_default": "local/offline",
            "external_llm_default_enabled": False,
            "external_vector_db_default_enabled": False,
        },
        "errors": errors,
        "warnings": warnings,
        "honest_limitations": [
            "This milestone provides managed cloud inference templates only.",
            "No SageMaker endpoint, Vertex AI endpoint, IAM role, service account, image registry, or cloud resource is created.",
            "No model artifact is uploaded or downloaded during tests.",
            "Production use requires model packaging, cloud security review, authentication, logging, monitoring, and cost controls.",
        ],
    }


def generate_report(payload: dict[str, Any]) -> str:
    summary = payload["template_summary"]
    lines = [
        "# Milestone 18 — Managed Cloud AI Deployment Templates",
        "",
        "## Objective",
        "Add CI-safe AWS SageMaker and Google Vertex AI style inference templates that wrap model outputs with FailSafeML-X reliability envelopes.",
        "",
        "## Validation Summary",
        f"- Passed: `{payload['passed']}`",
        f"- Checked files: `{len(payload['checked_files'])}`",
        f"- AWS SageMaker template present: `{summary['aws_sagemaker_template']}`",
        f"- Google Vertex AI template present: `{summary['gcp_vertex_ai_template']}`",
        f"- Cloud SDKs required for tests: `{summary['cloud_sdks_required_for_tests']}`",
        f"- Cloud credentials required for tests: `{summary['cloud_credentials_required_for_tests']}`",
        f"- Live cloud deployment performed: `{summary['live_cloud_deployment_performed']}`",
        f"- External provider default: `{summary['external_provider_default']}`",
        "",
        "## Template Exercise Results",
        "| Target | Trust Score | Routing | External Calls |",
        "|---|---:|---|---|",
    ]
    for item in payload["template_exercises"]:
        lines.append(
            f"| `{item['target']}` | `{item['trust_score']}` | `{item['routing_decision']}` | `{item['external_calls_performed']}` |"
        )
    lines.extend([
        "",
        "## Honest Limitations",
    ])
    lines.extend(f"- {item}" for item in payload["honest_limitations"])
    if payload["warnings"]:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = validate_cloud_ai_templates()
    result_path = RESULTS_DIR / "m18_cloud_ai_templates.json"
    report_path = REPORTS_DIR / "milestone_18_cloud_ai_templates.md"

    payload["artifacts"] = {
        "result": str(result_path.relative_to(PROJECT_ROOT)),
        "report": str(report_path.relative_to(PROJECT_ROOT)),
        "docs": "docs/managed_cloud_ai.md",
        "aws_template": "cloud/aws/sagemaker/inference.py",
        "gcp_template": "cloud/gcp/vertex_ai/predictor.py",
    }

    result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(generate_report(payload), encoding="utf-8")

    print(f"Wrote {result_path}")
    print(f"Wrote {report_path}")

    if not payload["passed"]:
        raise SystemExit(1)

    print("M18 completed successfully.")


if __name__ == "__main__":
    main()
