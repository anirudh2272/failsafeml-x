from __future__ import annotations

from pathlib import Path

import pandas as pd

from failsafemlx.data.loaders import load_csv_dataset
from failsafemlx.data.schema import load_dataset_schema
from failsafemlx.data.validators import validate_dataset
from scripts.run_m15c_dataset_validation import run_m15c


def test_schema_loader_reads_healthcare_schema():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    assert schema.dataset_name == "healthcare_sample"
    assert schema.target_column == "risk_label"
    assert "age" in schema.numeric_columns


def test_csv_loader_reads_sample_dataset():
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    assert len(df) >= 10
    assert "risk_label" in df.columns


def test_healthcare_sample_validation_passes():
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    result = validate_dataset(df, schema)
    assert result.passed is True
    assert result.errors == []


def test_missing_required_column_is_error():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    df = load_csv_dataset("data/samples/healthcare_sample.csv").drop(columns=["glucose"])
    result = validate_dataset(df, schema)
    assert result.passed is False
    assert any("Missing required columns" in error for error in result.errors)


def test_non_numeric_value_is_error():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    df["age"] = df["age"].astype("object")
    df.loc[0, "age"] = "not-a-number"
    result = validate_dataset(df, schema)
    assert result.passed is False
    assert any("non-numeric" in error for error in result.errors)


def test_duplicate_rows_are_warning_not_error():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    result = validate_dataset(df, schema)
    assert result.passed is True
    assert any("Duplicate rows" in warning for warning in result.warnings)


def test_class_imbalance_is_warning():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    df["risk_label"] = 0
    df.loc[0, "risk_label"] = 1
    result = validate_dataset(df, schema)
    assert result.passed is True
    assert any("class imbalance" in warning for warning in result.warnings)


def test_leakage_like_column_is_warning():
    schema = load_dataset_schema("data/schemas/healthcare_schema.json")
    df = load_csv_dataset("data/samples/healthcare_sample.csv")
    df["target_leak_score"] = df["risk_label"]
    result = validate_dataset(df, schema)
    assert result.passed is True
    assert any("leakage" in warning.lower() for warning in result.warnings)


def test_timestamp_ordering_issue_is_warning():
    schema = load_dataset_schema("data/schemas/energy_schema.json")
    df = load_csv_dataset("data/samples/energy_sample.csv")
    df = df.iloc[::-1].reset_index(drop=True)
    result = validate_dataset(df, schema)
    assert result.passed is True
    assert any("not sorted" in warning for warning in result.warnings)


def test_m15c_runner_writes_outputs():
    payload = run_m15c()
    assert payload["passed"] is True
    assert Path("experiments/results/m15c_dataset_validation.json").exists()
    assert Path("reports/milestone_15c_dataset_validation.md").exists()
