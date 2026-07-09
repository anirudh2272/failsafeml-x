from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VectorAdapterStatus:
    name: str
    enabled: bool
    status: str
    message: str


def external_vector_db_enabled() -> bool:
    return os.getenv("FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB", "false").lower() == "true"


class BaseVectorAdapter:
    name = "base"

    def status(self) -> VectorAdapterStatus:
        return VectorAdapterStatus(
            name=self.name,
            enabled=False,
            status="stub",
            message="Base adapter is not directly usable.",
        )

    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        raise NotImplementedError


class LocalVectorAdapter(BaseVectorAdapter):
    name = "local"

    def status(self) -> VectorAdapterStatus:
        return VectorAdapterStatus(
            name=self.name,
            enabled=True,
            status="available",
            message="Local lexical retrieval is available and requires no vector database.",
        )


class _ExternalAdapterStub(BaseVectorAdapter):
    name = "external_stub"

    def status(self) -> VectorAdapterStatus:
        enabled = external_vector_db_enabled()
        return VectorAdapterStatus(
            name=self.name,
            enabled=enabled,
            status="disabled" if not enabled else "not_configured",
            message=(
                "External vector adapters are disabled by default. "
                "Set FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=true and configure credentials to use this adapter."
            ),
        )

    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        if not external_vector_db_enabled():
            raise RuntimeError(
                f"{self.name} is disabled by default for CI-safe execution. "
                "Set FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=true only for real external usage."
            )
        raise RuntimeError(f"{self.name} is a stub and has no live client configured.")


class ChromaAdapterStub(_ExternalAdapterStub):
    name = "chroma"


class QdrantAdapterStub(_ExternalAdapterStub):
    name = "qdrant"


class PineconeAdapterStub(_ExternalAdapterStub):
    name = "pinecone"


class WeaviateAdapterStub(_ExternalAdapterStub):
    name = "weaviate"


def vector_adapter_statuses() -> list[dict[str, object]]:
    adapters: list[BaseVectorAdapter] = [
        LocalVectorAdapter(),
        ChromaAdapterStub(),
        QdrantAdapterStub(),
        PineconeAdapterStub(),
        WeaviateAdapterStub(),
    ]
    return [adapter.status().__dict__ for adapter in adapters]
