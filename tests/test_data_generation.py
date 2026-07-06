from failsafemlx.data.synthetic import make_energy_timeseries, make_healthcare_risk_dataset
from failsafemlx.features.timeseries import make_lag_features


def test_healthcare_dataset_shape():
    X, y = make_healthcare_risk_dataset(n_samples=100, random_state=7)
    assert X.shape == (100, 14)
    assert len(y) == 100
    assert set(y.unique()) <= {0, 1}


def test_timeseries_lag_features_nonempty():
    df = make_energy_timeseries(n_points=300, random_state=7)
    X, y = make_lag_features(df)
    assert len(X) == len(y)
    assert len(X) > 50
    assert "demand_lag_24" in X.columns
