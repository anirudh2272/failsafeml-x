from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

from failsafemlx.reliability.failure_taxonomy import FailureSignal, compute_trust_score
from failsafemlx.reliability.repair_engine import build_repair_plan
from failsafemlx.reliability.rl_router import RouterState, rule_based_router

API_ENDPOINTS = {
    "GET /health": "Liveness and project metadata.",
    "POST /reliability/score": "Return trust score, failures, repair plan, and router action for one prediction.",
    "POST /reliability/batch": "Return summary statistics for a batch of prediction reliability requests.",
}


@dataclass(frozen=True)
class ReliabilityRequest:
    request_id: str
    domain: str
    predicted_label: int
    probability: float
    conformal_set_size: float
    drift_score: float
    ood_score: float
    model_age_days: int
    recent_error_rate: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_demo_requests(n: int = 80, random_state: int = 42) -> list[ReliabilityRequest]:
    """Create deterministic synthetic API payloads for M7 demos and tests."""
    rng = np.random.default_rng(random_state)
    requests: list[ReliabilityRequest] = []
    for i in range(n):
        risk_mode = rng.choice(["low", "medium", "high"], p=[0.48, 0.34, 0.18])
        if risk_mode == "low":
            prob = float(rng.choice([rng.uniform(0.03, 0.22), rng.uniform(0.78, 0.97)]))
            drift = float(rng.uniform(0.0, 0.16))
            ood = float(rng.uniform(0.0, 0.30))
            set_size = float(rng.uniform(1.0, 1.08))
            age = int(rng.integers(1, 35))
            err = float(rng.uniform(0.02, 0.10))
        elif risk_mode == "medium":
            prob = float(rng.uniform(0.28, 0.72))
            drift = float(rng.uniform(0.12, 0.38))
            ood = float(rng.uniform(0.18, 0.58))
            set_size = float(rng.uniform(1.05, 1.55))
            age = int(rng.integers(30, 95))
            err = float(rng.uniform(0.08, 0.22))
        else:
            prob = float(rng.uniform(0.35, 0.68))
            drift = float(rng.uniform(0.32, 0.86))
            ood = float(rng.uniform(0.55, 0.96))
            set_size = float(rng.uniform(1.35, 2.0))
            age = int(rng.integers(75, 220))
            err = float(rng.uniform(0.18, 0.42))
        requests.append(
            ReliabilityRequest(
                request_id=f"demo-{i:04d}",
                domain="healthcare_risk" if i % 2 == 0 else "energy_forecast",
                predicted_label=int(prob >= 0.5),
                probability=round(prob, 4),
                conformal_set_size=round(set_size, 4),
                drift_score=round(drift, 4),
                ood_score=round(ood, 4),
                model_age_days=age,
                recent_error_rate=round(err, 4),
            )
        )
    return requests


def _request_failures(request: ReliabilityRequest) -> list[FailureSignal]:
    uncertainty = 1.0 - abs(request.probability - 0.5) * 2.0
    failures: list[FailureSignal] = []
    if request.drift_score >= 0.25:
        failures.append(
            FailureSignal(
                "F1_DATA_DRIFT",
                "high" if request.drift_score >= 0.50 else "medium",
                f"API drift_score={request.drift_score} crossed the serving threshold.",
                "Flag data pipeline drift and route affected requests away from full automation.",
            )
        )
    if uncertainty >= 0.62:
        failures.append(
            FailureSignal(
                "F3_LOW_CONFIDENCE_PREDICTION",
                "medium" if uncertainty >= 0.78 else "low",
                f"Probability={request.probability} gives uncertainty={round(uncertainty, 4)}.",
                "Use abstention or human review for low-margin decisions.",
            )
        )
    if request.ood_score >= 0.60:
        failures.append(
            FailureSignal(
                "F4_OUT_OF_DISTRIBUTION_INPUT",
                "high" if request.ood_score < 0.85 else "critical",
                f"API ood_score={request.ood_score} crossed the serving threshold.",
                "Block automatic action and collect review labels.",
            )
        )
    if request.conformal_set_size > 1.25:
        failures.append(
            FailureSignal(
                "F8_WIDE_PREDICTION_INTERVAL",
                "medium",
                f"Conformal set/interval size={request.conformal_set_size}.",
                "Expose uncertainty interval/set and avoid point-only automation.",
            )
        )
    if request.model_age_days >= 120 or request.recent_error_rate >= 0.24:
        failures.append(
            FailureSignal(
                "F9_MODEL_DECAY_OVER_TIME",
                "medium" if request.recent_error_rate < 0.32 else "high",
                f"Model age={request.model_age_days} days; recent_error_rate={request.recent_error_rate}.",
                "Schedule retraining evaluation and compare against a backup model.",
            )
        )
    major_conditions = sum(
        [
            request.drift_score >= 0.35,
            request.ood_score >= 0.60,
            request.conformal_set_size > 1.35,
            request.recent_error_rate >= 0.24,
        ]
    )
    if major_conditions >= 2:
        failures.append(
            FailureSignal(
                "F10_UNSAFE_AUTO_DECISION",
                "critical",
                f"{major_conditions} major serving reliability conditions are active.",
                "Disable automatic decisioning for this request and require review.",
            )
        )
    return failures


