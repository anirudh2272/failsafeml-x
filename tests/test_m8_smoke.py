from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m8_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m8_final_packaging.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M8 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m8_final_packaging.json"
    report_path = root / "reports" / "milestone_8_final_packaging.md"
    card_path = root / "reports" / "final_project_card.md"
    figure_path = root / "reports" / "figures" / "m8_system_architecture.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert card_path.exists()
    assert figure_path.exists()
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M8_FINAL_PACKAGING_AND_PORTFOLIO_RELEASE"
    assert len(payload["completed_milestones"]) == 8
