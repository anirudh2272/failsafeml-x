from __future__ import annotations

import numpy as np
import pandas as pd

from failsafemlx.reliability.drift import feature_drift_report, population_stability_index, prediction_drift_report


def test_population_stability_index_detects_shift():
    rng = np.random.default_rng(7)
    ref = rng.normal(0, 1, 500)
    cur = rng.normal(1.5, 1, 500)
    assert population_stability_index(ref, cur) > 0.2


def test_feature_drift_report_flags_shifted_column():
    rng = np.random.default_rng(11)
    ref = pd.DataFrame({"a": rng.normal(0, 1, 300), "b": rng.normal(0, 1, 300)})
    cur = ref.copy()
    cur["a"] = cur["a"] + 2.0
    report = feature_drift_report(ref, cur)
    assert report["drift_detected"] is True
    assert report["num_features_drifted"] >= 1
    assert report["top_drifted_features"][0]["feature"] == "a"


def test_prediction_drift_report_flags_changed_scores():
    ref = np.linspace(0.1, 0.9, 200)
    cur = np.clip(ref + 0.25, 0, 1)
    report = prediction_drift_report(ref, cur)
    assert report["prediction_drift_detected"] is True
