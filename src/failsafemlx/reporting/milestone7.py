from __future__ import annotations

from pathlib import Path

from failsafemlx.utils.io import ensure_dir


def _dict_lines(values: dict) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {key}: {value}" for key, value in values.items()]


def write_m7_report(results: dict, path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    summary = results["serving_demo_summary"]
    lines = [
        "# Milestone 7 — API, Dashboard, and Demo Layer",
        "",
        "## Objective",
        "",
        "Expose FailSafeML-X through a serving-oriented interface so model predictions can be inspected with trust scores, failure signals, repair plans, and router decisions.",
        "",
        "## API Contract",
        "",
        *[f"- `{endpoint}` — {description}" for endpoint, description in results["api_contract"].items()],
        "",
        "## Demo Batch Summary",
        "",
        f"- Number of scored requests: {summary['num_requests']}",
        f"- Mean trust score: {summary['mean_trust_score']}",
        f"- Min trust score: {summary['min_trust_score']}",
        f"- Max trust score: {summary['max_trust_score']}",
        f"- Auto-accept rate: {summary['auto_accept_rate']}",
        f"- Review/defer rate: {summary['review_or_defer_rate']}",
        "",
        "### Router Action Counts",
        *_dict_lines(summary["router_action_counts"]),
        "",
        "### Top Failure IDs",
        *_dict_lines(summary["top_failure_ids"]),
        "",
        "## Generated Artifacts",
        "",
        f"- `{results['artifacts']['api_dashboard_results']}`",
        f"- `{results['artifacts']['api_action_summary_plot']}`",
        f"- `{results['artifacts']['streamlit_dashboard']}`",
        f"- `{results['artifacts']['fastapi_app']}`",
        "",
        "## How to Run Locally",
        "",
        "```bash",
        "uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload",
        "streamlit run apps/streamlit_dashboard.py",
        "```",
        "",
        "## Honest Limitation",
        "",
        "Milestone 7 is a local demo serving layer. It exposes the reliability logic through API and dashboard artifacts, but it is not a production deployment, authentication system, or cloud release.",
        "",
        "## Next Milestone",
        "",
        "Milestone 8 should package the system for reproducible deployment with Docker, final documentation, and a complete demo script.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
