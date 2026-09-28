#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX="${1:?GPU index is required}"
PORT="${2:?Loopback port is required}"
MODEL_SNAPSHOT="${MODEL_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--google--gemma-4-31B-it/snapshots/842da3794eaa0b77d5f08bae87a17459d91ff475}"
ASSISTANT_SNAPSHOT="${ASSISTANT_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--google--gemma-4-31B-it-assistant/snapshots/627c5ec1458b9086b841a91e0512fd31fd2fbbf1}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/gemma4-vllm024/bin/vllm}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-8}"

[[ "$GPU_INDEX" =~ ^[0-9]+$ ]] || { echo "GPU index must be nonnegative" >&2; exit 2; }
[[ "$PORT" =~ ^[0-9]+$ ]] || { echo "port must be an integer" >&2; exit 2; }
[[ "$MAX_NUM_SEQS" =~ ^[1-9][0-9]*$ ]] || { echo "MAX_NUM_SEQS must be positive" >&2; exit 2; }
[[ -d "$MODEL_SNAPSHOT" ]] || { echo "missing Gemma snapshot: $MODEL_SNAPSHOT" >&2; exit 1; }
[[ -d "$ASSISTANT_SNAPSHOT" ]] || { echo "missing MTP assistant: $ASSISTANT_SNAPSHOT" >&2; exit 1; }
[[ -x "$VLLM_BIN" ]] || { echo "missing vLLM executable: $VLLM_BIN" >&2; exit 1; }

export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES="$GPU_INDEX"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export VLLM_HOST_IP=127.0.0.1
export VLLM_ENABLE_V1_MULTIPROCESSING=0

SPECULATIVE_CONFIG="$(
  printf '{"method":"mtp","model":"%s","num_speculative_tokens":4}' \
    "$ASSISTANT_SNAPSHOT"
)"

exec "$VLLM_BIN" serve "$MODEL_SNAPSHOT" \
  --served-model-name google/gemma-4-31B-it \
  --dtype bfloat16 \
  --kv-cache-dtype bfloat16 \
  --max-model-len 262144 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs "$MAX_NUM_SEQS" \
  --gpu-memory-utilization 0.95 \
  --host 127.0.0.1 \
  --port "$PORT" \
  --language-model-only \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking":true}' \
  --async-scheduling \
  --speculative-config "$SPECULATIVE_CONFIG"
