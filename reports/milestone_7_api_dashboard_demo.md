# Milestone 7 — API, Dashboard, and Demo Layer

## Objective

Expose FailSafeML-X through a serving-oriented interface so model predictions can be inspected with trust scores, failure signals, repair plans, and router decisions.

## API Contract

- `GET /health` — Liveness and project metadata.
- `POST /reliability/score` — Return trust score, failures, repair plan, and router action for one prediction.
- `POST /reliability/batch` — Return summary statistics for a batch of prediction reliability requests.

## Demo Batch Summary

- Number of scored requests: 90
- Mean trust score: 75.6889
- Min trust score: 0.0
- Max trust score: 100.0
- Auto-accept rate: 0.4222
- Review/defer rate: 0.5778

### Router Action Counts
- ACTIVE_LEARNING: 16
- AUTO_ACCEPT: 38
- HUMAN_REVIEW: 31
- RETRAIN_EVAL: 5

### Top Failure IDs
- F3_LOW_CONFIDENCE_PREDICTION: 37
- F8_WIDE_PREDICTION_INTERVAL: 32
- F1_DATA_DRIFT: 21
- F10_UNSAFE_AUTO_DECISION: 16
- F9_MODEL_DECAY_OVER_TIME: 15
- F4_OUT_OF_DISTRIBUTION_INPUT: 14

## Generated Artifacts

- `experiments/results/m7_api_dashboard_demo.json`
- `reports/figures/m7_api_router_action_summary.png`
- `apps/streamlit_dashboard.py`
- `src/failsafemlx/serving/fastapi_app.py`

## How to Run Locally

```bash
uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload
streamlit run apps/streamlit_dashboard.py
```

## Honest Limitation

Milestone 7 is a local demo serving layer. It exposes the reliability logic through API and dashboard artifacts, but it is not a production deployment, authentication system, or cloud release.

## Next Milestone

Milestone 8 should package the system for reproducible deployment with Docker, final documentation, and a complete demo script.
