from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RAGDocument:
    doc_id: str
    title: str
    text: str
    source: str
    created_at: str
    version: str
    trust_level: str


def _parse_metadata_block(raw_text: str) -> tuple[dict[str, str], str]:
    text = raw_text.strip()
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    metadata: dict[str, str] = {}
    end_index: int | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    if end_index is None:
        return {}, text
    body = "\n".join(lines[end_index + 1 :]).strip()
    return metadata, body


def load_markdown_documents(path: str | Path) -> list[RAGDocument]:
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Document path does not exist: {root}")

    files = sorted(root.glob("*.md")) if root.is_dir() else [root]
    documents: list[RAGDocument] = []

    for file_path in files:
        raw = file_path.read_text(encoding="utf-8")
        metadata, body = _parse_metadata_block(raw)
        doc_id = metadata.get("doc_id", file_path.stem)
        documents.append(
            RAGDocument(
                doc_id=doc_id,
                title=metadata.get("title", doc_id.replace("_", " ").title()),
                text=body,
                source=metadata.get("source", "unknown"),
                created_at=metadata.get("created_at", "unknown"),
                version=metadata.get("version", "unknown"),
                trust_level=metadata.get("trust_level", "unknown"),
            )
        )
    return documents


def load_query_cases(path: str | Path) -> list[dict[str, Any]]:
    query_path = Path(path)
    payload = json.loads(query_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("RAGOps query cases file must contain a list of cases.")
    for i, case in enumerate(payload):
        if not isinstance(case, dict):
            raise ValueError(f"Query case {i} is not an object.")
        for required in ["id", "query", "answer_text"]:
            if required not in case:
                raise ValueError(f"Query case {i} is missing required field: {required}")
    return payload
