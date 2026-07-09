from __future__ import annotations

from pathlib import Path

import pytest

from failsafemlx.agents.provider_agent import ProviderAwareReliabilityAgent, analyze_with_provider
from failsafemlx.providers.base import ExternalProviderDisabledError
from failsafemlx.providers.router import get_provider
from scripts.run_m15d_provider_agent_integration import run_m15d


BASE_CASE = {
    "sample_id": "provider_agent_test",
    "prediction": "manual_review_needed",
    "trust_score": 0.38,
    "failure_ids": ["F4_OUT_OF_DISTRIBUTION_INPUT", "F10_UNSAFE_AUTO_DECISION"],
    "uncertainty": 0.83,
    "calibration_error": 0.14,
    "drift_score": 0.58,
    "ood_score": 0.88,
    "domain": "test_domain",
}


def test_provider_aware_agent_uses_local_provider_by_default():
    output = ProviderAwareReliabilityAgent().analyze(BASE_CASE)
    assert output["provider_used"] == "local"
    assert output["used_external_api"] is False
    assert output["provider_metadata"]["used_external_api"] is False


def test_provider_aware_output_contains_required_sections():
    output = analyze_with_provider(BASE_CASE, provider_name="local")
    assert output["failure_explanation"]
    assert output["repair_recommendation"]["action_id"] == "R4_ROUTE_TO_HUMAN_REVIEW"
    assert output["risk_summary"]["risk_level"] == "critical"
    assert "human" in output["human_review_note"].lower() or "review" in output["human_review_note"].lower()
    assert output["provider_explanation"]


def test_external_provider_is_blocked_by_default():
    with pytest.raises(ExternalProviderDisabledError):
        get_provider("openai_compatible", allow_external=False)


def test_external_provider_request_falls_back_to_local_when_blocked():
    output = analyze_with_provider(BASE_CASE, provider_name="bedrock", allow_external=False)
    assert output["provider_requested"] == "bedrock"
    assert output["provider_used"] == "local"
    assert output["used_external_api"] is False
    assert output["provider_metadata"]["fallback_reason"] == "external_provider_blocked_by_default"
    assert output["warnings"]


def test_no_secrets_required_for_local_provider_path(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_API_KEY", raising=False)
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    output = analyze_with_provider(BASE_CASE, provider_name="local")
    assert output["provider_used"] == "local"
    assert output["used_external_api"] is False


def test_provider_metadata_is_json_compatible():
    output = analyze_with_provider(BASE_CASE, provider_name="local")
    metadata = output["provider_metadata"]
    assert metadata["provider"] == "local"
    assert "model" in metadata
    assert "usage" in metadata


def test_m15d_runner_generates_outputs():
    payload = run_m15d()
    assert payload["passed"] is True
    assert payload["external_api_calls_used"] is False
    assert Path("experiments/results/m15d_provider_agent_integration.json").exists()
    assert Path("reports/milestone_15d_provider_agent_integration.md").exists()
