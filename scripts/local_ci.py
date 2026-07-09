from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("\n$ " + " ".join(command), flush=True)
    env = os.environ.copy()
    if "pytest" in command:
        env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True, env=env)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local CI checks for FailSafeML-X.")
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Also run local Docker build validation. Requires Docker to be installed and running.",
    )
    args = parser.parse_args()

    commands = [
        [sys.executable, "scripts/run_m8_final_packaging.py"],
        [sys.executable, "scripts/run_m9_cicd_software_quality.py"],
        [sys.executable, "scripts/run_m10_agentic_reliability.py"],
        [sys.executable, "scripts/run_m11_airflow_orchestration.py"],
        [sys.executable, "scripts/run_m12_spark_drift_pipeline.py"],
        [sys.executable, "scripts/run_m13_ai_security.py"],
        [sys.executable, "scripts/run_m14_inference_optimization.py"],
        [sys.executable, "scripts/run_m15a_provider_abstraction.py"],
        [sys.executable, "scripts/run_m15b_ragops_reliability.py"],
        [sys.executable, "scripts/run_m15c_dataset_validation.py"],
        [sys.executable, "scripts/run_m15d_provider_agent_integration.py"],
        [sys.executable, "scripts/run_m15e_experiment_registry.py"],
        [sys.executable, "scripts/run_m16_monitoring_metrics.py"],
        [sys.executable, "scripts/run_m17_infra_templates.py"],
        [sys.executable, "scripts/run_m18_cloud_ai_templates.py"],
        [sys.executable, "scripts/run_m19_finetuning_scaffold.py"],
        [sys.executable, "scripts/run_m20_final_advanced_packaging.py"],
        [sys.executable, "-m", "pytest"],
    ]

    for command in commands:
        run(command)

    if args.docker:
        run(["docker", "build", "-t", "failsafeml-x:local-ci", "."])

    print("\nLocal CI checks passed.")


if __name__ == "__main__":
    main()
