#!/usr/bin/env bash
set -uo pipefail

cd /opt/proof-workshop || exit 1

gemma_run="runs/v050_reviewer2_adversarial_all36_gemma4_bf16_mtp4_t04_gpu0_b4_12k_20260823_1100"
qwen_run="runs/v050_reviewer2_adversarial_all36_qwen36_t04_gpu0_b4_12k_20260823_1115"
gemma_service="v037-gemma-bf16-8020"
qwen_service="v050-qwen36-bf16-thinking-8026"
restore_needed=0

restore_gemma() {
  if [[ "$restore_needed" -ne 1 ]]; then
    return
  fi
  if tmux has-session -t "$qwen_service" 2>/dev/null; then
    tmux kill-session -t "$qwen_service"
  fi
  sleep 15
  if ! tmux has-session -t "$gemma_service" 2>/dev/null; then
    tmux new-session -d -s "$gemma_service" \
      "cd /opt/proof-workshop && bash cognitive_well_harness_v0_3_35_cap_continuation_recovery_20260822/launch_gemma4_bf16_mtp4.sh 0 8020"
  fi
}

while true; do
  state=$(jq -r '.state // "missing"' "$gemma_run/status.json" 2>/dev/null)
  if [[ "$state" == "completed" ]]; then
    break
  fi
  sleep 30
done

if tmux has-session -t "$gemma_service" 2>/dev/null; then
  tmux kill-session -t "$gemma_service"
fi
restore_needed=1
trap restore_gemma EXIT
sleep 15

tmux new-session -d -s "$qwen_service" \
  "cd /opt/proof-workshop && bash cognitive_well_harness_v0_3_38_qwen36_three_persona_review_fusion_20260822/launch_qwen36_bf16_thinking.sh 0 8026"

ready=0
for _ in $(seq 1 120); do
  if curl -fsS http://127.0.0.1:8026/v1/models 2>/dev/null \
    | jq -e '.data[] | select(.id == "Qwen/Qwen3.6-27B")' >/dev/null; then
    ready=1
    break
  fi
  sleep 5
done
if [[ "$ready" -ne 1 ]]; then
  echo "Qwen GPU0 service did not become ready"
  exit 1
fi

python -m cognitive_well_harness_v0_3_50_reviewer2_adversarial_20260823.run \
  --output-dir "$qwen_run" \
  --reviewer-model qwen36 \
  --gpu-index 0 \
  --endpoint http://127.0.0.1:8026/v1 \
  --temperature 0.4 \
  --batch-size 4 \
  --quiet \
  > "${qwen_run}.run.log" 2>&1
exit $?
