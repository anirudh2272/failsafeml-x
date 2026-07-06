from __future__ import annotations

from pathlib import Path

from failsafemlx.packaging.final_artifacts import (
    KEY_ARTIFACTS,
    MILESTONES,
    build_final_packaging_summary,
    generate_m8_artifacts,
    write_architecture_figure,
)


def test_final_milestone_registry_contains_m1_to_m8():
    ids = [item["id"] for item in MILESTONES]
    assert ids == ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]
    assert all(item["status"] == "Complete" for item in MILESTONES)


def test_key_artifacts_include_release_files():
    assert "README.md" in KEY_ARTIFACTS
    assert "Dockerfile" in KEY_ARTIFACTS
    assert "docker-compose.yml" in KEY_ARTIFACTS
    assert "docs/demo_script.md" in KEY_ARTIFACTS
    assert "docs/resume_bullets.md" in KEY_ARTIFACTS


def test_release_summary_schema_uses_existing_root():
    root = Path(__file__).resolve().parents[1]
    summary = build_final_packaging_summary(root)
    assert summary["project"] == "FailSafeML-X"
    assert summary["milestone"] == "M8_FINAL_PACKAGING_AND_PORTFOLIO_RELEASE"
    assert summary["release_readiness"]["dockerfile_present"] is True
    assert summary["release_readiness"]["gitignore_present"] is True


def test_architecture_figure_writer(tmp_path):
    path = write_architecture_figure(tmp_path / "arch.png")
    assert path.exists()
    assert path.stat().st_size > 1000


def test_generate_m8_artifacts_in_temp_repo(tmp_path):
    for relative in ["Dockerfile", "docker-compose.yml", ".gitignore", ".env.example", "README.md"]:
        (tmp_path / relative).write_text("placeholder", encoding="utf-8")
    for relative in [
        "docs/architecture.md",
        "docs/demo_script.md",
        "docs/github_release_checklist.md",
        "docs/resume_bullets.md",
        "docs/patent_screening_memo.md",
    ]:
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_text("placeholder", encoding="utf-8")
    summary = generate_m8_artifacts(tmp_path)
    assert summary["status"] == "completed"
    assert (tmp_path / "experiments/results/m8_final_packaging.json").exists()
    assert (tmp_path / "reports/milestone_8_final_packaging.md").exists()
    assert (tmp_path / "reports/final_project_card.md").exists()
    assert (tmp_path / "reports/figures/m8_system_architecture.png").exists()
