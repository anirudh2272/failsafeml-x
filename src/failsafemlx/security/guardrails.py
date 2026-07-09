from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .prompt_injection import detect_prompt_injection
from .tool_safety import classify_tool_request


SECRET_PATTERNS: dict[str, str] = {
    "openai_like_key": r"\bsk-[A-Za-z0-9_-]{16,}\b",
    "aws_access_key_id": r"\bAKIA[0-9A-Z]{16}\b",
    "bearer_token": r"\bbearer\s+[A-Za-z0-9._~+/-]{20,}\b",
    "private_key_block": r"-----BEGIN\s+(RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY-----",
    "password_assignment": r"\b(password|passwd|pwd)\s*[:=]\s*[^\s]{6,}",
    "api_key_assignment": r"\b(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[^\s]{8,}",
}

HIGH_RISK_FAILURE_IDS = {
    "F1_DATA_DRIFT",
    "F4_OUT_OF_DISTRIBUTION_INPUT",
    "F7_CALIBRATION_FAILURE",
    "F9_MODEL_DECAY_OVER_TIME",
    "F10_UNSAFE_AUTO_DECISION",
}


@dataclass(frozen=True)
class SecretScanResult:
    detected: bool
    matched_types: list[str]
    redacted_preview: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GuardrailDecision:
    decision: str
    allowed_auto_decision: bool
    severity: str
    reasons: list[str]
    recommended_route: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_secret_like_strings(text: str) -> dict[str, Any]:
    """Detect secret-like strings without storing or printing full secrets."""
    raw_text = text or ""
    matched = [
        name
        for name, pattern in SECRET_PATTERNS.items()
        if re.search(pattern, raw_text, flags=re.IGNORECASE)
    ]

    redacted = raw_text
    for pattern in SECRET_PATTERNS.values():
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted, flags=re.IGNORECASE)
    if len(redacted) > 160:
        redacted = redacted[:157] + "..."

    return SecretScanResult(
        detected=bool(matched),
        matched_types=matched,
        redacted_preview=redacted,
        recommendation=(
            "Remove or rotate the secret and do not include it in prompts, logs, reports, or tool calls."
            if matched
            else "No secret-like string detected by local patterns."
        ),
    ).to_dict()


def _severity_from_reason_count(count: int) -> str:
    if count >= 4:
        return "critical"
    if count >= 2:
        return "high"
    if count == 1:
        return "medium"
    return "low"


def should_block_auto_decision(envelope: dict[str, Any]) -> dict[str, Any]:
    """Decide whether a model decision should be blocked from automatic execution."""
    reasons: list[str] = []
    trust_score = float(envelope.get("trust_score", 1.0))
    failure_ids = set(envelope.get("failure_ids", []) or [])
    requested_action = str(envelope.get("requested_action", "auto_decision"))

    if trust_score < 0.50:
        reasons.append("trust_score_below_0.50")
    elif trust_score < 0.70:
        reasons.append("trust_score_below_0.70")

    high_risk_failures = sorted(failure_ids.intersection(HIGH_RISK_FAILURE_IDS))
    if high_risk_failures:
        reasons.append("high_risk_failure_ids:" + ",".join(high_risk_failures))

    if requested_action.lower() in {"auto_accept", "auto_approve", "execute_without_review"}:
        reasons.append("unsafe_requested_action")

    if bool(envelope.get("contains_secret", False)):
        reasons.append("secret_like_content_present")

    if bool(envelope.get("prompt_injection_detected", False)):
        reasons.append("prompt_injection_detected")

    blocked = bool(reasons)
    return GuardrailDecision(
        decision="block_auto_decision" if blocked else "allow_auto_decision",
        allowed_auto_decision=not blocked,
        severity=_severity_from_reason_count(len(reasons)),
        reasons=reasons,
        recommended_route="human_review" if blocked else "automated_decision_allowed",
    ).to_dict()


def route_with_guardrails(
    reliability_envelope: dict[str, Any],
    user_request: str = "",
    tool_request: str = "",
) -> dict[str, Any]:
    """Combine ML reliability signals with text/tool security checks."""
    injection = detect_prompt_injection(user_request)
    tool_safety = classify_tool_request(tool_request)
    secret_scan = detect_secret_like_strings("\n".join([user_request or "", tool_request or ""]))

    enriched = dict(reliability_envelope)
    enriched["prompt_injection_detected"] = injection["detected"]
    enriched["contains_secret"] = secret_scan["detected"]
    if not tool_safety["allowed"]:
        enriched["requested_action"] = "execute_without_review"

    decision = should_block_auto_decision(enriched)

    return {
        "guardrail_version": "m13_local_security_guardrails_v1",
        "decision": decision,
        "prompt_injection": injection,
        "tool_safety": tool_safety,
        "secret_scan": secret_scan,
        "scope_note": "Deterministic local guardrails for project validation; not a formal security certification.",
    }


def evaluate_security_case(case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one complete M13 security scenario."""
    return route_with_guardrails(
        reliability_envelope=case.get("reliability_envelope", {}),
        user_request=case.get("user_request", ""),
        tool_request=case.get("tool_request", ""),
    )
