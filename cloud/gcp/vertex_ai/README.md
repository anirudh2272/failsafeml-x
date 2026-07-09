# Google Vertex AI Template

This folder contains a **template-only** Vertex AI predictor for FailSafeML-X.

It demonstrates how a Vertex-style prediction handler could wrap model outputs with a reliability envelope while keeping provider settings local/offline by default.

No Google Cloud credentials, Vertex AI SDK, container build, or live endpoint is required for tests.

## Honest limitation

This is not a live Vertex AI deployment. It is a CI-safe template that can be adapted after model packaging, service account, network, logging, monitoring, and security review.
