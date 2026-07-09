from __future__ import annotations

import json
import os
from typing import Any

from failsafemlx.providers.base import BaseLLMProvider, ExternalProviderDisabledError
from failsafemlx.providers.bedrock import BedrockConverseProvider
from failsafemlx.providers.local import LocalDeterministicProvider
from failsafemlx.providers.openai_compatible import OpenAICompatibleProvider
from failsafemlx.providers.schemas import ProviderRequest, ProviderResponse


SUPPORTED_PROVIDERS = {"local", "openai_compatible", "bedrock"}


def external_providers_enabled() -> bool:
    return os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_LLM", "false").strip().lower() in {"1", "true", "yes"}


def get_provider(name: str | None = None, allow_external: bool | None = None) -> BaseLLMProvider:
    provider_name = (name or os.getenv("FAILSAFEMLX_LLM_PROVIDER") or "local").strip().lower()
    if provider_name not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider_name}'. Supported providers: {sorted(SUPPORTED_PROVIDERS)}")

    if provider_name == "local":
        return LocalDeterministicProvider()

    allow = external_providers_enabled() if allow_external is None else allow_external
    if not allow:
        raise ExternalProviderDisabledError(
            "External LLM providers are disabled by default. Set FAILSAFEMLX_ENABLE_EXTERNAL_LLM=true "
            "or call get_provider(..., allow_external=True) intentionally."
        )

    if provider_name == "openai_compatible":
        return OpenAICompatibleProvider()
    if provider_name == "bedrock":
        return BedrockConverseProvider()
    raise AssertionError("unreachable provider branch")


def build_reliability_prompt(analysis: dict[str, Any]) -> str:
    compact = {
        "case": analysis.get("case", {}),
        "failure_explanations": analysis.get("failure_explanations", []),
        "trust_summary": analysis.get("trust_summary", {}),
        "drift_ood_summary": analysis.get("drift_ood_summary", {}),
        "recommended_action": analysis.get("recommended_action", {}),
    }
    return (
        "Summarize this FailSafeML-X reliability analysis for an ML reviewer. "
        "Keep the explanation concise and do not override guardrail or human-review decisions.\n\n"
        + json.dumps(compact, indent=2, sort_keys=True)
    )


def generate_reliability_explanation(
    analysis: dict[str, Any],
    provider_name: str | None = None,
    allow_external: bool | None = None,
) -> dict[str, Any]:
    provider = get_provider(provider_name, allow_external=allow_external)
    request = ProviderRequest(
        prompt=build_reliability_prompt(analysis),
        system_prompt=(
            "You explain ML reliability decisions. You must preserve FailSafeML-X safety routing, "
            "avoid claiming certification, and recommend human review when the reliability envelope requires it."
        ),
    )
    response: ProviderResponse = provider.generate(request)
    return response.to_dict()
