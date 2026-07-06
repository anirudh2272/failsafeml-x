from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Callable

import numpy as np

ACTIONS = (
    "AUTO_ACCEPT",
    "ABSTAIN",
    "HUMAN_REVIEW",
    "ACTIVE_LEARNING",
    "RETRAIN_EVAL",
)


@dataclass(frozen=True)
class RouterState:
    trust_score: float
    uncertainty: float
    drift_flag: bool
    ood_flag: bool
    failure_count: int
    unsafe_probability: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discretize_state(state: RouterState) -> tuple[int, int, int, int, int]:
    """Convert continuous reliability signals into a compact tabular RL state."""
    trust_bin = int(np.digitize([state.trust_score], [40, 60, 80])[0])
    uncertainty_bin = int(np.digitize([state.uncertainty], [0.25, 0.50, 0.75])[0])
    drift_bin = int(bool(state.drift_flag))
    ood_bin = int(bool(state.ood_flag))
    failure_bin = min(int(state.failure_count), 5)
    return (trust_bin, uncertainty_bin, drift_bin, ood_bin, failure_bin)


def simulate_router_states(n: int = 750, random_state: int = 42) -> list[RouterState]:
    """Build a deterministic synthetic reliability-routing simulator.

    The states are not real patient, finance, or production data. They provide a
    reproducible environment for comparing a learned repair router against a
    static rule baseline before using real historical incident labels.
    """
    rng = np.random.default_rng(random_state)
    states: list[RouterState] = []
    for _ in range(n):
        trust = float(np.clip(rng.normal(62, 22), 0, 100))
        uncertainty = float(np.clip(rng.beta(2.2, 3.0), 0, 1))
        drift = bool(rng.random() < (0.18 + 0.45 * uncertainty + (0.25 if trust < 45 else 0.0)))
        ood = bool(rng.random() < (0.10 + 0.35 * uncertainty + (0.20 if drift else 0.0)))
        failure_count = int(np.clip(rng.poisson(1.0 + 2.2 * uncertainty + 1.5 * drift + 1.2 * ood), 0, 8))
        logit = (
            -2.15
            + 0.045 * (60 - trust)
            + 1.85 * uncertainty
            + 0.95 * float(drift)
            + 1.10 * float(ood)
            + 0.22 * failure_count
        )
        unsafe_probability = float(1.0 / (1.0 + np.exp(-logit)))
        states.append(
            RouterState(
                trust_score=round(trust, 4),
                uncertainty=round(uncertainty, 4),
                drift_flag=drift,
                ood_flag=ood,
                failure_count=failure_count,
                unsafe_probability=round(unsafe_probability, 4),
            )
        )
    return states


def reward_for_action(action: str, state: RouterState) -> float:
    """Cost-sensitive reward for reliability routing.

    The reward prefers automation only when unsafe probability is low. Review,
    active learning, and retraining have costs, but they avoid the large penalty
    of unsafe automation.
    """
    p_unsafe = state.unsafe_probability
    if action == "AUTO_ACCEPT":
        return float((1.0 - p_unsafe) * 3.0 + p_unsafe * -12.0)
    if action == "HUMAN_REVIEW":
        # Review is safer but has operational cost; it is valuable for riskier cases.
        return float(-1.35 + 2.10 * p_unsafe)
    if action == "ABSTAIN":
        return float(-1.90 + 1.10 * p_unsafe)
    if action == "ACTIVE_LEARNING":
        return float(-1.65 + 1.70 * p_unsafe + 0.35 * state.uncertainty)
    if action == "RETRAIN_EVAL":
        drift_bonus = 0.85 if (state.drift_flag or state.ood_flag or state.failure_count >= 4) else -0.25
        return float(-2.35 + 2.25 * p_unsafe + drift_bonus)
    raise ValueError(f"Unknown router action: {action}")


