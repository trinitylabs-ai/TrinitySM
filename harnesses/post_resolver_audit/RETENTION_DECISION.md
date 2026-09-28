# Retain the post-resolver auditor

On 2026-09-21, the user decided to keep the existing auditor after reviewing the
completed R2-to-R3 diagnostic: "ok then i think the auditor is good. we should keep it."

Subsequent scheduling update: the user requested twelve concurrent audits per model.
B 1.10.0 implements twelve Gemma and twelve Qwen slots; the original retention
decision below used four slots. The four-approval decision rule is unchanged.

Retain the current design: Gemma and Qwen audit the proof changes in independent
forward and reverse presentation orders, using the existing Markdown prompt and
reasoning-plus-answer BF. Preserve four-call concurrency and mechanical validation
V2, including code-owned request, proof and response identities. For each model,
both orders must validly approve R3 to replace R2; the combined strategy requires
all four approvals. Otherwise retain R2. Auditors never receive grades or reference
solutions. This decision retains the existing strategies without selecting a new
single-model default or changing the frozen released harness.

## Evidence for retention

Run: `proofbench_r2_r3_score_changes_20260921T173049Z`.

All 19 unequal-score pairs completed, with 76 audit responses (28 reused and 48 new).
Evaluation uses existing single-pass IMOBench B.5 grades. Cases were selected by
score difference for this diagnostic; grades were used only for evaluation after
audit selection.

| R2/R3 score distinction | Cases | Gemma correct | Qwen correct | Combined correct |
|---|---:|---:|---:|---:|
| 0/1 versus 6/7 | 5 | 5 | 5 | 5 |
| 6 versus 7 | 3 | 2 | 1 | 2 |
| 0 versus 1 | 11 | 3 | 3 | 2 |

All three selection strategies retained all four improvements from 0/1 to 6/7
and blocked the single 6-to-1 regression. Qwen had one incorrect individual vote
on that regression, but its other order rejected R3 and the final selection kept R2.
The useful observed behavior is preserving these major improvements and preventing
the major regression. Exact-score agreement should be reported alongside these
separate counts, rather than used alone to assess the auditor.

The retained design still misses some distinctions within each score band: all
four votes accepted the 7-to-6 regression on Advanced-022/t10_r01, and the combined
rule rejected all eight 0-to-1 improvements. The five cases spanning the low/high
score boundary are encouraging evidence, not a general correctness guarantee.

Source report:
verified votes and paired scores in the local archive `proofbench_r2_r3_score_changes_20260921T173049Z/validated/REPORT.md`.
The experiment artifacts remain in the local experiment archive.

This records the retention decision. It makes no new model calls, changes no
prompts, and does not claim that the independent auditor is already integrated
into the released Harness 1.8.0 pipeline.
