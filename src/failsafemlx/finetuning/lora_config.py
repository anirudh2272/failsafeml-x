from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LoRAConfig:
    """Dependency-free representation of a PEFT LoRA configuration template."""

    base_model_name: str = "placeholder-local-reliability-explainer"
    task_type: str = "CAUSAL_LM"
    r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "v_proj")
    bias: str = "none"
    gradient_checkpointing: bool = False
    max_seq_length: int = 1024
    learning_rate: float = 2e-4
    num_train_epochs: int = 1
    per_device_train_batch_size: int = 1

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["target_modules"] = list(self.target_modules)
        return payload

    def to_peft_dict(self) -> dict[str, Any]:
        """Return the subset that maps cleanly to peft.LoraConfig."""
        return {
            "task_type": self.task_type,
            "r": self.r,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
            "target_modules": list(self.target_modules),
            "bias": self.bias,
        }


def default_lora_config(**overrides: Any) -> LoRAConfig:
    allowed = set(LoRAConfig.__dataclass_fields__)
    unknown = set(overrides) - allowed
    if unknown:
        raise ValueError(f"Unknown LoRAConfig override(s): {sorted(unknown)}")
    return LoRAConfig(**overrides)


def validate_lora_config(config: LoRAConfig) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if config.r <= 0:
        errors.append("LoRA rank r must be positive.")
    if config.lora_alpha <= 0:
        errors.append("lora_alpha must be positive.")
    if not 0 <= config.lora_dropout < 1:
        errors.append("lora_dropout must be in [0, 1).")
    if not config.target_modules:
        errors.append("At least one target module must be specified.")
    if config.max_seq_length < 128:
        warnings.append("max_seq_length is very small for explanation-style fine-tuning.")
    if config.num_train_epochs > 3:
        warnings.append("High epoch count may overfit the small scaffold dataset.")
    if config.base_model_name.startswith("placeholder"):
        warnings.append("Base model is a placeholder; choose a real compatible model before actual training.")

    return {
        "passed": not errors,
        "config": config.to_dict(),
        "peft_config_preview": config.to_peft_dict(),
        "errors": errors,
        "warnings": warnings,
    }
