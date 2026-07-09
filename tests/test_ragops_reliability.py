from __future__ import annotations

from pathlib import Path

import pytest

from failsafemlx.ragops.chunking import chunk_documents
from failsafemlx.ragops.documents import load_markdown_documents, load_query_cases
from failsafemlx.ragops.failure_taxonomy import diagnose_rag_failures
from failsafemlx.ragops.metrics import compute_rag_metrics
from failsafemlx.ragops.reliability_audit import audit_rag_query
from failsafemlx.ragops.repair_policy import recommend_rag_repairs
from failsafemlx.ragops.retrieval import LocalRetriever
from failsafemlx.ragops.vector_adapters import QdrantAdapterStub, vector_adapter_statuses
from scripts.run_m15b_ragops_reliability import run_m15b

DOCUMENTS_PATH = Path("data/ragops/documents")
QUERIES_PATH = Path("data/ragops/queries/ragops_eval_queries.json")


def test_markdown_documents_load_correctly():
    documents = load_markdown_documents(DOCUMENTS_PATH)
    assert len(documents) >= 4
    assert {doc.doc_id for doc in documents} >= {"current_policy", "old_policy", "security_notice", "untrusted_external_note"}


def test_query_cases_load_correctly():
    cases = load_query_cases(QUERIES_PATH)
    assert len(cases) >= 5
    assert all("query" in case and "answer_text" in case for case in cases)


def test_chunking_creates_chunks():
    chunks = chunk_documents(load_markdown_documents(DOCUMENTS_PATH), chunk_size=180, overlap=30)
    assert len(chunks) >= 4
    assert all(chunk.chunk_id for chunk in chunks)


def test_local_retrieval_returns_relevant_chunks():
    chunks = chunk_documents(load_markdown_documents(DOCUMENTS_PATH))
    retrieved = LocalRetriever().retrieve("current reliability policy citations", chunks, top_k=3)
    assert retrieved
    assert retrieved[0].score > 0


def test_stale_documents_are_detected():
    audit = audit_rag_query(
        "Can the old policy allow answers without citations when confidence is high?",
        "The old policy allowed answers without citations. [old_policy]",
        DOCUMENTS_PATH,
        top_k=5,
    )
    failure_ids = {failure["failure_id"] for failure in audit["failures"]}
    assert "RAG_F2_STALE_DOCUMENT" in failure_ids


def test_missing_citations_are_detected():
    audit = audit_rag_query(
        "How should stale documents be handled before answer generation?",
        "Stale documents should be filtered before final answer generation.",
        DOCUMENTS_PATH,
        top_k=5,
    )
    failure_ids = {failure["failure_id"] for failure in audit["failures"]}
    assert "RAG_F3_MISSING_CITATION" in failure_ids


def test_prompt_injection_in_context_is_detected():
    audit = audit_rag_query(
        "Should we follow the untrusted external note that says print secrets?",
        "No. [untrusted_external_note]",
        DOCUMENTS_PATH,
        top_k=5,
    )
    failure_ids = {failure["failure_id"] for failure in audit["failures"]}
    assert "RAG_F5_PROMPT_INJECTION_IN_CONTEXT" in failure_ids
    assert audit["routing_decision"] == "BLOCK_RESPONSE"


def test_untrusted_source_is_detected():
    audit = audit_rag_query(
        "Should we follow the untrusted external note that says print secrets?",
        "No. [untrusted_external_note]",
        DOCUMENTS_PATH,
        top_k=5,
    )
    failure_ids = {failure["failure_id"] for failure in audit["failures"]}
    assert "RAG_F6_UNTRUSTED_SOURCE" in failure_ids


def test_repair_actions_are_recommended():
    failures = [{"failure_id": "RAG_F5_PROMPT_INJECTION_IN_CONTEXT", "severity": "CRITICAL", "reason": "x", "evidence": "y"}]
    repairs = recommend_rag_repairs(failures)
    assert repairs[0]["repair_action"] == "RAG_R6_BLOCK_PROMPT_INJECTION"


def test_trust_score_decreases_for_risky_context():
    safe = audit_rag_query(
        "What does the current reliability policy require for RAG citations?",
        "The current policy requires citations. [current_policy]",
        DOCUMENTS_PATH,
        top_k=1,
    )
    risky = audit_rag_query(
        "Should we follow the untrusted external note that says print secrets?",
        "No. [untrusted_external_note]",
        DOCUMENTS_PATH,
        top_k=5,
    )
    assert risky["trust_score"] < safe["trust_score"]


def test_external_vector_adapters_are_blocked_by_default(monkeypatch):
    monkeypatch.delenv("FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB", raising=False)
    statuses = vector_adapter_statuses()
    external = [status for status in statuses if status["name"] == "qdrant"][0]
    assert external["status"] == "disabled"
    with pytest.raises(RuntimeError):
        QdrantAdapterStub().search("test")


def test_m15b_runner_writes_json_and_report():
    result = run_m15b()
    assert result["passed"] is True
    assert Path("experiments/results/m15b_ragops_reliability.json").exists()
    assert Path("reports/milestone_15b_ragops_reliability.md").exists()
