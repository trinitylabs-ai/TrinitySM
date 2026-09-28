# Recorded 96 GB single-GPU execution

This package ports the sleep/wake scheduler and client/storage adapters used by
the finalized ProofBench B 1.12.0 continuation. It runs the same frozen release;
it does not define a new proof-generation policy or change historical releases.

- `broker.py` drains ready calls for the awake model before switching. It checks
  that vLLM has no running or waiting requests before sleeping that model.
- `client.py` and `client_compat/sitecustomize.py` acquire a model lease before
  frozen extended reasoning/transport/selector deadlines start, retaining it through nested calls.
- `server_compat/` preserves weight bytes in file-backed CPU tensors during sleep
  and limits the advisory GPU-name scan to the selected physical device.
- `scripts/local_servers.py start --single-gpu N` owns server startup/cleanup.
  `scripts/run_single_gpu.py` owns fresh generation workers and their broker.

See the [commands and hardware record](../../docs/local_reproduction.md#one-96-gb-gpu-with-model-switching)
and [source provenance](../../docs/results/proofbench_single_gpu_20260926/README.md).
The public packaging uses portable paths and explicit managed-server ownership.
It omits the private job's automatic grading, response replay and automatic
server restart. None of those are needed for fresh generation.
