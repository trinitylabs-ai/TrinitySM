# Recorded one-GPU continuation of final ProofBench

The finalized B 1.12.0 run began with two GPUs and continued on **one NVIDIA
RTX PRO 6000 Blackwell 96 GB GPU** after the second GPU went offline. The
continuation retained 16 previously processed portfolios and admitted the
remaining 44 portfolios. This was an executed recovery configuration.

| Setting or observation | Recorded value |
|---|---|
| Harness release | B 1.12.0, unchanged frozen engine |
| Active GPU | GPU 0 only; GPU 1 offline/unused |
| Weight precision / speculative decoding | BF16 / MTP 4 |
| Sleeping weights | Byte-preserving file-backed CPU mmap, vLLM sleep level 1 |
| Gemma KV allocation | 30,064,771,072 bytes (28 GiB) |
| Final proof concurrency | Gemma 8; Qwen 12 |
| Comparison concurrency | 12 |
| Quiet interval before model switch | 20 seconds, after active calls drain |
| Queue delay | Excluded from inference deadlines |
| Completed model switches in saved snapshot | 26 |
| Released logical leases | Gemma 4,329; Qwen 1,965 |
| Scheduler error in saved snapshot | None |

The [portable run record](RUN_RECORD.json) identifies the suite, continuation,
snapshot time, original adapter hashes and publication adaptations. Lease counts
are scheduling records, not counts of problems or physical inference requests.
The full final score matrix covers both the preserved earlier work and the
single-GPU continuation; it is not a separate fresh one-GPU benchmark.

The [public adapter](../../../harnesses/single_gpu/README.md) uses the final
recorded broker implementation and client/storage hooks, with portable paths,
managed process cleanup and a fresh generation-only entry point. Its automated
checks supplement the actual continuation evidence; they do not claim that the
new public wrapper has rerun all 60 problems.

The earlier documentation incorrectly described a 192 GB layout with both
models resident and called 96 GB switching unimplemented. That description
and its unnecessary 1.13.0 profile have been withdrawn. Both documented GPU
layouts use B 1.12.0.
