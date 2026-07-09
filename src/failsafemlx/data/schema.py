from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSchema:
    dataset_name: str
    task_type: str
    required_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    target_column: str
    timestamp_column: str | None = None
    allowed_target_values: list[Any] | None = None
    imbalance_threshold: float = 0.15
    leakage_keywords: list[str] = field(
        default_factory=lambda: ["target_leak", "label_copy", "outcome_future", "future_result"]
    )


def load_dataset_schema(path: str | Path) -> DatasetSchema:
    schema_path = Path(path)
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    return DatasetSchema(
        dataset_name=str(payload["dataset_name"]),
        task_type=str(payload["task_type"]),
        required_columns=list(payload.get("required_columns", [])),
        numeric_columns=list(payload.get("numeric_columns", [])),
        categorical_columns=list(payload.get("categorical_columns", [])),
        target_column=str(payload["target_column"]),
        timestamp_column=payload.get("timestamp_column"),
        allowed_target_values=payload.get("allowed_target_values"),
        imbalance_threshold=float(payload.get("imbalance_threshold", 0.15)),
        leakage_keywords=list(payload.get("leakage_keywords", []))
        or ["target_leak", "label_copy", "outcome_future", "future_result"],
    )
