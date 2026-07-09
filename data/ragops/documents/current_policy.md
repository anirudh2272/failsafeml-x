---
doc_id: current_policy
title: Current Reliability Policy
source: internal_policy
created_at: 2026-01-15
version: v2
trust_level: trusted
---

The current reliability policy requires every automated RAG answer to include citations to trusted retrieved context. Current routing rules say that stale documents should be filtered before final answer generation. High-risk answers must be routed to human review when evidence conflicts. Trusted internal policy v2 supersedes old policy v1. If citations are missing, the response should be repaired before acceptance.
