from __future__ import annotations

from pathlib import Path

from failsafemlx.utils.io import ensure_dir


def _fmt_bool(value: bool) -> str:
    return "True" if bool(value) else "False"


def write_m3_report(results: dict, path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)

    hc = results["datasets"]["healthcare_classification"]
    en = results["datasets"]["energy_timeseries"]
    lines = [
        "# Milestone 3 — Drift and Out-of-Distribution Detection",
        "",
        "## Objective",
        "",
        "Add reliability monitoring that detects when current inference inputs or predictions no longer resemble the reference training/evaluation distribution.",
        "",
        "## Dataset A — Healthcare-Style Risk Classification",
        "",
        f"- Model: {hc['model']}",
        f"- Reference accuracy: {hc['reference_metrics']['accuracy']}",
        f"- Current shifted accuracy: {hc['current_shifted_metrics']['accuracy']}",
        f"- Feature drift detected: {_fmt_bool(hc['drift_summary']['feature_drift_detected'])}",
        f"- Prediction drift detected: {_fmt_bool(hc['drift_summary']['prediction_drift_detected'])}",
        f"- OOD warning: {_fmt_bool(hc['drift_summary']['ood_warning'])}",
        f"- Risk level: {hc['drift_summary']['risk_level']}",
        "",
        "### Top Healthcare Drifted Features",
    ]
    for row in hc["feature_drift_report"]["top_drifted_features"][:5]:
        lines.append(
            f"- {row['feature']}: PSI={row['psi']}, KS={row['ks_statistic']}, p={row['ks_p_value']}"
        )

    lines.extend([
        "",
        "## Dataset B — Energy-Style Time-Series Regression",
        "",
        f"- Model: {en['model']}",
        f"- Reference MAE: {en['reference_metrics']['mae']}",
        f"- Current shifted MAE: {en['current_shifted_metrics']['mae']}",
        f"- Feature drift detected: {_fmt_bool(en['drift_summary']['feature_drift_detected'])}",
        f"- Prediction drift detected: {_fmt_bool(en['drift_summary']['prediction_drift_detected'])}",
        f"- OOD warning: {_fmt_bool(en['drift_summary']['ood_warning'])}",
        f"- Risk level: {en['drift_summary']['risk_level']}",
        "",
        "### Top Energy Drifted Features",
    ])
    for row in en["feature_drift_report"]["top_drifted_features"][:5]:
        lines.append(
            f"- {row['feature']}: PSI={row['psi']}, KS={row['ks_statistic']}, p={row['ks_p_value']}"
        )

    lines.extend([
        "",
        "## Generated Figures",
        "",
        f"- `{results['artifacts']['healthcare_drift_plot']}`",
        f"- `{results['artifacts']['energy_drift_plot']}`",
        "",
        "## Honest Limitation",
        "",
        "Milestone 3 detects drift and OOD conditions, but it still does not automatically repair the model or change deployment decisions. Those actions begin in Milestone 4 and Milestone 5.",
        "",
        "## Next Milestone",
        "",
        "Milestone 4 should convert reliability signals into a failure taxonomy and trust score so the system can explain why a prediction should be trusted, deferred, or escalated.",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
