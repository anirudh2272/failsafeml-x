terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.25.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kube_context
}

resource "kubernetes_namespace" "failsafemlx" {
  metadata {
    name = var.namespace
    labels = {
      app       = "failsafeml-x"
      component = "ml-reliability"
    }
  }
}

resource "kubernetes_deployment" "api" {
  metadata {
    name      = "failsafeml-x-api"
    namespace = kubernetes_namespace.failsafemlx.metadata[0].name
    labels = {
      app       = "failsafeml-x"
      component = "api"
    }
  }

  spec {
    replicas = var.replica_count

    selector {
      match_labels = {
        app       = "failsafeml-x"
        component = "api"
      }
    }

    template {
      metadata {
        labels = {
          app       = "failsafeml-x"
          component = "api"
        }
        annotations = {
          "prometheus.io/scrape" = tostring(var.enable_prometheus_scrape)
          "prometheus.io/path"   = var.prometheus_path
          "prometheus.io/port"   = tostring(var.container_port)
        }
      }

      spec {
        container {
          name  = "failsafeml-x-api"
          image = var.image

          port {
            container_port = var.container_port
          }

          env {
            name  = "FAILSAFEMLX_PROVIDER_MODE"
            value = "local"
          }

          env {
            name  = "FAILSAFEMLX_ENABLE_EXTERNAL_LLM"
            value = "false"
          }

          env {
            name  = "FAILSAFEMLX_ENABLE_EXTERNAL_VECTOR_DB"
            value = "false"
          }

          env {
            name  = "FAILSAFEMLX_DEPLOYMENT_PROFILE"
            value = "terraform-template"
          }

          resources {
            limits = {
              cpu    = var.cpu_limit
              memory = var.memory_limit
            }
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = var.container_port
            }
            initial_delay_seconds = 10
            period_seconds        = 15
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = var.container_port
            }
            initial_delay_seconds = 20
            period_seconds        = 30
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "api" {
  metadata {
    name      = "failsafeml-x-api"
    namespace = kubernetes_namespace.failsafemlx.metadata[0].name
    labels = {
      app       = "failsafeml-x"
      component = "api"
    }
  }

  spec {
    selector = {
      app       = "failsafeml-x"
      component = "api"
    }

    port {
      name        = "http"
      port        = var.service_port
      target_port = var.container_port
    }

    type = var.service_type
  }
}
