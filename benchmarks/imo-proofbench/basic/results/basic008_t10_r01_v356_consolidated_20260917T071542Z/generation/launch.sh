#!/usr/bin/env bash
set -euo pipefail
cd /opt/proof-workshop
exec /home/user/miniconda3/envs/math/bin/python -u -B -m cognitive_well_harness_v0_3_356_v349_discrete_consolidation_20260917.selected_resume --source-run /opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic_p008_t10_r01_raw_roots_v344_20260916T155741Z/generation/run --problem-file /opt/proof-workshop/benchmarks/imo-proofbench/basic/problems/PB-Basic-008.json --proof-file /opt/proof-workshop/benchmarks/imo-proofbench/basic/results/pipeline_raw_bf/proofs/PB-Basic-008/t10_r01/submitted.md --output-dir /opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic008_t10_r01_v356_consolidated_20260917T071542Z/generation/run --execute-models
