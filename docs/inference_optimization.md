# Inference Optimization Benchmark

Milestone 14 adds a lightweight inference benchmark for FailSafeML-X.

## Purpose

The goal is to measure local inference behavior before making optimization or deployment claims.

M14 measures:

- single-row prediction latency
- vectorized batch prediction latency
- mini-batch prediction-loop latency
- p50 and p95 latency
- rows-per-second throughput
- optional ONNX Runtime availability

## Running the Benchmark

```bash
python scripts/run_m14_inference_optimization.py
```

Outputs:

- `experiments/results/m14_inference_optimization.json`
- `reports/milestone_14_inference_optimization.md`

## Optional ONNX Runtime

`requirements-optimization.txt` includes optional optimization dependencies. These are not required for tests.

The default benchmark is intentionally sklearn-compatible so the repository remains portable and lightweight.

## Scope

M14 does not claim production serving, GPU acceleration, Triton deployment, vLLM deployment, or guaranteed speedup. It adds benchmark instrumentation and reusable mini-batch inference utilities.
