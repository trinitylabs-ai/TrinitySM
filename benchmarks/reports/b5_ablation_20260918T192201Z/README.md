# Corrected ablation evaluation

IMO-ProofBench Basic and Advanced use the published **IMOBench B.5** rubric,
including official per-problem reference solutions and grading guidelines.
New grades use `gpt-5.6-sol / xhigh`, one isolated call per distinct proof.
Existing B.5 grades for unchanged proofs are retained. Prior grades and solver
reviews are excluded from grader inputs. Strict-v2 ProofBench grades were deleted.

The completed B.5 set contains **128 no-BF proofs**: 120 Advanced proofs and eight
Basic proofs for Basic-009 and Basic-026 with seeds matching the BF configuration.
There are no new solver calls. Private grader requests and responses stay under
per-benchmark `grading/work/` directories. The task manifests pin the mathematical
inputs; the official dataset provides reference solutions and guidelines.

IMO 2026 already has two strict-v2 grades for every ablation proof. Its reporting
matrices use **pass 1 for all three configurations**, including Oracle@4 from
that same pass: raw without BF gives 18.75/42 Average and 21/42 Oracle@4;
raw with BF gives 19/42 and 21/42; full harness gives 24/42 and 29/42.
No IMO grading is scheduled by this plan.

All 128 grades completed, with no failures; successful traces passed the
isolation audit. See [the matrices](REPORT.md) and
[portable proof/grade bindings](../../../docs/public_release/proofbench_ablation_b5.json).
