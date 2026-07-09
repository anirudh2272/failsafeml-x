"""Fine-tuning scaffolds for FailSafeML-X reliability explanations.

This package is intentionally dependency-light. It prepares instruction-tuning
data and LoRA/PEFT configuration templates without downloading models or running
training during tests.
"""

from .dataset_builder import (
    REQUIRED_INSTRUCTION_FIELDS,
    build_dataset_from_reliability_cases,
    build_instruction_record,
    generate_sample_reliability_records,
    load_jsonl,
    validate_instruction_dataset,
    write_jsonl,
)
from .lora_config import LoRAConfig, default_lora_config, validate_lora_config
from .training_stub import create_training_plan, render_training_stub, validate_training_plan

__all__ = [
    "REQUIRED_INSTRUCTION_FIELDS",
    "build_dataset_from_reliability_cases",
    "build_instruction_record",
    "generate_sample_reliability_records",
    "load_jsonl",
    "validate_instruction_dataset",
    "write_jsonl",
    "LoRAConfig",
    "default_lora_config",
    "validate_lora_config",
    "create_training_plan",
    "render_training_stub",
    "validate_training_plan",
]
