# Dataset Loader and Validation Layer

Milestone 15C adds a lightweight dataset ingestion and validation layer to FailSafeML-X. The goal is to make the project ready to evaluate real CSV datasets before reliability scoring, rather than relying only on synthetic benchmark generation.

## What It Checks

The validator performs dependency-light checks for:

- required columns
- numeric columns
- categorical columns
- target-column existence
- missing values
- duplicate rows
- invalid target values
- severe class imbalance
- leakage-like column names
- timestamp parsing and ordering for time-series datasets

## Why This Matters

FailSafeML-X is a reliability layer. Reliability evaluation is only meaningful if the input dataset is structurally valid. Dataset validation helps prevent misleading calibration, drift, uncertainty, and repair-routing results caused by broken or leaky data.

## How to Run

```bash
python scripts/run_m15c_dataset_validation.py
```

Then run:

```bash
python -m pytest
python scripts/local_ci.py
```

## Scope and Limitations

This is a lightweight local validation layer. It does not claim full production data governance, live data contracts, feature-store validation, Great Expectations integration, or Pandera integration. Those tools can be added later as optional integrations.
