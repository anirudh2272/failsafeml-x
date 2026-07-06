from __future__ import annotations

from pathlib import Path

from failsafemlx.utils.io import ensure_dir


def write_m4_report(results: dict, path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    hc = results["datasets"]["healthcare_classification"]
    en = results["datasets"]["energy_timeseries"]

    lines = [
        "# Milestone 4 — Failure Taxonomy and Trust Score",
        "",
        "## Objective",
        "",
        "Convert M2 uncertainty/calibration signals and M3 drift/OOD signals into an explainable failure taxonomy, trust score, and deployment routing decision.",
        "",
        "## Dataset A — Healthcare-Style Risk Classification",
        "",
        f"- Model: {hc['model']}",
        f"- Trust score: {hc['trust_summary']['trust_score']}",
        f"- Risk level: {hc['trust_summary']['risk_level']}",
        f"- Routing decision: {hc['trust_summary']['routing_decision']}",
        f"- Number of active failure signals: {hc['trust_summary']['num_failures']}",
        "",
        "### Active Healthcare Failure Signals",
    ]
    for failure in hc["failure_signals"]:
        lines.extend([
            f"- {failure['failure_id']} — {failure['name']} ({failure['severity']})",
            f"  - Evidence: {failure['evidence']}",
            f"  - Recommended action: {failure['recommended_action']}",
        ])

    lines.extend([
        "",
        "## Dataset B — Energy-Style Time-Series Regression",
        "",
        f"- Model: {en['model']}",
        f"- Trust score: {en['trust_summary']['trust_score']}",
        f"- Risk level: {en['trust_summary']['risk_level']}",
        f"- Routing decision: {en['trust_summary']['routing_decision']}",
        f"- Number of active failure signals: {en['trust_summary']['num_failures']}",
        "",
        "### Active Energy Failure Signals",
    ])
    for failure in en["failure_signals"]:
        lines.extend([
            f"- {failure['failure_id']} — {failure['name']} ({failure['severity']})",
            f"  - Evidence: {failure['evidence']}",
            f"  - Recommended action: {failure['recommended_action']}",
        ])

    lines.extend([
        "",
        "## Generated Figures",
        "",
        f"- `{results['artifacts']['trust_score_plot']}`",
        f"- `{results['artifacts']['failure_count_plot']}`",
        "",
        "## Honest Limitation",
        "",
        "Milestone 4 explains failures and recommends routing decisions, but it still does not execute repairs. The trust score should be treated as a transparent engineering heuristic, not as a safety certification.",
        "",
        "## Next Milestone",
        "",
        "Milestone 5 should implement the repair engine: recalibration, abstention, threshold adjustment, backup-model switching, active-learning queue creation, and before/after reliability benchmarks.",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
