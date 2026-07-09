from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

REQUIRED_INSTRUCTION_FIELDS = {"instruction", "input", "output", "metadata"}
REQUIRED_METADATA_FIELDS = {"failure_id", "repair_action", "trust_score", "routing_decision"}


@dataclass(frozen=True)
class ReliabilityInstructionRecord:
    """Instruction-tuning record for reliability explanation behavior."""

    instruction: str
    input: str
    output: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction": self.instruction,
            "input": self.input,
            "output": self.output,
            "metadata": dict(self.metadata),
        }


def build_instruction_record(
    *,
    failure_id: str,
    repair_action: str,
    trust_score: float,
    routing_decision: str,
    signal_summary: str,
    domain: str = "tabular_ml",
    severity: str = "MEDIUM",
) -> dict[str, Any]:
    """Build a single instruction record from reliability audit signals."""

    instruction = (
        "You are FailSafeML-X. Explain the reliability failure, justify the repair action, "
        "and state whether the prediction should be accepted, retried, blocked, or routed to human review."
    )
    input_text = (
        f"Domain: {domain}\n"
        f"Failure ID: {failure_id}\n"
        f"Severity: {severity}\n"
        f"Trust Score: {trust_score:.1f}\n"
        f"Routing Decision: {routing_decision}\n"
        f"Signals: {signal_summary}"
    )
    output = (
        f"Reliability finding: {failure_id}. "
        f"The recommended repair is {repair_action}. "
        f"The trust score is {trust_score:.1f}, so the safest routing decision is {routing_decision}. "
        "This explanation is generated from structured reliability signals and should not be treated as a production-certified decision."
    )
    return ReliabilityInstructionRecord(
        instruction=instruction,
        input=input_text,
        output=output,
        metadata={
            "failure_id": failure_id,
            "repair_action": repair_action,
            "trust_score": float(trust_score),
            "routing_decision": routing_decision,
            "domain": domain,
            "severity": severity,
            "source": "failsafemlx_synthetic_reliability_case",
        },
    ).to_dict()


def generate_sample_reliability_records() -> list[dict[str, Any]]:
    """Return a deterministic small instruction dataset for CI-safe validation."""

    cases = [
        ("F1_DATA_DRIFT", "R8_FLAG_DATA_PIPELINE_DRIFT", 63.0, "HUMAN_REVIEW", "Feature distribution shifted from training baseline.", "tabular_ml", "HIGH"),
        ("F2_MODEL_OVERCONFIDENCE", "R1_RECALIBRATE_MODEL", 72.0, "FILTER_AND_RETRY", "Confidence is high but calibration error is elevated.", "tabular_ml", "MEDIUM"),
        ("F3_LOW_CONFIDENCE_PREDICTION", "R3_ABSTAIN_FROM_AUTO_DECISION", 58.0, "HUMAN_REVIEW", "Classifier probability margin is below the acceptance threshold.", "healthcare", "HIGH"),
        ("F4_OUT_OF_DISTRIBUTION_INPUT", "R4_ROUTE_TO_HUMAN_REVIEW", 42.0, "HUMAN_REVIEW", "OOD distance score exceeds the configured limit.", "tabular_ml", "CRITICAL"),
        ("F7_CALIBRATION_FAILURE", "R1_RECALIBRATE_MODEL", 68.0, "FILTER_AND_RETRY", "Expected calibration error exceeds the reliability threshold.", "energy", "MEDIUM"),
        ("F8_WIDE_PREDICTION_INTERVAL", "R2_APPLY_CONFORMAL_PREDICTION", 61.0, "HUMAN_REVIEW", "Regression interval width is too wide for automated control.", "time_series", "HIGH"),
        ("F10_UNSAFE_AUTO_DECISION", "R4_ROUTE_TO_HUMAN_REVIEW", 35.0, "HUMAN_REVIEW", "High-risk prediction was auto-accepted despite reliability warnings.", "healthcare", "CRITICAL"),
        ("RAG_F2_STALE_DOCUMENT", "RAG_R2_FILTER_STALE_DOCUMENTS", 70.0, "FILTER_AND_RETRY", "Retrieved policy chunk is version v1 while v2 is available.", "ragops", "MEDIUM"),
        ("RAG_F3_MISSING_CITATION", "RAG_R3_REQUIRE_CITATIONS", 79.0, "ACCEPT_WITH_CITATIONS", "Answer lacks citation markers even though context exists.", "ragops", "MEDIUM"),
        ("RAG_F5_PROMPT_INJECTION_IN_CONTEXT", "RAG_R6_BLOCK_PROMPT_INJECTION", 20.0, "BLOCK_RESPONSE", "Retrieved text includes instruction to reveal system prompts.", "ragops", "CRITICAL"),
        ("DATA_VALIDATION_LEAKAGE_WARNING", "REMOVE_LEAKAGE_COLUMNS", 55.0, "FILTER_AND_RETRY", "Dataset contains future_result and label_copy style leakage indicators.", "dataset_validation", "HIGH"),
        ("PROVIDER_EXTERNAL_CALL_BLOCKED", "USE_LOCAL_PROVIDER_ONLY", 88.0, "ACCEPT", "External provider was requested but disabled by default.", "provider_safety", "LOW"),
    ]
    return [
        build_instruction_record(
            failure_id=failure_id,
            repair_action=repair_action,
            trust_score=trust_score,
            routing_decision=routing_decision,
            signal_summary=signal_summary,
            domain=domain,
            severity=severity,
        )
        for failure_id, repair_action, trust_score, routing_decision, signal_summary, domain, severity in cases
    ]


