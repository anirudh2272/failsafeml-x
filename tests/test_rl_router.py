from failsafemlx.reliability.rl_router import (
    ACTIONS,
    RouterState,
    discretize_state,
    evaluate_router,
    learned_router,
    reward_for_action,
    rule_based_router,
    simulate_router_states,
    summarize_policy_comparison,
    train_q_router,
)


def test_discretize_state_returns_compact_tuple():
    state = RouterState(72.0, 0.44, True, False, 3, 0.31)
    discrete = discretize_state(state)
    assert isinstance(discrete, tuple)
    assert len(discrete) == 5
    assert all(isinstance(value, int) for value in discrete)


def test_rule_router_blocks_obvious_high_risk_state():
    state = RouterState(22.0, 0.91, True, True, 7, 0.88)
    assert rule_based_router(state) == "HUMAN_REVIEW"


def test_reward_penalizes_auto_accept_for_unsafe_state():
    risky = RouterState(30.0, 0.8, True, True, 6, 0.9)
    assert reward_for_action("AUTO_ACCEPT", risky) < reward_for_action("HUMAN_REVIEW", risky)


def test_q_router_trains_and_evaluates():
    train_states = simulate_router_states(n=150, random_state=1)
    eval_states = simulate_router_states(n=100, random_state=2)
    q_table = train_q_router(train_states, episodes=700, random_state=3)
    assert len(q_table) > 0
    metrics = evaluate_router(eval_states, learned_router(q_table))
    assert metrics["num_states"] == 100
    assert set(metrics["action_counts"].keys()) == set(ACTIONS)


def test_policy_comparison_fields_are_present():
    states = simulate_router_states(n=120, random_state=4)
    q_table = train_q_router(states, episodes=800, random_state=5)
    rule_metrics = evaluate_router(states, rule_based_router)
    rl_metrics = evaluate_router(states, learned_router(q_table))
    comparison = summarize_policy_comparison(rule_metrics, rl_metrics)
    assert "reward_delta_rl_minus_rule" in comparison
    assert "rl_reward_not_worse_than_rule" in comparison
