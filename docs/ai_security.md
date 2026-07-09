# AI Security Guardrails

Milestone 13 adds deterministic local security checks to FailSafeML-X. The goal is to make the reliability layer safer when it is used with agentic workflows, tool calls, human-review notes, or future LLM integrations.

## Checks Added

- Prompt-injection pattern detection
- Secret-like string detection with redacted previews
- Unsafe tool/action request classification
- Reliability-aware auto-decision blocking
- Human-review routing for risky cases

## Why This Matters

FailSafeML-X already evaluates ML reliability risk through calibration, uncertainty, drift, OOD, trust score, failure taxonomy, repair actions, and routing. M13 adds an additional safety gate so that the system does not blindly execute unsafe instructions or expose sensitive-looking content.

## Local-Only Scope

The M13 guardrails are deterministic Python checks. They do not call external LLM APIs, security scanners, cloud services, or production monitoring systems.

## Honest Limitation

This milestone is a project-level AI security validation layer. It is not a formal penetration test, OWASP certification, SOC2 control, or production security deployment.
