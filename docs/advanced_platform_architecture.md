# Advanced Platform Architecture

FailSafeML-X is a **model-agnostic** reliability layer for ML systems. It is designed to wrap predictions, reliability signals, optional RAGOps evidence, and provider-aware explanations in a structured reliability envelope.

## System Flow

```text
CSV / synthetic data / RAG documents
  -> dataset validation and local loaders
  -> model prediction or retrieved context
  -> calibration, conformal uncertainty, drift, OOD, and RAGOps checks
  -> failure taxonomy
  -> trust score
  -> repair action policy
  -> routing decision
  -> model card, risk card, metrics, reports, and optional deployment templates
```

## Main Layers

1. **Reliability audit core**: calibration, conformal prediction, drift, OOD, trust scoring, failure taxonomy, and repair routing.
2. **Optional RAGOps reliability extension**: local document loading, chunking, retrieval quality metrics, citation checks, stale evidence detection, prompt-injection detection inside retrieved context, and RAG repair actions.
3. **Dataset validation**: schema checks, missingness, duplicates, class imbalance, leakage-like columns, and timestamp ordering checks.
4. **Provider abstraction**: local deterministic provider by default, with OpenAI-compatible and AWS Bedrock-style adapters disabled unless explicitly enabled.
5. **Monitoring and tracking**: Prometheus-style metrics, Grafana dashboard skeleton, local experiment registry, model card, and model risk card.
6. **Deployment and cloud templates**: Terraform, Helm, AWS SageMaker-style, and Google Vertex AI-style templates.
7. **Fine-tuning scaffold**: LoRA / PEFT instruction-data builder and training stub.

## Reliability Envelope

The final platform output is not only a prediction. It is a reliability envelope containing:

- prediction or retrieved context summary,
- reliability metrics,
- failure IDs,
- trust score,
- repair actions,
- routing decision,
- human-review note,
- provider metadata,
- honest limitations.

## Safety Boundary

This repository is not a production-certified platform. Local CI requires **no external API**, no OpenAI key, no AWS credentials, no GPU, no live vector database, no Kubernetes cluster, no Prometheus server, and no cloud deployment.
