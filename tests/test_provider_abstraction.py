from __future__ import annotations

import os

import pytest

from failsafemlx.agents.schemas import ReliabilityCase
from failsafemlx.agents.reliability_agent import ReliabilityAgent
from failsafemlx.providers.base import ExternalProviderDisabledError, ProviderConfigurationError
from failsafemlx.providers.openai_compatible import OpenAICompatibleProvider
from failsafemlx.providers.router import generate_reliability_explanation, get_provider
from scripts.run_m15a_provider_abstraction import run_m15a


def _analysis():
    case = ReliabilityCase(
        sample_id="provider-test",
        prediction=1,
        trust_score=0.33,
        failure_ids=["F4_OUT_OF_DISTRIBUTION_INPUT", "F10_UNSAFE_AUTO_DECISION"],
        drift_score=0.7,
        ood_score=0.9,
    )
    return ReliabilityAgent().analyze(case)


def test_local_provider_is_default_and_offline():
    provider = get_provider()
    response = provider.generate(
        request=__import__("failsafemlx.providers.schemas", fromlist=["ProviderRequest"]).ProviderRequest(
            prompt="Explain F10 unsafe auto decision."
        )
    )
    assert response.provider == "local"
    assert response.used_external_api is False
    assert "without calling an external LLM provider" in response.text


def test_openai_compatible_provider_blocked_by_default(monkeypatch):
    monkeypatch.setenv("FAILSAFEMLX_LLM_PROVIDER", "openai_compatible")
    monkeypatch.delenv("FAILSAFEMLX_ENABLE_EXTERNAL_LLM", raising=False)
    with pytest.raises(ExternalProviderDisabledError):
        get_provider()


def test_bedrock_provider_blocked_by_default(monkeypatch):
    monkeypatch.setenv("FAILSAFEMLX_LLM_PROVIDER", "bedrock")
    monkeypatch.delenv("FAILSAFEMLX_ENABLE_EXTERNAL_LLM", raising=False)
    with pytest.raises(ExternalProviderDisabledError):
        get_provider()


def test_local_reliability_explanation_generation():
    response = generate_reliability_explanation(_analysis(), provider_name="local")
    assert response["provider"] == "local"
    assert response["used_external_api"] is False
    assert "reliability envelope" in response["text"]


def test_openai_adapter_requires_configuration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)
    provider = OpenAICompatibleProvider(api_key=None, base_url=None)
    with pytest.raises(ProviderConfigurationError):
        provider.generate(
            request=__import__("failsafemlx.providers.schemas", fromlist=["ProviderRequest"]).ProviderRequest(
                prompt="test"
            )
        )


def test_m15a_runner_generates_outputs():
    result = run_m15a()
    assert result["passed"] is True
    assert result["external_api_calls_in_tests"] is False
    assert result["external_provider_default_behavior"]["openai_compatible"] == "blocked_by_default"
    assert result["external_provider_default_behavior"]["bedrock"] == "blocked_by_default"
