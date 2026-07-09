# Milestone 15D — Provider-Aware Agent Integration

## Objective

Connect the local deterministic reliability agent to the optional provider abstraction while keeping local/offline behavior as the default.

## Validation Summary

- Passed: True
- Cases evaluated: 3
- Providers used: local
- External provider blocked by default: True
- External API calls used: False
- Average trust score: 0.58

## Risk-Level Counts

- critical: 1
- high: 2

## Case Summaries

### m15d_safe_case

- Provider requested: local
- Provider used: local
- Used external API: False
- Risk level: high
- Recommended action: ACCEPT_WITH_MONITORING
- Recommended decision: accept
- Warning count: 0

### m15d_drift_case

- Provider requested: local
- Provider used: local
- Used external API: False
- Risk level: high
- Recommended action: R8_FLAG_DATA_PIPELINE_DRIFT
- Recommended decision: flag_drift
- Warning count: 0

### m15d_critical_case

- Provider requested: local
- Provider used: local
- Used external API: False
- Risk level: critical
- Recommended action: R4_ROUTE_TO_HUMAN_REVIEW
- Recommended decision: human_review
- Warning count: 0

### m15d_drift_case

- Provider requested: bedrock
- Provider used: local
- Used external API: False
- Risk level: high
- Recommended action: R8_FLAG_DATA_PIPELINE_DRIFT
- Recommended decision: flag_drift
- Warning count: 1

## Honest Limitation

M15D integrates provider-aware reliability explanations but does not call OpenAI, AWS Bedrock, or any paid provider during tests/local CI. External providers remain disabled by default and require explicit opt-in.

## Resume-Safe Claim

Integrated provider-aware reliability explanations with a local default provider and optional OpenAI-compatible/AWS Bedrock-style adapters disabled by default.
