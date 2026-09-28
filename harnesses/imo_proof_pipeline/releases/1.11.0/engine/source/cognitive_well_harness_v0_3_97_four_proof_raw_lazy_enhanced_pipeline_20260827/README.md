# Cognitive Well Harness v0.3.97

Problem-only, four-proof front end for the generic v0.3.96 enhanced review,
Fusion, and Resolver harness.

## Compact flow

```text
problem statement only
        |
        v
GPU 0 / Gemma4-31B BF16 MTP4 Max
  raw batch: 2 x t=1.0 + 2 x t=.7
  frozen high-stakes prompt, top_p=.95, top_k=64
        |
        v
GPU 0 / Gemma4-31B
  lazy-check batch of 4, t=.1
        |
        +-- NO_ISSUES ------------------------------+
        |                                           |
        +-- issue -> conditional in-place expansion |
                     t=.7                           |
        |                                           |
        +---------------- four checked proofs <-----+
                            |
             +--------------+---------------+
             |                              |
             v                              v
GPU 0 / Gemma4                      GPU 1 / Qwen3.6
  Reviewer 1 batch of 4, t=.1         Reviewer 2 batch of 4, t=.2
  then                                      (concurrent)
  Reviewer 3 batch of 4, t=.2
             |                              |
             +--------------+---------------+
                            v
                      review barrier
                            |
                            v
GPU 0 / Gemma4: Fusion batch of 4, t=.4
                            |
                            v
GPU 0 / Gemma4: Resolver batch of 4, t=.4
                            |
                            v
four resolved proofs + UNCERTIFIED_TRACE handoffs
```

Reviewer 1 uses the v0.3.89 conditional trace gate; Reviewer 3 uses the v0.3.92
scope-matched trace gate. Reviewer 2, Fusion, and Resolver retain the v0.3.96
configuration. Fusion starts only after both GPU review branches finish.

Every Gemma stage uses one shared GPU 0 service with the same immutable runtime
profile: Gemma4-31B, BF16, server-side MTP=4. This includes generation, checking,
expansion, Reviewers 1 and 3, trace processing, Fusion, and Resolver. Reviewer 2 is
the sole exception because it intentionally uses Qwen3.6 on GPU 1.

Exactly four checked proofs remain live after lazy expansion. If an expansion
changes a conclusion, the ancestor is retained as provenance but is not introduced
as a fifth live lane.

All prompts are cross-problem. The frozen raw prompt changes only the problem
statement bytes; no problem-specific mathematical structures or hints are injected.

## Dry run

```bash
python -m cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827.run \
  --problem-file path/to/problem.json \
  --output-dir runs/v097_dry \
  --dry-run
```

## Live run

```bash
python -m cognitive_well_harness_v0_3_97_four_proof_raw_lazy_enhanced_pipeline_20260827.run \
  --problem-file path/to/problem.json \
  --output-dir runs/v097_run \
  --gpu0-gemma-endpoint http://127.0.0.1:8030/v1 \
  --gpu1-qwen-endpoint http://127.0.0.1:8021/v1
```

The endpoint flag names are intentional: GPU 0 is the main Gemma device, and GPU 1
is reserved for Qwen Reviewer 2.
