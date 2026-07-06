from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m3_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m3_drift_ood.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M3 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m3_drift_ood.json"
    report_path = root / "reports" / "milestone_3_drift_ood.md"
    healthcare_plot = root / "reports" / "figures" / "m3_healthcare_feature_drift.png"
    energy_plot = root / "reports" / "figures" / "m3_energy_feature_drift.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert healthcare_plot.exists()
    assert energy_plot.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M3_DRIFT_AND_OOD_DETECTION"
    assert payload["datasets"]["healthcare_classification"]["drift_summary"]["feature_drift_detected"] is True
    assert payload["datasets"]["energy_timeseries"]["drift_summary"]["feature_drift_detected"] is True
