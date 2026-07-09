# Deployment Templates

Milestone 17 adds static Terraform and Helm templates for packaging the FailSafeML-X FastAPI reliability service.

## What is included

- Terraform Kubernetes namespace, deployment, and service template.
- Helm chart with deployment, service, and optional ingress templates.
- Offline/local provider defaults.
- Health probes for `/health`.
- Optional Prometheus scrape annotations aligned with the monitoring artifacts from M16.

## What is not claimed

This milestone does not execute Terraform, install Helm, create a Kubernetes cluster, deploy to cloud infrastructure, or validate production readiness.

## Provider safety defaults

The templates intentionally default to:

```text
FAILSAFEMLX_PROVIDER_MODE=local
FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false
FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false
```

That keeps deployments safe for local CI and avoids paid provider calls unless a future operator explicitly changes the configuration.

## Validation

Run:

```bash
python scripts/validate_infra_templates.py
python scripts/run_m17_infra_templates.py
```

The validation is static. It checks that required files exist and that the templates contain the expected service, provider-safety, health-probe, and monitoring-readiness markers.
