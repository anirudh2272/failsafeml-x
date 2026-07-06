from __future__ import annotations

from failsafemlx.serving.gateway import (
    API_ENDPOINTS,
    ReliabilityRequest,
    make_demo_requests,
    score_demo_batch,
    score_reliability_request,
    summarize_batch_responses,
)
from failsafemlx.serving.fastapi_app import create_app


def test_api_contract_contains_expected_endpoints():
    assert "GET /health" in API_ENDPOINTS
    assert "POST /reliability/score" in API_ENDPOINTS
    assert "POST /reliability/batch" in API_ENDPOINTS


def test_low_risk_request_can_auto_accept():
    request = ReliabilityRequest(
        request_id="safe-1",
        domain="healthcare_risk",
        predicted_label=1,
        probability=0.94,
        conformal_set_size=1.0,
        drift_score=0.02,
        ood_score=0.05,
        model_age_days=5,
        recent_error_rate=0.03,
    )
    response = score_reliability_request(request)
    assert response["trust"]["trust_score"] >= 80
    assert response["router"]["action"] == "AUTO_ACCEPT"
    assert response["router"]["auto_accept"] is True


def test_ood_drift_request_routes_away_from_automation():
    request = ReliabilityRequest(
        request_id="risk-1",
        domain="energy_forecast",
        predicted_label=0,
        probability=0.51,
        conformal_set_size=1.75,
        drift_score=0.72,
        ood_score=0.91,
        model_age_days=160,
        recent_error_rate=0.35,
    )
    response = score_reliability_request(request)
    failure_ids = {failure["failure_id"] for failure in response["trust"]["failure_signals"]}
    assert "F4_OUT_OF_DISTRIBUTION_INPUT" in failure_ids
    assert "F10_UNSAFE_AUTO_DECISION" in failure_ids
    assert response["router"]["action"] != "AUTO_ACCEPT"


def test_batch_summary_is_consistent():
    batch = score_demo_batch(n=18, random_state=10)
    summary = batch["summary"]
    assert summary["num_requests"] == 18
    assert 0.0 <= summary["auto_accept_rate"] <= 1.0
    assert summary["router_action_counts"]
    assert batch["responses"][0]["api_contract_version"] == "m7.v1"


def test_empty_batch_summary_is_safe():
    summary = summarize_batch_responses([])
    assert summary["num_requests"] == 0
    assert summary["auto_accept_rate"] == 0.0


def test_fastapi_app_factory_exposes_routes():
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/reliability/score" in paths
    assert "/reliability/batch" in paths
