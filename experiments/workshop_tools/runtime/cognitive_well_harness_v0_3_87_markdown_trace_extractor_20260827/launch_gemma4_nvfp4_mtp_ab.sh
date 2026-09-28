#!/usr/bin/env bash
set -euo pipefail

GPU_INDEX="${1:-0}"
PORT="${2:-8030}"
MTP_TOKENS="${3:-0}"
MODEL_REVISION="4135a98a9b728a548947683219633b25682223ac"
ASSISTANT_REVISION="627c5ec1458b9086b841a91e0512fd31fd2fbbf1"
MODEL_SNAPSHOT="${MODEL_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--nvidia--Gemma-4-31B-IT-NVFP4/snapshots/${MODEL_REVISION}}"
ASSISTANT_SNAPSHOT="${ASSISTANT_SNAPSHOT:-/home/user/.cache/huggingface/hub/models--google--gemma-4-31B-it-assistant/snapshots/${ASSISTANT_REVISION}}"
VLLM_BIN="${VLLM_BIN:-/home/user/miniconda3/envs/gemma4-vllm024/bin/vllm}"
COMPAT_PATH="${COMPAT_PATH:-/opt/proof-workshop/vllm_compat}"
GPU_MEMORY_UTILIZATION="${GEMMA_GPU_MEMORY_UTILIZATION:-0.985}"

case "${MTP_TOKENS}" in
  0|1|2|3|4) ;;
  *) echo "MTP_TOKENS must be one of 0, 1, 2, 3, or 4" >&2; exit 2 ;;
esac

export CUDA_VISIBLE_DEVICES="${GPU_INDEX}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONPATH="${COMPAT_PATH}${PYTHONPATH:+:${PYTHONPATH}}"
export VLLM_HOST_IP=127.0.0.1
export VLLM_ENABLE_V1_MULTIPROCESSING=0
export NCCL_SOCKET_IFNAME=lo
export GLOO_SOCKET_IFNAME=lo

SPEC_ARGS=()
if [[ "${MTP_TOKENS}" != "0" ]]; then
  SPECULATIVE_CONFIG="$({
    printf '{"method":"mtp","model":"%s","num_speculative_tokens":%s}' \
      "${ASSISTANT_SNAPSHOT}" "${MTP_TOKENS}"
  })"
  SPEC_ARGS=(--speculative-config "${SPECULATIVE_CONFIG}")
fi

exec "${VLLM_BIN}" serve "${MODEL_SNAPSHOT}" \
  --served-model-name nvidia/Gemma-4-31B-IT-NVFP4 \
  --quantization modelopt \
  --dtype bfloat16 \
  --kv-cache-dtype bfloat16 \
  --max-model-len 262144 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 8 \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --host 127.0.0.1 \
  --port "${PORT}" \
  --language-model-only \
  --reasoning-parser gemma4 \
  --structured-outputs-config '{"backend":"xgrammar","disable_any_whitespace":true}' \
  --default-chat-template-kwargs '{"enable_thinking":true}' \
  --async-scheduling \
  "${SPEC_ARGS[@]}"
