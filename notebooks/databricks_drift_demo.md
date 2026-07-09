# Databricks-Style Drift Monitoring Demo

This is a documentation-first notebook-style guide. It is safe to keep in GitHub because it does not require credentials, paid cloud resources, or a live Databricks cluster.

## 1. Install optional Spark dependencies

```bash
pip install -r requirements-spark.txt
```

## 2. Generate or load batches

```python
from failsafemlx.distributed.local_drift_fallback import generate_synthetic_drift_batches

reference_df, current_df = generate_synthetic_drift_batches(
    n_reference=100000,
    n_current=100000,
    n_features=20,
)
```

## 3. Run Spark-compatible drift analysis

```python
from failsafemlx.distributed.spark_drift import analyze_drift_spark_compatible

result = analyze_drift_spark_compatible(reference_df, current_df, top_k=10)
result["overall_severity"], result["top_drifted_features"][:3]
```

## 4. Databricks adaptation idea

In a live Databricks job, replace the synthetic Pandas batches with Spark tables:

```python
reference_spark = spark.table("ml_monitoring.reference_features")
current_spark = spark.table("ml_monitoring.current_features")

result = analyze_drift_spark_compatible(reference_spark, current_spark, top_k=10)
```

## Limitation

This project includes a Databricks-style workflow guide only. It does not claim an active Databricks deployment.
