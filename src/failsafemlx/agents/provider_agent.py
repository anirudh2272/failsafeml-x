from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from failsafemlx.agents.reliability_agent import ReliabilityAgent
from failsafemlx.agents.schemas import ReliabilityCase
from failsafemlx.providers.base import ExternalProviderDisabledError, ProviderConfigurationError
from failsafemlx.providers.router import external_providers_enabled, generate_reliability_explanation


@dataclass(frozen=True)
class ProviderAwareAgentResult:
    """Structured provider-aware reliability analysis output."""

    project: str
    milestone: str
    case_id: str
    provider_requested: str
    provider_used: str
    external_provider_enabled: bool
    used_external_api: bool
    local_analysis: dict[str, Any]
    provider_explanation: str
    failure_explanation: str
    repair_recommendation: dict[str, Any]
    risk_summary: dict[str, Any]
    human_review_note: str
    provider_metadata: dict[str, Any]
    warnings: list[str]
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _risk_summary(local_analysis: dict[str, Any]) -> dict[str, Any]:
    trust_summary = local_analysis.get("trust_summary", {})
    recommended_action = local_analysis.get("recommended_action", {})
    drift_ood = local_analysis.get("drift_ood_summary", {})
    failures = local_analysis.get("failure_explanations", [])

    severities = [str(item.get("severity", "unknown")).lower() for item in failures]
    critical_count = severities.count("critical")
    high_count = severities.count("high")
    medium_count = severities.count("medium")

    if critical_count:
        risk_level = "critical"
    elif high_count:
        risk_level = "high"
    elif medium_count:
        risk_level = "medium"
    else:
        risk_level = str(trust_summary.get("trust_band", "unknown"))

    return {
        "risk_level": risk_level,
        "trust_score": trust_summary.get("trust_score"),
        "trust_band": trust_summary.get("trust_band"),
        "critical_failure_count": critical_count,
        "high_failure_count": high_count,
        "medium_failure_count": medium_count,
        "recommended_decision": recommended_action.get("decision"),
        "recommended_action_id": recommended_action.get("action_id"),
        "drift_ood_severity": drift_ood.get("severity"),
    }


def _compact_failure_explanation(local_analysis: dict[str, Any]) -> str:
    failures = local_analysis.get("failure_explanations", [])
    if not failures:
        return "No named reliability failures were detected by the local reliability agent."
    parts = []
    for item in failures:
        parts.append(
            f"{item.get('failure_id', 'UNKNOWN')} ({item.get('severity', 'unknown')}): "
            f"{item.get('description', 'No description available')}"
        )
    return " | ".join(parts)


class ProviderAwareReliabilityAgent:
    """Connect the deterministic reliability agent to the optional provider abstraction.

    The default path uses the local deterministic provider. OpenAI-compatible and AWS
    Bedrock-style adapters remain blocked unless explicitly enabled by environment or
    function argument.
    """

    def __init__(self, provider_name: str | None = None, allow_external: bool | None = None) -> None:
        self.provider_name = provider_name or "local"
        self.allow_external = allow_external
        self.local_agent = ReliabilityAgent()

    def analyze(self, case: ReliabilityCase | dict[str, Any]) -> dict[str, Any]:
        normalized_case = ReliabilityCase(**case) if isinstance(case, dict) else case
        local_analysis = self.local_agent.analyze(normalized_case)
        warnings: list[str] = []

        try:
            provider_response = generate_reliability_explanation(
                local_analysis,
                provider_name=self.provider_name,
                allow_external=self.allow_external,
            )
        except ExternalProviderDisabledError as exc:
            warnings.append(str(exc))
            provider_response = generate_reliability_explanation(
                local_analysis,
                provider_name="local",
                allow_external=False,
            )
            provider_response["fallback_reason"] = "external_provider_blocked_by_default"
        except ProviderConfigurationError as exc:
            warnings.append(str(exc))
            provider_response = generate_reliability_explanation(
                local_analysis,
                provider_name="local",
                allow_external=False,
            )
            provider_response["fallback_reason"] = "external_provider_configuration_missing"

        repair = local_analysis.get("recommended_action", {})
        risk = _risk_summary(local_analysis)
        result = ProviderAwareAgentResult(
            project="FailSafeML-X",
            milestone="M15D_PROVIDER_AWARE_AGENT_INTEGRATION",
            case_id=normalized_case.sample_id,
            provider_requested=self.provider_name,
            provider_used=str(provider_response.get("provider", "unknown")),
            external_provider_enabled=external_providers_enabled() if self.allow_external is None else bool(self.allow_external),
            used_external_api=bool(provider_response.get("used_external_api", False)),
            local_analysis=local_analysis,
            provider_explanation=str(provider_response.get("text", "")),
            failure_explanation=_compact_failure_explanation(local_analysis),
            repair_recommendation=repair,
            risk_summary=risk,
            human_review_note=str(local_analysis.get("human_review_note", "")),
            provider_metadata={
                "provider": provider_response.get("provider"),
                "model": provider_response.get("model"),
                "raw_provider": provider_response.get("raw_provider"),
                "used_external_api": provider_response.get("used_external_api"),
                "fallback_reason": provider_response.get("fallback_reason"),
                "usage": provider_response.get("usage", {}),
            },
            warnings=warnings,
            limitations=[
                "Default provider-aware agent path is local and deterministic.",
                "External LLM providers are optional and disabled by default.",
                "Provider output explains reliability decisions but does not override safety routing.",
                "No production safety certification or live cloud deployment is claimed.",
            ],
        )
        return result.to_dict()


def analyze_with_provider(
    case: ReliabilityCase | dict[str, Any],
    provider_name: str | None = None,
    allow_external: bool | None = None,
) -> dict[str, Any]:
    """Convenience wrapper for provider-aware reliability analysis."""
    return ProviderAwareReliabilityAgent(provider_name=provider_name, allow_external=allow_external).analyze(case)
