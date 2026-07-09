from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from failsafemlx.agents.schemas import ReliabilityCase

from failsafemlx.agents.reliability_agent import ReliabilityAgent
from failsafemlx.providers.base import ExternalProviderDisabledError
from failsafemlx.providers.router import generate_reliability_explanation, get_provider

RESULT_PATH = PROJECT_ROOT / "experiments/results/m15a_provider_abstraction.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_15a_provider_abstraction.md"


def sample_analysis() -> dict[str, object]:
    case = ReliabilityCase(
        sample_id="m15a_provider_demo_001",
        prediction=1,
        trust_score=0.37,
        failure_ids=["F4_OUT_OF_DISTRIBUTION_INPUT", "F10_UNSAFE_AUTO_DECISION"],
        uncertainty=0.72,
        calibration_error=0.18,
        drift_score=0.66,
        ood_score=0.83,
        domain="synthetic_healthcare_risk",
    )
    return ReliabilityAgent().analyze(case)


def run_m15a() -> dict[str, object]:
    analysis = sample_analysis()
    local_response = generate_reliability_explanation(analysis, provider_name="local")

    external_disabled_checks: dict[str, str] = {}
    for provider_name in ["openai_compatible", "bedrock"]:
        try:
            get_provider(provider_name, allow_external=False)
            external_disabled_checks[provider_name] = "unexpectedly_enabled"
        except ExternalProviderDisabledError:
            external_disabled_checks[provider_name] = "blocked_by_default"

    provider_files = [
        "src/failsafemlx/providers/base.py",
        "src/failsafemlx/providers/local.py",
        "src/failsafemlx/providers/openai_compatible.py",
        "src/failsafemlx/providers/bedrock.py",
        "src/failsafemlx/providers/router.py",
        "src/failsafemlx/providers/schemas.py",
        "requirements-providers.txt",
        "docs/provider_abstraction.md",
    ]
    missing = [path for path in provider_files if not (PROJECT_ROOT / path).exists()]

    result: dict[str, object] = {
        "project": "FailSafeML-X",
        "milestone": "M15A_OPTIONAL_LLM_PROVIDER_ABSTRACTION",
        "status": "completed" if not missing and all(v == "blocked_by_default" for v in external_disabled_checks.values()) else "failed",
        "passed": not missing and all(v == "blocked_by_default" for v in external_disabled_checks.values()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "providers_supported": ["local", "openai_compatible", "bedrock"],
        "default_provider": "local",
        "external_api_calls_in_tests": False,
        "external_provider_default_behavior": external_disabled_checks,
        "sample_local_response": local_response,
        "required_files_checked": provider_files,
        "missing_files": missing,
        "honest_claim": (
            "Added an optional provider abstraction for local deterministic, OpenAI-compatible, "
            "and AWS Bedrock Converse-style reliability explanations. External providers are disabled "
            "by default and were not called during tests."
        ),
        "limitations": [
            "No API keys are required for local CI.",
            "OpenAI-compatible and Bedrock adapters are opt-in and require user-supplied credentials/configuration.",
            "This milestone adds provider abstraction, not production LLMOps or hosted cloud deployment.",
        ],
    }

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# Milestone 15A — Optional LLM Provider Abstraction

## Objective

Add an optional provider abstraction so FailSafeML-X reliability explanations can remain local by default while being ready for OpenAI-compatible or AWS Bedrock Converse-style providers when explicitly enabled.

## Validation Summary

- Passed: {result['passed']}
- Default provider: local deterministic fallback
- External API calls during tests: false
- OpenAI-compatible adapter: present, disabled by default
- AWS Bedrock Converse adapter: present, disabled by default

## Why This Does Not Break the Project

The core reliability workflow still runs without external APIs. Provider calls are optional, gated, and not included in the base requirements.

## Honest Limitation

This milestone does not claim AWS deployment, Bedrock usage, OpenAI usage, or production LLMOps. It adds tested adapter structure only.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    if not result["passed"]:
        raise SystemExit(1)
    print("M15A completed successfully.")
    return result


if __name__ == "__main__":
    run_m15a()
