# AWS SageMaker Template

This folder contains a **template-only** SageMaker inference entrypoint for FailSafeML-X.

It demonstrates how a managed inference endpoint could wrap a model prediction with a FailSafeML-X reliability envelope:

```text
request payload -> model prediction -> reliability envelope -> response JSON
```

## Safety defaults

The template is local/offline by default:

```text
FAILSAFEMLX_PROVIDER_MODE=local
FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false
FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false
```

No AWS credentials, SageMaker SDK, container build, or live endpoint is required for tests.

## Honest limitation

This is not a live SageMaker deployment and does not upload a model artifact. It is an entrypoint template that can be adapted after model packaging, registry, IAM, network, monitoring, and security review.
