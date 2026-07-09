# Distributed Drift Pipeline

Milestone 12 adds a PySpark-compatible drift monitoring layer for FailSafeML-X.

## Purpose

Production ML systems often score data in large daily or hourly batches. M12 adds a lightweight distributed-style pipeline that compares a reference feature batch against a current feature batch and reports reliability risk before automated decisions are trusted.

## Metrics

The pipeline reports:

- feature mean shift
- standard-deviation shift
- PSI-style distribution drift score
- top drifted features
- feature-level severity
- overall batch severity

## Execution Modes

### Local fallback

```bash
python scripts/run_m12_spark_drift_pipeline.py
```

The default mode uses Pandas and NumPy. This keeps tests lightweight and avoids requiring Spark for normal development.

### PySpark-compatible path

`src/failsafemlx/distributed/spark_drift.py` accepts Pandas DataFrames and Spark DataFrame-like objects that expose `toPandas()`. This gives the project a Spark-compatible interface without requiring a Spark cluster in CI.

## Databricks-Style Workflow

The notebook-style guide in `notebooks/databricks_drift_demo.md` shows how the module would be used inside a Databricks or Spark workflow.

## Scope and Limitation

This milestone does not claim a live Databricks deployment, managed Spark job, streaming pipeline, or production scheduler. It provides local validation plus cloud/Spark-ready structure.
