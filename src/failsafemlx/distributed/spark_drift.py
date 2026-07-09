from __future__ import annotations

from typing import Any

import pandas as pd

from .local_drift_fallback import analyze_drift_local


def _pyspark_available() -> bool:
    try:
        import pyspark  # noqa: F401
    except Exception:
        return False
    return True


def _to_pandas(frame: Any) -> pd.DataFrame:
    """Convert supported local/Spark-like frames to Pandas."""

    if isinstance(frame, pd.DataFrame):
        return frame
    if hasattr(frame, "toPandas"):
        return frame.toPandas()
    raise TypeError("Expected a pandas DataFrame or Spark DataFrame-like object with toPandas().")


def analyze_drift_spark_compatible(
    reference: Any,
    current: Any,
    *,
    top_k: int = 5,
    bins: int = 10,
) -> dict[str, Any]:
    """Run Spark-compatible drift analysis with deterministic local fallback.

    If PySpark is not installed, this function still works on Pandas DataFrames.
    If Spark DataFrame-like objects are passed, they are converted to Pandas for
    lightweight validation in this repository. The code is intentionally
    dependency-optional so normal tests do not require Spark or Databricks.
    """

    reference_pd = _to_pandas(reference)
    current_pd = _to_pandas(current)
    result = analyze_drift_local(reference_pd, current_pd, top_k=top_k, bins=bins).to_dict()
    result["spark_available"] = _pyspark_available()
    result["spark_execution_mode"] = (
        "spark_dataframe_adapter" if not isinstance(reference, pd.DataFrame) else "pandas_input_adapter"
    )
    result["claim_scope"] = "PySpark-compatible interface with local fallback; no Databricks deployment claimed."
    return result
