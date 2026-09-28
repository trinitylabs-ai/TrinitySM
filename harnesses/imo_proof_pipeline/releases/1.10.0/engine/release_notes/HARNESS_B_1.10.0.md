# B 1.10.0: twelve concurrent audits per model

Raise post-resolver R2/R3 audits from four shared slots to two independent pools:
twelve Gemma and twelve Qwen logical calls, twenty-four total. Both server profiles
now allow twelve concurrent sequences. Other model/serving settings are retained.
Save configured limits and observed concurrency, total and per model.

Keep all prompts, BF text and transport, seed keys, temperatures, token caps,
mechanical validation and the four-approval replacement policy unchanged.
Each changed lane receives exactly four independent audit calls; identical pairs
skip inference. Four eligible lanes supply only eight calls per model; larger
standalone audit queues can use all twelve. No extra calls are added to fill slots.
Generation and R1/R2/R3 remain four-lane batches. Resume uses the saved release and
reuses completed audit calls. Published 1.9.0/1.8.0/1.7.0 remain unchanged.

This source/profile change requires a minor version under the release publisher.
No proof benchmarks or new inference calls were launched for this change.
