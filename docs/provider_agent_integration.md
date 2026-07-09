# Provider-Aware Agent Integration

Milestone 15D connects the deterministic FailSafeML-X reliability agent to the optional LLM provider abstraction added in M15A.

## Purpose

The goal is to generate structured, provider-aware reliability explanations while preserving the core FailSafeML-X safety behavior:

- local deterministic provider by default
- optional OpenAI-compatible adapter
- optional AWS Bedrock Converse-style adapter
- external providers blocked unless explicitly enabled
- no API keys required for tests or local CI
- provider output never overrides repair routing or human-review decisions

## Local-First Behavior

By default, the provider-aware agent uses the local deterministic provider. This keeps the project reproducible and safe for offline review.

```bash
python scripts/run_m15d_provider_agent_integration.py
```

## Optional External Providers

External providers remain disabled unless explicitly enabled:

```bash
export FAILSAFEMLX_ENABLE_EXTERNAL_LLM=true
export FAILSAFEMLX_LLM_PROVIDER=openai_compatible
```

or:

```bash
export FAILSAFEMLX_ENABLE_EXTERNAL_LLM=true
export FAILSAFEMLX_LLM_PROVIDER=bedrock
```

Do not enable these unless credentials and model access are intentionally configured.

## Output

The provider-aware agent returns JSON-compatible fields:

- failure explanation
- repair recommendation
- risk summary
- human-review note
- provider explanation
- provider metadata
- warnings
- honest limitations

## Honest Limitations

M15D does not claim live OpenAI usage, live AWS Bedrock usage, production deployment, or safety certification. It adds a provider-aware integration pattern that remains local/offline by default.