def rule_based_router(state: RouterState) -> str:
    """Static baseline router derived from M4/M5 style guardrails."""
    if state.ood_flag or state.trust_score < 35 or state.failure_count >= 5:
        return "HUMAN_REVIEW"
    if state.drift_flag and state.uncertainty >= 0.55:
        return "RETRAIN_EVAL"
    if state.uncertainty >= 0.62:
        return "ACTIVE_LEARNING"
    if state.trust_score >= 78 and state.uncertainty <= 0.32 and not state.drift_flag:
        return "AUTO_ACCEPT"
    return "HUMAN_REVIEW"


QTable = dict[tuple[int, int, int, int, int], dict[str, float]]


def train_q_router(
    states: list[RouterState],
    *,
    episodes: int = 7000,
    learning_rate: float = 0.18,
    epsilon: float = 0.20,
    random_state: int = 42,
) -> QTable:
    """Train a one-step tabular Q router over synthetic reliability states."""
    rng = np.random.default_rng(random_state)
    q_table: QTable = defaultdict(lambda: {action: 0.0 for action in ACTIONS})
    if not states:
        return {}
    for _ in range(episodes):
        state = states[int(rng.integers(0, len(states)))]
        discrete = discretize_state(state)
        if rng.random() < epsilon:
            action = ACTIONS[int(rng.integers(0, len(ACTIONS)))]
        else:
            action = max(q_table[discrete], key=q_table[discrete].get)
        reward = reward_for_action(action, state)
        old_value = q_table[discrete][action]
        q_table[discrete][action] = old_value + learning_rate * (reward - old_value)
    return {state_key: dict(action_values) for state_key, action_values in q_table.items()}


def learned_router(q_table: QTable) -> Callable[[RouterState], str]:
    def route(state: RouterState) -> str:
        discrete = discretize_state(state)
        if discrete not in q_table:
            return rule_based_router(state)
        action_values = q_table[discrete]
        return max(action_values, key=action_values.get)

    return route


def evaluate_router(states: list[RouterState], router: Callable[[RouterState], str]) -> dict[str, Any]:
    if not states:
        return {
            "num_states": 0,
            "expected_reward": 0.0,
            "automation_rate": 0.0,
            "expected_unsafe_auto_decision_rate": 0.0,
            "review_or_defer_rate": 0.0,
            "action_counts": {},
        }
    actions = [router(state) for state in states]
    rewards = np.array([reward_for_action(action, state) for action, state in zip(actions, states)], dtype=float)
    auto_mask = np.array([action == "AUTO_ACCEPT" for action in actions], dtype=bool)
    unsafe_auto = np.array([state.unsafe_probability for state in states], dtype=float)[auto_mask]
    action_counts = dict(Counter(actions))
    return {
        "num_states": int(len(states)),
        "expected_reward": round(float(np.mean(rewards)), 4),
        "automation_rate": round(float(np.mean(auto_mask)), 4),
        "expected_unsafe_auto_decision_rate": round(float(np.mean(unsafe_auto)), 4) if unsafe_auto.size else 0.0,
        "review_or_defer_rate": round(float(np.mean(~auto_mask)), 4),
        "action_counts": {action: int(action_counts.get(action, 0)) for action in ACTIONS},
    }


def summarize_policy_comparison(rule_metrics: dict[str, Any], rl_metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "reward_delta_rl_minus_rule": round(float(rl_metrics["expected_reward"] - rule_metrics["expected_reward"]), 4),
        "unsafe_auto_rate_delta_rl_minus_rule": round(
            float(rl_metrics["expected_unsafe_auto_decision_rate"] - rule_metrics["expected_unsafe_auto_decision_rate"]), 4
        ),
        "automation_rate_delta_rl_minus_rule": round(float(rl_metrics["automation_rate"] - rule_metrics["automation_rate"]), 4),
        "rl_reward_not_worse_than_rule": bool(rl_metrics["expected_reward"] >= rule_metrics["expected_reward"]),
    }
