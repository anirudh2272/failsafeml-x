# FailSafeML-X Terraform Template

This directory contains a static Terraform deployment template for packaging the FailSafeML-X FastAPI reliability service on Kubernetes.

## Scope

This is a template-only milestone:

- Terraform is not executed during tests.
- No Kubernetes cluster is required.
- No cloud credentials are required.
- No real secrets are included.
- External LLM and vector database providers default to disabled/offline mode.

## Intended service

The template targets the local FastAPI service defined by the project Dockerfile:

```text
uvicorn failsafemlx.serving.fastapi_app:app --host 0.0.0.0 --port 8000 --app-dir src
```

## Safety defaults

The deployment environment intentionally defaults to:

```text
FAILSAFEMLX_PROVIDER_MODE=local
FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false
FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false
```

These defaults ensure the reliability service can be packaged without triggering paid external APIs or cloud AI provider calls.
