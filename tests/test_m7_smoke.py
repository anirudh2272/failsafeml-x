from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m7_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m7_api_dashboard_demo.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M7 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m7_api_dashboard_demo.json"
    report_path = root / "reports" / "milestone_7_api_dashboard_demo.md"
    plot_path = root / "reports" / "figures" / "m7_api_router_action_summary.png"
    dashboard_path = root / "apps" / "streamlit_dashboard.py"
    api_path = root / "src" / "failsafemlx" / "serving" / "fastapi_app.py"
    assert metrics_path.exists()
    assert report_path.exists()
    assert plot_path.exists()
    assert dashboard_path.exists()
    assert api_path.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M7_API_DASHBOARD_AND_DEMO"
    assert payload["m7_reliability_summary"]["api_contract_defined"] is True
