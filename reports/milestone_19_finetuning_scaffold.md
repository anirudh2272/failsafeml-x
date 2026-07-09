# Milestone 19 — LoRA / PEFT Fine-Tuning Scaffold

## Objective
Add a CI-safe fine-tuning scaffold for reliability explanation and failure-routing examples.

## Validation Summary
- Passed: `True`
- Instruction records: `12`
- Unique failure IDs: `12`
- Domains covered: `dataset_validation, energy, healthcare, provider_safety, ragops, tabular_ml, time_series`
- Training performed: `False`
- Model download performed: `False`
- GPU required for tests: `False`
- Adapter weights created: `False`

## Generated Files
- `data/fine_tuning/reliability_explanations_sample.jsonl`
- `docs/optional_lora_training_stub.md`
- `reports/milestone_19_finetuning_scaffold.md`
- `experiments/results/m19_finetuning_scaffold.json`

## LoRA Configuration Preview
```json
{
  "base_model_name": "placeholder-local-reliability-explainer",
  "task_type": "CAUSAL_LM",
  "r": 8,
  "lora_alpha": 16,
  "lora_dropout": 0.05,
  "target_modules": [
    "q_proj",
    "v_proj"
  ],
  "bias": "none",
  "gradient_checkpointing": false,
  "max_seq_length": 1024,
  "learning_rate": 0.0002,
  "num_train_epochs": 1,
  "per_device_train_batch_size": 1
}
```

## Honest Limitations
- This milestone creates a LoRA/PEFT scaffold only; no model is fine-tuned.
- The sample dataset is small and synthetic; real training requires a larger reviewed dataset.
- No GPU, model download, Hugging Face login, or external provider call is required for tests.
- Before real training, review privacy, licensing, evaluation quality, and model safety constraints.

## Warnings
- Base model is a placeholder; choose a real compatible model before actual training.
- Base model is a placeholder; actual training requires choosing a compatible model.
