from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split

from failsafemlx.data.synthetic import make_energy_timeseries, make_healthcare_risk_dataset
from failsafemlx.evaluation.metrics import classification_metrics, regression_metrics
from failsafemlx.features.timeseries import make_lag_features
from failsafemlx.models.baselines import build_healthcare_models, build_timeseries_models, predict_positive_probability
from failsafemlx.reliability.drift import feature_drift_report, prediction_drift_report, summarize_drift
from failsafemlx.reliability.ood import MahalanobisOODDetector
from failsafemlx.reporting.milestone3 import write_m3_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow


def make_shifted_healthcare_current(X):
    shifted = X.copy()
    shifted["age_like"] = shifted["age_like"] + 1.25
    shifted["glucose_like"] = shifted["glucose_like"] + 1.10
    shifted["bp_like"] = shifted["bp_like"] + 0.80
    shifted["activity_score"] = shifted["activity_score"] - 0.90
    shifted["lab_marker_1"] = shifted["lab_marker_1"] + 0.75
    return shifted


def run_healthcare_drift_ood(random_state: int = 42) -> dict:
    X, y = make_healthcare_risk_dataset(n_samples=1700, random_state=random_state)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=random_state
    )
    X_ref, X_current_base, y_ref, y_current = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=random_state
    )
    X_current = make_shifted_healthcare_current(X_current_base)

    model_name = "random_forest"
    model = build_healthcare_models(random_state=random_state)[model_name]
    model.fit(X_train, y_train)
    ref_prob = predict_positive_probability(model, X_ref)
    current_prob = predict_positive_probability(model, X_current)

    reference_metrics = classification_metrics(y_ref.to_numpy(), ref_prob)
    current_metrics = classification_metrics(y_current.to_numpy(), current_prob)
    feat_report = feature_drift_report(X_ref, X_current)
    pred_report = prediction_drift_report(ref_prob, current_prob)
    ood_detector = MahalanobisOODDetector(threshold_quantile=0.95).fit(X_train)
    ood_report = ood_detector.report(X_current)
    drift_summary = summarize_drift(feat_report, pred_report, ood_report)

    log_metrics_optional_mlflow(
        run_name="m3_healthcare_drift_ood_random_forest",
        metrics={
            "reference_accuracy": reference_metrics["accuracy"],
            "current_accuracy": current_metrics["accuracy"],
            "num_features_drifted": feat_report["num_features_drifted"],
            "prediction_psi": pred_report["psi"],
            "ood_rate": ood_report["ood_rate"],
        },
        params={"dataset": "synthetic_healthcare", "model": model_name},
    )

    return {
        "dataset": "synthetic_healthcare_risk",
        "task": "binary_classification",
        "model": model_name,
        "num_train": int(len(X_train)),
        "num_reference": int(len(X_ref)),
        "num_current_shifted": int(len(X_current)),
        "reference_metrics": reference_metrics,
        "current_shifted_metrics": current_metrics,
        "feature_drift_report": feat_report,
        "prediction_drift_report": pred_report,
        "ood_report": ood_report,
        "drift_summary": drift_summary,
    }


def make_shifted_energy_current(X):
    shifted = X.copy()
    if "temperature_proxy" in shifted.columns:
        shifted["temperature_proxy"] = shifted["temperature_proxy"] + 5.0
    for col in [c for c in shifted.columns if c.startswith("demand_lag_")][:3]:
        shifted[col] = shifted[col] + 7.5
    if "rolling_mean_24" in shifted.columns:
        shifted["rolling_mean_24"] = shifted["rolling_mean_24"] + 6.0
    return shifted


