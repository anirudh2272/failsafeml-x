from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m2_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m2_uncertainty_calibration.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M2 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m2_uncertainty_calibration.json"
    report_path = root / "reports" / "milestone_2_uncertainty_calibration.md"
    calibration_plot = root / "reports" / "figures" / "m2_healthcare_calibration.png"
    interval_plot = root / "reports" / "figures" / "m2_energy_prediction_intervals.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert calibration_plot.exists()
    assert interval_plot.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M2_UNCERTAINTY_AND_CALIBRATION_ENGINE"
