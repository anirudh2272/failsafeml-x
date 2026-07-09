# Milestone 17 — Terraform and Helm Deployment Templates

## Objective
Add static Terraform and Helm templates for packaging the FailSafeML-X FastAPI reliability service while preserving safe local/offline provider defaults.

## Validation Summary
- Passed: `True`
- Checked files: `10`
- Terraform files: `4`
- Helm files: `5`
- Service target: `FailSafeML-X FastAPI API service on port 8000`
- Provider default: `local/offline`
- External LLM default enabled: `False`
- External vector DB default enabled: `False`

## Template Files
| File | Purpose |
|---|---|
| `infra/terraform/main.tf` | Kubernetes namespace, deployment, and service template |
| `infra/terraform/variables.tf` | Configurable image, replica, service, and resource parameters |
| `infra/terraform/outputs.tf` | Static output references for namespace and service |
| `charts/failsafeml-x/Chart.yaml` | Helm chart metadata |
| `charts/failsafeml-x/values.yaml` | Safe local/offline defaults |
| `charts/failsafeml-x/templates/deployment.yaml` | FastAPI deployment template |
| `charts/failsafeml-x/templates/service.yaml` | Kubernetes service template |
| `charts/failsafeml-x/templates/ingress.yaml` | Optional ingress template |

## Safety Defaults
```text
FAILSAFEMLX_PROVIDER_MODE=local
FAILSAFEMLX_ENABLE_EXTERNAL_LLM=false
FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB=false
```

## Honest Limitations
- Validation is static and does not run terraform plan/apply.
- Validation is static and does not run helm template/install.
- No Kubernetes cluster or cloud deployment is created by this milestone.
- Production deployment requires real cluster, image registry, networking, authentication, and security review.
