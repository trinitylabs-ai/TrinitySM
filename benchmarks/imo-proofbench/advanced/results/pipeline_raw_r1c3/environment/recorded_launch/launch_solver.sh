#!/usr/bin/env bash
set -euo pipefail
cd /opt/proof-workshop/exports/v263-v290-mtp4-original-recovery-assets-20260912T181928Z/source
exec env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/opt/proof-workshop/exports/v263-v290-mtp4-original-recovery-assets-20260912T181928Z/source /home/user/miniconda3/envs/math/bin/python -u -B /opt/proof-workshop/exports/v263-v290-mtp4-original-recovery-assets-20260912T181928Z/source/scripts/run_v263_v290.py --problem-dir /opt/proof-workshop/data/imo_proofbench_advanced_problem_only --output-dir /opt/proof-workshop/runs/advanced001_030_v263_v290_frozen_run01 --gemma-endpoint http://127.0.0.1:8030/v1 --qwen-endpoint http://127.0.0.1:8027/v1 --model-timeout-sec 600 --seed-namespace v263-v290:problem-only --raw-seed-offset 0 --resume --execute-models
