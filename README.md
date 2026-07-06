# FailSafeML-X

**Self-Healing Reliability Layer for Real-World Machine Learning Systems**

FailSafeML-X is a research-grade and portfolio-grade AI/ML systems prototype for auditing machine-learning predictions before they are allowed to trigger automated decisions. It is intentionally **not a RAG project**. The project focuses on ML reliability failures such as calibration error, high uncertainty, data drift, out-of-distribution inputs, model decay, unsafe automation, and decision-routing risk.

The system converts a raw model prediction into a structured reliability decision envelope:

```text
prediction → uncertainty → drift/OOD signals → failure taxonomy → trust score → repair plan → router action
```

## Project Status

This repository contains a completed locally verified prototype through Milestone 8.

| Milestone | Component | Status |
|---|---|---|
| M1 | Baseline multi-domain reliability benchmark | Complete |
| M2 | Uncertainty and calibration engine | Complete |
| M3 | Drift and out-of-distribution detection | Complete |
| M4 | Failure taxonomy and trust score | Complete |
| M5 | Repair engine and before/after benchmark | Complete |
| M6 | RL-style repair router | Complete |
| M7 | FastAPI, Streamlit dashboard, and demo layer | Complete |
| M8 | Final packaging, Docker, docs, and portfolio artifacts | Complete |

Expected local validation:

```text
47 passed
M8 completed successfully.
```

## Problem

ML systems can fail even when model accuracy looks acceptable. A prediction may be high confidence but poorly calibrated, generated on shifted data, affected by out-of-distribution inputs, or unsafe to automate without human review.

FailSafeML-X treats reliability as a first-class system layer. Instead of only returning a prediction, it produces:

- uncertainty and calibration diagnostics,
- drift and OOD signals,
- explicit failure IDs,
- trust score,
- repair plan,
- routing decision,
- API/dashboard output,
- reproducible benchmark reports.

## Core Research Question

Can a model-agnostic reliability layer reduce unsafe automated ML decisions by detecting reliability failures and routing predictions through targeted repair actions such as abstention, human review, active learning, threshold adjustment, and retrain evaluation?

## Key Contributions

### 1. Multi-Domain Reliability Benchmark

The project uses reproducible synthetic healthcare-style classification and energy-style time-series regression benchmarks.

### 2. Calibration and Conformal Uncertainty

Milestone 2 adds calibration bins, expected calibration error, confidence summaries, conformal prediction sets, and conformal prediction intervals.

### 3. Drift and OOD Detection

Milestone 3 detects feature drift, prediction drift, and distance-based out-of-distribution risk.

### 4. Failure Taxonomy and Trust Score

Milestone 4 maps reliability signals into named failure IDs, severity levels, trust scores, and deployment-routing recommendations.

### 5. Repair Engine

Milestone 5 applies repair actions and reports before/after safety tradeoffs, including unsafe auto-decision rate and automation tradeoff plots.

### 6. RL-Style Repair Router

Milestone 6 compares rule-based routing with a cost-sensitive tabular Q-learning repair router.

### 7. API and Dashboard Demo Layer

Milestone 7 exposes reliability scoring through FastAPI and provides a Streamlit dashboard.

### 8. Final Packaging

Milestone 8 adds Docker support, release checklist, architecture documentation, demo script, resume bullets, project card, and a preliminary patent-screening note.

## Architecture

```text
Data + Features
   |
   v
Baseline ML Models
   |
   v
Prediction + Probability / Interval
   |
   +--> Calibration + Conformal Uncertainty
   +--> Drift + OOD Detection
   +--> Failure Taxonomy
   +--> Trust Score
   |
   v
Repair Engine
   |
   +--> Accept
   +--> Abstain
   +--> Human Review
   +--> Active Learning Queue
   +--> Threshold Adjustment
   +--> Retrain Evaluation
   |
   v
RL-Style Router
   |
   v
FastAPI / Streamlit Demo Layer
```

## Technology Stack

| Area | Tools |
|---|---|
| ML baselines | scikit-learn, Random Forest, Gradient Boosting, Logistic Regression |
| Reliability | calibration metrics, conformal prediction, drift detection, OOD scoring |
| Repair logic | rule-based repair engine, abstention, human review, active learning, threshold adjustment |
| RL routing | tabular Q-learning style router, rule baseline |
| API | FastAPI, Uvicorn |
| Dashboard | Streamlit |
| Reporting | JSON, Markdown, Matplotlib figures |
| Packaging | Dockerfile, Docker Compose, Makefile |
| Testing | Pytest |

## Repository Structure

