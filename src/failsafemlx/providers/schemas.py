from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

ProviderName = Literal["local", "openai_compatible", "bedrock"]


@dataclass(frozen=True)
class ProviderRequest:
    """Provider-neutral request envelope for reliability explanation generation."""

    prompt: str
    system_prompt: str = "You are a reliability analyst for ML decision systems."
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int = 500
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderResponse:
    """Provider-neutral response envelope used by local and optional external adapters."""

    provider: str
    model: str
    text: str
    used_external_api: bool
    usage: dict[str, Any] = field(default_factory=dict)
    raw_provider: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
