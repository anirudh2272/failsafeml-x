from __future__ import annotations

REPAIR_MAP = {
    "RAG_F1_LOW_CONTEXT_RELEVANCE": "RAG_R7_RERANK_CONTEXT",
    "RAG_F2_STALE_DOCUMENT": "RAG_R2_FILTER_STALE_DOCUMENTS",
    "RAG_F3_MISSING_CITATION": "RAG_R3_REQUIRE_CITATIONS",
    "RAG_F4_CONFLICTING_EVIDENCE": "RAG_R4_ROUTE_TO_HUMAN_REVIEW",
    "RAG_F5_PROMPT_INJECTION_IN_CONTEXT": "RAG_R6_BLOCK_PROMPT_INJECTION",
    "RAG_F6_UNTRUSTED_SOURCE": "RAG_R5_REMOVE_UNTRUSTED_CONTEXT",
    "RAG_F7_INSUFFICIENT_CONTEXT": "RAG_R1_RETRIEVE_MORE_CONTEXT",
    "RAG_F8_OVER_RETRIEVAL_NOISE": "RAG_R7_RERANK_CONTEXT",
    "RAG_F9_UNSAFE_ANSWER_REQUEST": "RAG_R10_ABSTAIN_FROM_ANSWERING",
    "RAG_F10_EXTERNAL_PROVIDER_BLOCKED": "RAG_R8_USE_LOCAL_PROVIDER_ONLY",
}


def recommend_rag_repairs(failures: list[dict[str, str]]) -> list[dict[str, str]]:
    repairs: list[dict[str, str]] = []
    seen: set[str] = set()
    for failure in failures:
        failure_id = failure.get("failure_id", "")
        action_id = REPAIR_MAP.get(failure_id, "RAG_R4_ROUTE_TO_HUMAN_REVIEW")
        if action_id in seen:
            continue
        seen.add(action_id)
        repairs.append(
            {
                "failure_id": failure_id,
                "repair_action": action_id,
                "reason": f"Recommended because {failure_id} was detected.",
            }
        )
    return repairs