```text
failsafeml-x/
  apps/
    streamlit_dashboard.py
  configs/
  docs/
    architecture.md
    demo_script.md
    github_release_checklist.md
    patent_screening_memo.md
    resume_bullets.md
  scripts/
    run_m1_baseline.py
    run_m2_uncertainty_calibration.py
    run_m3_drift_ood.py
    run_m4_failure_taxonomy.py
    run_m5_repair_engine.py
    run_m6_rl_router.py
    run_m7_api_dashboard_demo.py
    run_m8_final_packaging.py
  src/failsafemlx/
    data/
    evaluation/
    features/
    models/
    packaging/
    reliability/
    reporting/
    serving/
    utils/
  tests/
  Dockerfile
  docker-compose.yml
  Makefile
```

## Quick Start

### 1. Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run tests

```bash
python -m pytest
```

Expected:

```text
47 passed
```

### 3. Run all milestones

```bash
python scripts/run_m1_baseline.py
python scripts/run_m2_uncertainty_calibration.py
python scripts/run_m3_drift_ood.py
python scripts/run_m4_failure_taxonomy.py
python scripts/run_m5_repair_engine.py
python scripts/run_m6_rl_router.py
python scripts/run_m7_api_dashboard_demo.py
python scripts/run_m8_final_packaging.py
```

Expected final line:

```text
M8 completed successfully.
```

## Run API

```bash
uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Run Dashboard

```bash
PYTHONPATH=src streamlit run apps/streamlit_dashboard.py
```

## Docker

Build and run API:

```bash
docker build -t failsafemlx-api:local .
docker run -p 8000:8000 failsafemlx-api:local
```

Or use Docker Compose:

```bash
docker compose up --build
```

API:

```text
http://127.0.0.1:8000/docs
```

Dashboard:

```text
http://127.0.0.1:8501
```

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Service health and project metadata |
| `POST /reliability/score` | Score one prediction reliability request |
| `POST /reliability/batch` | Score a demo batch and return summary statistics |

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `experiments/results/m1_baseline_metrics.json` | Baseline metrics |
| `experiments/results/m2_uncertainty_calibration.json` | Calibration and conformal uncertainty results |
| `experiments/results/m3_drift_ood.json` | Drift and OOD results |
| `experiments/results/m4_failure_taxonomy_trust_score.json` | Failure taxonomy and trust scoring results |
| `experiments/results/m5_repair_engine_before_after.json` | Repair before/after benchmark |
| `experiments/results/m6_rl_repair_router.json` | RL router benchmark |
| `experiments/results/m7_api_dashboard_demo.json` | API/dashboard demo summary |
| `experiments/results/m8_final_packaging.json` | Final release packaging summary |
| `reports/milestone_*.md` | Reproducible milestone reports |
| `reports/figures/*.png` | Generated plots |
| `reports/final_project_card.md` | Portfolio project card |

## Suggested Resume Bullet

Built FailSafeML-X, a model-agnostic ML reliability layer that detects calibration failure, uncertainty, drift, OOD inputs, model decay, and unsafe automation risk, then routes predictions through repair actions including abstention, human review, active-learning queues, threshold adjustment, and retrain evaluation, with reproducible pytest validation, FastAPI serving, Streamlit dashboarding, and Docker-ready packaging.

## Honest Limitations

This is a research and portfolio prototype, not a production-certified safety system.

Current limitations:

- Synthetic benchmarks only.
- No real hospital, grid, finance, or enterprise dataset is included.
- Repair policies are deterministic/simulated and require real-world validation.
- RL routing is tabular and prototype-level, not a deep RL production policy.
- API/dashboard are local demo layers, not hardened cloud deployments.
- Security, authentication, persistence, CI/CD, and monitoring hardening are future work.
- Patentability is not claimed.

## Future Work

Planned extensions:

- Evaluate on public real-world datasets.
- Add MLflow experiment tracking and DVC data versioning.
- Add Prometheus/Grafana monitoring.
- Add Kubernetes manifests.
- Add deeper RL or contextual bandit routing.
- Add LLM-generated reliability explanations with strict guardrails.
- Add human-labeled validation and statistical significance testing.

## Research and Patent Note

FailSafeML-X does not claim novelty over uncertainty estimation, conformal prediction, drift detection, human-in-the-loop ML, MLOps monitoring, or reinforcement learning individually.

The potentially interesting direction is the integrated decision envelope that combines calibrated uncertainty, drift/OOD risk, explicit failure taxonomy, repair-plan generation, and cost-sensitive routing for model-agnostic reliability operations.

Patentability is not claimed. The repository includes a preliminary, non-legal patent-screening memo only.
