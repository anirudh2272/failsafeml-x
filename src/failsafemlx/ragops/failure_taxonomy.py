from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .retrieval import RetrievedChunk


@dataclass(frozen=True)
class RAGFailure:
    failure_id: str
    severity: str
    reason: str
    evidence: str

    def to_dict(self) -> dict[str, str]:
        return {
            "failure_id": self.failure_id,
            "severity": self.severity,
            "reason": self.reason,
            "evidence": self.evidence,
        }


def diagnose_rag_failures(metrics: dict[str, float], retrieved_chunks: list[RetrievedChunk]) -> list[dict[str, str]]:
    failures: list[RAGFailure] = []

    if not retrieved_chunks:
        failures.append(RAGFailure("RAG_F7_INSUFFICIENT_CONTEXT", "HIGH", "No context was retrieved.", "retrieved_chunk_count=0"))
        return [failure.to_dict() for failure in failures]

    if metrics.get("context_relevance_score", 0.0) < 0.20:
        failures.append(RAGFailure("RAG_F1_LOW_CONTEXT_RELEVANCE", "MEDIUM", "Retrieved context has low lexical relevance to the query.", f"score={metrics.get('context_relevance_score')}"))

    if metrics.get("stale_context_rate", 0.0) > 0.0:
        failures.append(RAGFailure("RAG_F2_STALE_DOCUMENT", "HIGH", "Retrieved context contains stale document versions.", f"rate={metrics.get('stale_context_rate')}"))

    if metrics.get("citation_coverage_score", 0.0) < 0.50:
        failures.append(RAGFailure("RAG_F3_MISSING_CITATION", "MEDIUM", "Answer lacks sufficient citations to retrieved context.", f"coverage={metrics.get('citation_coverage_score')}"))

    if metrics.get("conflicting_evidence_score", 0.0) >= 0.75:
        failures.append(RAGFailure("RAG_F4_CONFLICTING_EVIDENCE", "HIGH", "Retrieved context contains conflicting evidence versions.", f"score={metrics.get('conflicting_evidence_score')}"))

    if metrics.get("prompt_injection_risk_score", 0.0) > 0.0:
        failures.append(RAGFailure("RAG_F5_PROMPT_INJECTION_IN_CONTEXT", "CRITICAL", "Retrieved context contains prompt-injection-like instructions.", f"risk={metrics.get('prompt_injection_risk_score')}"))

    if metrics.get("trusted_source_rate", 1.0) <= 0.75:
        failures.append(RAGFailure("RAG_F6_UNTRUSTED_SOURCE", "HIGH", "Retrieved context contains too many untrusted sources.", f"trusted_source_rate={metrics.get('trusted_source_rate')}"))

    if metrics.get("retrieval_noise_score", 0.0) > 0.50:
        failures.append(RAGFailure("RAG_F8_OVER_RETRIEVAL_NOISE", "MEDIUM", "Retrieved set contains low-relevance noise.", f"noise={metrics.get('retrieval_noise_score')}"))

    return [failure.to_dict() for failure in failures]
