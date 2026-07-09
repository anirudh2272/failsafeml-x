# Software Engineering and CI/CD Notes

FailSafeML-X is structured as a research-grade ML reliability system with a lightweight software engineering layer for testing, validation, reproducibility, and review.

## Repository Design

The project separates:

- `src/failsafemlx/` for reusable Python modules
- `scripts/` for milestone runners
- `tests/` for pytest validation
- `reports/` for milestone reports
- `experiments/results/` for generated JSON outputs
- `apps/` for Streamlit dashboard code
- `docs/` for architecture and operational documentation

## CI/CD Design

The GitHub Actions workflow validates the project on push, pull request, and manual workflow dispatch.

The CI workflow runs:

1. dependency installation
2. pytest validation
3. M8 final packaging validation
4. M9 software-quality validation
5. Docker build validation

## Local CI

Run:

```bash
python scripts/local_ci.py
```

Optional Docker build validation:

```bash
python scripts/local_ci.py --docker
```

## Project Structure Validation

Run:

```bash
python scripts/validate_project_structure.py
```

This checks required files, README hygiene, Git tracking hygiene, key scripts, key reports, API/dashboard entrypoints, and packaging files.

## Testing Strategy

The project uses pytest for:

- data generation validation
- metric validation
- calibration and conformal prediction checks
- drift and OOD checks
- failure taxonomy checks
- repair engine validation
- RL router validation
- API/serving validation
- final packaging validation
- M9 structure validation

## Scope

M9 adds CI/CD and software engineering hardening. It does not claim production deployment, cloud hosting, production monitoring, or safety certification.


## M12 Note

Local CI also runs M12 distributed drift validation.
