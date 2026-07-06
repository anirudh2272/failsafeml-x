.PHONY: test m1 m2 m3 m4 m5 m6 m7 m8 all api dashboard

test:
	python -m pytest

m1:
	python scripts/run_m1_baseline.py

m2:
	python scripts/run_m2_uncertainty_calibration.py

m3:
	python scripts/run_m3_drift_ood.py

m4:
	python scripts/run_m4_failure_taxonomy.py

m5:
	python scripts/run_m5_repair_engine.py

m6:
	python scripts/run_m6_rl_router.py

m7:
	python scripts/run_m7_api_dashboard_demo.py

m8:
	python scripts/run_m8_final_packaging.py

all: test m1 m2 m3 m4 m5 m6 m7 m8

api:
	uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload --port 8000

dashboard:
	PYTHONPATH=src streamlit run apps/streamlit_dashboard.py
