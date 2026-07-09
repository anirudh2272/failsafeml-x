from __future__ import annotations

from abc import ABC, abstractmethod

from failsafemlx.providers.schemas import ProviderRequest, ProviderResponse


class ProviderConfigurationError(RuntimeError):
    """Raised when an external provider is requested without required configuration."""


class ExternalProviderDisabledError(RuntimeError):
    """Raised when code tries to call an external provider without explicit opt-in."""


class BaseLLMProvider(ABC):
    """Minimal provider interface for optional LLM-backed explanations."""

    provider_name: str

    @abstractmethod
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate text for a provider-neutral reliability explanation request."""
