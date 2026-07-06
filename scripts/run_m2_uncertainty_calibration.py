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
from failsafemlx.reliability.calibration import calibration_bins, calibration_summary
from failsafemlx.reliability.conformal import (
    binary_conformal_prediction_sets,
    regression_conformal_interval,
    summarize_intervals,
    summarize_prediction_sets,
)
from failsafemlx.reporting.milestone2 import write_m2_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow


def run_healthcare_uncertainty(random_state: int = 42, alpha: float = 0.1) -> dict:
    X, y = make_healthcare_risk_dataset(n_samples=1600, random_state=random_state)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=random_state
    )
    X_cal, X_test, y_cal, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=random_state
    )

    model_name = "random_forest"
    model = build_healthcare_models(random_state=random_state)[model_name]
    model.fit(X_train, y_train)
    prob_cal = predict_positive_probability(model, X_cal)
    prob_test = predict_positive_probability(model, X_test)

    metrics = classification_metrics(y_test.to_numpy(), prob_test)
    cal_summary = calibration_summary(y_test.to_numpy(), prob_test)
    cal_bins = calibration_bins(y_test.to_numpy(), prob_test)
    pred_sets, qhat = binary_conformal_prediction_sets(
        y_cal.to_numpy(), prob_cal, prob_test, alpha=alpha
    )
    pred_set_summary = summarize_prediction_sets(y_test.to_numpy(), pred_sets)
    pred_set_summary.update({"qhat": round(float(qhat), 4), "alpha": alpha, "target_coverage": round(1 - alpha, 4)})

    log_metrics_optional_mlflow(
        run_name="m2_healthcare_uncertainty_random_forest",
        metrics={**metrics, **{f"calibration_{k}": v for k, v in cal_summary.items() if isinstance(v, (int, float))}, **{f"conformal_{k}": v for k, v in pred_set_summary.items() if isinstance(v, (int, float))}},
        params={"dataset": "synthetic_healthcare", "model": model_name, "alpha": alpha},
    )

    return {
        "dataset": "synthetic_healthcare_risk",
        "task": "binary_classification",
        "model": model_name,
        "num_train": int(len(X_train)),
        "num_calibration": int(len(X_cal)),
        "num_test": int(len(X_test)),
        "metrics": metrics,
        "calibration_summary": cal_summary,
        "calibration_bins": cal_bins,
        "conformal_prediction_sets": pred_set_summary,
    }


def run_energy_uncertainty(random_state: int = 42, alpha: float = 0.1) -> dict:
    df = make_energy_timeseries(n_points=1300, random_state=random_state)
    X, y = make_lag_features(df)
    n = len(X)
    train_end = int(n * 0.60)
    cal_end = int(n * 0.80)
    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_cal, y_cal = X.iloc[train_end:cal_end], y.iloc[train_end:cal_end]
    X_test, y_test = X.iloc[cal_end:], y.iloc[cal_end:]

    model_name = "gradient_boosting_regressor"
    model = build_timeseries_models(random_state=random_state)[model_name]
    model.fit(X_train, y_train)
    pred_cal = model.predict(X_cal)
    pred_test = model.predict(X_test)

    metrics = regression_metrics(y_test.to_numpy(), pred_test)
    lower, upper, qhat = regression_conformal_interval(
        y_cal.to_numpy(), pred_cal, pred_test, alpha=alpha
    )
    interval_summary = summarize_intervals(y_test.to_numpy(), lower, upper)
    interval_summary.update({"qhat": round(float(qhat), 4), "alpha": alpha, "target_coverage": round(1 - alpha, 4)})

    log_metrics_optional_mlflow(
        run_name="m2_energy_uncertainty_gradient_boosting",
        metrics={**metrics, **{f"conformal_{k}": v for k, v in interval_summary.items() if isinstance(v, (int, float))}},
        params={"dataset": "synthetic_energy_timeseries", "model": model_name, "alpha": alpha},
    )

    return {
        "dataset": "synthetic_energy_demand",
        "task": "time_series_regression",
        "model": model_name,
        "num_train": int(len(X_train)),
        "num_calibration": int(len(X_cal)),
        "num_test": int(len(X_test)),
        "metrics": metrics,
        "conformal_prediction_intervals": interval_summary,
        "plot_payload": {
            "y_test": y_test.to_numpy().tolist(),
            "pred_test": pred_test.tolist(),
            "lower": lower.tolist(),
            "upper": upper.tolist(),
        },
    }


