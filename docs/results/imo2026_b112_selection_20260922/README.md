# Fresh B 1.12.0 IMO 2026 results with both selectors

All six problems were generated fresh end to end with the identical frozen B 1.12.0 harness and recorded settings.

P1 completed first; P2–P6 were then rerun fresh. The same frozen release, launch parameters, server/model settings and grading protocol are verified for every problem. These problems informed selector development; this is not a held-out evaluation.

## Every selected lane final

| Problem | Lane | Stage | Pass 1 | Pass 2 | Mean | Cross-lane winner |
|---|---|---|---:|---:|---:|---|
| imo2026_p1 | [t07_r01](proofs/imo2026_p1/t07_r01.md) | refinement_2 | 7 | 7 | 7 |  |
| imo2026_p1 | [t07_r02](proofs/imo2026_p1/t07_r02.md) | refinement_3 | 7 | 7 | 7 | yes |
| imo2026_p1 | [t10_r01](proofs/imo2026_p1/t10_r01.md) | refinement_2 | 7 | 7 | 7 |  |
| imo2026_p1 | [t10_r02](proofs/imo2026_p1/t10_r02.md) | refinement_2 | 7 | 7 | 7 |  |
| imo2026_p2 | [t07_r01](proofs/imo2026_p2/t07_r01.md) | refinement_3 | 4 | 4 | 4 |  |
| imo2026_p2 | [t07_r02](proofs/imo2026_p2/t07_r02.md) | refinement_2 | 4 | 4 | 4 | yes |
| imo2026_p2 | [t10_r01](proofs/imo2026_p2/t10_r01.md) | refinement_2 | 3 | 3 | 3 |  |
| imo2026_p2 | [t10_r02](proofs/imo2026_p2/t10_r02.md) | refinement_2 | 4 | 4 | 4 |  |
| imo2026_p3 | [t07_r01](proofs/imo2026_p3/t07_r01.md) | refinement_3 | 1 | 2 | 1.5 |  |
| imo2026_p3 | [t07_r02](proofs/imo2026_p3/t07_r02.md) | refinement_2 | 2 | 1 | 1.5 |  |
| imo2026_p3 | [t10_r01](proofs/imo2026_p3/t10_r01.md) | refinement_2 | 1 | 1 | 1 |  |
| imo2026_p3 | [t10_r02](proofs/imo2026_p3/t10_r02.md) | refinement_2 | 2 | 2 | 2 | yes |
| imo2026_p4 | [t07_r01](proofs/imo2026_p4/t07_r01.md) | refinement_3 | 7 | 7 | 7 | yes |
| imo2026_p4 | [t07_r02](proofs/imo2026_p4/t07_r02.md) | refinement_3 | 6 | 6 | 6 |  |
| imo2026_p4 | [t10_r01](proofs/imo2026_p4/t10_r01.md) | refinement_2 | 2 | 2 | 2 |  |
| imo2026_p4 | [t10_r02](proofs/imo2026_p4/t10_r02.md) | refinement_1 | 5 | 5 | 5 |  |
| imo2026_p5 | [t07_r01](proofs/imo2026_p5/t07_r01.md) | refinement_3 | 6 | 6 | 6 |  |
| imo2026_p5 | [t07_r02](proofs/imo2026_p5/t07_r02.md) | refinement_2 | 3 | 3 | 3 |  |
| imo2026_p5 | [t10_r01](proofs/imo2026_p5/t10_r01.md) | refinement_3 | 6 | 6 | 6 | yes |
| imo2026_p5 | [t10_r02](proofs/imo2026_p5/t10_r02.md) | refinement_2 | 3 | 3 | 3 |  |
| imo2026_p6 | [t07_r01](proofs/imo2026_p6/t07_r01.md) | refinement_3 | 3 | 3 | 3 |  |
| imo2026_p6 | [t07_r02](proofs/imo2026_p6/t07_r02.md) | refinement_2 | 3 | 3 | 3 |  |
| imo2026_p6 | [t10_r01](proofs/imo2026_p6/t10_r01.md) | refinement_3 | 3 | 3 | 3 | yes |
| imo2026_p6 | [t10_r02](proofs/imo2026_p6/t10_r02.md) | refinement_2 | 3 | 3 | 3 |  |

## Provenance

- imo2026_p1: generation 1.12.0; run `imo2026_B_1_12_0_p1_20260922T151110Z_native`; order disagreements 6/12. Generation elapsed: 92.5 minutes.
- imo2026_p2: generation 1.12.0; run `imo2026_B_1_12_0_p2_p6_20260922T153924Z_p2`; order disagreements 3/12. Generation elapsed: 108.2 minutes.
- imo2026_p3: generation 1.12.0; run `imo2026_B_1_12_0_p2_p6_20260922T153924Z_p3`; order disagreements 3/12. Generation elapsed: 132.7 minutes.
- imo2026_p4: generation 1.12.0; run `imo2026_B_1_12_0_p2_p6_20260922T153924Z_p4`; order disagreements 1/12. Generation elapsed: 119.7 minutes.
- imo2026_p5: generation 1.12.0; run `imo2026_B_1_12_0_p2_p6_20260922T153924Z_p5`; order disagreements 2/12. Generation elapsed: 115.8 minutes.
- imo2026_p6: generation 1.12.0; run `imo2026_B_1_12_0_p2_p6_20260922T153924Z_p6`; order disagreements 3/12. Generation elapsed: 124.5 minutes.

Each proof has two independent Strict Olympiad v2 grades, including preserved evaluator answers. Hashes and every vote are in SCORECARD.json. Reference bodies and machine-specific execution logs are excluded. Source evidence hashes preserve the link to the complete local archive.

Recompute and verify from the repository root: `python -B scripts/verify_latest_selection.py`. No inference calls or reference solutions are needed.
