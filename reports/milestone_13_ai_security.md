# Milestone 13 — AI Security and Guardrail Tests

## Objective

Add deterministic AI security checks around FailSafeML-X so unsafe prompts, unsafe tool requests, secret-like content, and unsafe ML auto-decisions are blocked or routed to human review.

## What M13 Adds

- Prompt-injection pattern detection
- Secret-like string detection with redacted previews
- Unsafe tool/action request classification
- Reliability-aware auto-decision blocking
- Human-review routing for high-risk cases
- Local security checklist
- JSON and Markdown security validation outputs

## Validation Summary

- Passed: True
- Cases evaluated: 5
- Blocked or human-review cases: 4
- Auto-allowed low-risk cases: 1
- Required paths checked: 8

## Case Results

- `prompt_injection_attempt` → block_auto_decision (human_review, severity=medium)
- `secret_like_input` → block_auto_decision (human_review, severity=medium)
- `unsafe_tool_request` → block_auto_decision (human_review, severity=medium)
- `unsafe_ml_auto_decision` → block_auto_decision (human_review, severity=high)
- `safe_low_risk_decision` → allow_auto_decision (automated_decision_allowed, severity=low)

## Security Concepts Covered

M13 is inspired by common LLM/application security risk areas such as prompt injection, sensitive information disclosure, unsafe tool use, excessive agency, and unsafe output handling.

## Generated Outputs

- `experiments/results/m13_ai_security.json`
- `reports/milestone_13_ai_security.md`
- `security/ai_security_checklist.md`

## Honest Limitation

M13 provides deterministic local guardrail tests and documentation. It does not claim formal OWASP compliance, penetration testing, production security monitoring, or safety certification.
