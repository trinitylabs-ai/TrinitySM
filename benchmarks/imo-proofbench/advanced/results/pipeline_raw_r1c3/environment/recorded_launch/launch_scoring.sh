#!/usr/bin/env bash
set -euo pipefail
cd /opt/proof-workshop/runs/advanced_raw_r1c3_imobench_incremental_20260913
exec env -u PYTHONPATH -u PYTHONHOME -u OPENAI_BASE_URL -u OPENAI_API_BASE -u GEMMA_ENDPOINT -u QWEN_ENDPOINT CUDA_VISIBLE_DEVICES= NVIDIA_VISIBLE_DEVICES=none PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 nice -n 10 /opt/proof-workshop/runs/advanced_raw_r1c3_imobench_incremental_20260913/.venv/bin/python -u -B /opt/proof-workshop/runs/advanced_raw_r1c3_imobench_incremental_20260913/watcher.py --source-run /opt/proof-workshop/runs/advanced001_030_v263_v290_frozen_run01 --output-dir /opt/proof-workshop/runs/advanced_raw_r1c3_imobench_incremental_20260913 "$@" >> /opt/proof-workshop/runs/advanced_raw_r1c3_imobench_incremental_20260913/watcher.log 2>&1
