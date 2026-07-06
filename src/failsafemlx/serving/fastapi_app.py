from __future__ import annotations

from typing import Any

from failsafemlx.serving.gateway import API_ENDPOINTS, score_demo_batch, score_reliability_request, summarize_batch_responses


def create_app():
    """Create the FastAPI app.

    FastAPI is intentionally imported inside this function so the core reliability
    package remains usable even when optional serving dependencies are absent.
    """
    try:
        from fastapi import FastAPI
    except ImportError as exc:  # pragma: no cover - exercised only when optional deps are absent
        raise RuntimeError("Install serving dependencies with `pip install fastapi uvicorn`.") from exc

    app = FastAPI(
        title="FailSafeML-X Reliability API",
        version="0.7.0",
        description="API façade for trust scoring, failure taxonomy, repair planning, and router decisions.",
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "project": "FailSafeML-X",
            "milestone": "M7_API_DASHBOARD_AND_DEMO",
            "available_endpoints": API_ENDPOINTS,
        }

    @app.post("/reliability/score")
    def reliability_score(payload: dict[str, Any]) -> dict[str, Any]:
        return score_reliability_request(payload)

    @app.post("/reliability/batch")
    def reliability_batch(payloads: list[dict[str, Any]]) -> dict[str, Any]:
        responses = [score_reliability_request(payload) for payload in payloads]
        return {"responses": responses, "summary": summarize_batch_responses(responses)}

    @app.get("/demo/batch")
    def demo_batch() -> dict[str, Any]:
        return score_demo_batch(n=25, random_state=7)

    return app


app = create_app()