def write_healthcare_calibration_plot(healthcare: dict, path: Path) -> Path:
    bins = [row for row in healthcare["calibration_bins"] if row["count"] > 0]
    x = [row["mean_probability"] for row in bins]
    y = [row["empirical_positive_rate"] for row in bins]
    sizes = [max(row["count"], 10) for row in bins]
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(6, 5))
    plt.plot([0, 1], [0, 1], linestyle="--", label="perfect calibration")
    plt.scatter(x, y, s=sizes, alpha=0.75, label="observed bins")
    plt.xlabel("Mean predicted positive probability")
    plt.ylabel("Empirical positive rate")
    plt.title("M2 Healthcare Calibration Reliability")
    plt.legend()
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_energy_interval_plot(energy: dict, path: Path, max_points: int = 160) -> Path:
    payload = energy.pop("plot_payload")
    y_test = np.asarray(payload["y_test"][:max_points], dtype=float)
    pred_test = np.asarray(payload["pred_test"][:max_points], dtype=float)
    lower = np.asarray(payload["lower"][:max_points], dtype=float)
    upper = np.asarray(payload["upper"][:max_points], dtype=float)
    t = np.arange(len(y_test))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(10, 5))
    plt.plot(t, y_test, label="actual")
    plt.plot(t, pred_test, label="prediction")
    plt.fill_between(t, lower, upper, alpha=0.2, label="90% conformal interval")
    plt.xlabel("Test time index")
    plt.ylabel("Synthetic demand")
    plt.title("M2 Energy Forecast Prediction Intervals")
    plt.legend()
    plt.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def main() -> None:
    ensure_dir(ROOT / "experiments/results")
    ensure_dir(ROOT / "reports/figures")

    healthcare = run_healthcare_uncertainty()
    energy = run_energy_uncertainty()

    calibration_plot = write_healthcare_calibration_plot(
        healthcare, ROOT / "reports/figures/m2_healthcare_calibration.png"
    )
    interval_plot = write_energy_interval_plot(
        energy, ROOT / "reports/figures/m2_energy_prediction_intervals.png"
    )

    results = {
        "project": "FailSafeML-X",
        "milestone": "M2_UNCERTAINTY_AND_CALIBRATION_ENGINE",
        "status": "completed",
        "honest_claim": "Uncertainty and calibration reporting are implemented. No self-healing repair policy or novelty claim yet.",
        "datasets": {
            "healthcare_classification": healthcare,
            "energy_timeseries": energy,
        },
        "artifacts": {
            "calibration_plot": str(calibration_plot.relative_to(ROOT)),
            "prediction_interval_plot": str(interval_plot.relative_to(ROOT)),
        },
        "m2_reliability_summary": {
            "classification_calibration_warning": healthcare["calibration_summary"]["calibration_warning"],
            "classification_conformal_target_met": bool(healthcare["conformal_prediction_sets"]["coverage"] >= healthcare["conformal_prediction_sets"]["target_coverage"] - 0.03),
            "regression_conformal_target_met": bool(energy["conformal_prediction_intervals"]["coverage"] >= energy["conformal_prediction_intervals"]["target_coverage"] - 0.03),
            "m2_limitation": "Reliability signals are measured, but repairs are not yet triggered.",
        },
        "next_milestone": "M3_DRIFT_AND_OOD_DETECTION",
    }

    metrics_path = write_json(results, ROOT / "experiments/results/m2_uncertainty_calibration.json")
    report_path = write_m2_report(results, ROOT / "reports/milestone_2_uncertainty_calibration.md")

    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {calibration_plot}")
    print(f"Wrote {interval_plot}")
    print("M2 completed successfully.")


if __name__ == "__main__":
    main()
