from __future__ import annotations

from pathlib import Path

from failsafemlx.utils.io import ensure_dir


def _action_lines(plan: dict) -> list[str]:
    lines: list[str] = []
    for action in plan["repair_actions"]:
        lines.extend([
            f"- {action['repair_id']} — {action['name']} ({action['execution_mode']})",
            f"  - Priority: {action['priority']}",
            f"  - Trigger failures: {', '.join(action['trigger_failures'])}",
            f"  - Rationale: {action['rationale']}",
        ])
    if not lines:
        lines.append("- No repair actions were triggered.")
    return lines


def write_m5_report(results: dict, path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    hc = results["datasets"]["healthcare_classification"]
    en = results["datasets"]["energy_timeseries"]

    lines = [
        "# Milestone 5 — Repair Engine and Before/After Benchmark",
        "",
        "## Objective",
        "",
        "Turn M4 failure-taxonomy outputs into executable repair policies and measure before/after safety tradeoffs on labeled synthetic evaluation data.",
        "",
        "## Dataset A — Healthcare-Style Risk Classification",
        "",
        f"- Repair policy: {hc['repair_benchmark']['repair_policy']}",
        f"- Unsafe auto-decision rate before repair: {hc['repair_effect_summary']['unsafe_auto_decision_rate_before']}",
        f"- Unsafe auto-decision rate after repair: {hc['repair_effect_summary']['unsafe_auto_decision_rate_after']}",
        f"- Automation rate before repair: {hc['repair_effect_summary']['automation_rate_before']}",
        f"- Automation rate after repair: {hc['repair_effect_summary']['automation_rate_after']}",
        f"- Active-learning queue size: {hc['repair_benchmark']['active_learning_queue_size']}",
        "",
        "### Healthcare Repair Actions",
        *_action_lines(hc["repair_plan"]),
        "",
        "## Dataset B — Energy-Style Time-Series Regression",
        "",
        f"- Repair policy: {en['repair_benchmark']['repair_policy']}",
        f"- Unsafe auto-decision rate before repair: {en['repair_effect_summary']['unsafe_auto_decision_rate_before']}",
        f"- Unsafe auto-decision rate after repair: {en['repair_effect_summary']['unsafe_auto_decision_rate_after']}",
        f"- Automation rate before repair: {en['repair_effect_summary']['automation_rate_before']}",
        f"- Automation rate after repair: {en['repair_effect_summary']['automation_rate_after']}",
        f"- Active-learning queue size: {en['repair_benchmark']['active_learning_queue_size']}",
        "",
        "### Energy Repair Actions",
        *_action_lines(en["repair_plan"]),
        "",
        "## Generated Figures",
        "",
        f"- `{results['artifacts']['unsafe_rate_plot']}`",
        f"- `{results['artifacts']['automation_tradeoff_plot']}`",
        "",
        "## Honest Limitation",
        "",
        "Milestone 5 implements repair policies as engineering guardrails and evaluates them on labeled synthetic data. The repair engine reduces unsafe automation primarily through abstention, stricter thresholds, conformal guardrails, and human-review routing. It is not a production safety certification and it does not yet perform online retraining.",
        "",
        "## Next Milestone",
        "",
        "Milestone 6 should add an RL-style repair router that learns when to accept, abstain, defer, request review, or trigger retraining using a cost-sensitive reward function.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