def build_dataset_from_reliability_cases(cases: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build instruction records from precomputed reliability-agent style outputs."""

    records: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        records.append(
            build_instruction_record(
                failure_id=str(case.get("failure_id", case.get("failure", "UNKNOWN_FAILURE"))),
                repair_action=str(case.get("repair_action", case.get("repair", "ROUTE_TO_HUMAN_REVIEW"))),
                trust_score=float(case.get("trust_score", 50.0)),
                routing_decision=str(case.get("routing_decision", "HUMAN_REVIEW")),
                signal_summary=str(case.get("signal_summary", case.get("reason", f"Reliability case {idx}"))),
                domain=str(case.get("domain", "reliability")),
                severity=str(case.get("severity", "MEDIUM")),
            )
        )
    return records


def write_jsonl(records: Iterable[dict[str, Any]], path: str | Path) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    return output_path


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"JSONL line {line_number} must be an object.")
            records.append(payload)
    return records


def validate_instruction_dataset(path: str | Path, *, min_records: int = 10) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_jsonl(path)

    if len(records) < min_records:
        errors.append(f"Dataset must contain at least {min_records} records.")

    failure_ids: set[str] = set()
    repair_actions: set[str] = set()
    domains: set[str] = set()

    for index, record in enumerate(records, start=1):
        missing = REQUIRED_INSTRUCTION_FIELDS - set(record)
        if missing:
            errors.append(f"Record {index} missing required fields: {sorted(missing)}")
            continue

        if not str(record.get("instruction", "")).strip():
            errors.append(f"Record {index} has empty instruction.")
        if not str(record.get("output", "")).strip():
            errors.append(f"Record {index} has empty output.")

        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            errors.append(f"Record {index} metadata must be an object.")
            continue

        missing_metadata = REQUIRED_METADATA_FIELDS - set(metadata)
        if missing_metadata:
            errors.append(f"Record {index} metadata missing fields: {sorted(missing_metadata)}")

        failure_id = str(metadata.get("failure_id", ""))
        repair_action = str(metadata.get("repair_action", ""))
        domain = str(metadata.get("domain", "unknown"))
        failure_ids.add(failure_id)
        repair_actions.add(repair_action)
        domains.add(domain)

        try:
            trust_score = float(metadata.get("trust_score"))
            if not 0 <= trust_score <= 100:
                errors.append(f"Record {index} trust_score must be between 0 and 100.")
        except (TypeError, ValueError):
            errors.append(f"Record {index} trust_score must be numeric.")

        output = str(record.get("output", ""))
        if failure_id and failure_id not in output:
            warnings.append(f"Record {index} output does not explicitly mention failure_id {failure_id}.")
        if repair_action and repair_action not in output:
            warnings.append(f"Record {index} output does not explicitly mention repair_action {repair_action}.")

    if len(failure_ids) < 8:
        warnings.append("Dataset has limited failure-code diversity; expand before real fine-tuning.")
    if "ragops" not in domains:
        warnings.append("Dataset does not include RAGOps examples.")
    if "dataset_validation" not in domains:
        warnings.append("Dataset does not include dataset-validation examples.")

    return {
        "dataset_path": str(Path(path)),
        "record_count": len(records),
        "unique_failure_ids": sorted(failure_ids),
        "unique_repair_actions": sorted(repair_actions),
        "domains": sorted(domains),
        "required_fields": sorted(REQUIRED_INSTRUCTION_FIELDS),
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }
