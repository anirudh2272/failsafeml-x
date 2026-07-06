from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import matplotlib.pyplot as plt

from failsafemlx.serving.gateway import API_ENDPOINTS, score_demo_batch
from failsafemlx.reporting.milestone7 import write_m7_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow


def write_action_summary_plot(results: dict, path: Path) -> Path:
    counts = results["serving_demo_summary"]["router_action_counts"]
    labels = list(counts.keys())
    values = [counts[label] for label in labels]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8.5, 4.8))
    plt.bar(labels, values)
    plt.ylabel("Requests")
    plt.title("M7 API Demo Router Actions")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports/figures")
    batch = score_demo_batch(n=90, random_state=707)
    summary = batch["summary"]
    sample_responses = batch["responses"][:12]

    results = {
        "project": "FailSafeML-X",
        "milestone": "M7_API_DASHBOARD_AND_DEMO",
        "status": "completed",
        "honest_claim": "A local API/dashboard demo layer is implemented for reliability scoring, failure explanation, repair planning, and routing inspection. No production deployment claim yet.",
        "api_contract": API_ENDPOINTS,
        "serving_demo_summary": summary,
        "sample_responses": sample_responses,
        "m7_reliability_summary": {
            "api_contract_defined": True,
            "dashboard_artifact_defined": True,
            "demo_batch_scored": summary["num_requests"] > 0,
            "m7_limitation": "Local serving demo only; authentication, persistence, and production deployment are not included yet.",
        },
        "next_milestone": "M8_DOCKER_FINAL_DOCUMENTATION_AND_DEMO",
    }

    action_plot = write_action_summary_plot(results, ROOT / "reports/figures/m7_api_router_action_summary.png")
    results["artifacts"] = {
        "api_dashboard_results": "experiments/results/m7_api_dashboard_demo.json",
        "api_action_summary_plot": str(action_plot.relative_to(ROOT)),
        "streamlit_dashboard": "apps/streamlit_dashboard.py",
        "fastapi_app": "src/failsafemlx/serving/fastapi_app.py",
    }

    log_metrics_optional_mlflow(
        run_name="m7_api_dashboard_demo",
        metrics={
            "mean_trust_score": summary["mean_trust_score"],
            "auto_accept_rate": summary["auto_accept_rate"],
            "review_or_defer_rate": summary["review_or_defer_rate"],
        },
        params={"milestone": "M7", "layer": "api_dashboard_demo"},
    )

    metrics_path = write_json(results, ROOT / "experiments/results/m7_api_dashboard_demo.json")
    report_path = write_m7_report(results, ROOT / "reports/milestone_7_api_dashboard_demo.md")
    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {action_plot}")
    print(f"Wrote {ROOT / 'apps/streamlit_dashboard.py'}")
    print(f"Wrote {ROOT / 'src/failsafemlx/serving/fastapi_app.py'}")
    print("M7 completed successfully.")


if __name__ == "__main__":
    main()
