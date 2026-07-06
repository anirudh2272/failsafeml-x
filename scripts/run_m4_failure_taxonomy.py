from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import matplotlib.pyplot as plt

from failsafemlx.reliability.failure_taxonomy import build_failure_profile
from failsafemlx.reporting.milestone4 import write_m4_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow

from run_m2_uncertainty_calibration import run_energy_uncertainty, run_healthcare_uncertainty
from run_m3_drift_ood import run_energy_drift_ood, run_healthcare_drift_ood


def write_trust_score_plot(results: dict, path: Path) -> Path:
    datasets = ["healthcare_classification", "energy_timeseries"]
    labels = ["Healthcare", "Energy"]
    scores = [results["datasets"][key]["trust_summary"]["trust_score"] for key in datasets]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7, 4.5))
    plt.bar(labels, scores)
    plt.ylim(0, 100)
    plt.ylabel("Trust score (0-100)")
    plt.title("M4 Trust Scores After Reliability Signals")
    for i, score in enumerate(scores):
        plt.text(i, score + 2, str(score), ha="center")
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_failure_count_plot(results: dict, path: Path) -> Path:
    datasets = ["healthcare_classification", "energy_timeseries"]
    labels = ["Healthcare", "Energy"]
    counts = [results["datasets"][key]["trust_summary"]["num_failures"] for key in datasets]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7, 4.5))
    plt.bar(labels, counts)
    plt.ylabel("Active failure-signal count")
    plt.title("M4 Active Failure Signals")
    for i, count in enumerate(counts):
        plt.text(i, count + 0.1, str(count), ha="center")
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports/figures")

    m2_healthcare = run_healthcare_uncertainty()
    m2_energy = run_energy_uncertainty()
    m3_healthcare = run_healthcare_drift_ood()
    m3_energy = run_energy_drift_ood()

    healthcare_profile = build_failure_profile("healthcare_classification", m2_healthcare, m3_healthcare)
    energy_profile = build_failure_profile("energy_timeseries", m2_energy, m3_energy)

    results = {
        "project": "FailSafeML-X",
        "milestone": "M4_FAILURE_TAXONOMY_AND_TRUST_SCORE",
        "status": "completed",
        "honest_claim": "Failure taxonomy and trust-score routing are implemented. No automated repair execution or self-healing claim yet.",
        "datasets": {
            "healthcare_classification": healthcare_profile,
            "energy_timeseries": energy_profile,
        },
        "m4_reliability_summary": {
            "healthcare_routing_decision": healthcare_profile["trust_summary"]["routing_decision"],
            "energy_routing_decision": energy_profile["trust_summary"]["routing_decision"],
            "m4_limitation": "Signals are translated into taxonomy and routing recommendations, but repairs are not yet triggered.",
        },
        "next_milestone": "M5_REPAIR_ENGINE_AND_BEFORE_AFTER_BENCHMARK",
    }

    trust_plot = write_trust_score_plot(results, ROOT / "reports/figures/m4_trust_scores.png")
    count_plot = write_failure_count_plot(results, ROOT / "reports/figures/m4_failure_counts.png")
    results["artifacts"] = {
        "trust_score_plot": str(trust_plot.relative_to(ROOT)),
        "failure_count_plot": str(count_plot.relative_to(ROOT)),
    }

    log_metrics_optional_mlflow(
        run_name="m4_failure_taxonomy_trust_score",
        metrics={
            "healthcare_trust_score": healthcare_profile["trust_summary"]["trust_score"],
            "energy_trust_score": energy_profile["trust_summary"]["trust_score"],
            "healthcare_failure_count": healthcare_profile["trust_summary"]["num_failures"],
            "energy_failure_count": energy_profile["trust_summary"]["num_failures"],
        },
        params={"milestone": "M4", "policy": "heuristic_trust_score"},
    )

    metrics_path = write_json(results, ROOT / "experiments/results/m4_failure_taxonomy_trust_score.json")
    report_path = write_m4_report(results, ROOT / "reports/milestone_4_failure_taxonomy_trust_score.md")

    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {trust_plot}")
    print(f"Wrote {count_plot}")
    print("M4 completed successfully.")


if __name__ == "__main__":
    main()
