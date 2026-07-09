# Optional RAGOps Reliability Extension

Milestone 15B extends FailSafeML-X with a local-first RAGOps reliability layer. The core project remains a model-agnostic ML reliability platform; this extension adds reliability auditing for retrieval-augmented generation pipelines.

## Why RAGOps Belongs Here

RAG systems can fail even when the language model appears fluent. Retrieved context may be stale, irrelevant, untrusted, conflicting, or malicious. FailSafeML-X already diagnoses ML reliability failures and routes risky decisions through repair policies, so RAG context reliability fits naturally as another reliability domain.

## Local-First Workflow

```text
User Query
→ Document Loader
→ Chunker
→ Local Retriever
→ Retrieved Context
→ RAG Reliability Audit
→ Failure IDs
→ Repair Actions
→ Trust Score
→ RAG Reliability Envelope
```

## Failure Modes

The extension checks for low context relevance, stale document versions, missing citations, conflicting evidence, prompt injection in retrieved context, untrusted sources, insufficient context, and over-retrieval noise.

## Repair Policy

Detected failures map to repair actions such as filtering stale documents, requiring citations, blocking prompt injection, removing untrusted context, reranking context, retrieving more context, or routing to human review.

## Optional Vector Database Design

The repository includes adapter stubs for Chroma, Qdrant, Pinecone, and Weaviate. These are disabled by default and are not required for tests. The validated path is local lexical retrieval.

## Run

```bash
python scripts/run_m15b_ragops_reliability.py
```

## Honest Limitation

This is not a production RAG deployment. It does not call OpenAI, AWS Bedrock, or live vector databases. It is a deterministic local reliability extension designed for testing, CI, and portfolio demonstration.
