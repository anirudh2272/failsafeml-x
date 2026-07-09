from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from failsafemlx.optimization.inference_benchmark import run_local_inference_benchmark

RESULT_PATH = PROJECT_ROOT / "experiments/results/m14_inference_optimization.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_14_inference_optimization.md"

REQUIRED_PATHS = [
    "scripts/run_m14_inference_optimization.py",
    "src/failsafemlx/optimization/__init__.py",
    "src/failsafemlx/optimization/inference_benchmark.py",
    "src/failsafemlx/optimization/batch_inference.py",
    "tests/test_inference_optimization.py",
    "docs/inference_optimization.md",
    "requirements-optimization.txt",
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    benchmark = result["benchmark"]
    single = benchmark["latency"]["single_row"]
    batch = benchmark["latency"]["vectorized_batch"]
    mini = benchmark["latency"]["mini_batch_loop"]
    onnx = benchmark["optional_onnx_runtime"]

    content = f"""# Milestone 14 — Inference Optimization Benchmark

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

- Passed: {result['passed']}
- Required paths checked: {result['required_paths_checked']}
- Benchmark rows: {benchmark['num_benchmark_rows']}
- Batch size: {benchmark['batch_size']}
- Repeats per mode: {benchmark['repeats']}

## Benchmark Results

| Mode | Mean latency ms | p50 ms | p95 ms | Throughput rows/s |
|---|---:|---:|---:|---:|
| Single row predict_proba | {single['mean_latency_ms']} | {single['p50_latency_ms']} | {single['p95_latency_ms']} | {single['throughput_rows_per_second']} |
| Vectorized batch predict_proba | {batch['mean_latency_ms']} | {batch['p50_latency_ms']} | {batch['p95_latency_ms']} | {batch['throughput_rows_per_second']} |
| Mini-batch prediction loop | {mini['mean_latency_ms']} | {mini['p50_latency_ms']} | {mini['p95_latency_ms']} | {mini['throughput_rows_per_second']} |

## Optional Optimization Path

- ONNX Runtime available: {onnx['available']}
- Note: {onnx['note']}

## Generated Outputs

- `experiments/results/m14_inference_optimization.json`
- `reports/milestone_14_inference_optimization.md`

## Honest Limitation

M14 measures local inference latency and throughput for a compact sklearn model. It does not claim GPU serving, production deployment, Triton deployment, vLLM acceleration, or guaranteed speedup across hardware.
"""
    path.write_text(content, encoding="utf-8")


def run_m14() -> dict[str, Any]:
    missing_paths = [path for path in REQUIRED_PATHS if not (PROJECT_ROOT / path).exists()]
    errors = [f"Missing required path: {path}" for path in missing_paths]
    warnings: list[str] = []

    benchmark = run_local_inference_benchmark(batch_size=128, repeats=10)

    for name, stats in benchmark["latency"].items():
        if stats["mean_latency_ms"] <= 0:
            errors.append(f"{name} mean latency must be positive.")
        if stats["p95_latency_ms"] < stats["p50_latency_ms"]:
            errors.append(f"{name} p95 latency should be greater than or equal to p50 latency.")
        if stats["throughput_rows_per_second"] <= 0:
            errors.append(f"{name} throughput must be positive.")

    if benchmark["prediction_summary"]["num_predictions"] != benchmark["num_benchmark_rows"]:
        errors.append("Mini-batch prediction count does not match benchmark row count.")

    result: dict[str, Any] = {
        "project": "FailSafeML-X",
        "milestone": "M14_INFERENCE_OPTIMIZATION_BENCHMARK",
        "status": "completed" if not errors else "failed",
        "passed": not errors,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "required_paths_checked": len(REQUIRED_PATHS),
        "missing_required_paths": missing_paths,
        "benchmark": benchmark,
        "errors": errors,
        "warnings": warnings,
        "generated_outputs": [
            str(RESULT_PATH.relative_to(PROJECT_ROOT)),
            str(REPORT_PATH.relative_to(PROJECT_ROOT)),
        ],
        "honest_claim": "Added local inference benchmarking for latency, p50/p95, throughput, and mini-batch inference. No production-serving or GPU acceleration claim is made.",
        "next_milestone": "M15_TERRAFORM_HELM_DEPLOYMENT_TEMPLATES",
    }

    write_json(RESULT_PATH, result)
    write_report(REPORT_PATH, result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")

    if not result["passed"]:
        print("M14 validation failed. Review errors above.")
        raise SystemExit(1)

    print("M14 completed successfully.")
    return result


def main() -> None:
    run_m14()


if __name__ == "__main__":
    main()
