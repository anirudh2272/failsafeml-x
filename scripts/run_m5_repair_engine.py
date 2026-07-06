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
from sklearn.model_selection import train_test_split

from failsafemlx.data.synthetic import make_energy_timeseries, make_healthcare_risk_dataset
from failsafemlx.features.timeseries import make_lag_features
from failsafemlx.models.baselines import build_healthcare_models, build_timeseries_models, predict_positive_probability
from failsafemlx.reliability.failure_taxonomy import build_failure_profile
from failsafemlx.reliability.repair_engine import (
    build_repair_plan,
    classification_repair_benchmark,
    regression_repair_benchmark,
    summarize_repair_effect,
)
from failsafemlx.reporting.milestone5 import write_m5_report
from failsafemlx.utils.io import ensure_dir, write_json
from failsafemlx.utils.tracking import log_metrics_optional_mlflow

from run_m2_uncertainty_calibration import run_energy_uncertainty, run_healthcare_uncertainty
from run_m3_drift_ood import (
    make_shifted_energy_current,
    make_shifted_healthcare_current,
    run_energy_drift_ood,
    run_healthcare_drift_ood,
)


def healthcare_current_predictions(random_state: int = 42):
    X, y = make_healthcare_risk_dataset(n_samples=1700, random_state=random_state)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.40, stratify=y, random_state=random_state
    )
    _, X_current_base, _, y_current = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=random_state
    )
    X_current = make_shifted_healthcare_current(X_current_base)
    model = build_healthcare_models(random_state=random_state)["random_forest"]
    model.fit(X_train, y_train)
    y_prob = predict_positive_probability(model, X_current)
    return y_current.to_numpy(), y_prob


def energy_current_predictions(random_state: int = 42):
    df = make_energy_timeseries(n_points=1350, random_state=random_state)
    X, y = make_lag_features(df)
    n = len(X)
    train_end = int(n * 0.60)
    ref_end = int(n * 0.80)
    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_current_base, y_current = X.iloc[ref_end:], y.iloc[ref_end:]
    X_current = make_shifted_energy_current(X_current_base)
    model = build_timeseries_models(random_state=random_state)["gradient_boosting_regressor"]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_current)
    return y_current.to_numpy(), y_pred


def write_before_after_plot(results: dict, path: Path, metric_key: str, title: str, ylabel: str) -> Path:
    datasets = ["healthcare_classification", "energy_timeseries"]
    labels = ["Healthcare", "Energy"]
    before = [results["datasets"][key]["repair_effect_summary"][f"{metric_key}_before"] for key in datasets]
    after = [results["datasets"][key]["repair_effect_summary"][f"{metric_key}_after"] for key in datasets]
    x = list(range(len(labels)))
    width = 0.35
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8, 4.8))
    plt.bar([i - width / 2 for i in x], before, width=width, label="Before repair")
    plt.bar([i + width / 2 for i in x], after, width=width, label="After repair")
    plt.xticks(x, labels)
    plt.ylim(0, 1.05)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
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

    hc_y, hc_prob = healthcare_current_predictions()
    en_y, en_pred = energy_current_predictions()

    hc_benchmark = classification_repair_benchmark(hc_y, hc_prob)
    en_benchmark = regression_repair_benchmark(
        en_y,
        en_pred,
        qhat=m2_energy["conformal_prediction_intervals"]["qhat"],
        critical_drift=bool(m3_energy["drift_summary"]["feature_drift_detected"] or m3_energy["drift_summary"]["ood_warning"]),
    )

    results = {
        "project": "FailSafeML-X",
        "milestone": "M5_REPAIR_ENGINE_AND_BEFORE_AFTER_BENCHMARK",
        "status": "completed",
        "honest_claim": "Repair-policy execution and before/after safety benchmarking are implemented on synthetic labeled evaluation data. No online retraining or production safety claim yet.",
        "datasets": {
            "healthcare_classification": {
                "dataset": healthcare_profile["dataset"],
                "task": healthcare_profile["task"],
                "repair_plan": build_repair_plan(healthcare_profile),
                "repair_benchmark": hc_benchmark,
                "repair_effect_summary": summarize_repair_effect(hc_benchmark),
            },
            "energy_timeseries": {
                "dataset": energy_profile["dataset"],
                "task": energy_profile["task"],
                "repair_plan": build_repair_plan(energy_profile),
                "repair_benchmark": en_benchmark,
                "repair_effect_summary": summarize_repair_effect(en_benchmark),
            },
        },
        "m5_reliability_summary": {
            "healthcare_unsafe_rate_reduced": True,
            "energy_unsafe_rate_reduced": True,
            "m5_limitation": "Repair policies reduce unsafe automation mostly by abstaining and routing cases to review; online retraining is scheduled but not executed yet.",
        },
        "next_milestone": "M6_RL_REPAIR_ROUTER",
    }

    # Compute booleans from generated summaries instead of assuming success.
    results["m5_reliability_summary"]["healthcare_unsafe_rate_reduced"] = (
        results["datasets"]["healthcare_classification"]["repair_effect_summary"]["unsafe_auto_decision_rate_after"]
        <= results["datasets"]["healthcare_classification"]["repair_effect_summary"]["unsafe_auto_decision_rate_before"]
    )
    results["m5_reliability_summary"]["energy_unsafe_rate_reduced"] = (
        results["datasets"]["energy_timeseries"]["repair_effect_summary"]["unsafe_auto_decision_rate_after"]
        <= results["datasets"]["energy_timeseries"]["repair_effect_summary"]["unsafe_auto_decision_rate_before"]
    )

    unsafe_plot = write_before_after_plot(
        results,
        ROOT / "reports/figures/m5_unsafe_auto_decision_rate.png",
        "unsafe_auto_decision_rate",
        "M5 Unsafe Auto-Decision Rate Before vs After Repair",
        "Unsafe auto-decision rate",
    )
    automation_plot = write_before_after_plot(
        results,
        ROOT / "reports/figures/m5_automation_tradeoff.png",
        "automation_rate",
        "M5 Automation Tradeoff Before vs After Repair",
        "Automation rate",
    )
    results["artifacts"] = {
        "unsafe_rate_plot": str(unsafe_plot.relative_to(ROOT)),
        "automation_tradeoff_plot": str(automation_plot.relative_to(ROOT)),
    }

    log_metrics_optional_mlflow(
        run_name="m5_repair_engine_before_after",
        metrics={
            "healthcare_unsafe_before": results["datasets"]["healthcare_classification"]["repair_effect_summary"]["unsafe_auto_decision_rate_before"],
            "healthcare_unsafe_after": results["datasets"]["healthcare_classification"]["repair_effect_summary"]["unsafe_auto_decision_rate_after"],
            "energy_unsafe_before": results["datasets"]["energy_timeseries"]["repair_effect_summary"]["unsafe_auto_decision_rate_before"],
            "energy_unsafe_after": results["datasets"]["energy_timeseries"]["repair_effect_summary"]["unsafe_auto_decision_rate_after"],
        },
        params={"milestone": "M5", "policy": "repair_engine_abstention_threshold_conformal"},
    )

    metrics_path = write_json(results, ROOT / "experiments/results/m5_repair_engine_before_after.json")
    report_path = write_m5_report(results, ROOT / "reports/milestone_5_repair_engine_before_after.md")
    print(f"Wrote {metrics_path}")
    print(f"Wrote {report_path}")
    print(f"Wrote {unsafe_plot}")
    print(f"Wrote {automation_plot}")
    print("M5 completed successfully.")


if __name__ == "__main__":
    main()
