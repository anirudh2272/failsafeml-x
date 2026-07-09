from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .chunking import chunk_documents
from .documents import load_markdown_documents
from .failure_taxonomy import diagnose_rag_failures
from .metrics import compute_rag_metrics
from .repair_policy import recommend_rag_repairs
from .retrieval import LocalRetriever

SEVERITY_PENALTY = {"LOW": 5, "MEDIUM": 15, "HIGH": 30, "CRITICAL": 50}


@dataclass(frozen=True)
class RAGReliabilityEnvelope:
    query: str
    retrieved_chunk_count: int
    retrieved_chunks: list[dict[str, Any]]
    metrics: dict[str, float]
    failures: list[dict[str, str]]
    repair_actions: list[dict[str, str]]
    trust_score: int
    routing_decision: str
    provider_mode: str
    honest_limitations: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def compute_trust_score(failures: list[dict[str, str]]) -> int:
    score = 100
    for failure in failures:
        score -= SEVERITY_PENALTY.get(failure.get("severity", "LOW"), 5)
    return max(0, min(100, score))


def choose_routing_decision(failures: list[dict[str, str]]) -> str:
    ids = {failure.get("failure_id", "") for failure in failures}
    severities = {failure.get("severity", "") for failure in failures}
    if "CRITICAL" in severities:
        return "BLOCK_RESPONSE"
    if "HIGH" in severities:
        if "RAG_F2_STALE_DOCUMENT" in ids or "RAG_F6_UNTRUSTED_SOURCE" in ids:
            return "FILTER_AND_RETRY"
        return "HUMAN_REVIEW"
    if "RAG_F7_INSUFFICIENT_CONTEXT" in ids or "RAG_F1_LOW_CONTEXT_RELEVANCE" in ids:
        return "RETRY_RETRIEVAL"
    return "ACCEPT_WITH_CITATIONS"


def audit_rag_query(
    query: str,
    answer_text: str,
    documents_path: str | Path,
    top_k: int = 5,
) -> dict[str, Any]:
    documents = load_markdown_documents(documents_path)
    chunks = chunk_documents(documents)
    retrieved = LocalRetriever().retrieve(query, chunks, top_k=top_k)
    metrics = compute_rag_metrics(query, answer_text, retrieved)
    failures = diagnose_rag_failures(metrics, retrieved)
    repairs = recommend_rag_repairs(failures)
    trust_score = compute_trust_score(failures)
    routing_decision = choose_routing_decision(failures)

    envelope = RAGReliabilityEnvelope(
        query=query,
        retrieved_chunk_count=len(retrieved),
        retrieved_chunks=[chunk.__dict__.copy() for chunk in retrieved],
        metrics=metrics,
        failures=failures,
        repair_actions=repairs,
        trust_score=trust_score,
        routing_decision=routing_decision,
        provider_mode="local_retriever_only",
        honest_limitations="M15B is a local-first RAG reliability audit extension. It does not claim live vector database, OpenAI, Bedrock, or production RAG deployment.",
    )
    return envelope.to_dict()


def aggregate_audits(audits: list[dict[str, Any]]) -> dict[str, Any]:
    failure_counter: Counter[str] = Counter()
    repair_counter: Counter[str] = Counter()
    trust_scores: list[int] = []
    for audit in audits:
        trust_scores.append(int(audit.get("trust_score", 0)))
        for failure in audit.get("failures", []):
            failure_counter[failure.get("failure_id", "UNKNOWN")] += 1
        for repair in audit.get("repair_actions", []):
            repair_counter[repair.get("repair_action", "UNKNOWN")] += 1
    return {
        "audit_count": len(audits),
        "average_trust_score": round(sum(trust_scores) / len(trust_scores), 4) if trust_scores else 0.0,
        "failure_counts": dict(sorted(failure_counter.items())),
        "repair_action_counts": dict(sorted(repair_counter.items())),
    }
