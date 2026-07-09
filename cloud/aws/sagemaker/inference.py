"""SageMaker-style inference template for FailSafeML-X.

This module is intentionally dependency-light and CI-safe. It does not require
boto3, sagemaker, AWS credentials, or external provider calls.
"""
from __future__ import annotations

import json
import os
from typing import Any


DEFAULT_PROVIDER_ENV = {
    "FAILSAFEMLX_PROVIDER_MODE": "local",
    "FAILSAFEMLX_ENABLE_EXTERNAL_LLM": "false",
    "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB": "false",
}


def _provider_metadata() -> dict[str, Any]:
    return {
        "provider_mode": os.getenv("FAILSAFEMLX_PROVIDER_MODE", "local"),
        "external_llm_enabled": os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_LLM", "false").lower() == "true",
        "external_vector_db_enabled": os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB", "false").lower() == "true",
        "external_calls_performed": False,
    }


def _score_reliability(features: dict[str, Any], prediction: Any) -> dict[str, Any]:
    missing_count = sum(value is None for value in features.values())
    trust_score = max(0, 100 - (missing_count * 15))
    failures: list[dict[str, Any]] = []
    repair_actions: list[str] = []

    if missing_count:
        failures.append({
            "failure_id": "F11_MISSING_FEATURE_VALUES",
            "severity": "MEDIUM",
            "reason": f"{missing_count} feature values are missing.",
        })
        repair_actions.append("R10_REQUEST_MORE_FEATURES")

    routing_decision = "ACCEPT" if trust_score >= 80 else "HUMAN_REVIEW"
    return {
        "prediction": prediction,
        "trust_score": trust_score,
        "failures": failures,
        "repair_actions": repair_actions,
        "routing_decision": routing_decision,
        "provider_metadata": _provider_metadata(),
    }


def model_fn(model_dir: str) -> dict[str, Any]:
    """Load a model artifact.

    This template returns metadata only so tests remain cloud-free.
    Replace with actual deserialization after packaging a validated model.
    """
    return {
        "model_dir": model_dir,
        "model_loaded": False,
        "template_mode": True,
        "model_name": "failsafeml-x-template-model",
    }


def input_fn(request_body: str | bytes, request_content_type: str = "application/json") -> dict[str, Any]:
    if request_content_type != "application/json":
        raise ValueError(f"Unsupported content type: {request_content_type}")
    if isinstance(request_body, bytes):
        request_body = request_body.decode("utf-8")
    payload = json.loads(request_body)
    if not isinstance(payload, dict):
        raise ValueError("SageMaker input payload must be a JSON object.")
    return payload


def predict_fn(input_data: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    features = input_data.get("features", input_data)
    if not isinstance(features, dict):
        raise ValueError("Expected `features` to be a JSON object.")

    prediction = input_data.get("prediction", "template_prediction")
    reliability = _score_reliability(features, prediction)
    return {
        "model_name": model.get("model_name", "failsafeml-x-template-model"),
        "managed_cloud_target": "aws_sagemaker",
        "reliability_envelope": reliability,
        "honest_limitations": [
            "Template entrypoint only; no live SageMaker endpoint was deployed.",
            "No external LLM, vector DB, or AWS service call is performed by this template.",
        ],
    }


def output_fn(prediction: dict[str, Any], accept: str = "application/json") -> str:
    if accept != "application/json":
        raise ValueError(f"Unsupported accept type: {accept}")
    return json.dumps(prediction)
