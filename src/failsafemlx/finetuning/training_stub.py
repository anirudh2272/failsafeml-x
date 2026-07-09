from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .lora_config import LoRAConfig

OPTIONAL_TRAINING_PACKAGES = [
    "torch",
    "transformers",
    "datasets",
    "peft",
    "accelerate",
    "trl",
]


@dataclass(frozen=True)
class FineTuningPlan:
    dataset_path: str
    output_dir: str
    base_model_name: str
    training_enabled_by_default: bool
    downloads_models_during_tests: bool
    requires_gpu_for_tests: bool
    optional_packages: tuple[str, ...]
    command_preview: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_path": self.dataset_path,
            "output_dir": self.output_dir,
            "base_model_name": self.base_model_name,
            "training_enabled_by_default": self.training_enabled_by_default,
            "downloads_models_during_tests": self.downloads_models_during_tests,
            "requires_gpu_for_tests": self.requires_gpu_for_tests,
            "optional_packages": list(self.optional_packages),
            "command_preview": self.command_preview,
        }


def create_training_plan(
    dataset_path: str | Path,
    output_dir: str | Path = "artifacts/lora_reliability_explainer",
    config: LoRAConfig | None = None,
) -> FineTuningPlan:
    cfg = config or LoRAConfig()
    command = (
        "python -m failsafemlx.finetuning.training_stub "
        f"--dataset {dataset_path} --output-dir {output_dir} --base-model {cfg.base_model_name}"
    )
    return FineTuningPlan(
        dataset_path=str(dataset_path),
        output_dir=str(output_dir),
        base_model_name=cfg.base_model_name,
        training_enabled_by_default=False,
        downloads_models_during_tests=False,
        requires_gpu_for_tests=False,
        optional_packages=tuple(OPTIONAL_TRAINING_PACKAGES),
        command_preview=command,
    )


def validate_training_plan(plan: FineTuningPlan) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if plan.training_enabled_by_default:
        errors.append("Training must be disabled by default for CI-safe scaffold validation.")
    if plan.downloads_models_during_tests:
        errors.append("Model downloads must not occur during tests.")
    if plan.requires_gpu_for_tests:
        errors.append("GPU must not be required for tests.")
    if not plan.optional_packages:
        warnings.append("Optional package list is empty; training docs may be incomplete.")
    if "placeholder" in plan.base_model_name:
        warnings.append("Base model is a placeholder; actual training requires choosing a compatible model.")

    return {
        "passed": not errors,
        "plan": plan.to_dict(),
        "errors": errors,
        "warnings": warnings,
    }


def render_training_stub(plan: FineTuningPlan, config: LoRAConfig) -> str:
    """Render a non-executing training recipe for future optional use."""

    packages = ", ".join(plan.optional_packages)
    return f"""# Optional LoRA/PEFT Training Stub

This file is a scaffold. It intentionally does not run training during tests.

Dataset: `{plan.dataset_path}`
Output directory: `{plan.output_dir}`
Base model placeholder: `{plan.base_model_name}`
Optional packages: `{packages}`

## PEFT configuration preview

```json
{config.to_peft_dict()}
```

## Manual training path

1. Install optional dependencies from `requirements-finetuning.txt`.
2. Replace the placeholder base model with a compatible open model.
3. Review the dataset for privacy, label quality, and license safety.
4. Run training outside CI on an approved machine.
5. Save only adapter weights and document evaluation results.

No GPU training, model download, or adapter export is performed by this scaffold.
"""
