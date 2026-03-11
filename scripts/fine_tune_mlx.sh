#!/usr/bin/env bash
set -euo pipefail

# Fine-tune Qwen2.5-7B-Instruct with LoRA using MLX
# Usage: bash scripts/fine_tune_mlx.sh data/train.jsonl

DATA=${1:-data/train.jsonl}

mlx_lm.lora \
  --model mlx-community/Qwen2.5-7B-Instruct \
  --data "$DATA" \
  --train-batch-size 1 \
  --steps 2000 \
  --learning-rate 2e-4 \
  --lora-r 8 --lora-alpha 16 --lora-dropout 0.05 \
  --max-seq-length 2048 \
  --output ./lora-openscad
