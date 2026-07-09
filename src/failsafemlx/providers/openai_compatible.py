from __future__ import annotations

import json
import os
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from failsafemlx.providers.base import BaseLLMProvider, ProviderConfigurationError
from failsafemlx.providers.schemas import ProviderRequest, ProviderResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI-compatible Chat Completions adapter.

    This adapter is optional and is not used in tests or local CI. It is designed for
    providers exposing an OpenAI-compatible `/chat/completions` endpoint.
    """

    provider_name = "openai_compatible"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_COMPATIBLE_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_COMPATIBLE_BASE_URL") or "").rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL") or os.getenv("OPENAI_COMPATIBLE_MODEL") or "gpt-4o-mini"
        self.timeout_seconds = timeout_seconds

    def _validate(self) -> None:
        if not self.api_key:
            raise ProviderConfigurationError("OPENAI_API_KEY or OPENAI_COMPATIBLE_API_KEY is required.")
        if not self.base_url:
            raise ProviderConfigurationError("OPENAI_BASE_URL or OPENAI_COMPATIBLE_BASE_URL is required.")

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        self._validate()
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": request.model or self.model,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout_seconds) as response:  # nosec B310 - opt-in provider adapter
                response_json = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ProviderConfigurationError(f"OpenAI-compatible provider HTTP error: {exc.code}") from exc
        except URLError as exc:
            raise ProviderConfigurationError(f"OpenAI-compatible provider connection error: {exc}") from exc

        choices = response_json.get("choices", [])
        text = ""
        if choices:
            text = choices[0].get("message", {}).get("content", "")
        usage = response_json.get("usage", {})
        return ProviderResponse(
            provider=self.provider_name,
            model=payload["model"],
            text=text,
            used_external_api=True,
            usage=usage,
            raw_provider="openai_compatible_chat_completions",
        )
