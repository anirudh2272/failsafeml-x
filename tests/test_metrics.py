import numpy as np

from failsafemlx.evaluation.metrics import classification_metrics, expected_calibration_error, regression_metrics


def test_expected_calibration_error_range():
    y_true = np.array([0, 0, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])
    ece = expected_calibration_error(y_true, y_prob, n_bins=2)
    assert 0.0 <= ece <= 1.0


def test_classification_metrics_keys():
    y_true = np.array([0, 1, 1, 0, 1, 0])
    y_prob = np.array([0.1, 0.8, 0.7, 0.2, 0.9, 0.3])
    metrics = classification_metrics(y_true, y_prob)
    assert {"accuracy", "f1", "auroc", "brier_score", "expected_calibration_error"} <= set(metrics)


def test_regression_metrics_keys():
    y_true = np.array([10.0, 12.0, 15.0])
    y_pred = np.array([11.0, 12.5, 14.0])
    metrics = regression_metrics(y_true, y_pred)
    assert {"mae", "rmse", "mape", "r2"} <= set(metrics)