def run_energy_drift_ood(random_state: int = 42) -> dict:
    df = make_energy_timeseries(n_points=1350, random_state=random_state)
    X, y = make_lag_features(df)
    n = len(X)
    train_end = int(n * 0.60)
    ref_end = int(n * 0.80)
    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_ref, y_ref = X.iloc[train_end:ref_end], y.iloc[train_end:ref_end]
    X_current_base, y_current = X.iloc[ref_end:], y.iloc[ref_end:]
    X_current = make_shifted_energy_current(X_current_base)

    model_name = "gradient_boosting_regressor"
    model = build_timeseries_models(random_state=random_state)[model_name]
    model.fit(X_train, y_train)
    ref_pred = model.predict(X_ref)
    current_pred = model.predict(X_current)

    reference_metrics = regression_metrics(y_ref.to_numpy(), ref_pred)
    current_metrics = regression_metrics(y_current.to_numpy(), current_pred)
    feat_report = feature_drift_report(X_ref, X_current)
    pred_report = prediction_drift_report(ref_pred, current_pred)
    ood_detector = MahalanobisOODDetector(threshold_quantile=0.95).fit(X_train)
    ood_report = ood_detector.report(X_current)
    drift_summary = summarize_drift(feat_report, pred_report, ood_report)

    log_metrics_optional_mlflow(
        run_name="m3_energy_drift_ood_gradient_boosting",
        metrics={
            "reference_mae": reference_metrics["mae"],
            "current_mae": current_metrics["mae"],
            "num_features_drifted": feat_report["num_features_drifted"],
            "prediction_psi": pred_report["psi"],
            "ood_rate": ood_report["ood_rate"],
        },
        params={"dataset": "synthetic_energy_timeseries", "model": model_name},
    )

    return {
        "dataset": "synthetic_energy_demand",
        "task": "time_series_regression",
        "model": model_name,
        "num_train": int(len(X_train)),
        "num_reference": int(len(X_ref)),
        "num_current_shifted": int(len(X_current)),
        "reference_metrics": reference_metrics,
        "current_shifted_metrics": current_metrics,
        "feature_drift_report": feat_report,
        "prediction_drift_report": pred_report,
        "ood_report": ood_report,
        "drift_summary": drift_summary,
    }


def write_drift_bar_plot(dataset_result: dict, path: Path, title: str) -> Path:
    details = dataset_result["feature_drift_report"]["feature_details"][:8]
    names = [row["feature"] for row in details]
    psi_values = [row["psi"] for row in details]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(10, 5))
    plt.bar(range(len(names)), psi_values)
    plt.xticks(range(len(names)), names, rotation=35, ha="right")
    plt.ylabel("Population Stability Index")
    plt.title(title)
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports/figures")

    healthcare = run_healthcare_drift_ood()
    energy = run_energy_drift_ood()

    healthcare_plot = write_drift_bar_plot(
        healthcare,
        ROOT / "reports/figures/m3_healthcare_feature_drift.png",
        "M3 Healthcare Feature Drift",
    )
    energy_plot = write_drift_bar_plot(
        energy,
        ROOT / "reports/figures/m3_energy_feature_drift.png",
        "M3 Energy Feature Drift",
    )

    results = {
        "project": "FailSafeML-X",
        "milestone": "M3_DRIFT_AND_OOD_DETECTION",
        "status": "completed",
        "honest_claim": "Drift and out-of-distribution detection are implemented. No automated repair policy or self-healing claim yet.",
        "datasets": {
            "healthcare_classification": healthcare,
            "energy_timeseries": energy,
        },
        "artifacts": {
            "healthcare_drift_plot": str(healthcare_plot.relative_to(ROOT)),
            "energy_drift_plot": str(energy_plot.relative_to(ROOT)),
        },
        "m3_reliability_summary": {
            "healthcare_risk_level": healthcare["drift_summary"]["risk_level"],
            "energy_risk_level": energy["drift_summary"]["risk_level"],
            "m3_limitation": "Drift/OOD signals are measured, but repairs are not yet triggered.",
        },
        "next_milestone": "M4_FAILURE_TAXONOMY_AND_TRUST_SCORE",
    }

    metrics_path = write_json(results, ROOT / "experiments/results/m3_drift_ood.json")
    report_path = write_m3_report(results, ROOT / "reports/milestone_3_drift_ood.md")

    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {healthcare_plot}")
    print(f"Wrote {energy_plot}")
    print("M3 completed successfully.")


if __name__ == "__main__":
    main()
