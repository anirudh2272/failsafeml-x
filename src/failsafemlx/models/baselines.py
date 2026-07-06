from __future__ import annotations

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_healthcare_models(random_state: int = 42) -> dict[str, object]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=random_state)),
            ]
        ),
        "gradient_boosting": GradientBoostingClassifier(
            random_state=random_state,
            n_estimators=120,
            learning_rate=0.06,
            max_depth=3,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def build_timeseries_models(random_state: int = 42) -> dict[str, object]:
    return {
        "gradient_boosting_regressor": GradientBoostingRegressor(
            random_state=random_state,
            n_estimators=140,
            learning_rate=0.05,
            max_depth=3,
        ),
    }


def predict_positive_probability(model: object, X) -> np.ndarray:
    if not hasattr(model, "predict_proba"):
        raise TypeError("Classification model must expose predict_proba for reliability metrics.")
    return model.predict_proba(X)[:, 1]
