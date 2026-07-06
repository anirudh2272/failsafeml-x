from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m4_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m4_failure_taxonomy.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M4 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m4_failure_taxonomy_trust_score.json"
    report_path = root / "reports" / "milestone_4_failure_taxonomy_trust_score.md"
    trust_plot = root / "reports" / "figures" / "m4_trust_scores.png"
    failure_plot = root / "reports" / "figures" / "m4_failure_counts.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert trust_plot.exists()
    assert failure_plot.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M4_FAILURE_TAXONOMY_AND_TRUST_SCORE"
    assert payload["datasets"]["healthcare_classification"]["trust_summary"]["num_failures"] >= 1
    assert payload["datasets"]["energy_timeseries"]["trust_summary"]["num_failures"] >= 1
