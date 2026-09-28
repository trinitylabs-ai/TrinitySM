#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/opt/proof-workshop"
MTP4_OUTPUT="${ROOT_DIR}/runs/v088_bf16_mtp4_extended36_s2_32k_20260827"
MTP2_OUTPUT="${ROOT_DIR}/runs/v088_bf16_mtp2_extended36_s2_32k_20260827"
MTP2_CONTROLLER_PID="${1:?pass the active MTP2 controller PID}"
OLD_GPU0_SESSION="v088-bf16-mtp4-extended36-s2-gpu0-8030-20260827"
NEW_GPU0_SESSION="v088-bf16-mtp2-handoff-gpu0-8030-20260827"
DUAL_RUNNER_SESSION="v088-bf16-mtp2-dualgpu-32k-c4-20260827"
LAUNCHER="${ROOT_DIR}/cognitive_well_harness_v0_3_87_markdown_trace_extractor_20260827/launch_gemma4_bf16_mtp_ab.sh"

while [[ ! -f "${MTP4_OUTPUT}/summary.json" ]]; do
  sleep 15
done

if [[ -f "${MTP2_OUTPUT}/summary.json" ]]; then
  exit 0
fi

if kill -0 "${MTP2_CONTROLLER_PID}" 2>/dev/null; then
  controller_command="$(ps -p "${MTP2_CONTROLLER_PID}" -o args=)"
  if [[ "${controller_command}" != *"v088_bf16_mtp2_extended36_s2_32k_20260827"* ]]; then
    echo "Refusing to signal PID ${MTP2_CONTROLLER_PID}: command does not match MTP2 run" >&2
    exit 1
  fi
  kill -INT "${MTP2_CONTROLLER_PID}"
  sleep 15
  if kill -0 "${MTP2_CONTROLLER_PID}" 2>/dev/null; then
    kill -INT "${MTP2_CONTROLLER_PID}"
    sleep 5
  fi
  if kill -0 "${MTP2_CONTROLLER_PID}" 2>/dev/null; then
    kill -INT "${MTP2_CONTROLLER_PID}"
    sleep 5
  fi
fi

for _ in $(seq 1 24); do
  running="$({ curl -fsS http://127.0.0.1:8032/metrics || true; } | awk '/^vllm:num_requests_running\{/{print $2; exit}')"
  if [[ -z "${running}" || "${running}" == "0.0" ]]; then
    break
  fi
  sleep 5
done

tmux kill-session -t "${OLD_GPU0_SESSION}"
for _ in $(seq 1 60); do
  if ! curl -fsS http://127.0.0.1:8030/health >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

tmux new-session -d -s "${NEW_GPU0_SESSION}" -c "${ROOT_DIR}" \
  "${LAUNCHER}" 0 8030 2
for _ in $(seq 1 120); do
  if curl -fsS http://127.0.0.1:8030/health >/dev/null 2>&1; then
    break
  fi
  sleep 5
done
curl -fsS http://127.0.0.1:8030/health >/dev/null

tmux new-session -d -s "${DUAL_RUNNER_SESSION}" -c "${ROOT_DIR}" \
  python -m cognitive_well_harness_v0_3_87_markdown_trace_extractor_20260827.run_extended_mtp_top2 \
  --output-dir runs/v088_bf16_mtp2_extended36_s2_32k_20260827 \
  --endpoint http://127.0.0.1:8030/v1 \
  --endpoint http://127.0.0.1:8032/v1 \
  --mtp 2 \
  --workers 4 \
  --samples-per-proof 2 \
  --seed 20260827 \
  --model google/gemma-4-31B-it \
  --max-tokens 32768 \
  --high-cap-max-tokens 0 \
  --resume
