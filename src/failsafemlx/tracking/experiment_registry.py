from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
from typing import Any


@dataclass(frozen=True)
class GitSnapshot:
    """Best-effort git metadata captured without requiring a git repository."""

    commit: str
    branch: str
    dirty: bool
    available: bool


@dataclass(frozen=True)
class ExperimentRecord:
    """A dependency-light local experiment registry record.

    The record intentionally uses JSON-compatible fields so it can be stored in
    source control, attached to reports, or later imported into MLflow/DVC.
    """

    run_id: str
    project: str
    milestone: str
    dataset_name: str
    model_name: str
    created_at_utc: str
    metrics: dict[str, Any]
    reliability_summary: dict[str, Any]
    failure_counts: dict[str, int]
    repair_action_counts: dict[str, int]
    trust_score_summary: dict[str, float]
    warnings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)
    git: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run_git_command(args: list[str], project_root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return completed.stdout.strip()
    except Exception:
        return None


def capture_git_snapshot(project_root: str | Path = ".") -> GitSnapshot:
    root = Path(project_root)
    commit = _run_git_command(["rev-parse", "--short", "HEAD"], root)
    branch = _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], root)
    status = _run_git_command(["status", "--porcelain"], root)
    available = commit is not None and branch is not None
    return GitSnapshot(
        commit=commit or "unavailable",
        branch=branch or "unavailable",
        dirty=bool(status) if status is not None else False,
        available=available,
    )


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _summarize_trust_scores(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "mean": round(sum(values) / len(values), 4),
    }


def _int_dict(payload: dict[str, Any] | None) -> dict[str, int]:
    if not payload:
        return {}
    return {str(key): int(value) for key, value in sorted(payload.items())}


def build_experiment_record(
    *,
    milestone_results: dict[str, Any],
    project_root: str | Path = ".",
    run_id: str = "m15e_local_registry_run",
) -> ExperimentRecord:
    """Build a local registry record from existing milestone outputs.

    This function is intentionally schema-tolerant: it extracts the reliability
    fields available in current milestone JSON files without requiring a central
    tracking server or a live MLflow/DVC installation.
    """

    m15b = milestone_results.get("m15b", {})
    m15c = milestone_results.get("m15c", {})
    m15d = milestone_results.get("m15d", {})
    m14 = milestone_results.get("m14", {})

    rag_aggregate = m15b.get("aggregate", {}) if isinstance(m15b, dict) else {}
    dataset_results = m15c.get("dataset_results", []) if isinstance(m15c, dict) else []
    provider_cases = m15d.get("case_summaries", []) if isinstance(m15d, dict) else []

    dataset_errors = int(m15c.get("total_errors", 0)) if isinstance(m15c, dict) else 0
    dataset_warnings = int(m15c.get("total_warnings", 0)) if isinstance(m15c, dict) else 0
    dataset_count = int(m15c.get("dataset_count", len(dataset_results))) if isinstance(m15c, dict) else 0

    trust_values: list[float] = []
    if "average_trust_score" in rag_aggregate:
        trust_values.append(_safe_float(rag_aggregate.get("average_trust_score")))
    if isinstance(m15d, dict) and "average_trust_score" in m15d:
        trust_values.append(_safe_float(m15d.get("average_trust_score")))
    for case in provider_cases:
        if isinstance(case, dict) and "trust_score" in case:
            trust_values.append(_safe_float(case.get("trust_score")))

    failure_counts = _int_dict(rag_aggregate.get("failure_counts"))
    provider_failure_counts = _int_dict(m15d.get("failure_counts")) if isinstance(m15d, dict) else {}
    for failure_id, count in provider_failure_counts.items():
        failure_counts[failure_id] = failure_counts.get(failure_id, 0) + count

    repair_action_counts = _int_dict(rag_aggregate.get("repair_action_counts"))
    provider_repair_counts = _int_dict(m15d.get("repair_action_counts")) if isinstance(m15d, dict) else {}
    for action_id, count in provider_repair_counts.items():
        repair_action_counts[action_id] = repair_action_counts.get(action_id, 0) + count

    latency = {}
    benchmark = m14.get("benchmark", {}) if isinstance(m14, dict) else {}
    if isinstance(benchmark, dict):
        latency = benchmark.get("latency", {}) or {}

    git_snapshot = capture_git_snapshot(project_root)

    metrics = {
        "dataset_count": dataset_count,
        "dataset_validation_errors": dataset_errors,
        "dataset_validation_warnings": dataset_warnings,
        "rag_average_trust_score": _safe_float(rag_aggregate.get("average_trust_score")),
        "provider_agent_average_trust_score": _safe_float(m15d.get("average_trust_score")) if isinstance(m15d, dict) else 0.0,
        "external_api_calls_used": bool(m15d.get("external_api_calls_used", False)) if isinstance(m15d, dict) else False,
        "inference_latency_modes_tracked": sorted(latency.keys()) if isinstance(latency, dict) else [],
    }

    reliability_summary = {
        "dataset_validation_passed": bool(m15c.get("passed", False)) if isinstance(m15c, dict) else False,
        "ragops_passed": bool(m15b.get("passed", False)) if isinstance(m15b, dict) else False,
        "provider_agent_passed": bool(m15d.get("passed", False)) if isinstance(m15d, dict) else False,
        "external_providers_disabled_by_default": bool(m15d.get("external_provider_blocked_by_default", True)) if isinstance(m15d, dict) else True,
        "dataset_names": [str(item.get("dataset_name")) for item in dataset_results if isinstance(item, dict)],
    }

    warnings = []
    if dataset_warnings:
        warnings.append(f"Dataset validation produced {dataset_warnings} warning(s).")
    if failure_counts:
        warnings.append("Reliability failures were detected and routed through repair policies.")
    if not git_snapshot.available:
        warnings.append("Git metadata was unavailable; this can happen when running from an extracted ZIP.")

    limitations = [
        "This is a local JSON experiment registry, not a live MLflow Tracking Server.",
        "This milestone does not require DVC remotes, cloud storage, or credentials.",
        "Model risk card content is generated from prototype milestone outputs and is not a formal compliance document.",
    ]

    return ExperimentRecord(
        run_id=run_id,
        project="FailSafeML-X",
        milestone="M15E_EXPERIMENT_REGISTRY_MODEL_RISK_CARD",
        dataset_name="healthcare_sample + energy_sample + ragops_eval_queries",
        model_name="FailSafeML-X reliability envelope prototype",
        created_at_utc=_now_utc(),
        metrics=metrics,
        reliability_summary=reliability_summary,
        failure_counts=failure_counts,
        repair_action_counts=repair_action_counts,
        trust_score_summary=_summarize_trust_scores(trust_values),
        warnings=warnings,
        limitations=limitations,
        artifacts={
            "registry_json": "experiments/results/m15e_experiment_registry.json",
            "model_risk_card": "reports/model_risk_card.md",
            "milestone_report": "reports/milestone_15e_experiment_registry.md",
        },
        git=asdict(git_snapshot),
    )


def save_experiment_record(record: ExperimentRecord, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


def load_experiment_record(path: str | Path) -> ExperimentRecord:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ExperimentRecord(**payload)


def append_experiment_record_jsonl(record: ExperimentRecord, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
