"""Vertex AI-style predictor template for FailSafeML-X.

This module is intentionally dependency-light and does not import google-cloud-aiplatform.
"""
from __future__ import annotations

import os
from typing import Any


class FailSafeMLXVertexPredictor:
    """CI-safe Vertex-style predictor skeleton."""

    def __init__(self) -> None:
        self.model_loaded = False
        self.model_name = "failsafeml-x-template-model"

    def load(self, artifacts_uri: str) -> None:
        self.artifacts_uri = artifacts_uri
        self.model_loaded = False

    def predict(self, instances: list[dict[str, Any]]) -> dict[str, Any]:
        predictions = []
        for instance in instances:
            features = instance.get("features", instance)
            missing_count = sum(value is None for value in features.values()) if isinstance(features, dict) else 0
            trust_score = max(0, 100 - (missing_count * 15))
            failures = []
            repair_actions = []
            if missing_count:
                failures.append({
                    "failure_id": "F11_MISSING_FEATURE_VALUES",
                    "severity": "MEDIUM",
                    "reason": f"{missing_count} feature values are missing.",
                })
                repair_actions.append("R10_REQUEST_MORE_FEATURES")

            predictions.append({
                "prediction": instance.get("prediction", "template_prediction"),
                "reliability_envelope": {
                    "trust_score": trust_score,
                    "failures": failures,
                    "repair_actions": repair_actions,
                    "routing_decision": "ACCEPT" if trust_score >= 80 else "HUMAN_REVIEW",
                    "provider_metadata": {
                        "provider_mode": os.getenv("FAILSAFEMLX_PROVIDER_MODE", "local"),
                        "external_llm_enabled": os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_LLM", "false").lower() == "true",
                        "external_vector_db_enabled": os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB", "false").lower() == "true",
                        "external_calls_performed": False,
                    },
                },
            })

        return {
            "managed_cloud_target": "gcp_vertex_ai",
            "predictions": predictions,
            "honest_limitations": [
                "Template predictor only; no live Vertex AI endpoint was deployed.",
                "No external LLM, vector DB, or Google Cloud service call is performed by this template.",
            ],
        }
