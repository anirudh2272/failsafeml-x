from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import matplotlib.pyplot as plt

from failsafemlx.reliability.rl_router import (
    ACTIONS,
    evaluate_router,
    learned_router,
    rule_based_router,
    simulate_router_states,
    summarize_policy_comparison,
    train_q_router,
)
from failsafemlx.reporting.milestone6 import write_m6_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow


def write_action_mix_plot(results: dict, path: Path) -> Path:
    labels = list(ACTIONS)
    rule_counts = [results["router_evaluation"]["rule_based_router"]["action_counts"][action] for action in labels]
    rl_counts = [results["router_evaluation"]["q_learning_router"]["action_counts"][action] for action in labels]
    x = list(range(len(labels)))
    width = 0.35
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(9.5, 4.8))
    plt.bar([i - width / 2 for i in x], rule_counts, width=width, label="Rule baseline")
    plt.bar([i + width / 2 for i in x], rl_counts, width=width, label="Q-learning router")
    plt.xticks(x, labels, rotation=25, ha="right")
    plt.ylabel("Number of routed states")
    plt.title("M6 Router Action Mix")
    plt.legend()
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_reward_plot(results: dict, path: Path) -> Path:
    labels = ["Rule baseline", "Q-learning router"]
    values = [
        results["router_evaluation"]["rule_based_router"]["expected_reward"],
        results["router_evaluation"]["q_learning_router"]["expected_reward"],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6.8, 4.8))
    plt.bar(labels, values)
    plt.ylabel("Expected reward")
    plt.title("M6 Router Expected Reward Comparison")
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports/figures")

    train_states = simulate_router_states(n=1250, random_state=42)
    eval_states = simulate_router_states(n=600, random_state=314)
    q_table = train_q_router(train_states, episodes=9000, learning_rate=0.18, epsilon=0.22, random_state=42)
    q_router = learned_router(q_table)

    rule_metrics = evaluate_router(eval_states, rule_based_router)
    rl_metrics = evaluate_router(eval_states, q_router)
    comparison = summarize_policy_comparison(rule_metrics, rl_metrics)

    results = {
        "project": "FailSafeML-X",
        "milestone": "M6_RL_REPAIR_ROUTER",
        "status": "completed",
        "honest_claim": "A cost-sensitive tabular Q-learning repair router is implemented and benchmarked against a rule baseline in a synthetic reliability-routing simulator. No production RL deployment claim yet.",
        "environment": {
            "environment_type": "synthetic_reliability_routing_simulator",
            "num_training_states": len(train_states),
            "num_evaluation_states": len(eval_states),
            "state_representation": "trust_score_bin, uncertainty_bin, drift_flag, ood_flag, failure_count_bin",
            "action_space": list(ACTIONS),
        },
        "q_learning_config": {
            "episodes": 9000,
            "learning_rate": 0.18,
            "epsilon": 0.22,
            "learned_q_states": len(q_table),
        },
        "router_evaluation": {
            "rule_based_router": rule_metrics,
            "q_learning_router": rl_metrics,
            "comparison": comparison,
        },
        "m6_reliability_summary": {
            "rl_reward_not_worse_than_rule": comparison["rl_reward_not_worse_than_rule"],
            "m6_limitation": "The router is trained in a synthetic one-step simulator; real incident replay data is needed before claiming deployment validity.",
        },
        "next_milestone": "M7_API_DASHBOARD_AND_DEMO",
    }

    action_plot = write_action_mix_plot(results, ROOT / "reports/figures/m6_router_action_mix.png")
    reward_plot = write_reward_plot(results, ROOT / "reports/figures/m6_router_reward_comparison.png")
    results["artifacts"] = {
        "router_action_mix_plot": str(action_plot.relative_to(ROOT)),
        "router_reward_comparison_plot": str(reward_plot.relative_to(ROOT)),
    }

    log_metrics_optional_mlflow(
        run_name="m6_rl_repair_router",
        metrics={
            "rule_expected_reward": rule_metrics["expected_reward"],
            "rl_expected_reward": rl_metrics["expected_reward"],
            "reward_delta": comparison["reward_delta_rl_minus_rule"],
            "rl_unsafe_auto_rate": rl_metrics["expected_unsafe_auto_decision_rate"],
        },
        params={"milestone": "M6", "router": "tabular_q_learning"},
    )

    metrics_path = write_json(results, ROOT / "experiments/results/m6_rl_repair_router.json")
    report_path = write_m6_report(results, ROOT / "reports/milestone_6_rl_repair_router.md")
    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {action_plot}")
    print(f"Wrote {reward_plot}")
    print("M6 completed successfully.")


if __name__ == "__main__":
    main()
