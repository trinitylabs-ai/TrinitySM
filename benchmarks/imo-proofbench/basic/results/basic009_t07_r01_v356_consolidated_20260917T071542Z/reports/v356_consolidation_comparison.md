# V356 consolidated harness validation

V349 geometry/root implementation with the V353 discrete extension. Validation replays each original selected certificate, then regenerates the proof with mandatory budget forcing and grades independently. No new detection, matching, formalization or certificate searches are performed.

| Problem | Original score | Previous successful version | V356 score | Status |
|---|---:|---:|---:|---|
| imo2026_p2 (t07_r02, R1-C3) | 4/7 | V349: 6/7 | 6/7 | completed |
| PB-Basic-008 (t10_r01, raw) | 1/7 | V344: 6/7 | 6/7 | completed |
| PB-Basic-009 (t07_r01, R1-C3) | 1/7 | V353: 7/7 | 7/7 | completed |

The Basic scores use the official IMOBench rubric; P2 uses the strict Olympiad policy. All are independent gpt-5.6-sol / xhigh calls.

Validation: 115 targeted tests passed. All three original certificates replayed successfully; exported lemmas, appendices, tool-purpose context and source-edit instructions are byte-identical to the successful versions.

Frozen release SHA-256: `b899438a603c521d5b40f1fc97fbedc0bbfb7c82d086223014e1e3f706b11e68`.

[Frozen package](/opt/proof-workshop/cognitive_well_harness_v0_3_356_v349_discrete_consolidation_20260917/README.md) · [Compatibility checks](/opt/proof-workshop/benchmarks/launches/v356_consolidation_20260917T071542Z/compatibility.json) · [Tests](/opt/proof-workshop/benchmarks/launches/v356_consolidation_20260917T071542Z/targeted_tests.log)

One launcher preflight failed because V356 was missing from a duplicate package registry. No model calls ran in that attempt. The launcher entry was fixed and all retries use fresh preflight directories; the frozen harness did not change.

## imo2026_p2

**6/7**. The coordinate reduction, circumcenter formula, target polynomial T, and explicit algebraic certificate form a valid route to the conclusion. The remaining issue is a routine but load-bearing orientation check: for each of the three angle equalities, the two signed cross products must be shown to have the same sign before the displayed polynomial equation follows. This can be repaired directly from positive barycentric coordinates supplied by the interiority hypotheses.

First issue: The proof uses dot/cross as the cotangent of an unsigned angle, although the correct general formula has an absolute value on the cross product; it only broadly asserts, without explicitly verifying, that the relevant oriented cross products have matching signs.

[Proof](/opt/proof-workshop/benchmarks/imo2026/results/p2_t07_r02_v356_consolidated_20260917T071542Z/proofs/imo2026_p2/t07_r02/tool_rewrite.md) · [External grade](/opt/proof-workshop/benchmarks/imo2026/results/p2_t07_r02_v356_consolidated_20260917T071542Z/grades/imo2026_p2/t07_r02/tool_rewrite/strict/summary.json)

## PB-Basic-008

**6/7**. 

First issue: See official grade.

[Proof](/opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic008_t10_r01_v356_consolidated_20260917T071542Z/proofs/PB-Basic-008/t10_r01/tool_rewrite.md) · [External grade](/opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic008_t10_r01_v356_consolidated_20260917T071542Z/grades/PB-Basic-008/t10_r01/tool_rewrite/result.json)

## PB-Basic-009

**7/7**. 

First issue: See official grade.

[Proof](/opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic009_t07_r01_v356_consolidated_20260917T071542Z/proofs/PB-Basic-009/t07_r01/tool_rewrite.md) · [External grade](/opt/proof-workshop/benchmarks/imo-proofbench/basic/results/basic009_t07_r01_v356_consolidated_20260917T071542Z/grades/PB-Basic-009/t07_r01/tool_rewrite/result.json)