def score_reliability_request(payload: dict[str, Any] | ReliabilityRequest) -> dict[str, Any]:
    """Score one API-like request and return a full decision envelope."""
    request = payload if isinstance(payload, ReliabilityRequest) else ReliabilityRequest(**payload)
    failures = _request_failures(request)
    failure_profile = {
        "request_id": request.request_id,
        "failure_signals": [failure.to_dict() for failure in failures],
        **compute_trust_score(failures),
    }
    repair_plan = build_repair_plan(failure_profile)
    trust_score = failure_profile["trust_score"]
    uncertainty = 1.0 - abs(request.probability - 0.5) * 2.0
    unsafe_probability = float(
        np.clip(
            0.03
            + 0.006 * (100 - trust_score)
            + 0.35 * uncertainty
            + 0.22 * (request.drift_score >= 0.25)
            + 0.28 * (request.ood_score >= 0.60),
            0.0,
            0.99,
        )
    )
    state = RouterState(
        trust_score=trust_score,
        uncertainty=round(float(uncertainty), 4),
        drift_flag=bool(request.drift_score >= 0.25),
        ood_flag=bool(request.ood_score >= 0.60),
        failure_count=len(failures),
        unsafe_probability=round(unsafe_probability, 4),
    )
    router_action = rule_based_router(state)
    return {
        "request_id": request.request_id,
        "domain": request.domain,
        "prediction": {
            "predicted_label": request.predicted_label,
            "probability": request.probability,
        },
        "trust": failure_profile,
        "repair_plan": repair_plan,
        "router": {
            "router_type": "rule_based_serving_router",
            "state": state.to_dict(),
            "action": router_action,
            "auto_accept": router_action == "AUTO_ACCEPT",
        },
        "api_contract_version": "m7.v1",
    }


def summarize_batch_responses(responses: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize a batch of scored API responses for dashboard cards."""
    if not responses:
        return {
            "num_requests": 0,
            "mean_trust_score": 0.0,
            "auto_accept_rate": 0.0,
            "review_or_defer_rate": 0.0,
            "router_action_counts": {},
            "top_failure_ids": {},
        }
    action_counts = Counter(response["router"]["action"] for response in responses)
    failure_counts: Counter[str] = Counter()
    for response in responses:
        for failure in response["trust"]["failure_signals"]:
            failure_counts[failure["failure_id"]] += 1
    trust_values = np.array([response["trust"]["trust_score"] for response in responses], dtype=float)
    auto_rate = action_counts.get("AUTO_ACCEPT", 0) / len(responses)
    return {
        "num_requests": int(len(responses)),
        "mean_trust_score": round(float(np.mean(trust_values)), 4),
        "min_trust_score": round(float(np.min(trust_values)), 4),
        "max_trust_score": round(float(np.max(trust_values)), 4),
        "auto_accept_rate": round(float(auto_rate), 4),
        "review_or_defer_rate": round(float(1.0 - auto_rate), 4),
        "router_action_counts": dict(action_counts),
        "top_failure_ids": dict(failure_counts.most_common(6)),
    }


def score_demo_batch(n: int = 80, random_state: int = 42) -> dict[str, Any]:
    requests = make_demo_requests(n=n, random_state=random_state)
    responses = [score_reliability_request(request) for request in requests]
    return {
        "requests": [request.to_dict() for request in requests],
        "responses": responses,
        "summary": summarize_batch_responses(responses),
    }
