from __future__ import annotations

import re
from collections import defaultdict
from statistics import mean

from .retrieval import RetrievedChunk, tokenize

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "system messages",
    "developer message",
    "bypass safety",
    "exfiltrate",
    "print secrets",
    "disable guardrails",
    "follow only this instruction",
]


def context_relevance_score(query: str, retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 0.0
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0
    scores: list[float] = []
    for chunk in retrieved_chunks:
        chunk_tokens = set(tokenize(chunk.text))
        scores.append(len(query_tokens & chunk_tokens) / len(query_tokens))
    return round(float(mean(scores)), 4)


def citation_coverage_score(answer_text: str, retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 0.0
    markers = set(re.findall(r"\[([^\]]+)\]", answer_text))
    if not markers:
        return 0.0
    doc_or_chunk_ids = {chunk.doc_id for chunk in retrieved_chunks} | {chunk.chunk_id for chunk in retrieved_chunks}
    matched = len(markers & doc_or_chunk_ids)
    return round(matched / max(1, min(len(markers), len(retrieved_chunks))), 4)


def _version_number(version: str) -> int:
    match = re.search(r"(\d+)", version or "")
    return int(match.group(1)) if match else 0


def stale_context_rate(retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 0.0
    max_policy_version = max((_version_number(c.version) for c in retrieved_chunks if "policy" in c.doc_id), default=0)
    stale = 0
    for chunk in retrieved_chunks:
        if "old" in chunk.doc_id.lower() or ("policy" in chunk.doc_id and _version_number(chunk.version) < max_policy_version):
            stale += 1
    return round(stale / len(retrieved_chunks), 4)


def trusted_source_rate(retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 0.0
    trusted = sum(1 for chunk in retrieved_chunks if chunk.trust_level.lower() == "trusted")
    return round(trusted / len(retrieved_chunks), 4)


def conflicting_evidence_score(retrieved_chunks: list[RetrievedChunk]) -> float:
    if len(retrieved_chunks) < 2:
        return 0.0
    by_topic: dict[str, set[str]] = defaultdict(set)
    for chunk in retrieved_chunks:
        if "policy" in chunk.doc_id.lower():
            by_topic["policy"].add(chunk.version)
    conflict_topics = sum(1 for versions in by_topic.values() if len(versions) > 1)
    return 1.0 if conflict_topics else 0.0


def prompt_injection_risk_score(retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 0.0
    risky = 0
    for chunk in retrieved_chunks:
        lower = chunk.text.lower()
        if any(pattern in lower for pattern in PROMPT_INJECTION_PATTERNS):
            risky += 1
    return round(risky / len(retrieved_chunks), 4)


def retrieval_noise_score(query: str, retrieved_chunks: list[RetrievedChunk]) -> float:
    if not retrieved_chunks:
        return 1.0
    low_relevance = sum(1 for chunk in retrieved_chunks if chunk.score < 0.08)
    return round(low_relevance / len(retrieved_chunks), 4)


def compute_rag_metrics(query: str, answer_text: str, retrieved_chunks: list[RetrievedChunk]) -> dict[str, float]:
    return {
        "context_relevance_score": context_relevance_score(query, retrieved_chunks),
        "citation_coverage_score": citation_coverage_score(answer_text, retrieved_chunks),
        "stale_context_rate": stale_context_rate(retrieved_chunks),
        "trusted_source_rate": trusted_source_rate(retrieved_chunks),
        "conflicting_evidence_score": conflicting_evidence_score(retrieved_chunks),
        "prompt_injection_risk_score": prompt_injection_risk_score(retrieved_chunks),
        "retrieval_noise_score": retrieval_noise_score(query, retrieved_chunks),
    }
