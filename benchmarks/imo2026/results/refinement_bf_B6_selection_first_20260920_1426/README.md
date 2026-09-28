# B: role-specific refinement BF results

**Completed six-problem comparison, 20 September 2026.** B averages **4.396/7**, versus **4.042/7** for archived A: **+0.354/7**. Both-pass full-credit proofs increase from **5/24 to 8/24**. Best-per-problem totals are **29/42 for A and 30/42 for B** in both grading passes.

B uses role-specific chat-BF continuation wording with the same four lazy-checked starting proofs per problem, archived seed policy, sampling and configured refinement budgets. A reuses archived original-cue proofs and saved grades. P4 was completed in a separate run and imported; P1, P2, P3, P5 and P6 supply the other 20 B proofs.

This is a descriptive comparison against historical controls. Proof-dependent later seeds and actual compute can diverge. It does not establish a causal or statistically significant improvement.

**Scope:** all 24 final B submissions and 48 grades are complete. Independent selector results and the later P3 recovery are excluded from this snapshot. Oracle/best scores below use external grades; they are not selector scores.

## Full B score matrix

Each cell is **(pass 1, pass 2)** out of 7. Candidate links open the exact submitted proof.

| Problem | t10_r01 | t10_r02 | t07_r01 | t07_r02 | Mean / 7 |
|---|---|---|---|---|---:|
| P1 | [(7, 7)](proofs/B/imo2026_p1/t10_r01.md) | [(7, 7)](proofs/B/imo2026_p1/t10_r02.md) | [(7, 7)](proofs/B/imo2026_p1/t07_r01.md) | [(7, 7)](proofs/B/imo2026_p1/t07_r02.md) | 7.000 |
| P2 | [(3, 3)](proofs/B/imo2026_p2/t10_r01.md) | [(3, 3)](proofs/B/imo2026_p2/t10_r02.md) | [(3, 3)](proofs/B/imo2026_p2/t07_r01.md) | [(4, 4)](proofs/B/imo2026_p2/t07_r02.md) | 3.250 |
| P3 | [(1, 1)](proofs/B/imo2026_p3/t10_r01.md) | [(1, 1)](proofs/B/imo2026_p3/t10_r02.md) | [(1, 1)](proofs/B/imo2026_p3/t07_r01.md) | [(2, 2)](proofs/B/imo2026_p3/t07_r02.md)† | 1.250 |
| P4 | [(2, 2)](proofs/B/imo2026_p4/t10_r01.md) | [(7, 7)](proofs/B/imo2026_p4/t10_r02.md) | [(7, 6)](proofs/B/imo2026_p4/t07_r01.md) | [(7, 7)](proofs/B/imo2026_p4/t07_r02.md) | 5.625 |
| P5 | [(7, 7)](proofs/B/imo2026_p5/t10_r01.md) | [(6, 6)](proofs/B/imo2026_p5/t10_r02.md) | [(7, 7)](proofs/B/imo2026_p5/t07_r01.md) | [(5, 5)](proofs/B/imo2026_p5/t07_r02.md) | 6.250 |
| P6 | [(3, 3)](proofs/B/imo2026_p6/t10_r01.md) | [(3, 3)](proofs/B/imo2026_p6/t10_r02.md) | [(3, 3)](proofs/B/imo2026_p6/t07_r01.md) | [(3, 3)](proofs/B/imo2026_p6/t07_r02.md) | 3.000 |

† P3 `t07_r02` submits its C1 fallback after a C2 execution failure. The other 23 B lanes reached C3. A completed C3 may retain an earlier proof unchanged; all scores bind to the exported proof hashes. Subsequent P3 recovery cannot replace this comparison entry.

## A versus B

| Problem | A mean / 7 | B mean / 7 | B − A | B refinement wall minutes |
|---|---:|---:|---:|---:|
| P1 | 7.000 | 7.000 | +0.000 | 66.76 |
| P2 | 3.375 | 3.250 | -0.125 | 80.10 |
| P3 | 1.625 | 1.250 | -0.375 | 104.76 |
| P4 | 4.500 | 5.625 | +1.125 | 116.29 |
| P5 | 5.000 | 6.250 | +1.250 | 81.65 |
| P6 | 2.750 | 3.000 | +0.250 | 105.15 |

| Metric | A | B |
|---|---:|---:|
| Mean across four candidates and both grades, equal weight per problem | 4.042 | 4.396 |
| Both grading passes award 7/7 | 5/24 | 8/24 |
| Sum of best scores per problem, pass 1 / pass 2 | 29 / 29 | 30 / 30 |
| Lanes reaching C3 | 22/24 | 23/24 |
| Fallback submissions | 2/24 | 1/24 |
| Proofs with grading-pass disagreement | 4/24 | 1/24 |

The primary metric averages the two grades per proof, then four proofs per problem and six problems equally. This experiment does not use the lower-total-pass convention of the main release tables. Repeated grades share the same evaluator and may share errors. Refinement wall time excludes raw/lazy generation, grading and selection; concurrent lane durations must not be summed. Comparable whole-arm timing for archived A is unavailable.

## Grading and evidence

Grader: **gpt-5.6-sol / xhigh**, **Strict Olympiad v2**, two isolated calls per B proof. All 48 B grading invocations completed with no retry errors. A reuses 48 saved grades. First valid numerical judgments are retained, including any verdict/metadata disagreement.

- [Machine-readable comparison](comparison.json): all 48 A/B submissions, 96 grade links, hashes, fallback records and checkpoint timings.
- [B grading evidence](grades/B) and [archived A grading evidence](grades/A): individual judgments and explanations.
- [Generation provenance](provenance/generation.json), [exact B continuation cues](provenance/role_specific_cues.json), [grading configuration](grading/configuration.json), and [rubric](grading/strict_olympiad_policy_v2.txt).
- [Manifest](manifest.json): published file hashes and source artifact identities.
- [Reference source metadata](grading/reference_sources.json). External reference bodies and raw grader requests are not distributed; see the [reference setup policy](../../../../docs/public_release/grading/README.md).

Historical source pointers in provenance use `source_workspace/` or `publication_source/` labels. They describe the original source layout, not files bundled in this archive. Full GPU transport traces remain in the original runs.

Verify the published evidence from the repository root:

```bash
python3 scripts/verify_refinement_bf_results.py
```
