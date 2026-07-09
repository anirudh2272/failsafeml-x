from __future__ import annotations

import os
from typing import Any

from failsafemlx.providers.base import BaseLLMProvider, ProviderConfigurationError
from failsafemlx.providers.schemas import ProviderRequest, ProviderResponse


class BedrockConverseProvider(BaseLLMProvider):
    """Optional Amazon Bedrock Converse API adapter.

    This adapter imports boto3 only when external Bedrock generation is requested.
    It is not used by tests or local CI and requires AWS credentials/model access.
    """

    provider_name = "bedrock"

    def __init__(
        self,
        model_id: str | None = None,
        region_name: str | None = None,
    ) -> None:
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID")
        self.region_name = region_name or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"

    def _client(self) -> Any:
        try:
            import boto3  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency path
            raise ProviderConfigurationError("boto3 is required for Bedrock provider. Install requirements-providers.txt.") from exc
        return boto3.client("bedrock-runtime", region_name=self.region_name)

    def _validate(self) -> None:
        if not self.model_id:
            raise ProviderConfigurationError("BEDROCK_MODEL_ID is required for Bedrock provider.")

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self._validate()
        client = self._client()
        response = client.converse(
            modelId=request.model or self.model_id,
            system=[{"text": request.system_prompt}],
            messages=[{"role": "user", "content": [{"text": request.prompt}]}],
            inferenceConfig={
                "temperature": request.temperature,
                "maxTokens": request.max_tokens,
            },
        )
        output = response.get("output", {}).get("message", {}).get("content", [])
        text_parts = [item.get("text", "") for item in output if isinstance(item, dict)]
        text = "\n".join(part for part in text_parts if part)
        return ProviderResponse(
            provider=self.provider_name,
            model=request.model or self.model_id or "bedrock-model-unspecified",
            text=text,
            used_external_api=True,
            usage=response.get("usage", {}),
            raw_provider="amazon_bedrock_converse",
        )
