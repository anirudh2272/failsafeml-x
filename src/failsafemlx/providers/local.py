from __future__ import annotations

from failsafemlx.providers.base import BaseLLMProvider
from failsafemlx.providers.schemas import ProviderRequest, ProviderResponse


class LocalDeterministicProvider(BaseLLMProvider):
    """No-network provider used by tests, demos, CI, and offline portfolio review."""

    provider_name = "local"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        prompt = request.prompt.strip()
        compact_prompt = " ".join(prompt.split())
        if len(compact_prompt) > 500:
            compact_prompt = compact_prompt[:497] + "..."

        text = (
            "Local reliability explanation: FailSafeML-X analyzed the reliability envelope "
            "without calling an external LLM provider. Review the failure IDs, trust score, "
            "drift/OOD indicators, repair action, and human-review routing before allowing "
            f"automation. Input summary: {compact_prompt}"
        )
        return ProviderResponse(
            provider=self.provider_name,
            model=request.model or "local-deterministic-reliability-explainer",
            text=text,
            used_external_api=False,
            usage={"prompt_chars": len(request.prompt), "response_chars": len(text)},
            raw_provider="deterministic_local_fallback",
        )
