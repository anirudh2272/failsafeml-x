# Recruiter Walkthrough

## One-minute pitch

FailSafeML-X is a model-agnostic ML reliability platform prototype that audits predictions before automated decisions are allowed. It detects uncertainty, calibration failure, drift, OOD risk, RAGOps evidence failures, provider safety issues, and dataset validation problems, then assigns trust scores and repair actions.

## What to show first

1. `README.md` for the project overview.
2. `reports/advanced_project_card.md` for the final executive summary.
3. `reports/model_risk_card.md` for model-risk documentation.
4. `monitoring/prometheus_metrics_example.txt` and `monitoring/grafana_dashboard_spec.json` for monitoring readiness.
5. `scripts/local_ci.py` to prove reproducibility.

## Skills demonstrated

- Python ML systems engineering
- FastAPI and Streamlit demo design
- Calibration, uncertainty, drift, and OOD checks
- RAGOps reliability auditing
- Provider abstraction with local/offline safety defaults
- Dataset validation
- Experiment tracking and model-risk documentation
- Prometheus/Grafana-ready monitoring artifacts
- Terraform and Helm deployment templates
- AWS SageMaker / Vertex AI style inference templates
- LoRA / PEFT fine-tuning scaffold
- CI/CD and automated tests

## Honest phrasing

Use: “locally validated prototype,” “template,” “scaffold,” “provider abstraction,” and “monitoring-ready artifacts.”

Do not say: production deployed, cloud deployed, certified, live Bedrock/OpenAI production integration, trained LoRA adapter, or enterprise monitoring deployment unless those steps are actually completed later.
