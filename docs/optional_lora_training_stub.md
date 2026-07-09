# Optional LoRA/PEFT Training Stub

This file is a scaffold. It intentionally does not run training during tests.

Dataset: `data/fine_tuning/reliability_explanations_sample.jsonl`
Output directory: `artifacts/lora_reliability_explainer`
Base model placeholder: `placeholder-local-reliability-explainer`
Optional packages: `torch, transformers, datasets, peft, accelerate, trl`

## PEFT configuration preview

```json
{'task_type': 'CAUSAL_LM', 'r': 8, 'lora_alpha': 16, 'lora_dropout': 0.05, 'target_modules': ['q_proj', 'v_proj'], 'bias': 'none'}
```

## Manual training path

1. Install optional dependencies from `requirements-finetuning.txt`.
2. Replace the placeholder base model with a compatible open model.
3. Review the dataset for privacy, label quality, and license safety.
4. Run training outside CI on an approved machine.
5. Save only adapter weights and document evaluation results.

No GPU training, model download, or adapter export is performed by this scaffold.
