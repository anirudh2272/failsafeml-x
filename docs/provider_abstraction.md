# Optional LLM Provider Abstraction

FailSafeML-X keeps the core reliability workflow local and deterministic by default. This milestone adds an optional provider abstraction for reliability explanation generation.

## Providers

Supported provider modes:

- `local` — deterministic fallback, used by tests and local CI
- `openai_compatible` — optional Chat Completions-compatible adapter
- `bedrock` — optional AWS Bedrock Converse-style adapter

## Default Behavior

External providers are disabled by default. Local CI and tests do not use API keys, do not call OpenAI-compatible APIs, and do not call AWS Bedrock.

```bash
FAILSAFEMLX_LLM_PROVIDER=local
```

## Optional External Provider Usage

OpenAI-compatible provider configuration:

```bash
export FAILSAFEMLX_ENABLE_EXTERNAL_LLM=true
export FAILSAFEMLX_LLM_PROVIDER=openai_compatible
export OPENAI_COMPATIBLE_BASE_URL="https://your-provider.example/v1"
export OPENAI_COMPATIBLE_API_KEY="..."
export OPENAI_COMPATIBLE_MODEL="..."
```

AWS Bedrock-style provider configuration:

```bash
export FAILSAFEMLX_ENABLE_EXTERNAL_LLM=true
export FAILSAFEMLX_LLM_PROVIDER=bedrock
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID="your-bedrock-model-id"
```

Install optional dependencies only when needed:

```bash
pip install -r requirements-providers.txt
```

## Scope

This is a provider-abstraction scaffold. It does not claim AWS deployment, OpenAI production usage, Bedrock production usage, or production LLMOps. The reliability system remains fully runnable offline.
