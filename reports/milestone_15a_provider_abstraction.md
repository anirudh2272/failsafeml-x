# Milestone 15A — Optional LLM Provider Abstraction

## Objective

Add an optional provider abstraction so FailSafeML-X reliability explanations can remain local by default while being ready for OpenAI-compatible or AWS Bedrock Converse-style providers when explicitly enabled.

## Validation Summary

- Passed: True
- Default provider: local deterministic fallback
- External API calls during tests: false
- OpenAI-compatible adapter: present, disabled by default
- AWS Bedrock Converse adapter: present, disabled by default

## Why This Does Not Break the Project

The core reliability workflow still runs without external APIs. Provider calls are optional, gated, and not included in the base requirements.

## Honest Limitation

This milestone does not claim AWS deployment, Bedrock usage, OpenAI usage, or production LLMOps. It adds tested adapter structure only.
