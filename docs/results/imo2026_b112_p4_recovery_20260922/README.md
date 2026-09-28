# P4 saved-lane recovery

Original frozen B 1.12.0 results are preserved. Only t10_r02 resumes at R2; the other three lane proofs and matching grades are reused. This is a separately labeled recovery, not a fresh generation.

| Lane | Before stage | Before grades | After stage | After grades | Mean change |
|---|---|---|---|---|---:|
| t07_r01 | refinement_3 | [7, 7] | refinement_3 | [7, 7] | +0 |
| t07_r02 | refinement_3 | [6, 6] | refinement_3 | [6, 6] | +0 |
| t10_r01 | refinement_2 | [2, 2] | refinement_2 | [2, 2] | +0 |
| t10_r02 | refinement_1 | [5, 5] | refinement_2 | [7, 7] | +2 |

Cross-lane winner: **t10_r02**, grades **[7, 7]**.
Order disagreement: 1/12.

## Six-problem aggregate (mean of two grades)

| Portfolio | Average /7 | Oracle@4 /42 | Selector@1 /42 |
|---|---:|---:|---:|
| original_fresh_uniform_suite | 4.125 | 29 | 29 |
| with_explicit_p4_recovery | 4.208 | 29 | 29 |

See REPORT.json for all votes, fallback records, grade provenance, and stage times.
