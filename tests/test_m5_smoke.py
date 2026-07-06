from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m5_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m5_repair_engine.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M5 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m5_repair_engine_before_after.json"
    report_path = root / "reports" / "milestone_5_repair_engine_before_after.md"
    unsafe_plot = root / "reports" / "figures" / "m5_unsafe_auto_decision_rate.png"
    automation_plot = root / "reports" / "figures" / "m5_automation_tradeoff.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert unsafe_plot.exists()
    assert automation_plot.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M5_REPAIR_ENGINE_AND_BEFORE_AFTER_BENCHMARK"
    assert payload["m5_reliability_summary"]["healthcare_unsafe_rate_reduced"] is True
    assert payload["m5_reliability_summary"]["energy_unsafe_rate_reduced"] is True
