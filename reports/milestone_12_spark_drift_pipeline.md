# Milestone 12 — PySpark / Databricks-Style Drift Pipeline

## Objective

Add a distributed-style drift monitoring layer for large-batch feature reliability checks. The implementation exposes a PySpark-compatible adapter while keeping a deterministic Pandas/NumPy fallback for local tests.

## What M12 Adds

- `src/failsafemlx/distributed/local_drift_fallback.py`
- `src/failsafemlx/distributed/spark_drift.py`
- `scripts/run_m12_spark_drift_pipeline.py`
- `notebooks/databricks_drift_demo.md`
- `docs/distributed_drift_pipeline.md`
- `requirements-spark.txt`

## Drift Metrics

The pipeline computes:

- feature mean shift
- feature standard-deviation shift
- PSI-style distribution drift score
- top drifted features
- feature-level severity labels
- overall batch drift severity

## Validation Summary

- Passed: True
- Engine: local_pandas_numpy_fallback
- Spark available locally: False
- Reference rows: 1500
- Current rows: 1500
- Feature count: 8
- Mean PSI: 0.095715
- Max PSI: 0.478323
- Overall severity: high

## Top Drifted Features

- `feature_0`: PSI=0.478323, severity=high, mean_shift=0.708108, std_shift=0.00264
- `feature_1`: PSI=0.187396, severity=moderate, mean_shift=0.329922, std_shift=0.310481
- `feature_2`: PSI=0.047255, severity=stable, mean_shift=0.198658, std_shift=0.024433
- `feature_5`: PSI=0.016204, severity=stable, mean_shift=0.039164, std_shift=0.043918
- `feature_4`: PSI=0.010235, severity=stable, mean_shift=0.006305, std_shift=0.007926

## Generated Outputs

- `experiments/results/m12_spark_drift_pipeline.json`
- `reports/milestone_12_spark_drift_pipeline.md`

## Honest Limitation

M12 provides a PySpark-compatible interface and Databricks-style workflow documentation. It does not claim that a Databricks cluster or production Spark job has been deployed.
