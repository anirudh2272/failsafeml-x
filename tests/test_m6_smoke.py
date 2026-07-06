from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_m6_script_runs_and_writes_outputs():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "run_m6_rl_router.py"
    result = subprocess.run([sys.executable, str(script)], cwd=root, text=True, capture_output=True, check=True)
    assert "M6 completed successfully" in result.stdout
    metrics_path = root / "experiments" / "results" / "m6_rl_repair_router.json"
    report_path = root / "reports" / "milestone_6_rl_repair_router.md"
    action_plot = root / "reports" / "figures" / "m6_router_action_mix.png"
    reward_plot = root / "reports" / "figures" / "m6_router_reward_comparison.png"
    assert metrics_path.exists()
    assert report_path.exists()
    assert action_plot.exists()
    assert reward_plot.exists()
    payload = json.loads(metrics_path.read_text())
    assert payload["status"] == "completed"
    assert payload["milestone"] == "M6_RL_REPAIR_ROUTER"
    assert payload["m6_reliability_summary"]["rl_reward_not_worse_than_rule"] is True
