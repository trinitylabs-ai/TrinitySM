# Completed final-refinement grading

Six completed Refinement 3 proofs previously had no B.5 grade in the reporting snapshot. Their final proof files are now graded and replace the earlier Refinement 2 selections. No solver calls or proof edits were made.

Grader: **gpt-5.6-sol / xhigh**, one isolated automated B.5 call per proof, with official reference solutions and per-problem guidelines. All six calls completed; isolation audits confirmed one grading turn and zero tool calls. Prior grades and solver reviews were excluded from model inputs.

| Problem | Lane | Earlier Refinement 2 | Final Refinement 3 |
|---|---|---:|---:|
| PB-Advanced-017 | `t07_r01` | 0/7 | 6/7 |
| PB-Advanced-017 | `t10_r01` | 7/7 | 7/7 |
| PB-Advanced-018 | `t07_r01` | 0/7 | 0/7 |
| PB-Advanced-018 | `t07_r02` | 0/7 | 0/7 |
| PB-Advanced-018 | `t10_r01` | 1/7 | 1/7 |
| PB-Advanced-018 | `t10_r02` | 1/7 | 1/7 |

**Advanced:** Average **38.57% (81/210) → 39.29% (82.5/210)**; Oracle@4 remains **48.10% (101/210)**.

**All IMO-ProofBench:** Average **59.29% (249/420) → 59.64% (250.5/420)**; Oracle@4 remains **66.43% (279/420)**. Basic and IMO 2026 are unchanged. The full-harness ablation uses the same updated final selections.

The [manifest](../manifest.json) binds all proof, grade, report and isolation-audit files by hash and retains the replaced selections for provenance. Individual grading explanations are stored beside this report in the per-problem directories.
