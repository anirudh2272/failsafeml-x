from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from failsafemlx.ragops.documents import load_markdown_documents, load_query_cases
from failsafemlx.ragops.reliability_audit import aggregate_audits, audit_rag_query
from failsafemlx.ragops.vector_adapters import vector_adapter_statuses

DOCUMENTS_PATH = PROJECT_ROOT / "data/ragops/documents"
QUERIES_PATH = PROJECT_ROOT / "data/ragops/queries/ragops_eval_queries.json"
RESULT_PATH = PROJECT_ROOT / "experiments/results/m15b_ragops_reliability.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_15b_ragops_reliability.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    aggregate = result["aggregate"]
    failures = "\n".join(f"- {k}: {v}" for k, v in aggregate["failure_counts"].items()) or "- None"
    repairs = "\n".join(f"- {k}: {v}" for k, v in aggregate["repair_action_counts"].items()) or "- None"
    cases = "\n".join(
        f"- {audit['case_id']}: trust={audit['trust_score']}, route={audit['routing_decision']}, failures={len(audit['failures'])}"
        for audit in result["query_audits"]
    )
    content = f"""# Milestone 15B — RAGOps Reliability Extension

## Objective

Add an optional local-first RAGOps reliability layer to FailSafeML-X for auditing retrieved context, citation coverage, stale evidence, unsafe retrieved text, untrusted sources, and RAG repair routing.

## Validation Summary

- Passed: {result['passed']}
- Documents loaded: {result['document_count']}
- Query cases audited: {aggregate['audit_count']}
- Average trust score: {aggregate['average_trust_score']}

## Query Audit Summary

{cases}

## Failure Counts

{failures}

## Repair Action Counts

{repairs}

## External Vector Adapter Status

External vector database adapters are present as stubs and disabled by default. Local lexical retrieval is the validated CI-safe path.

## Generated Outputs

- `experiments/results/m15b_ragops_reliability.json`
- `reports/milestone_15b_ragops_reliability.md`

## Honest Limitation

This milestone does not claim production RAG deployment, live vector database integration, live OpenAI or AWS Bedrock calls, or production monitoring. It is a local-first RAG reliability audit extension.
"""
    path.write_text(content, encoding="utf-8")


def run_m15b() -> dict[str, Any]:
    documents = load_markdown_documents(DOCUMENTS_PATH)
    query_cases = load_query_cases(QUERIES_PATH)
    audits: list[dict[str, Any]] = []

    for case in query_cases:
        audit = audit_rag_query(
            query=str(case["query"]),
            answer_text=str(case["answer_text"]),
            documents_path=DOCUMENTS_PATH,
            top_k=int(case.get("top_k", 5)),
        )
        audit["case_id"] = str(case["id"])
        audits.append(audit)

    aggregate = aggregate_audits(audits)
    failure_ids = {failure["failure_id"] for audit in audits for failure in audit["failures"]}
    required_failure_ids = {
        "RAG_F2_STALE_DOCUMENT",
        "RAG_F3_MISSING_CITATION",
        "RAG_F5_PROMPT_INJECTION_IN_CONTEXT",
        "RAG_F6_UNTRUSTED_SOURCE",
    }
    errors: list[str] = []
    if len(documents) < 4:
        errors.append("Expected at least four RAGOps sample documents.")
    if len(query_cases) < 5:
        errors.append("Expected at least five RAGOps query cases.")
    missing = required_failure_ids - failure_ids
    if missing:
        errors.append(f"Missing required RAG failure IDs in audits: {sorted(missing)}")

    result: dict[str, Any] = {
        "milestone": "M15B_RAGOPS_RELIABILITY_EXTENSION",
        "project": "FailSafeML-X",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "document_count": len(documents),
        "query_case_count": len(query_cases),
        "query_audits": audits,
        "aggregate": aggregate,
        "vector_adapter_statuses": vector_adapter_statuses(),
        "errors": errors,
        "honest_claim": "Extended FailSafeML-X with an optional local-first RAGOps reliability layer for auditing retrieved context, stale or unsafe evidence, citation coverage, RAG failure IDs, and repair routing.",
        "honest_limitations": "No production RAG deployment, live vector database integration, live OpenAI calls, or live AWS Bedrock calls are claimed.",
    }

    _write_json(RESULT_PATH, result)
    _write_report(REPORT_PATH, result)
    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if not result["passed"]:
        raise SystemExit("M15B validation failed: " + "; ".join(errors))

    print("M15B completed successfully.")
    return result


if __name__ == "__main__":
    run_m15b()
