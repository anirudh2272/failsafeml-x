# Milestone 14 — Inference Optimization Benchmark

## Objective

Add a lightweight local inference benchmark to FailSafeML-X so model-serving behavior can be measured before making deployment or optimization claims.

## What M14 Adds

- Local sklearn-compatible inference benchmark
- Single-row latency measurement
- Vectorized batch latency measurement
- Mini-batch prediction utility
- p50 and p95 latency reporting
- Throughput reporting in rows per second
- Optional ONNX Runtime availability check
- JSON and Markdown benchmark outputs

## Validation Summary

- Passed: True
- Required paths checked: 7
- Benchmark rows: 150
- Batch size: 128
- Repeats per mode: 10

## Benchmark Results

| Mode | Mean latency ms | p50 ms | p95 ms | Throughput rows/s |
|---|---:|---:|---:|---:|
| Single row predict_proba | 0.355287 | 0.354917 | 0.35836 | 2814.621961 |
| Vectorized batch predict_proba | 0.374104 | 0.372604 | 0.380437 | 400957.807914 |
| Mini-batch prediction loop | 1.502804 | 1.502688 | 1.509502 | 99813.415447 |

## Optional Optimization Path

- ONNX Runtime available: False
- Note: ONNX Runtime is optional and was not required for this milestone.

## Generated Outputs

- `experiments/results/m14_inference_optimization.json`
- `reports/milestone_14_inference_optimization.md`

## Honest Limitation

M14 measures local inference latency and throughput for a compact sklearn model. It does not claim GPU serving, production deployment, Triton deployment, vLLM acceleration, or guaranteed speedup across hardware.
