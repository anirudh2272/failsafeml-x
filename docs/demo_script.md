# Demo Script

## 1. Explain the problem

Machine-learning systems can produce confident but unreliable predictions when calibration degrades, data distribution changes, inputs become out-of-distribution, or the model ages over time.

## 2. Explain the system

FailSafeML-X audits each prediction using calibration, conformal uncertainty, drift/OOD signals, failure taxonomy, trust scoring, repair planning, and an RL-style repair router.

## 3. Run the validation

```bash
python -m pytest
python scripts/run_m1_baseline.py
python scripts/run_m2_uncertainty_calibration.py
python scripts/run_m3_drift_ood.py
python scripts/run_m4_failure_taxonomy.py
python scripts/run_m5_repair_engine.py
python scripts/run_m6_rl_router.py
python scripts/run_m7_api_dashboard_demo.py
python scripts/run_m8_final_packaging.py
```

## 4. Show generated reports

Open the `reports/` folder and show the milestone reports and plots.

## 5. Show API

```bash
uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## 6. Show dashboard

```bash
PYTHONPATH=src streamlit run apps/streamlit_dashboard.py
```

## 7. Honest conclusion

The project demonstrates a reliability and repair layer on deterministic synthetic benchmarks. Real deployment would require domain data, human-labeled validation, security hardening, monitoring integration, and external review.
