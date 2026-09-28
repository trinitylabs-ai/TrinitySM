#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/opt/proof-workshop"
MAIN_SUMMARY="${ROOT_DIR}/runs/v088_bf16_mtp4_trace_gate_selector_32proof_s2_b4_2gpu_20260827/summary.json"

while [[ ! -f "${MAIN_SUMMARY}" ]]; do
  sleep 15
done

cd "${ROOT_DIR}"
exec python -m cognitive_well_harness_v0_3_88_bf16_mtp4_trace_gate_selector_20260827.reviewer3_audit \
  --output-dir runs/v088_reviewer3_hidden_trace_audit_shortlist10_bf16_mtp4_b4_2gpu_20260827 \
  --endpoint http://127.0.0.1:8030/v1 \
  --endpoint http://127.0.0.1:8032/v1 \
  --workers-per-endpoint 4 \
  --sample-profile shortlist10 \
  --seed 20260827 \
  --model google/gemma-4-31B-it
