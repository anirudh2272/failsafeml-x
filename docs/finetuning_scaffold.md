# LoRA / PEFT Fine-Tuning Scaffold

Milestone 19 adds a safe fine-tuning scaffold for FailSafeML-X reliability explanations.

The scaffold prepares instruction-style records from reliability failures, repair actions, trust scores, routing decisions, RAGOps failures, dataset-validation warnings, and provider-safety events. It also includes a dependency-free LoRA configuration template and a non-executing training plan.

## What this milestone does

- Generates `data/fine_tuning/reliability_explanations_sample.jsonl`.
- Validates instruction-tuning records.
- Provides a LoRA/PEFT configuration preview.
- Provides an optional training stub for future manual training.
- Documents required optional packages.
- Runs entirely in local CI without GPU, model downloads, API keys, or external services.

## What this milestone does not do

No model is fine-tuned. The scaffold does not download a base model, does not call Hugging Face, does not create adapter weights, and does not require a GPU.

## Why this belongs in FailSafeML-X

FailSafeML-X already generates structured reliability decisions. A future fine-tuned explanation model could learn to summarize those structured signals in consistent operational language. This milestone prepares the data and configuration path without making unsupported training claims.

## How to run

```bash
python scripts/run_m19_finetuning_scaffold.py
python -m pytest
python scripts/local_ci.py
```

## Optional future training path

Real training should happen only after a larger reviewed dataset is created. Before running training, review privacy, licensing, label quality, safety behavior, and evaluation metrics. Install optional packages from `requirements-finetuning.txt` only when intentionally training outside CI.

## Honest resume language

Added a LoRA/PEFT fine-tuning scaffold and instruction-data builder for FailSafeML-X reliability explanations, with dataset validation, configuration templates, and CI-safe tests that do not require GPU training or model downloads.
