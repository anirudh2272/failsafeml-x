# FailSafeML-X AI Security Checklist

## Prompt Safety

- [x] Detect attempts to ignore system/developer instructions
- [x] Detect requests to reveal hidden prompts or private reasoning
- [x] Detect jailbreak-like wording
- [x] Route suspicious prompt content to human review

## Sensitive Data Safety

- [x] Detect secret-like strings such as API keys, bearer tokens, private keys, and password assignments
- [x] Redact previews before writing reports
- [x] Avoid storing full detected secrets in Markdown reports

## Tool Safety

- [x] Block destructive filesystem/database requests from automatic execution
- [x] Block guardrail-bypass requests
- [x] Block unreviewed external actions
- [x] Require human review for unsafe tool requests

## ML Decision Safety

- [x] Block automatic decisions when trust score is low
- [x] Block automatic decisions for high-risk failure IDs
- [x] Block unsafe requested actions such as auto-accepting high-risk decisions
- [x] Route unsafe cases to human review

## Scope Note

This checklist documents deterministic local project guardrails. It does not claim formal security certification or production compliance.
