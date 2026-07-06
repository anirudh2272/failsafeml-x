from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from failsafemlx.utils.io import ensure_dir, write_json

MILESTONES: list[dict[str, str]] = [
    {"id": "M1", "name": "Baseline reliability benchmark", "status": "Complete"},
    {"id": "M2", "name": "Uncertainty and calibration engine", "status": "Complete"},
    {"id": "M3", "name": "Drift and OOD detection", "status": "Complete"},
    {"id": "M4", "name": "Failure taxonomy and trust score", "status": "Complete"},
    {"id": "M5", "name": "Repair engine and before/after benchmark", "status": "Complete"},
    {"id": "M6", "name": "RL-style repair router", "status": "Complete"},
    {"id": "M7", "name": "API, dashboard, and demo layer", "status": "Complete"},
    {"id": "M8", "name": "Final packaging, Docker, docs, and portfolio artifacts", "status": "Complete"},
]

KEY_ARTIFACTS: dict[str, str] = {
    "README.md": "Polished GitHub README",
    "Dockerfile": "Container image for the FastAPI reliability service",
    "docker-compose.yml": "Local API and dashboard composition",
    "Makefile": "Convenience commands for tests, milestones, API, and dashboard",
    "docs/architecture.md": "Architecture explanation",
    "docs/demo_script.md": "Walkthrough script for recruiters, professors, and demos",
    "docs/github_release_checklist.md": "Public-release checklist",
    "docs/resume_bullets.md": "Resume and portfolio positioning",
    "docs/patent_screening_memo.md": "Preliminary non-legal patent-screening note",
}


def build_final_packaging_summary(root: Path) -> dict[str, Any]:
    reports_dir = root / "reports"
    results_dir = root / "experiments/results"
    generated_reports = sorted(str(path.relative_to(root)) for path in reports_dir.glob("milestone_*.md")) if reports_dir.exists() else []
    generated_results = sorted(str(path.relative_to(root)) for path in results_dir.glob("m*_*.json")) if results_dir.exists() else []
    return {
        "project": "FailSafeML-X",
        "milestone": "M8_FINAL_PACKAGING_AND_PORTFOLIO_RELEASE",
        "status": "completed",
        "honest_claim": "Final repository packaging, Docker files, documentation, demo script, and portfolio artifacts are prepared. This is still a research prototype, not a certified production safety system.",
        "completed_milestones": MILESTONES,
        "key_artifacts": KEY_ARTIFACTS,
        "generated_reports_detected": generated_reports,
        "generated_results_detected": generated_results,
        "release_readiness": {
            "tests_defined": True,
            "dockerfile_present": (root / "Dockerfile").exists(),
            "compose_present": (root / "docker-compose.yml").exists(),
            "gitignore_present": (root / ".gitignore").exists(),
            "env_example_present": (root / ".env.example").exists(),
            "readme_present": (root / "README.md").exists(),
            "docs_present": all((root / path).exists() for path in [
                "docs/architecture.md",
                "docs/demo_script.md",
                "docs/github_release_checklist.md",
                "docs/resume_bullets.md",
                "docs/patent_screening_memo.md",
            ]),
        },
        "next_action": "Create a GitHub repository, commit the cleaned final package, add screenshots, and use the README/demo script for portfolio presentation.",
    }


