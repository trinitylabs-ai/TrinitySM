# ProofBench B 1.12.0 progress — 24 September 2026

**Partial run, paused after a GPU driver failure.** Run: `proofbench_B_1_12_0_twice_20260923T032058Z`.

IMOBench B.5, gpt-5.6-sol/xhigh, two independent grades per available proof. This snapshot contains 126 judgments of 63 proofs across 16 reported problems; the planned suite has 60 problems and 480 judgments.

Average and Oracle@4 totals include only complete four-lane portfolios. Selector@1 aggregates the same portfolios when selection completed. Missing lanes are unavailable, never zero. These priority-ordered partial results are not a representative full-suite estimate.

| Problem | t07_r01 | t07_r02 | t10_r01 | t10_r02 | Average | Oracle@4 | Selector@1 | Order disagreements | Generation minutes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PB-Basic-001 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 12/12 (100.0%) | 49.5 |
| PB-Basic-002 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 2/12 (16.7%) | 76.8 |
| PB-Basic-003 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 5/12 (41.7%) | 105.8 |
| PB-Basic-004 | 7/7 | 7/7 | 6/6 | 7/7 | 6.75 | 7 | 7 | 6/12 (50.0%) | 80.8 |
| PB-Basic-005 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 4/12 (33.3%) | 103.6 |
| PB-Basic-006 | 1/1 | 7/1 | 7/7 | 0/0 | 3 | 7 | 7 | 2/12 (16.7%) | 127.3 |
| PB-Basic-007 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | 1 | 3/12 (25.0%) | 112.7 |
| PB-Basic-008 | 7/7 | 7/7 | 6/6 | 7/7 | 6.75 | 7 | 7 | 1/12 (8.3%) | 116.0 |
| PB-Basic-009 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | 1 | 6/12 (50.0%) | 126.1 |
| PB-Basic-010 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 9/12 (75.0%) | 31.5 |
| PB-Basic-011 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 6/12 (50.0%) | 79.0 |
| PB-Basic-012 | 7/7 | 7/7 | 7/7 | 7/7 | 7 | 7 | 7 | 6/12 (50.0%) | 79.5 |
| PB-Basic-022 | 1/1 | 1/1 | 1/1 | 1/1 | 1 | 1 | 1 | 2/12 (16.7%) | 92.0 |
| PB-Basic-026 | 0/0 | missing | 0/0 | 1/1 | — | — | 1 | 1/6 (16.7%) | 140.6 |
| PB-Basic-029 | 0/0 | 1/1 | 1/1 | 0/0 | 0.5 | 1 | 1 | 1/12 (8.3%) | 123.9 |
| PB-Advanced-002 | 1/1 | 6/6 | 1/1 | 1/1 | 2.25 | 6 | — | incomplete | 38.3 |

Each lane cell shows pass 1 / pass 2. The three summary columns use the mean of the two grades per proof. Presentation-order disagreement is counted separately for each model and unordered pair.

Advanced 002 contains saved lazy-checked fallbacks: refinement and cross-lane selection did not finish. Basic 026 has one missing lane; its Selector@1 comes from three available candidates. Completed offline format recoveries are included in selection, with the original response preserved. Independent lane-recovery experiments are not substituted into this native-run snapshot.

| Set | Complete portfolios | Average | Oracle@4 | Selector@1 |
|---|---:|---:|---:|---:|
| Basic | 14/30 | 69/98 | 74/98 | 74/98 |
| Advanced | 1/30 | 2.25/7 | 6/7 | unavailable |

This page publishes the score and selection summary. Full proof, grading-response and comparison-response artifacts remain preserved in the local run archive.
