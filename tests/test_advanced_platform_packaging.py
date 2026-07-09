from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.validate_advanced_platform import validate_advanced_platform

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_advanced_docs_exist_and_are_honest():
    required = [
        PROJECT_ROOT / "docs/advanced_platform_architecture.md",
        PROJECT_ROOT / "docs/recruiter_walkthrough.md",
        PROJECT_ROOT / "docs/research_summary.md",
    ]
    for path in required:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8").lower()
        assert "failsafeml-x" in text
        assert "model-agnostic" in text or path.name == "recruiter_walkthrough.md"
        assert "not" in text


def test_validate_advanced_platform_contract():
    result = validate_advanced_platform()
    assert result["passed"] is True, result.get("errors")
    assert result["scripts_checked"] >= 24
    assert "optional RAGOps reliability auditing" in result["capability_tags"]
    assert any("not production" in item.lower() or "not production-certified" in item.lower() for item in result["honest_limitations"])


def test_m20_runner_writes_artifacts():
    subprocess.run([sys.executable, "scripts/run_m20_final_advanced_packaging.py"], cwd=PROJECT_ROOT, check=True)
    result_path = PROJECT_ROOT / "experiments/results/m20_final_advanced_packaging.json"
    report_path = PROJECT_ROOT / "reports/milestone_20_final_advanced_packaging.md"
    card_path = PROJECT_ROOT / "reports/advanced_project_card.md"
    svg_path = PROJECT_ROOT / "reports/figures/advanced_platform_architecture.svg"

    for path in [result_path, report_path, card_path, svg_path]:
        assert path.exists(), path

    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["passed"] is True, result.get("errors")
    assert "M20_FINAL_ADVANCED_PACKAGING" == result["milestone"]
    assert "LoRA/PEFT fine-tuning scaffold".lower() in card_path.read_text(encoding="utf-8").lower()


def test_local_ci_includes_m20():
    text = (PROJECT_ROOT / "scripts/local_ci.py").read_text(encoding="utf-8")
    assert "run_m20_final_advanced_packaging.py" in text


def test_github_actions_includes_m20_if_present():
    workflow = PROJECT_ROOT / ".github/workflows/ci.yml"
    if workflow.exists():
        assert "run_m20_final_advanced_packaging.py" in workflow.read_text(encoding="utf-8")
