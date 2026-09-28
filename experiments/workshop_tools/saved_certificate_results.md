# Workshop Tools: historical consolidation validation

**Experimental extension.** This report records the historical `0.3.356` tool
implementation. See the [experimental guide](README.md) for its role
in Proof Workshop.

V356 combines the V349 geometry and real-root paths with the V353 discrete tools and synthesis binding. It excludes the V354/V355 geometry derivation exporter. Runtime dispatch uses tool operations, not problem IDs.

Fresh proof regeneration from the originally selected saved certificates reproduced all three earlier successes:

| Problem and source | Original score | Earlier tool score | V356 score |
|---|---:|---:|---:|
| IMO 2026 P2, t07_r02 final refinement | 4 | 6 (V349) | **6/7** |
| Basic-008, t10_r01 raw | 1 | 6 (V344) | **6/7** |
| Basic-009, t07_r01 final refinement | 1 | 7 (V353) | **7/7** |

P2 uses the strict gold-informed Olympiad rubric; the Basic cases use the official IMOBench ProofAutoGrader rubric. All three were independent gpt-5.6-sol / xhigh calls, with zero failed grading calls. P2 retains a minor missing orientation-sign justification; Basic-008 retains a minor missing boundary justification; Basic-009 is correct.

This validation reran proof writing, internal audits and final revision, with mandatory budget forcing. It replayed each original certificate and did not rerun detection, matching, formalization or certificate search. No prior rewritten proof, grading feedback or reference solution entered generation. These results establish successful regeneration for the saved cases, not a deterministic guarantee of future model scores.

Validation: 115 targeted tests passed. All three certificates replayed successfully. Lemmas, appendices, tool-purpose context and source-edit instructions are byte-identical to the successful versions; the first rewrite's system and user prompts also match exactly.

Frozen package: [V356](runtime/cognitive_well_harness_v0_3_356_v349_discrete_consolidation_20260917/README.md).

Release SHA-256: `b899438a603c521d5b40f1fc97fbedc0bbfb7c82d086223014e1e3f706b11e68`.

P2 strict-policy SHA-256: `1a8c5d02a7bd84a53ad011cf889ceaaca7ff94166536565bda49082649781ecf`.

[Detailed validation](../../benchmarks/launches/v356_consolidation_20260917T071542Z/comparison.md) · [Machine-readable comparison](../../benchmarks/launches/v356_consolidation_20260917T071542Z/comparison.json) · [Saved-certificate compatibility](../../benchmarks/launches/v356_consolidation_20260917T071542Z/compatibility.json).

Use [the experimental entry point](README.md) with a fresh output directory.
Add `--resume-selected-certificate-from SOURCE_NATIVE_RUN` for regeneration
from a selected saved certificate. Source-run paths must be available locally.
The release digest above belongs to the historical validation; the current
runtime inventory records the relocated public copy and its test fixtures.
