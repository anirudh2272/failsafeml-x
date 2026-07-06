from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np
from sklearn.model_selection import train_test_split

from failsafemlx.data.synthetic import make_energy_timeseries, make_healthcare_risk_dataset
from failsafemlx.evaluation.metrics import classification_metrics, initial_reliability_summary, regression_metrics
from failsafemlx.features.timeseries import make_lag_features
from failsafemlx.models.baselines import build_healthcare_models, build_timeseries_models, predict_positive_probability
from failsafemlx.reporting.milestone1 import write_m1_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow


def run_healthcare_classification(random_state: int = 42) -> dict:
    X, y = make_healthcare_risk_dataset(n_samples=1500, random_state=random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        stratify=y,
        random_state=random_state,
    )

    candidates = {}
    for name, model in build_healthcare_models(random_state=random_state).items():
        model.fit(X_train, y_train)
        y_prob = predict_positive_probability(model, X_test)
        metrics = classification_metrics(y_test.to_numpy(), y_prob)
        candidates[name] = {"model": model, "metrics": metrics}
        log_metrics_optional_mlflow(
            run_name=f"m1_healthcare_{name}",
            metrics=metrics,
            params={"dataset": "synthetic_healthcare", "model": name},
        )

    best_name = max(candidates, key=lambda n: candidates[n]["metrics"]["auroc"])
    best = candidates[best_name]
    return {
        "dataset": "synthetic_healthcare_risk",
        "task": "binary_classification",
        "best_model": best_name,
        "metrics": best["metrics"],
        "num_train": int(len(X_train)),
        "num_test": int(len(X_test)),
        "candidate_models": {name: val["metrics"] for name, val in candidates.items()},
    }


def run_energy_timeseries(random_state: int = 42) -> dict:
    df = make_energy_timeseries(n_points=1200, random_state=random_state)
    X, y = make_lag_features(df)

    split_idx = int(len(X) * 0.78)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    candidates = {}
    for name, model in build_timeseries_models(random_state=random_state).items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = regression_metrics(y_test.to_numpy(), y_pred)
        candidates[name] = {"model": model, "metrics": metrics}
        log_metrics_optional_mlflow(
            run_name=f"m1_energy_{name}",
            metrics=metrics,
            params={"dataset": "synthetic_energy_timeseries", "model": name},
        )

    best_name = min(candidates, key=lambda n: candidates[n]["metrics"]["rmse"])
    best = candidates[best_name]
    return {
        "dataset": "synthetic_energy_demand",
        "task": "time_series_regression",
        "best_model": best_name,
        "metrics": best["metrics"],
        "num_train": int(len(X_train)),
        "num_test": int(len(X_test)),
        "candidate_models": {name: val["metrics"] for name, val in candidates.items()},
    }


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports")

    healthcare = run_healthcare_classification()
    energy = run_energy_timeseries()

    results = {
        "project": "FailSafeML-X",
        "milestone": "M1_BASELINE_RELIABILITY",
        "status": "completed",
        "honest_claim": "Baseline multi-domain reliability benchmark is implemented. No self-healing or novelty claim yet.",
        "datasets": {
            "healthcare_classification": healthcare,
            "energy_timeseries": energy,
        },
        "initial_reliability_summary": initial_reliability_summary(healthcare, energy),
        "next_milestone": "M2_UNCERTAINTY_AND_CALIBRATION_ENGINE",
    }

    metrics_path = write_json(results, ROOT / "experiments/results/m1_baseline_metrics.json")
    report_path = write_m1_report(results, ROOT / "reports/milestone_1_baseline.md")

    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print("M1 completed successfully.")


if __name__ == "__main__":
    main()
