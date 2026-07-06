# Milestone 6 — RL Repair Router

## Objective

Add a lightweight reinforcement-learning-style repair router that learns whether to auto-accept, abstain, route to human review, queue for active learning, or trigger retraining evaluation from reliability state signals.

## Router Environment

- Environment type: synthetic_reliability_routing_simulator
- Number of evaluation states: 600
- State representation: trust_score_bin, uncertainty_bin, drift_flag, ood_flag, failure_count_bin
- Action space: AUTO_ACCEPT, ABSTAIN, HUMAN_REVIEW, ACTIVE_LEARNING, RETRAIN_EVAL

## Rule-Based Router Baseline

- Expected reward: -0.2008
- Automation rate: 0.0367
- Expected unsafe auto-decision rate: 0.0679
- Review/defer rate: 0.9633

### Rule-Based Action Counts
- AUTO_ACCEPT: 22
- ABSTAIN: 0
- HUMAN_REVIEW: 538
- ACTIVE_LEARNING: 25
- RETRAIN_EVAL: 15

## Q-Learning Router

- Expected reward: 0.1321
- Automation rate: 0.25
- Expected unsafe auto-decision rate: 0.1477
- Review/defer rate: 0.75
- Learned Q states: 287

### Q-Learning Action Counts
- AUTO_ACCEPT: 150
- ABSTAIN: 3
- HUMAN_REVIEW: 364
- ACTIVE_LEARNING: 9
- RETRAIN_EVAL: 74

## Policy Comparison

- Reward delta, RL minus rule: 0.3329
- Unsafe auto-rate delta, RL minus rule: 0.0798
- Automation-rate delta, RL minus rule: 0.2133
- RL reward not worse than rule: True

## Generated Figures

- `reports/figures/m6_router_action_mix.png`
- `reports/figures/m6_router_reward_comparison.png`

## Honest Limitation

Milestone 6 uses a synthetic reliability-routing simulator and tabular Q-learning. It demonstrates the decision layer and cost-sensitive evaluation harness, but it is not yet trained on real production incident histories. A real deployment would require historical labels, safety review, and prospective validation.

## Next Milestone

Milestone 7 should expose the reliability system through an API and dashboard so predictions, trust scores, failure signals, repair actions, and router decisions can be inspected interactively.