def write_architecture_figure(path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    width, height = 1500, 520
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title = "FailSafeML-X Reliability Decision Envelope"
    subtitle = "Goal: convert raw ML predictions into auditable trust, failure, repair, and routing decisions."
    draw.text((width // 2, 55), title, anchor="mm")
    draw.text((width // 2, height - 70), subtitle, anchor="mm")

    labels = [
        "Prediction",
        "Calibration\n+ Conformal",
        "Drift/OOD",
        "Failure\nTaxonomy",
        "Trust Score",
        "Repair\nEngine",
        "RL Router",
        "API/Dashboard",
    ]
    box_w, box_h = 135, 78
    gap = 42
    total_w = len(labels) * box_w + (len(labels) - 1) * gap
    x0 = (width - total_w) // 2
    y0 = 215
    for i, label in enumerate(labels):
        x = x0 + i * (box_w + gap)
        draw.rectangle((x, y0, x + box_w, y0 + box_h), outline="black", width=3)
        lines = label.split("\n")
        if len(lines) == 1:
            draw.text((x + box_w // 2, y0 + box_h // 2), lines[0], anchor="mm")
        else:
            draw.text((x + box_w // 2, y0 + box_h // 2 - 10), lines[0], anchor="mm")
            draw.text((x + box_w // 2, y0 + box_h // 2 + 12), lines[1], anchor="mm")
        if i < len(labels) - 1:
            x_start = x + box_w + 5
            x_end = x + box_w + gap - 5
            y_mid = y0 + box_h // 2
            draw.line((x_start, y_mid, x_end, y_mid), fill="black", width=2)
            draw.polygon([(x_end, y_mid), (x_end - 10, y_mid - 6), (x_end - 10, y_mid + 6)], fill="black")
    image.save(path)
    return path


def write_m8_report(summary: dict[str, Any], path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    lines = [
        "# Milestone 8 — Final Packaging and Portfolio Release",
        "",
        "## Objective",
        "",
        "Package FailSafeML-X as a GitHub-ready research and portfolio prototype with Docker support, final documentation, release checklist, demo script, and honest project positioning.",
        "",
        "## Completed Milestones",
        "",
        "| Milestone | Component | Status |",
        "|---|---|---|",
        *[f"| {item['id']} | {item['name']} | {item['status']} |" for item in summary["completed_milestones"]],
        "",
        "## Key Packaging Artifacts",
        "",
        *[f"- `{path}` — {description}" for path, description in summary["key_artifacts"].items()],
        "",
        "## Release Readiness",
        "",
        *[f"- {key}: {value}" for key, value in summary["release_readiness"].items()],
        "",
        "## Generated Reports Detected",
        "",
        *([f"- `{path}`" for path in summary["generated_reports_detected"]] or ["- None detected yet"]),
        "",
        "## Honest Limitation",
        "",
        "M8 packages the prototype for reproducible demonstration. It does not certify the system for safety-critical production use, does not prove broad novelty, and does not claim patentability.",
        "",
        "## Next Action",
        "",
        summary["next_action"],
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_project_card(path: str | Path) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    text = """# FailSafeML-X Project Card

## One-Line Summary

FailSafeML-X is a self-healing ML reliability prototype that turns raw model predictions into auditable trust scores, failure diagnoses, repair plans, and deployment routing decisions.

## What It Demonstrates

- Multi-domain ML benchmarking
- Calibration and conformal uncertainty
- Drift and OOD detection
- Failure taxonomy and trust scoring
- Repair-policy execution
- RL-style decision routing
- FastAPI and Streamlit demo layer
- Docker-ready final packaging

## Best Use

Portfolio, research discussion, PhD application support, and ML systems interview demonstration.

## Not Claimed

Production safety certification, state-of-the-art benchmark performance, or confirmed patentability.
"""
    path.write_text(text, encoding="utf-8")
    return path


def generate_m8_artifacts(root: Path) -> dict[str, Any]:
    ensure_dir(root / "experiments/results")
    ensure_dir(root / "reports/figures")
    ensure_dir(root / "docs")
    summary = build_final_packaging_summary(root)
    arch_path = write_architecture_figure(root / "reports/figures/m8_system_architecture.png")
    summary["artifacts"] = {
        "m8_results": "experiments/results/m8_final_packaging.json",
        "m8_report": "reports/milestone_8_final_packaging.md",
        "project_card": "reports/final_project_card.md",
        "architecture_figure": str(arch_path.relative_to(root)),
    }
    result_path = write_json(summary, root / "experiments/results/m8_final_packaging.json")
    report_path = write_m8_report(summary, root / "reports/milestone_8_final_packaging.md")
    card_path = write_project_card(root / "reports/final_project_card.md")
    summary["written_paths"] = [str(path.relative_to(root)) for path in [result_path, report_path, card_path, arch_path]]
    return summary
