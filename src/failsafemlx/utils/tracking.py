from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from failsafemlx.utils.io import ensure_dir


def log_metrics_optional_mlflow(run_name: str, metrics: dict[str, float], params: dict[str, Any] | None = None) -> None:
    """Log to MLflow if installed; otherwise write JSONL fallback.

    This avoids blocking Milestone 1 on MLflow installation issues, especially on
    systems running newer Python versions.
    """
    try:
        import mlflow  # type: ignore

        mlflow.set_experiment("failsafeml-x-m1")
        with mlflow.start_run(run_name=run_name):
            if params:
                mlflow.log_params(params)
            mlflow.log_metrics(metrics)
        return
    except Exception as exc:  # fallback is intentional
        fallback = Path("experiments/results/mlflow_fallback_runs.jsonl")
        ensure_dir(fallback.parent)
        payload = {
            "run_name": run_name,
            "params": params or {},
            "metrics": metrics,
            "note": f"MLflow unavailable or failed; fallback logging used. Error: {type(exc).__name__}: {exc}",
        }
        with fallback.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
