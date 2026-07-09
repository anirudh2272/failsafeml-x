from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate_advanced_platform import validate_advanced_platform

RESULT_PATH = PROJECT_ROOT / "experiments/results/m20_final_advanced_packaging.json"
REPORT_PATH = PROJECT_ROOT / "reports/milestone_20_final_advanced_packaging.md"
CARD_PATH = PROJECT_ROOT / "reports/advanced_project_card.md"
SVG_PATH = PROJECT_ROOT / "reports/figures/advanced_platform_architecture.svg"


def write_architecture_svg() -> None:
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1120\" height=\"640\" viewBox=\"0 0 1120 640\" role=\"img\" aria-label=\"FailSafeML-X advanced architecture\">
  <rect width=\"1120\" height=\"640\" fill=\"#ffffff\"/>
  <style>
    .box { fill: #f8fafc; stroke: #334155; stroke-width: 1.5; rx: 14; }
    .core { fill: #eef2ff; stroke: #3730a3; stroke-width: 1.7; rx: 14; }
    .safe { fill: #ecfdf5; stroke: #047857; stroke-width: 1.7; rx: 14; }
    .warn { fill: #fff7ed; stroke: #c2410c; stroke-width: 1.7; rx: 14; }
    .text { font-family: Arial, sans-serif; font-size: 16px; fill: #0f172a; }
    .small { font-family: Arial, sans-serif; font-size: 13px; fill: #334155; }
    .title { font-family: Arial, sans-serif; font-size: 26px; font-weight: 700; fill: #0f172a; }
    .arrow { stroke: #475569; stroke-width: 2; marker-end: url(#arrow); }
  </style>
  <defs><marker id=\"arrow\" markerWidth=\"10\" markerHeight=\"10\" refX=\"8\" refY=\"3\" orient=\"auto\"><path d=\"M0,0 L0,6 L9,3 z\" fill=\"#475569\"/></marker></defs>
  <text x=\"40\" y=\"45\" class=\"title\">FailSafeML-X — Advanced Reliability Platform Prototype</text>
  <rect x=\"40\" y=\"90\" width=\"210\" height=\"90\" class=\"box\"/><text x=\"62\" y=\"125\" class=\"text\">Data + RAG Inputs</text><text x=\"62\" y=\"150\" class=\"small\">CSV validation, schemas, docs</text>
  <rect x=\"310\" y=\"90\" width=\"230\" height=\"90\" class=\"core\"/><text x=\"332\" y=\"125\" class=\"text\">Reliability Audit Core</text><text x=\"332\" y=\"150\" class=\"small\">calibration, drift, OOD, trust</text>
  <rect x=\"600\" y=\"90\" width=\"230\" height=\"90\" class=\"core\"/><text x=\"622\" y=\"125\" class=\"text\">Failure + Repair Router</text><text x=\"622\" y=\"150\" class=\"small\">failure IDs, repair actions</text>
  <rect x=\"890\" y=\"90\" width=\"190\" height=\"90\" class=\"safe\"/><text x=\"912\" y=\"125\" class=\"text\">Routing Decision</text><text x=\"912\" y=\"150\" class=\"small\">accept, defer, review</text>
  <line x1=\"250\" y1=\"135\" x2=\"310\" y2=\"135\" class=\"arrow\"/><line x1=\"540\" y1=\"135\" x2=\"600\" y2=\"135\" class=\"arrow\"/><line x1=\"830\" y1=\"135\" x2=\"890\" y2=\"135\" class=\"arrow\"/>
  <rect x=\"40\" y=\"250\" width=\"240\" height=\"100\" class=\"box\"/><text x=\"62\" y=\"285\" class=\"text\">Optional RAGOps Layer</text><text x=\"62\" y=\"310\" class=\"small\">retrieval, citations, stale evidence</text><text x=\"62\" y=\"330\" class=\"small\">prompt-injection in context</text>
  <rect x=\"330\" y=\"250\" width=\"230\" height=\"100\" class=\"box\"/><text x=\"352\" y=\"285\" class=\"text\">Provider-Aware Agent</text><text x=\"352\" y=\"310\" class=\"small\">local default, external disabled</text><text x=\"352\" y=\"330\" class=\"small\">OpenAI/Bedrock-style adapters</text>
  <rect x=\"610\" y=\"250\" width=\"220\" height=\"100\" class=\"safe\"/><text x=\"632\" y=\"285\" class=\"text\">Monitoring + Registry</text><text x=\"632\" y=\"310\" class=\"small\">metrics, alerts, risk card</text><text x=\"632\" y=\"330\" class=\"small\">Prometheus/Grafana-ready</text>
  <rect x=\"880\" y=\"250\" width=\"200\" height=\"100\" class=\"warn\"/><text x=\"902\" y=\"285\" class=\"text\">Templates Only</text><text x=\"902\" y=\"310\" class=\"small\">Helm, Terraform, cloud AI</text><text x=\"902\" y=\"330\" class=\"small\">no live deployment claim</text>
  <line x1=\"160\" y1=\"250\" x2=\"160\" y2=\"180\" class=\"arrow\"/><line x1=\"445\" y1=\"250\" x2=\"445\" y2=\"180\" class=\"arrow\"/><line x1=\"720\" y1=\"250\" x2=\"720\" y2=\"180\" class=\"arrow\"/><line x1=\"980\" y1=\"250\" x2=\"980\" y2=\"180\" class=\"arrow\"/>
  <rect x=\"145\" y=\"430\" width=\"830\" height=\"105\" class=\"safe\"/><text x=\"175\" y=\"465\" class=\"text\">Final Safety Boundary</text><text x=\"175\" y=\"492\" class=\"small\">No paid APIs, no credentials, no GPU, no external vector DB, no live cloud deployment required for local CI.</text><text x=\"175\" y=\"517\" class=\"small\">Honest output: reliability envelope, model/risk cards, monitoring artifacts, docs, templates, and fine-tuning scaffold.</text>
  <line x1=\"560\" y1=\"350\" x2=\"560\" y2=\"430\" class=\"arrow\"/>
</svg>
"""
    SVG_PATH.write_text(svg, encoding="utf-8")


def _safe_markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def write_advanced_project_card(result: dict) -> None:
    CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    card = f"""# FailSafeML-X Advanced Project Card

Generated: {datetime.now(timezone.utc).isoformat()}

## Final Positioning

FailSafeML-X is a locally validated, model-agnostic ML reliability platform prototype. It wraps model predictions and RAG-style retrieved context with reliability checks, trust scoring, failure diagnosis, repair routing, human-review routing, monitoring-ready metrics, and reproducible documentation.

## Capabilities

{_safe_markdown_list(result.get('capability_tags', []))}

## What is validated locally

- Milestone scripts through M20 are present and checked.
- JSON result artifacts are generated for the advanced milestones.
- Reports, architecture docs, model card, model risk card, monitoring files, infrastructure templates, managed-cloud templates, and fine-tuning scaffold files are present.
- The default behavior remains local/offline and CI-safe.

## Honest limitations

{_safe_markdown_list(result.get('honest_limitations', []))}

## Recruiter-safe summary

Built FailSafeML-X, a model-agnostic ML reliability platform prototype with calibration, conformal uncertainty, drift/OOD detection, failure taxonomy, repair routing, RAGOps reliability auditing, provider-aware agentic explanations, dataset validation, model-risk documentation, monitoring artifacts, Terraform/Helm templates, managed-cloud inference templates, and a LoRA/PEFT fine-tuning scaffold.
"""
    CARD_PATH.write_text(card, encoding="utf-8")


def write_report(result: dict) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    summary = result.get("result_status_summary", {})
    report = f"""# Milestone 20 — Final Advanced Packaging

## Status

Passed: `{result['passed']}`

## Validation Summary

- Scripts checked: `{result['scripts_checked']}`
- Core paths checked: `{result['core_paths_checked']}`
- Module directories checked: `{result['module_dirs_checked']}`
- Result status summary: `{summary}`

## Capabilities Included

{_safe_markdown_list(result.get('capability_tags', []))}

## Generated Artifacts

- `experiments/results/m20_final_advanced_packaging.json`
- `reports/milestone_20_final_advanced_packaging.md`
- `reports/advanced_project_card.md`
- `reports/figures/advanced_platform_architecture.svg`
- `docs/advanced_platform_architecture.md`
- `docs/recruiter_walkthrough.md`
- `docs/research_summary.md`

## Honest Limitations

{_safe_markdown_list(result.get('honest_limitations', []))}

## Final Claim

FailSafeML-X is a locally validated, model-agnostic ML reliability platform prototype with reliability auditing, repair routing, optional RAGOps auditing, provider-aware explanations, monitoring-ready artifacts, deployment templates, managed-cloud templates, and fine-tuning scaffolds.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    # Create generated docs first, then validate that they exist and contain expected claims.
    write_architecture_svg()
    preliminary = validate_advanced_platform()
    write_advanced_project_card(preliminary)
    result = validate_advanced_platform()
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(result)

    print(f"Wrote {RESULT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {CARD_PATH}")
    print(f"Wrote {SVG_PATH}")

    if not result["passed"]:
        print(json.dumps(result, indent=2))
        raise SystemExit(1)

    print("M20 completed successfully.")


if __name__ == "__main__":
    main()
