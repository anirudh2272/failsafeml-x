from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["low", "medium", "high", "critical", "unknown"]
Decision = Literal["accept", "abstain", "human_review", "active_learning", "recalibrate", "flag_drift"]


@dataclass(frozen=True)
class ReliabilityCase:
    """Input envelope for deterministic reliability-agent analysis."""

    sample_id: str
    prediction: Any
    trust_score: float
    failure_ids: list[str] = field(default_factory=list)
    uncertainty: float | None = None
    calibration_error: float | None = None
    drift_score: float | None = None
    ood_score: float | None = None
    domain: str = "generic_ml"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolResult:
    """JSON-compatible result returned by a reliability-agent tool."""

    tool_name: str
    passed: bool
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentAnalysis:
    """Structured agent output for review, API use, and reporting."""

    project: str
    agent_name: str
    agent_mode: str
    optional_integrations: dict[str, bool]
    case: dict[str, Any]
    failure_explanations: list[dict[str, Any]]
    trust_summary: dict[str, Any]
    drift_ood_summary: dict[str, Any]
    recommended_action: dict[str, Any]
    human_review_note: str
    limitations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
