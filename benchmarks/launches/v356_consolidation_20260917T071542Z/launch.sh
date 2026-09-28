#!/usr/bin/env bash
set -euo pipefail
cd /opt/proof-workshop
exec /usr/bin/python3 -u -B /opt/proof-workshop/benchmarks/launches/v356_consolidation_20260917T071542Z/run_batch.py > /opt/proof-workshop/benchmarks/launches/v356_consolidation_20260917T071542Z/supervisor.log 2>&1
