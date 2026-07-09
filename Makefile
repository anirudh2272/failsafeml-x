.PHONY: m19 m18 m17 m16 m15e m15d m15c m15b m15a test m1 m2 m3 m4 m5 m6 m7 m8 all api dashboard m14

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

all: test m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 m11 m12 m13

api:
	uvicorn failsafemlx.serving.fastapi_app:app --app-dir src --reload --port 8000

dashboard:
	PYTHONPATH=src streamlit run apps/streamlit_dashboard.py


m9:
	python scripts/run_m9_cicd_software_quality.py

local-ci:
	python scripts/local_ci.py

m10:
	python scripts/run_m10_agentic_reliability.py


m11:
	python scripts/run_m11_airflow_orchestration.py

m12:
	python scripts/run_m12_spark_drift_pipeline.py

m13:
	python scripts/run_m13_ai_security.py

m14:
	python scripts/run_m14_inference_optimization.py


m15a:
	python scripts/run_m15a_provider_abstraction.py

m15b:
	python scripts/run_m15b_ragops_reliability.py

m15c:
	python scripts/run_m15c_dataset_validation.py

m15d:
	python scripts/run_m15d_provider_agent_integration.py


m15e:
	python scripts/run_m15e_experiment_registry.py


m16:
	python scripts/run_m16_monitoring_metrics.py


m17:
	python scripts/run_m17_infra_templates.py


m18:
	python scripts/run_m18_cloud_ai_templates.py


m19:
	python scripts/run_m19_finetuning_scaffold.py


m20:
	python scripts/run_m20_final_advanced_packaging.py
