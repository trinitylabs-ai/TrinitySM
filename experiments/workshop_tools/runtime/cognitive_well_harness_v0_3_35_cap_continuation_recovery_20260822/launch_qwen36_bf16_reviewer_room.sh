#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX="${1:?GPU index is required}"
PORT="${2:?Loopback port is required}"
MODEL_SNAPSHOT="${MODEL_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/gemma4-vllm024/bin/vllm}"

[[ "$GPU_INDEX" =~ ^[0-9]+$ ]] || { echo "GPU index must be nonnegative" >&2; exit 2; }
[[ "$PORT" =~ ^[0-9]+$ ]] || { echo "port must be an integer" >&2; exit 2; }
[[ -d "$MODEL_SNAPSHOT" ]] || { echo "missing Qwen snapshot: $MODEL_SNAPSHOT" >&2; exit 1; }
[[ -x "$VLLM_BIN" ]] || { echo "missing vLLM executable: $VLLM_BIN" >&2; exit 1; }

export CUDA_VISIBLE_DEVICES="$GPU_INDEX"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export VLLM_HOST_IP=127.0.0.1
export VLLM_ENABLE_V1_MULTIPROCESSING=0

exec "$VLLM_BIN" serve "$MODEL_SNAPSHOT" \
  --served-model-name Qwen/Qwen3.6-27B \
  --dtype bfloat16 \
  --kv-cache-dtype bfloat16 \
  --max-model-len 262144 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 4 \
  --gpu-memory-utilization 0.77 \
  --host 127.0.0.1 \
  --port "$PORT" \
  --language-model-only \
  --reasoning-parser qwen3 \
  --default-chat-template-kwargs '{"enable_thinking":true}' \
  --async-scheduling
