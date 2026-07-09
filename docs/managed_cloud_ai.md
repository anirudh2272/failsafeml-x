# Managed Cloud AI Deployment Templates

Milestone 18 adds template entrypoints for adapting FailSafeML-X to managed inference services such as AWS SageMaker and Google Vertex AI.

## Why this belongs in FailSafeML-X

FailSafeML-X is a reliability envelope around model outputs. Managed AI platforms commonly expose a prediction handler that receives a request and returns a response. The same pattern can wrap each prediction with:

- trust score,
- reliability failure IDs,
- repair actions,
- human-review routing,
- provider safety metadata,
- honest limitations.

## Included templates

| Path | Purpose |
|---|---|
| `cloud/aws/sagemaker/inference.py` | SageMaker-style `model_fn`, `input_fn`, `predict_fn`, and `output_fn` template |
| `cloud/aws/sagemaker/model.tar.gz.placeholder.md` | Placeholder documenting where a real model artifact would be packaged |
| `cloud/gcp/vertex_ai/predictor.py` | Vertex-style predictor class template |
| `cloud/aws/sagemaker/README.md` | AWS template notes and limitations |
| `cloud/gcp/vertex_ai/README.md` | GCP template notes and limitations |

## Safety defaults

The templates keep all external providers disabled by default:

```text
FAILSAFEMLX_PROVIDER_MODE=local
FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false
FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false
```

## What is validated

The milestone validates that templates:

- exist,
- expose managed-inference entrypoint functions/classes,
- wrap prediction output with reliability envelopes,
- include safe local/offline provider defaults,
- do not contain real secrets,
- do not require cloud SDKs for tests,
- do not create live cloud resources.

## Honest limitations

This milestone does not deploy to SageMaker or Vertex AI. It does not build containers, create endpoints, upload model artifacts, configure IAM/service accounts, set up production logging, or run live cloud inference.

## Run

```bash
python scripts/run_m18_cloud_ai_templates.py
```
