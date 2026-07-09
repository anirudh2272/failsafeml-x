from __future__ import annotations

from pathlib import Path

import pandas as pd


class DatasetLoadError(ValueError):
    """Raised when a dataset cannot be loaded safely."""


def load_csv_dataset(path: str | Path) -> pd.DataFrame:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise DatasetLoadError(f"Dataset file does not exist: {dataset_path}")
    if dataset_path.suffix.lower() != ".csv":
        raise DatasetLoadError(f"Only CSV datasets are supported by this lightweight loader: {dataset_path}")
    try:
        return pd.read_csv(dataset_path)
    except Exception as exc:  # pragma: no cover - defensive wrapper
        raise DatasetLoadError(f"Could not load CSV dataset {dataset_path}: {exc}") from exc
