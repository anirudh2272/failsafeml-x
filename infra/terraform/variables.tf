variable "namespace" {
  description = "Kubernetes namespace for the FailSafeML-X reliability service."
  type        = string
  default     = "failsafemlx"
}

variable "image" {
  description = "Container image for the FailSafeML-X FastAPI service."
  type        = string
  default     = "failsafeml-x:latest"
}

variable "replica_count" {
  description = "Number of API replicas."
  type        = number
  default     = 1
}

variable "container_port" {
  description = "Container port exposed by the FastAPI service."
  type        = number
  default     = 8000
}

variable "service_port" {
  description = "Kubernetes service port."
  type        = number
  default     = 80
}

variable "service_type" {
  description = "Kubernetes service type."
  type        = string
  default     = "ClusterIP"
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig. This is a placeholder for real deployments."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Optional Kubernetes context."
  type        = string
  default     = null
}

variable "enable_prometheus_scrape" {
  description = "Whether to expose Prometheus scrape annotations in the template."
  type        = bool
  default     = false
}

variable "prometheus_path" {
  description = "Metrics path placeholder. The local milestone generates metrics artifacts, not a live endpoint claim."
  type        = string
  default     = "/metrics"
}

variable "cpu_request" {
  description = "CPU request for the API container."
  type        = string
  default     = "250m"
}

variable "memory_request" {
  description = "Memory request for the API container."
  type        = string
  default     = "512Mi"
}

variable "cpu_limit" {
  description = "CPU limit for the API container."
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit for the API container."
  type        = string
  default     = "1Gi"
}
