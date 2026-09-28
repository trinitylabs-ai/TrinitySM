#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX="${1:?GPU index is required}"
PORT="${2:?Loopback port is required}"
MODEL_REVISION="4135a98a9b728a548947683219633b25682223ac"
MODEL_SNAPSHOT="${MODEL_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--nvidia--Gemma-4-31B-IT-NVFP4/snapshots/${MODEL_REVISION}}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/gemma4-vllm024/bin/vllm}"
COMPAT_PATH="${COMPAT_PATH:-/opt/proof-workshop/vllm_compat}"

export CUDA_VISIBLE_DEVICES="${GPU_INDEX}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONPATH="${COMPAT_PATH}${PYTHONPATH:+:${PYTHONPATH}}"
export VLLM_HOST_IP=127.0.0.1
export VLLM_ENABLE_V1_MULTIPROCESSING=0
export NCCL_SOCKET_IFNAME=lo
export GLOO_SOCKET_IFNAME=lo

exec "${VLLM_BIN}" serve "${MODEL_SNAPSHOT}" \
  --served-model-name nvidia/Gemma-4-31B-IT-NVFP4 \
  --quantization modelopt \
  --dtype bfloat16 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.90 \
  --host 127.0.0.1 \
  --port "${PORT}" \
  --language-model-only \
  --reasoning-parser gemma4 \
  --default-chat-template-kwargs '{"enable_thinking": true}' \
  --async-scheduling
