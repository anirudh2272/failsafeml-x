output "namespace" {
  description = "Namespace created by the template."
  value       = kubernetes_namespace.failsafemlx.metadata[0].name
}

output "service_name" {
  description = "Kubernetes service name for the API."
  value       = kubernetes_service.api.metadata[0].name
}

output "provider_mode" {
  description = "External provider default for this deployment template."
  value       = "local/offline"
}
