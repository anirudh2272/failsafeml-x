from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .chunking import RAGChunk

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    text: str
    score: float
    source: str
    created_at: str
    version: str
    trust_level: str


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _overlap_score(query_tokens: list[str], chunk_tokens: list[str]) -> float:
    if not query_tokens or not chunk_tokens:
        return 0.0
    q_counts = Counter(query_tokens)
    c_counts = Counter(chunk_tokens)
    overlap = sum(min(count, c_counts[token]) for token, count in q_counts.items())
    normalization = math.sqrt(sum(q_counts.values())) * math.sqrt(sum(c_counts.values()))
    return float(overlap / normalization) if normalization else 0.0


class LocalRetriever:
    """Dependency-free lexical retriever used for local tests and CI."""

    def retrieve(
        self,
        query: str,
        chunks: list[RAGChunk],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        query_tokens = tokenize(query)
        scored: list[RetrievedChunk] = []
        for chunk in chunks:
            score = _overlap_score(query_tokens, tokenize(chunk.text))
            if score > 0:
                scored.append(
                    RetrievedChunk(
                        chunk_id=chunk.chunk_id,
                        doc_id=chunk.doc_id,
                        text=chunk.text,
                        score=round(score, 4),
                        source=chunk.source,
                        created_at=chunk.created_at,
                        version=chunk.version,
                        trust_level=chunk.trust_level,
                    )
                )
        scored.sort(key=lambda item: (-item.score, item.doc_id, item.chunk_id))
        return scored[:top_k]
