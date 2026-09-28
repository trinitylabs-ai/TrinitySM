#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX="${1:-0}"
PORT="${2:-8020}"
MODEL_REVISION="4135a98a9b728a548947683219633b25682223ac"
ASSISTANT_REVISION="627c5ec1458b9086b841a91e0512fd31fd2fbbf1"
MODEL_SNAPSHOT="${MODEL_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--nvidia--Gemma-4-31B-IT-NVFP4/snapshots/${MODEL_REVISION}}"
ASSISTANT_SNAPSHOT="${ASSISTANT_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--google--gemma-4-31B-it-assistant/snapshots/${ASSISTANT_REVISION}}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/gemma4-vllm024/bin/vllm}"
COMPAT_PATH="${COMPAT_PATH:-/opt/proof-workshop/vllm_compat}"
GPU_MEMORY_UTILIZATION="${GEMMA_GPU_MEMORY_UTILIZATION:-0.90}"

export CUDA_VISIBLE_DEVICES="${GPU_INDEX}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONPATH="${COMPAT_PATH}${PYTHONPATH:+:${PYTHONPATH}}"
export VLLM_HOST_IP=127.0.0.1
export VLLM_ENABLE_V1_MULTIPROCESSING=0
export NCCL_SOCKET_IFNAME=lo
export GLOO_SOCKET_IFNAME=lo

SPECULATIVE_CONFIG="$(
  printf '{"method":"mtp","model":"%s","num_speculative_tokens":4}' \
    "${ASSISTANT_SNAPSHOT}"
)"

exec "${VLLM_BIN}" serve "${MODEL_SNAPSHOT}" \
  --served-model-name nvidia/Gemma-4-31B-IT-NVFP4 \
  --quantization modelopt \
  --dtype bfloat16 \
  --kv-cache-dtype fp8_e4m3 \
  --max-model-len 262144 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 8 \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --host 127.0.0.1 \
  --port "${PORT}" \
  --language-model-only \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --async-scheduling \
  --speculative-config "${SPECULATIVE_CONFIG}"
