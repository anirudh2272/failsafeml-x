# Milestone 15C — Dataset Loader and Validator Layer

## Objective

Add a lightweight, dependency-minimal dataset ingestion and validation layer so FailSafeML-X can evaluate CSV datasets before reliability scoring.

## Validation Summary

- Passed: True
- Datasets checked: 2
- Total errors: 0
- Total warnings: 0

## Dataset Results

### healthcare_sample

- Rows: 10
- Columns: 6
- Passed: True
- Errors: 0
- Warnings: 0

### energy_sample

- Rows: 10
- Columns: 5
- Passed: True
- Errors: 0
- Warnings: 0

## Checks Implemented

- CSV loading
- JSON schema loading
- required-column validation
- numeric-column validation
- categorical-column validation
- target-column validation
- missing-value detection
- duplicate-row detection
- class-imbalance warning
- leakage-like column detection
- timestamp parsing and ordering checks

## Honest Limitation

This milestone adds lightweight local dataset validation. It does not claim full data-quality governance, production data contracts, Great Expectations integration, or live feature-store validation.
