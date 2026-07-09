from __future__ import annotations

from dataclasses import dataclass

from .documents import RAGDocument


@dataclass(frozen=True)
class RAGChunk:
    chunk_id: str
    doc_id: str
    text: str
    source: str
    created_at: str
    version: str
    trust_level: str


def chunk_documents(
    documents: list[RAGDocument],
    chunk_size: int = 450,
    overlap: int = 80,
) -> list[RAGChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks: list[RAGChunk] = []
    for document in documents:
        text = " ".join(document.text.split())
        if not text:
            continue
        start = 0
        local_index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    RAGChunk(
                        chunk_id=f"{document.doc_id}_chunk_{local_index}",
                        doc_id=document.doc_id,
                        text=chunk_text,
                        source=document.source,
                        created_at=document.created_at,
                        version=document.version,
                        trust_level=document.trust_level,
                    )
                )
            if end >= len(text):
                break
            start = max(0, end - overlap)
            local_index += 1
    return chunks
