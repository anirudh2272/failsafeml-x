from __future__ import annotations

from typing import Any

from failsafemlx.agents.schemas import AgentAnalysis, ReliabilityCase
from failsafemlx.agents.tools import (
    explain_failure_ids,
    generate_human_review_note,
    recommend_repair_action,
    summarize_drift_ood_risk,
    summarize_trust_score,
)


def _optional_import_available(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


class ReliabilityAgent:
    """Deterministic agentic reliability analyst with optional LangGraph/LangChain hooks.

    The default path is intentionally local and deterministic so tests, demos, and
    portfolio review do not require API keys or external model calls.
    """

    def __init__(self, prefer_langgraph: bool = False) -> None:
        self.prefer_langgraph = prefer_langgraph
        self.optional_integrations = {
            "langgraph_available": _optional_import_available("langgraph"),
            "langchain_available": _optional_import_available("langchain"),
        }

    @property
    def agent_mode(self) -> str:
        if (
            self.prefer_langgraph
            and self.optional_integrations["langgraph_available"]
            and self.optional_integrations["langchain_available"]
        ):
            return "optional_langgraph_langchain_adapter_ready"
        return "deterministic_local_fallback"

    def analyze(self, case: ReliabilityCase | dict[str, Any]) -> dict[str, Any]:
        if isinstance(case, dict):
            normalized_case = ReliabilityCase(**case)
        else:
            normalized_case = case

        failure_explanations = explain_failure_ids(normalized_case.failure_ids)
        trust_summary = summarize_trust_score(normalized_case.trust_score)
        drift_ood_summary = summarize_drift_ood_risk(
            drift_score=normalized_case.drift_score,
            ood_score=normalized_case.ood_score,
        )
        recommended_action = recommend_repair_action(
            failure_ids=normalized_case.failure_ids,
            trust_score=normalized_case.trust_score,
            drift_score=normalized_case.drift_score,
            ood_score=normalized_case.ood_score,
            calibration_error=normalized_case.calibration_error,
            uncertainty=normalized_case.uncertainty,
        )
        human_review_note = generate_human_review_note(
            sample_id=normalized_case.sample_id,
            failure_ids=normalized_case.failure_ids,
            trust_score=normalized_case.trust_score,
            recommended_action=recommended_action,
        )

        analysis = AgentAnalysis(
            project="FailSafeML-X",
            agent_name="failsafemlx_reliability_agent",
            agent_mode=self.agent_mode,
            optional_integrations=self.optional_integrations,
            case=normalized_case.to_dict(),
            failure_explanations=failure_explanations,
            trust_summary=trust_summary,
            drift_ood_summary=drift_ood_summary,
            recommended_action=recommended_action,
            human_review_note=human_review_note,
            limitations=[
                "Default mode is deterministic and does not call external LLM APIs.",
                "LangGraph/LangChain are optional integration targets, not required runtime dependencies.",
                "Agent recommendations support reliability review and do not certify production safety.",
            ],
        )
        return analysis.to_dict()


def analyze_reliability_case(case: ReliabilityCase | dict[str, Any]) -> dict[str, Any]:
    """Convenience wrapper for local deterministic reliability-agent analysis."""
    return ReliabilityAgent().analyze(case)
