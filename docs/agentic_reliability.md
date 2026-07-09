# Agentic Reliability Layer

Milestone 10 adds a deterministic local reliability agent for FailSafeML-X.

## Purpose

The agent explains reliability failures and converts raw reliability signals into structured review outputs:

- failure ID explanations
- trust-score summaries
- drift/OOD risk summaries
- repair-action recommendations
- human-review notes

## Why deterministic fallback

The default path does not call external LLM APIs and does not require API keys. This keeps tests reproducible and lightweight.

## Optional LangGraph/LangChain readiness

The code detects whether LangGraph and LangChain are installed and exposes an adapter-ready mode flag. The current milestone does not require those packages and does not claim production agent deployment.

## Run

```bash
python scripts/run_m10_agentic_reliability.py
```

## Outputs

- `experiments/results/m10_agentic_reliability.json`
- `reports/milestone_10_agentic_reliability.md`

## Limitation

This is a structured local agent layer, not a live LLM service. It supports reliability explanation and review workflows but does not certify production safety.
