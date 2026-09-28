# Retained IMO 2026 strict-v2 grades

The user stopped the mixed-benchmark v2 study and requested deletion of all
strict-v2 IMO-ProofBench grading results. Basic and Advanced retain IMOBench B.5
for core results and ablations. Their generated proofs remain available, but
portable v2 grades, private grader outputs and mixed score reports were removed.
The [removal record](proofbench_v2_removal.json) records counts without scores.

The retained IMO portion is complete: **150 grades for 75 distinct proofs**,
using original repetitions **1 and 2**, with `gpt-5.6-sol / xhigh` and the unchanged
[strict-v2 policy](../../../docs/public_release/grading/strict_olympiad_policy_v2.txt).
The [retained inventory](retained_imo_manifest.json), [grades report](REPORT.md)
and [structured results](results.json) cover only IMO 2026. Identical proofs
share grades across cohort memberships. Repetitions 3 and 4 were removed as
recorded in the [two-grade retention record](two_grade_retention.json).

The core reporting matrix uses **one complete pass with the lower total
Average**, retaining its problem rows and Oracle@4 values together. Pass 1
has 24/42 Average and 29/42 Oracle@4; pass 2 has 24.50/42 and 29/42. The table
therefore reports pass 1, whose problem rows sum to its totals. All three
IMO ablation configurations report pass 1 for both metrics. Both passes
remain available in the evidence. IMO P2 tool rows separately retain
each input/rewrite's lower grade.

The [portable reporting evidence](../../../docs/public_release/imo2026_v2_lowest.json)
contains both passes for core proofs, all three IMO ablation settings and P2
rewrites. It contains no MechMath reference bodies. See the
[external-reference setup](../../../docs/public_release/grading/README.md#external-imo-reference-setup)
for operator downloads and rights information.

The original manifest and execution configurations remain input/protocol records
of the stopped experiment. They do not imply that ProofBench v2 scores are
retained or eligible for release. No grading or publication watcher is running.

Verify the reporting matrices without model calls:

```bash
python3 -B scripts/reproduce.py
```

The solver prompts, submitted proofs and evaluation policy strings are unchanged.
