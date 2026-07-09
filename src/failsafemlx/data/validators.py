from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from failsafemlx.data.schema import DatasetSchema


@dataclass
class DatasetValidationResult:
    dataset_name: str
    row_count: int
    column_count: int
    passed: bool
    errors: list[str]
    warnings: list[str]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _contains_leakage_keyword(column: str, keywords: list[str]) -> bool:
    normalized = column.lower()
    return any(keyword.lower() in normalized for keyword in keywords)


def validate_dataset(df: pd.DataFrame, schema: DatasetSchema) -> DatasetValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    columns = set(df.columns)
    missing_required = [column for column in schema.required_columns if column not in columns]
    if missing_required:
        errors.append(f"Missing required columns: {missing_required}")

    if schema.target_column not in columns:
        errors.append(f"Missing target column: {schema.target_column}")

    missing_counts = df.isna().sum()
    missing_columns = {column: int(count) for column, count in missing_counts.items() if int(count) > 0}
    if missing_columns:
        warnings.append(f"Missing values detected: {missing_columns}")

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count > 0:
        warnings.append(f"Duplicate rows detected: {duplicate_count}")

    for column in schema.numeric_columns:
        if column not in columns:
            continue
        converted = pd.to_numeric(df[column], errors="coerce")
        invalid_count = int(converted.isna().sum() - df[column].isna().sum())
        if invalid_count > 0:
            errors.append(f"Column {column} contains {invalid_count} non-numeric values")

    for column in schema.categorical_columns:
        if column not in columns:
            continue
        if df[column].nunique(dropna=True) == 0:
            warnings.append(f"Categorical column {column} has no non-null values")

    leakage_columns = [column for column in df.columns if _contains_leakage_keyword(column, schema.leakage_keywords)]
    if leakage_columns:
        warnings.append(f"Potential leakage-like columns detected: {leakage_columns}")

    target_summary: dict[str, Any] = {}
    if schema.target_column in columns:
        target_series = df[schema.target_column]
        target_summary = {
            "unique_values": sorted([str(value) for value in target_series.dropna().unique().tolist()]),
            "missing_count": int(target_series.isna().sum()),
        }
        if target_series.isna().any():
            errors.append(f"Target column {schema.target_column} contains missing values")

        if schema.allowed_target_values is not None:
            allowed = {str(value) for value in schema.allowed_target_values}
            observed = {str(value) for value in target_series.dropna().unique().tolist()}
            invalid = sorted(observed - allowed)
            if invalid:
                errors.append(f"Target column {schema.target_column} contains invalid values: {invalid}")

        if schema.task_type == "binary_classification" and len(target_series.dropna()) > 0:
            normalized_counts = target_series.value_counts(normalize=True, dropna=True)
            min_class_rate = float(normalized_counts.min()) if not normalized_counts.empty else 0.0
            target_summary["min_class_rate"] = round(min_class_rate, 4)
            if min_class_rate < schema.imbalance_threshold:
                warnings.append(
                    f"Severe class imbalance detected in {schema.target_column}: min class rate {min_class_rate:.3f}"
                )

    timestamp_summary: dict[str, Any] = {}
    if schema.timestamp_column:
        if schema.timestamp_column not in columns:
            errors.append(f"Missing timestamp column: {schema.timestamp_column}")
        else:
            timestamps = pd.to_datetime(df[schema.timestamp_column], errors="coerce")
            invalid_timestamps = int(timestamps.isna().sum())
            timestamp_summary["invalid_timestamp_count"] = invalid_timestamps
            if invalid_timestamps > 0:
                errors.append(f"Timestamp column {schema.timestamp_column} contains {invalid_timestamps} invalid timestamps")
            if not timestamps.is_monotonic_increasing:
                warnings.append(f"Timestamp column {schema.timestamp_column} is not sorted in increasing order")
            timestamp_summary["is_monotonic_increasing"] = bool(timestamps.is_monotonic_increasing)

    summary = {
        "columns": list(df.columns),
        "missing_columns": missing_columns,
        "duplicate_count": duplicate_count,
        "target_summary": target_summary,
        "timestamp_summary": timestamp_summary,
        "leakage_columns": leakage_columns,
    }

    return DatasetValidationResult(
        dataset_name=schema.dataset_name,
        row_count=int(len(df)),
        column_count=int(len(df.columns)),
        passed=not errors,
        errors=errors,
        warnings=warnings,
        summary=summary,
    )
