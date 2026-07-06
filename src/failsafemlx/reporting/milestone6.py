from __future__ import annotations

from pathlib import Path

from failsafemlx.utils.io import ensure_dir


def _action_lines(action_counts: dict[str, int]) -> list[str]:
    return [f"- {action}: {count}" for action, count in action_counts.items()]


def write_m6_report(results: dict, path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    rule = results["router_evaluation"]["rule_based_router"]
    rl = results["router_evaluation"]["q_learning_router"]
    comparison = results["router_evaluation"]["comparison"]

    lines = [
        "# Milestone 6 — RL Repair Router",
        "",
        "## Objective",
        "",
        "Add a lightweight reinforcement-learning-style repair router that learns whether to auto-accept, abstain, route to human review, queue for active learning, or trigger retraining evaluation from reliability state signals.",
        "",
        "## Router Environment",
        "",
        f"- Environment type: {results['environment']['environment_type']}",
        f"- Number of evaluation states: {results['environment']['num_evaluation_states']}",
        f"- State representation: {results['environment']['state_representation']}",
        f"- Action space: {', '.join(results['environment']['action_space'])}",
        "",
        "## Rule-Based Router Baseline",
        "",
        f"- Expected reward: {rule['expected_reward']}",
        f"- Automation rate: {rule['automation_rate']}",
        f"- Expected unsafe auto-decision rate: {rule['expected_unsafe_auto_decision_rate']}",
        f"- Review/defer rate: {rule['review_or_defer_rate']}",
        "",
        "### Rule-Based Action Counts",
        *_action_lines(rule["action_counts"]),
        "",
        "## Q-Learning Router",
        "",
        f"- Expected reward: {rl['expected_reward']}",
        f"- Automation rate: {rl['automation_rate']}",
        f"- Expected unsafe auto-decision rate: {rl['expected_unsafe_auto_decision_rate']}",
        f"- Review/defer rate: {rl['review_or_defer_rate']}",
        f"- Learned Q states: {results['q_learning_config']['learned_q_states']}",
        "",
        "### Q-Learning Action Counts",
        *_action_lines(rl["action_counts"]),
        "",
        "## Policy Comparison",
        "",
        f"- Reward delta, RL minus rule: {comparison['reward_delta_rl_minus_rule']}",
        f"- Unsafe auto-rate delta, RL minus rule: {comparison['unsafe_auto_rate_delta_rl_minus_rule']}",
        f"- Automation-rate delta, RL minus rule: {comparison['automation_rate_delta_rl_minus_rule']}",
        f"- RL reward not worse than rule: {comparison['rl_reward_not_worse_than_rule']}",
        "",
        "## Generated Figures",
        "",
        f"- `{results['artifacts']['router_action_mix_plot']}`",
        f"- `{results['artifacts']['router_reward_comparison_plot']}`",
        "",
        "## Honest Limitation",
        "",
        "Milestone 6 uses a synthetic reliability-routing simulator and tabular Q-learning. It demonstrates the decision layer and cost-sensitive evaluation harness, but it is not yet trained on real production incident histories. A real deployment would require historical labels, safety review, and prospective validation.",
        "",
        "## Next Milestone",
        "",
        "Milestone 7 should expose the reliability system through an API and dashboard so predictions, trust scores, failure signals, repair actions, and router decisions can be inspected interactively.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
