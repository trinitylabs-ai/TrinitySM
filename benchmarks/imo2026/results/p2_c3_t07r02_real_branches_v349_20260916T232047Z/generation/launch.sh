#!/usr/bin/env bash
set -euo pipefail
cd /opt/proof-workshop
exec /home/user/miniconda3/envs/math/bin/python -u -B -m cognitive_well_harness_v0_3_349_checked_real_branches_20260916.proof_harness --problem-file /opt/proof-workshop/benchmarks/imo2026/problems/imo2026_p2.json --proof-file /opt/proof-workshop/benchmarks/imo2026/results/p2_c3_t07r02_then_v326_20260915T054500Z/proofs/imo2026_p2/t07_r02/R1-C3.md --output-dir /opt/proof-workshop/benchmarks/imo2026/results/p2_c3_t07r02_real_branches_v349_20260916T232047Z/generation/run --master-seed 20260915 --gemma-endpoint http://127.0.0.1:8030/v1 --qwen-endpoint http://127.0.0.1:8027/v1 --execute-models --detection-from /opt/proof-workshop/benchmarks/imo2026/results/p2_c3_t07r02_v329_guards_20260915T220000Z/generation/run
