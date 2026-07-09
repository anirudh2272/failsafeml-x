from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ToolSafetyResult:
    allowed: bool
    severity: str
    risk_score: float
    blocked_categories: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


TOOL_RISK_PATTERNS: dict[str, list[str]] = {
    "destructive_filesystem": [
        r"\brm\s+-rf\b",
        r"\bdelete\b.{0,30}\b(all|everything|repository|database|logs)",
        r"\bwipe\b.{0,30}\b(files|disk|repository|database)",
    ],
    "database_destruction": [
        r"\bdrop\s+table\b",
        r"\btruncate\s+table\b",
        r"\bdelete\s+from\b.{0,40}\bwhere\s+1\s*=\s*1",
    ],
    "guardrail_bypass": [
        r"\bdisable\b.{0,40}\b(guardrail|safety|human review|validation)",
        r"\bauto[- ]?approve\b.{0,40}\b(all|everything|unsafe|high risk)",
        r"\bbypass\b.{0,40}\b(human review|safety|approval)",
    ],
    "secret_exfiltration": [
        r"\b(send|upload|post|exfiltrate|curl)\b.{0,80}\b(secret|token|api key|credential|password)",
        r"\bprintenv\b.{0,40}\b(send|upload|post|curl)",
    ],
    "unreviewed_external_action": [
        r"\b(send email|wire money|submit application|deploy to production)\b.{0,60}\bwithout\b.{0,30}\b(review|approval|confirmation)",
    ],
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def classify_tool_request(request_text: str) -> dict[str, Any]:
    """Classify whether a requested tool/action should be allowed automatically."""
    normalized = _normalize(request_text or "")
    blocked: list[str] = []

    for category, patterns in TOOL_RISK_PATTERNS.items():
        if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in patterns):
            blocked.append(category)

    risk_score = min(1.0, round(0.25 + 0.22 * len(blocked), 3)) if blocked else 0.0
    if len(blocked) >= 3:
        severity = "critical"
    elif len(blocked) == 2:
        severity = "high"
    elif len(blocked) == 1:
        severity = "medium"
    else:
        severity = "low"

    return ToolSafetyResult(
        allowed=not blocked,
        severity=severity,
        risk_score=risk_score,
        blocked_categories=blocked,
        recommendation=(
            "Do not execute automatically; require human review."
            if blocked
            else "Tool request did not match local high-risk action patterns."
        ),
    ).to_dict()
