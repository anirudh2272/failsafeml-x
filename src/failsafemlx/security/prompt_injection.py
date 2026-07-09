from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PromptInjectionResult:
    detected: bool
    severity: str
    risk_score: float
    matched_patterns: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


INJECTION_PATTERNS: dict[str, str] = {
    "ignore_previous_instructions": r"\b(ignore|disregard|forget)\b.{0,40}\b(previous|above|prior|system|developer)\b.{0,30}\binstruction",
    "system_prompt_exfiltration": r"\b(reveal|show|print|dump|expose)\b.{0,50}\b(system prompt|developer message|hidden instruction|policy)",
    "secret_exfiltration": r"\b(show|print|export|send|exfiltrate|leak)\b.{0,50}\b(secret|api key|token|credential|password)",
    "jailbreak_roleplay": r"\b(DAN|developer mode|jailbreak|unrestricted|no rules|bypass safety)\b",
    "tool_override": r"\b(call|invoke|run|execute)\b.{0,40}\btool\b.{0,60}\bwithout\b.{0,20}\b(permission|approval|validation)",
    "chain_of_thought_exfiltration": r"\b(show|reveal|print|dump)\b.{0,40}\b(chain of thought|private reasoning|scratchpad)",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_prompt_injection(text: str) -> dict[str, Any]:
    """Detect prompt-injection-like text using deterministic pattern checks.

    This is intentionally lightweight and local. It is not a replacement for a
    full red-team evaluation, but it gives the reliability agent a predictable
    first-pass guardrail for suspicious instructions.
    """
    normalized = _normalize(text or "")
    matched = [
        name
        for name, pattern in INJECTION_PATTERNS.items()
        if re.search(pattern, normalized, flags=re.IGNORECASE)
    ]

    risk_score = min(1.0, round(0.2 + 0.18 * len(matched), 3)) if matched else 0.0
    if len(matched) >= 3:
        severity = "critical"
    elif len(matched) == 2:
        severity = "high"
    elif len(matched) == 1:
        severity = "medium"
    else:
        severity = "low"

    recommendation = (
        "Block automated execution and route to human review."
        if matched
        else "No prompt-injection indicator detected by local patterns."
    )

    return PromptInjectionResult(
        detected=bool(matched),
        severity=severity,
        risk_score=risk_score,
        matched_patterns=matched,
        recommendation=recommendation,
    ).to_dict()
