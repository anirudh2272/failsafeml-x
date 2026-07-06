from failsafemlx.data.synthetic import make_healthcare_risk_dataset
from failsafemlx.models.baselines import build_healthcare_models, predict_positive_probability


def test_healthcare_model_smoke_train_predict():
    X, y = make_healthcare_risk_dataset(n_samples=180, random_state=11)
    model = build_healthcare_models(random_state=11)["gradient_boosting"]
    model.fit(X, y)
    probs = predict_positive_probability(model, X.head(5))
    assert len(probs) == 5
    assert all(0.0 <= p <= 1.0 for p in probs)
