# TrinitySM: Towards IMO Gold with Small Language Models — A Harness for Extended Reasoning and Proof Refinement

**Public release report — TrinitySM 0.1.0-rc.1**

The current default uses the frozen B 1.12.0 generation engine and a captured
Qwen-only final selector. Earlier run identities, proofs and grades remain in
the dated evidence bundles. Historical matrices and ablations are labeled below.

## Current results and selection policy

Updated **28 September 2026**. Final cross-lane selection uses **Qwen only**:
six lane pairs in two independent presentation orders, for **12 votes** and up
to 12 concurrent calls. Three available lanes require six votes. Ties follow
the recorded seed-derived candidate order, without using grades.

The **R2/R3 audit still uses Gemma and Qwen**, in both orders: four decisions
per eligible lane, all of which must choose R3 before it replaces R2.

The scores below are computed by re-tallying archived Qwen comparisons from
runs that recorded both models' votes. The generated proofs and grades are
unchanged. Each proof's two independent grades are averaged before computing
Average, Oracle@4 and Selector@1. Original selections remain in their archived
scorecards.

On these archived proof portfolios, Qwen-only selection matched the earlier
Gemma-and-Qwen tally on IMO and yielded a slightly higher ProofBench score; see
the [selection comparison](results/qwen_selection_20260928/README.md).
This retrospective comparison does not establish that Qwen-only selection is
generally superior.

### IMO 2026 — current

<!-- BEGIN QWEN IMO RESULTS -->
| Problem | Average | Selector@1 | Oracle@4 |
|---|---:|---:|---:|
| P1 | 7 | 7 | 7 |
| P2 | 3.75 | 4 | 4 |
| P3 | 1.5 | 2 | 2 |
| P4 | 5 | 7 | 7 |
| P5 | 4.5 | 6 | 6 |
| P6 | 3 | 3 | 3 |
| **Total (of 42)** | **24.75** | **29** | **29** |

[Qwen selections and archived proof grades](results/qwen_selection_20260928/README.md)
<!-- END QWEN IMO RESULTS -->

### IMO-ProofBench — current

<!-- BEGIN QWEN PROOFBENCH RESULTS -->
| Set | Problems | Proofs | Average | Selector@1 | Oracle@4 |
|---|---:|---:|---:|---:|---:|
| Basic | 30 | 119/120 | 78.13% | 82.38% | 82.62% |
| Advanced | 30 | 118/120 | 39.25% | 50.00% | 52.38% |
| Combined | 60 | 237/240 | 58.69% | 66.19% | 67.50% |

Three proofs are missing and are left out of the averages. The selector chose a
best-scoring proof, or one tied with it, on 52 of 60 problems, and never chose a
0–1 proof when a 6–7 proof was available.

[Qwen selections and comparison with the archived results](results/qwen_selection_20260928/README.md) ·
[SCORECARD.json](results/qwen_selection_20260928/SCORECARD.json)
<!-- END QWEN PROOFBENCH RESULTS -->

## Motivation and impact

**Our primary goal is to test how far extended reasoning and a carefully designed
harness can improve the mathematical proof performance of small language models
by building on their native reasoning capabilities, without additional
post-training.**

The raw-generation baseline shows substantial room for improvement on
Olympiad-level proof tasks, particularly on IMO-ProofBench Advanced.

**Our results suggest that high-level mathematical reasoning may not always
require very large foundation models.** On the tasks studied here, smaller,
locally served models produced stronger proofs when supported by a carefully
designed harness.

In our recorded experiments, TrinitySM improved externally graded proof
scores over raw generation by combining additional inference-time computation
with structured review and revision.

From raw generation without extended reasoning to the full harness, Basic Average
rises from **62.14% to 78.13%** and Advanced Average from **23.69% to 39.25%**.
Oracle@4 rises from **73.33% to 82.62%** on Basic and **30.95% to 52.38%** on
Advanced. On IMO 2026, Average is **18.75/42 → 24.75/42** and Oracle@4 is
**21/42 → 29/42**. These compare saved raw baselines with the current
two-grade means across different runs, not a controlled ablation.

These findings open a research direction toward making sophisticated mathematical
and logical capabilities available through local inference without hosted
service API calls.
The current generation and refinement workflow already supports that mode;
the reported external grading remains a separate evaluation step.

Our longer-term vision is for mobile phones and robots to carry these reasoning
capabilities on device, supporting decision-making, situational awareness and
understanding. The present evidence concerns mathematical proofs generated on
workstation GPUs. Deployment on smaller devices and transfer to those broader
tasks require separate validation of efficiency, reliability and capability.
The [future-work agenda](#future-work) connects this vision to targeted
post-training, more efficient inference and transfer into smaller models.

The contribution is a reproducible workflow for making more effective use of
locally served models' proof capabilities, together with the proofs and evaluation
evidence needed to inspect the outcome. These are retrospective comparisons
across saved configurations; additional inference compute and the combined
Gemma/Qwen workflow are part of the full-harness setting. Individual components'
effects are not isolated. Oracle@4 is an externally graded maximum across
candidates, and the grading schemes and selection rules are specified below.

## Historical score matrices

ProofBench reporting: **19 September 2026 (UTC)**; IMO v2 reporting: **18 September 2026**. **Workshop Pipeline** is the
composite statement-to-proof harness: **Workshop Draft** generates and checks
initial candidates, and **Workshop Refine** runs review and revision cycles.
**Workshop Tools** is an experimental, opt-in extension. Submitted proofs receive
separate automated grading by **gpt-5.6-sol / xhigh**.

The results describe saved experiments across their recorded implementations.
Core-pipeline results and results including experimental tool calls are shown
in separate matrices. The [composite documentation](../harnesses/proof_workshop/README.md)
and [module guide](../harnesses/modules/README.md) explain the workflow and
public names. Historical version IDs are retained below for reproducibility.

Model and hardware settings are recorded in the
[environment documentation](../ENVIRONMENT.md).

Both grading schemes use **gpt-5.6-sol with xhigh reasoning**. IMO-ProofBench
shows **percentage of maximum (acquired score/maximum score)**, calculated from
the original **0–7 grades**. IMO 2026 shows **scores only**, out of 7 per problem
and out of 42 overall. Percentages and fractional point totals are rounded to
two decimal places for display. The IMO-ProofBench percentages measure
normalized scores, not percentile ranks among other systems.

### IMO-ProofBench

<!-- BEGIN IMOBENCH SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Set</th>
      <th width="200" align="left">Grading scheme</th>
      <th width="200" align="right">Average</th>
      <th width="200" align="right">Oracle@4</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">Basic (30)</td><td align="left">IMOBench B.5</td><td align="right">80.00% (168/210)</td><td align="right">84.76% (178/210)</td></tr>
    <tr><td align="left">Advanced (30)</td><td align="left">IMOBench B.5</td><td align="right">39.29% (82.5/210)</td><td align="right">48.10% (101/210)</td></tr>
    <tr><td align="left">All IMOBench (60)</td><td align="left">IMOBench B.5</td><td align="right">59.64% (250.5/420)</td><td align="right">66.43% (279/420)</td></tr>
  </tbody>
</table>
<!-- END IMOBENCH SCORE MATRIX -->

**Comparison with the cited Cognitive Well paper:**
[Dang et al. (v2, 12 June 2026) report 87.6% on PB-Adv using Gemini 3.1 Pro,
at approximately US$9 per problem](https://arxiv.org/html/2602.16793v2). The archived core-only
result is **39.29% average (82.5/210)** and **48.10% Oracle@4 (101/210)** using
local Gemma 4 31B + Qwen3.6 27B, with external grading by gpt-5.6-sol/xhigh.
The paper describes a final model selection step when combining two pipeline
runs. Our average aggregates the available lane scores, while
Oracle@4 selects the highest external grade per problem after evaluation;
that selection is not available to the solver. The model backbones, inference
budgets, grading implementations and selection rules differ, so these figures
are not a controlled comparison of harness quality. The release does not
reproduce the paper's full pipeline. The citation credits the specific drafting ideas documented in
[Sources and papers](sources.md#cognitive-well-ideas-used-in-workshop-draft).

### IMO 2026

<!-- BEGIN IMO2026 SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Problem</th>
      <th width="200" align="left">Grading scheme</th>
      <th width="200" align="right">Average</th>
      <th width="200" align="right">Oracle@4</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">P1</td><td align="left">Strict v2 (pass 1)</td><td align="right">7/7</td><td align="right">7/7</td></tr>
    <tr><td align="left">P2</td><td align="left">Strict v2 (pass 1)</td><td align="right">3.25/7</td><td align="right">4/7</td></tr>
    <tr><td align="left">P3</td><td align="left">Strict v2 (pass 1)</td><td align="right">1.75/7</td><td align="right">2/7</td></tr>
    <tr><td align="left">P4</td><td align="left">Strict v2 (pass 1)</td><td align="right">4.25/7</td><td align="right">6/7</td></tr>
    <tr><td align="left">P5</td><td align="left">Strict v2 (pass 1)</td><td align="right">5/7</td><td align="right">7/7</td></tr>
    <tr><td align="left">P6</td><td align="left">Strict v2 (pass 1)</td><td align="right">2.75/7</td><td align="right">3/7</td></tr>
    <tr><td align="left">IMO 2026 (6)</td><td align="left">Strict v2 (pass 1)</td><td align="right">24/42</td><td align="right">29/42</td></tr>
  </tbody>
</table>
<!-- END IMO2026 SCORE MATRIX -->

Reported: the complete pass with the lower total Average across two separate automated v2 grading passes using the same evaluator (**pass 1**): **24.00/42 Average, 29/42 Oracle@4**. Other pass (**pass 2**): **24.50/42 Average, 29/42 Oracle@4**.

Every problem row and both metrics come from the selected pass, so the rows
sum to the overall totals. Ties in total Average select pass 1.
The [two-pass evidence](public_release/imo2026_v2_lowest.json) preserves both grades.

For IMO 2026, each fixed proof was graded in two separate calls to the same
**gpt-5.6-sol / xhigh** evaluator under strict v2. For the full-harness portfolio,
the scores agree on **20 of 24 proofs**, with a largest difference of **3 points**.
Repeated grading measures repeatability; agreement does not establish mathematical
correctness or rule out errors shared by both calls.
The [grading variation report](../benchmarks/reports/strict_v2_consistency_20260918T064715Z/REPORT.md#imo-2026-benchmark-and-ablation-variation)
compares both passes for the benchmark and all three ablation configurations.

IMO-ProofBench uses the IMOBench B.5 rubric; IMO 2026 uses the separate strict
Olympiad v2 policy. The same rubric split applies to ablations. Scores are
summarized separately for these two benchmarks.

## Release benchmark context

Final ProofBench run: **26 September 2026**; historical ProofBench snapshot: **17 September 2026**. IMO results retain their separate run and grading provenance. Both external graders use
**gpt-5.6-sol / xhigh**. IMO-ProofBench shows **percentage of maximum
(acquired score/maximum score)**. IMO 2026 shows **scores only**, out of 7
per problem and out of 42 overall.

### ProofBench release context

**All 60 problems have a completed final selection.** The finalized run has
**237 available proofs, each graded twice (474 judgments)** by
**gpt-5.6-sol / xhigh** under IMOBench B.5. Three proof lanes remain missing;
57 problems have four candidates and three problems have three candidates.

**Average** first averages the two grades for each available proof, then
averages the available lanes within each problem and weights all problems
equally. **Missing lanes are excluded from the lane count and remain
ungraded.** **Oracle@4** is the best available
externally graded candidate. **Selector@1** is the grade of the proof chosen
by the Qwen-only voter, which receives neither grades nor reference solutions.
Every column includes all 30 Basic and 30 Advanced problems.

The missing lanes are **Basic-026 / `t07_r02`**, **Advanced-003 / `t07_r02`**,
and **Advanced-015 / `t07_r01`**. Their previous-run scores were **0**,
**also missing**, and **1**, respectively. No fresh lane retries were launched.

Qwen-only selection chose a best-scoring available proof or tie on **52/60 problems**.
The eight misses were two selections of **6.5 instead of 7**, and six choices
within the **0–1** range. There were **no cases of choosing a 0–1 proof when
a 6–7 proof was available**. Basic-016 and Advanced-003 selections were
completed by deterministic repairs of saved response formatting. Advanced-002
completed after its 12 connection-refused Qwen comparisons were rerun.
All submitted proofs and original execution records were retained.

With the same available-lane rule applied to the previous single-grade
baseline, overall **Average is 59.64% → 58.69% (−0.95 percentage points)**
and **Oracle@4 is 66.43% → 67.50% (+1.07 points)**. The previous snapshot
has no cross-lane Selector@1 score. The current run averages two grades per
proof; these different runs and grading repetitions are not a controlled ablation.

[Qwen selections and comparison](results/qwen_selection_20260928/README.md) ·
[Machine-readable scorecard](results/qwen_selection_20260928/SCORECARD.json) ·
[Original proof and grading evidence](results/proofbench_b112_final_20260926/README.md)

The Qwen-only re-tally uses all 237 available proofs, 474 grading responses and
702 saved Qwen votes. Original and mechanically normalized responses remain
in the source evidence. Verify the scores, vote tallies, coverage and hashes offline:

```bash
python3 -B scripts/export_proofbench_final.py --verify
python3 -B scripts/report_qwen_selection.py --verify
```

**Historical comparison context:** [Dang et al. (v2, 12 June 2026) report 87.6% on PB-Adv
with Gemini 3.1 Pro at about US$9 per problem](https://arxiv.org/html/2602.16793v2).
Our local Gemma 4 31B + Qwen3.6 27B core pipeline records **39.29% average**
and **48.10% Oracle@4**, graded by gpt-5.6-sol/xhigh. The model backbones,
compute budgets, grading implementations and output-selection rules differ.
Oracle@4 selects the highest externally graded candidate after evaluation;
it is not a model-selected final proof. These figures do not establish a
controlled performance comparison.

### IMO 2026 release context

The current result is **24.75/42 Average, 29/42 Oracle@4 and 29/42
Selector@1**, using the mean of two independent strict-v2 grades per proof
from **gpt-5.6-sol / xhigh**. Final selection counts **72 saved Qwen votes**:
12 for each of the six problems. It uses the original seeded tie order.

The six portfolios were generated end to end with the same frozen B 1.12.0
engine and recorded settings: seed offset 0, four lanes, original lazy-check
and full-proof expansion, three refinements, and the dual-model R2/R3 audit.
This score update reuses their 24 final proofs and 48 grades; the original
run identities and selections remain in the
[dated evidence](results/imo2026_b112_selection_20260922/README.md).
These problems informed selector development, so this is not a held-out evaluation.

All six runs used the ten-minute comparison fallback policy. Re-tallying the
votes does not change the fixed portfolio's Average or Oracle@4. The
[Qwen-only scorecard](results/qwen_selection_20260928/SCORECARD.json) records
the selected lanes, vote IDs and links to the original proofs and grades.

The separate [P4 recovery experiment](results/imo2026_b112_p4_recovery_20260922/README.md)
is preserved as historical evidence and is excluded from the current headline.

Each lane supplies its stored final proof after the R2/R3 audit, or its last
completed checkpoint when a later stage failed. External grades never determine
which checkpoint is submitted.

In both current and historical ProofBench reporting, the **average** numerator
sums each problem's mean score across its available
lanes; **Oracle@4** sums each problem's maximum across up to four lanes.
IMO-ProofBench converts these totals to percentages of **210** for each
30-problem set or **420** for all 60 problems. IMO 2026 displays the point
totals directly, with a maximum of **7** per problem or **42** overall.
Each problem has equal weight. Percentages are normalized scores, not ranks
among other systems.

IMO-ProofBench and IMO 2026 use separate grading rubrics and are reported
separately. The experiments span several recorded implementations. These
tables above report core pipeline results. Results including experimental
tool calls appear under [Experimental feature: tool calls](public_release_report.md#experimental-tool-call-results).
The [full report](public_release_report.md) gives the selection rules,
denominators, version qualifications and supporting evidence.




## Ablation study — IMO-ProofBench

Both subsets compare **raw generation without extended reasoning, raw
generation with extended reasoning, and extended reasoning + the full harness**.
Basic and Advanced each contain
**30 problems**, with four candidate lanes per problem. Both raw configurations
use Gemma 4 31B with MTP=4, two candidates at temperature 1.0 and two at 0.7,
top-p 0.95 and top-k 64. All grades use the same IMOBench B.5 prompt, dataset,
per-problem references and guidelines, and gpt-5.6-sol / xhigh evaluator.
Average and Oracle@4 follow the main matrix's definitions, with a maximum of
**210** points for each subset.

**Both raw configurations enable native thinking**, with an initial output
limit of **65,536 tokens**. “Without extended reasoning” means a single request
that stops at EOS; it does not disable thinking. “With extended reasoning” adds
forced continuation after the initial answer, with the recovery limits below.

| Configuration | Saved output and inference policy |
|---|---|
| Raw without extended reasoning | One Gemma request per candidate, with a 65,536-token output limit and no continuation. |
| Raw with extended reasoning | Gemma draft before lazy checking, with a 65,536-token initial output limit, mandatory continuation and bounded recovery up to 131,072 output tokens per recovery request. |
| Extended reasoning + full harness | The current core portfolio for each subset: lazy checking, Gemma/Qwen reviews, fusion, audits and revisions, with the same checkpoint fallback policy as the main matrix. |

This is a **retrospective ablation across saved configurations**, not a
single-toggle controlled experiment. The initial system and user prompt hashes
match across all 30 Basic problems. Basic-009 and Basic-026 now use reruns without
extended reasoning, with seeds matching their extended reasoning runs. The separate raw-only and pipeline runners
also differ in continuation/recovery policy and timeouts, and the full portfolio
spans recorded implementations. Additional inference compute is part of the extended reasoning
and full-harness configurations; compute-matched effects and individual review,
fusion or audit contributions were not measured. Both Basic and Advanced use
B.5 for all three configurations; their strict-v2 grading results were removed.
Experimental tool calls are excluded.

The current [B.5 ablation evidence](public_release/proofbench_ablation_b5.json)
pins 718 proof/grade selections across Basic and Advanced. It reuses existing
B.5 grades for unchanged inputs and adds 128 grades: 120 Advanced proofs and
eight Basic rerun proofs, all generated without extended reasoning. Each proof uses one B.5 grade from
`gpt-5.6-sol / xhigh`. The full-harness row reuses the current
[core score snapshot](public_release/score_snapshot.json), including its
checkpoint fallback policy. The offline verifier checks coverage, proof hashes,
rubric and reference identities, generation records and every displayed metric.

The original [Basic ablation snapshot](public_release/ablation_snapshot.json)
and its 240 raw grades remain as historical evidence. Its eight older proofs
without extended reasoning for Basic-009 and Basic-026 are superseded in the current matrix.

### Basic

<!-- BEGIN BASIC_ABLATION SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Configuration</th>
      <th width="200" align="left">Grading scheme</th>
      <th width="200" align="right">Average</th>
      <th width="200" align="right">Oracle@4</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">Raw without extended reasoning</td><td align="left">IMOBench B.5</td><td align="right">62.14% (130.5/210)</td><td align="right">73.33% (154/210)</td></tr>
    <tr><td align="left">Raw with extended reasoning</td><td align="left">IMOBench B.5</td><td align="right">67.86% (142.5/210)</td><td align="right">80.95% (170/210)</td></tr>
    <tr><td align="left">Extended reasoning + full harness</td><td align="left">IMOBench B.5</td><td align="right">80.00% (168/210)</td><td align="right">84.76% (178/210)</td></tr>
  </tbody>
</table>
<!-- END BASIC_ABLATION SCORE MATRIX -->

### Advanced

<!-- BEGIN ADVANCED_ABLATION SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Configuration</th>
      <th width="200" align="left">Grading scheme</th>
      <th width="200" align="right">Average</th>
      <th width="200" align="right">Oracle@4</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">Raw without extended reasoning</td><td align="left">IMOBench B.5</td><td align="right">23.69% (49.75/210)</td><td align="right">30.95% (65/210)</td></tr>
    <tr><td align="left">Raw with extended reasoning</td><td align="left">IMOBench B.5</td><td align="right">25.36% (53.25/210)</td><td align="right">38.57% (81/210)</td></tr>
    <tr><td align="left">Extended reasoning + full harness</td><td align="left">IMOBench B.5</td><td align="right">39.29% (82.5/210)</td><td align="right">48.10% (101/210)</td></tr>
  </tbody>
</table>
<!-- END ADVANCED_ABLATION SCORE MATRIX -->

### Ablation summary

The Basic and Advanced ablations each cover **30 problems**, using four
candidate lanes per problem. Both compare **raw generation without extended
reasoning, raw generation with extended reasoning, and extended reasoning + the full
harness**. All three configurations use IMOBench B.5 grading by
**gpt-5.6-sol / xhigh**; each subset has a maximum score of **210**.

Both raw configurations use Gemma 4 31B; the full
harness adds lazy checking and Gemma/Qwen review, fusion, audit and revision.
The full-harness rows follow the main matrix's checkpoint fallback policy.

These are retrospective comparisons of saved runs. Runners, continuation
budgets and recorded implementations differ, so the results do not isolate
extended reasoning from extra inference compute or individual harness components.
Experimental tool calls are excluded. See the
[ablation evidence and settings](public_release_report.md#ablation-study--imo-proofbench).


## Ablation study — IMO 2026

All three settings use **strict v2** on the same six problems, four proofs per
problem, with two grading passes. This ablation reports **pass 1 for every
configuration**, using its Average and Oracle@4 together. These are retrospective
saved runs; tool rewrites are excluded.

Both raw settings enable native thinking with a 65,536-token initial output
limit. The difference is whether forced continuation follows the initial
answer: “without extended reasoning” is a single pass, not thinking disabled.

For comparison, pass 2 has Average/Oracle@4 totals of **18.75/42 and 21/42**
without extended reasoning, **18.25/42 and 21/42** with extended reasoning, and **24.50/42 and 29/42** for the
full harness.

See the [grading variation report](../benchmarks/reports/strict_v2_consistency_20260918T064715Z/REPORT.md#imo-2026-benchmark-and-ablation-variation)
for both passes and proof-level agreement in each IMO 2026 configuration.

<!-- BEGIN IMO2026_ABLATION SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Configuration</th>
      <th width="200" align="left">Grading scheme</th>
      <th width="200" align="right">Average</th>
      <th width="200" align="right">Oracle@4</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">Raw without extended reasoning</td><td align="left">Strict v2 (pass 1)</td><td align="right">18.75/42</td><td align="right">21/42</td></tr>
    <tr><td align="left">Raw with extended reasoning</td><td align="left">Strict v2 (pass 1)</td><td align="right">19/42</td><td align="right">21/42</td></tr>
    <tr><td align="left">Extended reasoning + full harness</td><td align="left">Strict v2 (pass 1)</td><td align="right">24/42</td><td align="right">29/42</td></tr>
  </tbody>
</table>
<!-- END IMO2026_ABLATION SCORE MATRIX -->

## Historical checkpoint and score accounting

Each problem has four candidate lanes. For each lane, use the first available
correctly graded checkpoint in this order: **Refinement 3 → Refinement 2 →
Refinement 1 → lazy-checked proof → raw proof**. An unchanged proof can reuse
a grade only when its proof hash and evaluation identity match. A higher score
at an earlier checkpoint never overrides this priority. No new grading calls
were made to extend the fallback order.

The average gives each problem equal weight. First take each problem's mean
across its available graded lanes, then sum those means. IMO-ProofBench
converts that total to a percentage:

`average percentage = 100 × sum(per-problem mean scores) / maximum points`

**Oracle@4** uses each problem's maximum across up to four available lanes.
For IMO-ProofBench:

`Oracle@4 percentage = 100 × sum(per-problem maximum scores) / maximum points`

Maximum points are **210** for Basic or Advanced and **420** for All IMOBench.
IMO 2026 displays the selected pass's mean and maximum scores for each problem,
out of **7**; the overall row sums them across six problems, out of **42**.
The fraction in each cell displays acquired points and maximum points. The combined IMOBench
average is the simple average of Basic and Advanced because both contain 30
problems. This problem weighting replaces the earlier report's weighting by
the number of scored lanes. A missing proof is excluded from its problem's
mean and maximum, rather than assigned a mathematical score of zero.

## Coverage

All **66 problems** have at least one included score. The report contains
**263 of 264** candidate selections: **208 Refinement 3**, **15 Refinement 2**,
**19 Refinement 1** and **21 lazy-checked** proofs. The expanded fallback order
recovers **40** previously omitted selections. All 120 Basic and 24 IMO
selections are present; Advanced has 119 of 120. All completed Refinement 3
outputs now use grades bound to those final proofs. The six previously
ungraded Advanced-017/018 outputs were graded with B.5 on 19 September 2026
(UTC); see the [completion report](../benchmarks/imo-proofbench/advanced/results/refinement3_b5_completion_20260919T012327Z/reports/REPORT.md).

The remaining missing selection is **Advanced-003, `t07_r02`**. Raw generation
failed when its extended reasoning continuation requested 131,072 output tokens
with at least 131,073 input tokens, exceeding the 262,144-token context limit.
No completed raw proof was saved. The problem's other three candidates are used.

The original 41 omissions were caused by 17 output/format validation failures,
11 reviewer token-cap stops, six timeouts, five bounded-recovery failures,
one missing expansion-prompt asset, and the raw-generation context overflow
above. Their earlier graded proofs are now used where available.

For IMO-ProofBench, the sum of per-problem means is **250.5/420** and the sum of
per-problem maxima is **279/420**. For IMO 2026, the selected lower-Average pass (pass 1) totals **24/42**
and **29/42**.
Scores are automated model judgments, not human adjudications or formal proof
certificates, and do not guarantee identical grades on future runs.

## Grading schemes

**IMOBench Basic and Advanced** use the published ProofAutoGrader rubric from
Appendix B.5 of *Towards Robust Mathematical Reasoning*, together with the
official per-problem grading guidelines. The specific guidelines take precedence.
Allowed scores are **0 (Incorrect), 1 (Partial), 6 (Almost), and 7 (Correct)**.
Each isolated grading call receives one problem, its reference solution, its
guidelines and one submitted proof. Accepted grades have verified zero tool calls;
solver reviews and prior scores are excluded from grading inputs.

The rubric follows the published autograder, while the evaluator here is
gpt-5.6-sol/xhigh. This does not reproduce the paper's Gemini 2.5 Pro evaluator or
its human grading results. See the bundled
[IMOBench prompt and attribution](public_release/grading/README.md).

**IMO 2026** uses the separate
[strict gold-informed Olympiad v2 policy](public_release/grading/strict_olympiad_policy_v2.txt),
allowing every integer score from **0 to 7**. It credits correctness as submitted
without filling missing arguments from the reference. The six v2 rules address
wrong answers, false statements, omitted arguments, quantifier coverage and
unsupported central inferences. The core matrix selects the complete pass with the lower total Average
across two separate automated grading passes using the same evaluator.
All problem rows and Oracle@4 values come from that pass; ties select pass 1.
The IMO ablation reports pass 1 for all three configurations, including both
metrics from that pass.

IMO grading calls receive a single problem, reference and proof. The final-pass grading
audit reports zero tool calls.

### Historical release grading notes

These paragraphs preserve the earlier README's grading convention and audit
history. The historical matrices above keep their original pass-selection
rules; the latest release tables in the root README report the mean of two
grades. The sampled-suite wrapper now also reports mean-per-proof scores; the
wrapper description retained below records its previous behavior.

IMOBench labels are Incorrect (0), Partial (1), Almost (6), and Correct (7).
The published rubric is used with our recorded external grader; this does not
reproduce the paper's Gemini 2.5 Pro evaluator or its human grading results.

The strict Olympiad v2 policy distinguishes wrong answers, false statements,
missing arguments and incomplete quantifier coverage. A score of 4 requires a
correct reduction to an explicit, true remaining identity; unsupported central
inferences are capped at 3. It is the project's evaluation policy, not an
official IMO jury rubric. ProofBench, including its ablation study, keeps B.5.

Here, "gold reference" means the MechMath team's third-party solution for IMO
2026, or the DeepMind dataset's `Solution` entry for IMO-ProofBench; see
[reference sources and rights](sources.md). MechMath reference text is
excluded from the release and must be [downloaded directly before external
grading](public_release/grading/README.md#external-imo-reference-setup).

The [bundled policies and attribution](public_release/grading/README.md)
record their exact hashes. Proofs and structured grades are linked from the
[machine-readable score snapshot](public_release/score_snapshot.json).

The grading skills and their scorer code are also included in this repository:
[IMOBench scoring](../benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/grading/scorer/SKILL.md)
and [strict Olympiad scoring](../benchmarks/imo2026/results/p2_t07_r02_v356_consolidated_20260917T071542Z/grading/strict_config/SKILL.md).
For current runs, use [score_proofbench.py](../scripts/score_proofbench.py) for B.5
and [score_imo_v2.py](../scripts/score_imo_v2.py) for strict v2. The strict skill
preserves the historical v1 workflow; the v2 adapter verifies its archived
dependencies and applies the current policy and evaluator isolation.

External grading is a separate evaluation step, started explicitly after
generation and selection finish. The harness never invokes these graders.
For a completed sampled suite, [grade its 48 final proofs separately](local_reproduction.md#grade-a-completed-sampled-suite)
with [grade_sampled_suite.py](../scripts/grade_sampled_suite.py) `--run-id <run-id>`.
This wrapper calls the two grading adapters above, using the hosted evaluator
and two separate passes per benchmark by default. It retains both passes and
reports the complete pass with the lower total Average for each benchmark,
along with proof hashes, generation times and fallback counts.

The [earlier single-pass audit](../benchmarks/imo2026/results/strict_v2_20260918T061000Z/reports/comparison.md)
preserves its v1 → v2 comparisons. Current reporting uses the later two-pass
IMO evidence, including all three ablation settings and the P2 tool rewrites.


## Model selection

TrinitySM uses the released Gemma 4 31B and Qwen3.6 27B checkpoints with
fixed weights throughout proof generation, review and revision. All of these
stages run at inference time: extended reasoning extends drafting, and reviews,
fusion, audits and three refinement passes help the models develop and repair
their arguments.

The primary reason for selecting Gemma 4 31B and Qwen3.6 27B was to reduce
potential training-data contamination on IMO 2026. Both models were released
before the competition, providing a temporal basis for this precaution.
Their full training corpora have not been independently audited. The
[model-selection notes](models.md#model-selection-and-contamination-risk)
document the release chronology, pinned revisions and scope of this claim.

### Model-selection summary

We use the released **Gemma 4 31B and Qwen3.6 27B checkpoints** with fixed weights
throughout proof generation, review and revision. All of these stages run at
inference time. Extended reasoning extends the initial reasoning. Reviews, fusion and
audits then identify weaknesses and guide revisions through three refinement
passes. The central idea is to repeatedly develop and examine an argument,
giving the models opportunities to turn partial progress into a stronger proof.

**Model selection was driven primarily by contamination risk.** We chose Gemma 4
31B and Qwen3.6 27B because both models were released before IMO 2026, aiming to
reduce the risk that the competition's problems and solutions had already entered
their training data. This timing supports the precaution; we have not independently
audited their training corpora. The [model-selection notes](models.md#model-selection-and-contamination-risk)
provide the release dates, sources and limits of this rationale.


## Generation inputs and internal review

The core solver receives statements, candidate proofs and internal reviews. Its
current fusion protocol produces qualitative mathematical verdicts, without
numeric self-grades or an external-rubric input. Official references, per-problem
grading guidelines and historical external grades belong to separate evaluation.
See the [executed boundary audit](reproduction/generation_boundary_audit.md) for
the actual prompt builders, tests and remaining packaging limitations.

## Experimental tool-call results

These tables contain only the seven retained trials across five problems. Every
row compares the **actual input proof → its rewritten proof**, scored out of 7,
and shows the change in points. IMO P2 has three separate trials; no untested
problems or suite-wide averages are included. The operation column names the
selected tool. IMOBench examples use **IMOBench B.5** and IMO P2 uses **strict
v2**, taking the lower of two grades for each input and rewrite separately.
Gain is the difference between those reported scores. Both use **gpt-5.6-sol / xhigh**.

The after proof is the latest completed graded rewrite selected for that
candidate in the release snapshot, not the highest-scoring historical attempt.
Input selection is bound to the tool run's saved source-proof hash. In particular,
Basic-008 starts from its raw proof (1/7), and Advanced-020 starts from Refinement 2
(0/7). These differ from their selected core proofs. IMO P2's three input and
output pairs are reported separately under the current reporting rubric.

Basic-008, Basic-009 and P2 `t07_r02` use **Workshop Tools 0.3.356**, replaying
previously selected certificates followed by new proof writing and auditing.
Other trials include earlier implementations. These trials do not
constitute a uniform full-pipeline tool benchmark or a controlled measurement
of tool effects. No new generation or grading calls were made for this report.
The [tool comparison snapshot](../experiments/workshop_tools/score_snapshot.json)
links the actual input and rewrite proofs to their original single grades and
exported run bindings. Current IMO scores use the [two-pass v2 evidence](public_release/imo2026_v2_lowest.json);
the offline verifier checks both repetitions and all seven input/rewrite pairs. The
[experimental guide](../experiments/workshop_tools/README.md#exposed-tools)
discloses the current tool menu, supported inputs, backends and workflow.

### IMO-ProofBench tool examples

<!-- BEGIN IMOBENCH_TOOLS SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Problem / input proof</th>
      <th width="200" align="left">Tool operation</th>
      <th width="200" align="right">Score before → after</th>
      <th width="200" align="right">Gain</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">Basic-008 (t10_r01)</td><td align="left">real_root_classification</td><td align="right">1/7 → 6/7</td><td align="right">+5</td></tr>
    <tr><td align="left">Basic-009 (t07_r01)</td><td align="left">uniform_partition_count</td><td align="right">1/7 → 7/7</td><td align="right">+6</td></tr>
    <tr><td align="left">Advanced-010 (t07_r01)</td><td align="left">exact_geometry</td><td align="right">0/7 → 0/7</td><td align="right">+0</td></tr>
    <tr><td align="left">Advanced-020 (t10_r02)</td><td align="left">symbolic_modular_order</td><td align="right">0/7 → 0/7</td><td align="right">+0</td></tr>
  </tbody>
</table>
<!-- END IMOBENCH_TOOLS SCORE MATRIX -->

### IMO 2026 tool examples

<!-- BEGIN IMO2026_TOOLS SCORE MATRIX -->
<table width="800">
  <thead>
    <tr>
      <th width="200" align="left">Problem / input proof</th>
      <th width="200" align="left">Tool operation</th>
      <th width="200" align="right">Score before → after</th>
      <th width="200" align="right">Gain</th>
    </tr>
  </thead>
  <tbody>
    <tr><td align="left">P2 (t07_r01)</td><td align="left">rational_identity</td><td align="right">3/7 → 5/7</td><td align="right">+2</td></tr>
    <tr><td align="left">P2 (t07_r02)</td><td align="left">exact_geometry</td><td align="right">3/7 → 5/7</td><td align="right">+2</td></tr>
    <tr><td align="left">P2 (t10_r01)</td><td align="left">exact_geometry</td><td align="right">4/7 → 5/7</td><td align="right">+1</td></tr>
  </tbody>
</table>
<!-- END IMO2026_TOOLS SCORE MATRIX -->

### Tool-extension summary

**Workshop Tools** can try to support a selected claim using exact algebraic,
geometry, real-root or discrete checks, then rewrite the proof using that
checked evidence. Claim matching and formalization can fail. A certificate
supports its specified claim; the submitted proof still needs separate grading.

Tool calls require an explicit opt-in. See the
[experimental guide](../experiments/workshop_tools/README.md) for saved-proof runs
and saved-certificate regeneration. The results below are separate from the
core benchmark matrices.

Each row compares the **actual input proof → its rewritten proof**, with scores
out of 7 and the point gain. Only the seven retained trials across five problems
are shown; IMO P2 has three separate trials. The saved rewrite is the latest
completed graded rewrite selected for that candidate in this release.

IMOBench examples use **IMOBench B.5**; IMO P2 uses **strict v2**, taking the
lower of two grades separately for each input and rewrite. Gain is the difference
between those reported scores. All grades use **gpt-5.6-sol / xhigh**. Basic-008,
Basic-009 and P2 `t07_r02` use **Workshop Tools 0.3.356**, replaying saved
certificates and regenerating proofs. Other trials include earlier versions. These are targeted
examples, not a benchmark-wide or compute-controlled estimate of tool effects.
The [experimental guide](../experiments/workshop_tools/README.md#exposed-tools)
lists the six exposed operations, their limits and exact backends.


## Future work

Producing one proof through the current full generation and refinement workflow
takes **more than an hour**. Our research target is to reduce this to **seconds
while preserving mathematical rigor**. We aim to combine smarter choices about
where to spend reasoning effort with deterministic mathematical tools,
quantization and a domain-specific mathematical formal language. The target
requires future validation of end-to-end latency and independently assessed
proof quality.

The results motivate seven research directions. These are proposed extensions;
the reported experiments use the recorded harness and model configurations.

1. **Targeted reasoning continuations.** Current extended reasoning supplies fixed
   "Wait. Continue…" instructions that ask the model to recheck its reasoning
   and bridge remaining gaps. A future controller could choose the next task:
   challenge a potentially mistaken premise, explore a different proof strategy,
   develop a missing lemma, or identify and invoke a useful tool. The aim is to
   escape repeated commitment to an unsuccessful approach. Compare these directed
   continuations with the current policy at matched inference budgets.
2. **Speed improvements.** Investigate [NVFP4 quantization](https://github.com/NVIDIA/Model-Optimizer/blob/main/examples/hf_ptq/README.md)
   on supported hardware and selective deployment of extended reasoning. The current
   continuation is mandatory; a learned or calibrated decision could skip it
   when the proof is already complete or redirect work when continuation is
   unproductive. Choose which reasoning branches and reviews merit further work,
   and delegate suitable calculations and checks to deterministic tools.
   Measure end-to-end latency, token use and independently graded proof quality
   against the recorded BF16 setup. Quantization, selective continuation and
   tool execution each need their own quality and latency comparison; together
   they form the proposed path from the current runtime toward seconds.
3. **A native grader, proof selector and early stopping.** Develop a local
   grader that uses the problem and candidate proof to assess completeness and
   select the strongest candidate. A confident internal 7/7 prediction could
   trigger immediate termination of further generation and refinement. Evaluate
   calibration and false acceptance against separate grading before relying on
   that stopping rule. Report the selected proof's external score as well as
   Oracle@4 to measure the selector's performance. Evaluation references and
   external grades would remain outside inference-time selection inputs.
4. **Larger open-weight foundation models.** Extend the experiments to recent,
   larger models and investigate how their mathematical capabilities interact
   with repeated review and revision. Complete Olympiad-level proofs remain the
   target. Compare raw and full-harness results with consistent evaluation and
   explicit inference budgets, recording model revisions and possible benchmark
   exposure so newer checkpoints do not silently inherit the current
   model-selection rationale.
5. **Reliable tool selection and formalization.** The experimental tool path
   is limited by choosing useful equations or expressions and translating
   natural-language claims into executable mathematics. The current interfaces
   accept typed requests that exact backends execute; general Python generation
   is a possible extension. Improve both forms of formalization, preserve
   assumptions and quantifiers, and ensure each checked result advances the
   original proof. Develop a domain-specific mathematical formal language with
   explicit variables, domains, assumptions, quantifiers and proof obligations.
   Compile supported statements into deterministic computations and checks, and
   return evidence the proof writer can use. This could reduce repeated reasoning
   in natural language and formalization retries. Measure successful encoding,
   total latency and independently graded proof improvement separately: an
   executable calculation alone is insufficient.
6. **Targeted post-training of small models.** Develop training tasks for
   sketching proof directions, detecting errors, verifying rigor, grading and
   comparing proofs. Use checked examples and carefully assessed feedback to
   strengthen native reasoning and verification. Evaluate on held-out problems
   to distinguish transferable mathematical skills from memorized solutions,
   and measure which capabilities still require repeated inference.
7. **Mathematical database search and few-shot guidance.** Investigate using
   Lean's [mathlib](https://github.com/leanprover-community/mathlib4) and other
   formal theorem libraries as sources of reusable mathematical knowledge.
   Existing [mathlib search methods](https://leanprover-community.github.io/blog/posts/searching-for-theorems-in-mathlib/)
   include natural-language retrieval and Loogle's search by types and
   subexpressions. A future local retrieval stage could query from the problem,
   a proposed lemma or an unresolved subgoal, then select relevant statements
   and proof examples. Present a few examples with concise mathematical
   explanations, explicit hypotheses and source identifiers as few-shot prompts
   to suggest proof strategies and avoid rediscovering known results. Check that
   the retrieved hypotheses match the current setting; use Lean to verify
   applications where the subgoal has been faithfully formalized. Build a local
   index from a pinned library revision to preserve reproducibility without
   hosted inference. Keep benchmark reference solutions outside the index and
   report exact or near matches to benchmark problems. Compare no retrieval,
   retrieved statements alone, and statements with proof examples at matched
   inference budgets, measuring retrieval overhead, total solving time and
   independently graded proof quality.

The longer-term ambition is a strong, open teacher model capable of
gold-medal-level performance on IMO mathematics, with reasoning and verification
skills that can be transferred into small models for local and edge devices.
Targeted post-training and distillation offer a research path toward making
advanced mathematical reasoning widely accessible. This capability has yet to
be demonstrated by the present work.

### Research agenda summary

Producing one proof with the current full workflow takes **more than an hour**.
Our research target is to bring that time down to **seconds while preserving
mathematical rigor** through smarter computation choices, deterministic tool
use, quantization and a domain-specific mathematical formal language. Reaching
this target requires future validation of both speed and proof quality.

We see seven directions for extending TrinitySM:

1. **Targeted reasoning continuations.** The current extended reasoning policy uses
   fixed "Wait. Continue…" instructions to recheck reasoning and close gaps.
   We want to choose a direction for each continuation: challenge the current
   strategy, develop an alternative proof approach to escape a cognitive well,
   or identify and invoke a useful mathematical tool.
2. **Faster inference and selective computation.** Evaluate NVFP4 quantization,
   make the currently mandatory extended reasoning optional, and choose when further
   reasoning, review or tool execution is useful. Delegate suitable calculations
   and checks to deterministic tools. Measure time to a completed proof alongside
   mathematical quality as we work toward the seconds-scale target.
3. **Better selection and calibrated quality estimates.** Evaluate the built-in
   [R2/R3 and cross-lane selectors](harness_b_selection.md) on fresh runs,
   then develop calibrated quality predictions and early stopping for apparently
   complete proofs. An internal prediction can be wrong. Measure the quality of
   a deployable selected proof alongside the externally measured Oracle@4.
4. **Larger open-weight foundation models.** Test recent, larger models with the
   same harness to investigate how gains in underlying mathematical capability
   translate into complete Olympiad-level proofs. Compare raw generation and
   the full workflow under documented inference budgets.
5. **More effective tool use.** Tool calls remain experimental. Models struggle
   to choose useful equations and expressions and to translate natural-language
   claims into executable mathematical representations. Improve claim selection,
   formalization into symbolic inputs or Python code, and integration of checked
   results into the proof. Develop a domain-specific mathematical formal language
   for expressing claims and assumptions precisely and compiling them into
   deterministic computations and checks.
6. **Targeted post-training of small models.** Train proof-direction sketching,
   error detection, rigor verification, grading and proof assessment. The goal
   is to strengthen the models' own mathematical capabilities alongside the
   inference-time harness.
7. **Mathematical database search and few-shot guidance.** Explore retrieval from
   formal theorem libraries such as Lean's [mathlib](https://github.com/leanprover-community/mathlib4).
   Find relevant lemma and theorem statements, along with useful proof examples,
   and supply a small selection as few-shot hints for the current problem or
   subgoal. Pair the formal material with concise explanations and explicit
   assumptions to help the model identify a promising proof direction. A local,
   versioned index could support this without hosted API calls. Evaluate whether
   retrieval improves proof quality and reduces solving time, checking that each
   proposed theorem application satisfies its hypotheses.

Our longer-term ambition is to develop a strong, open teacher model capable of
gold-medal-level IMO performance, then transfer its reasoning and verification
skills into small models that can run on local and edge devices. Making these
capabilities widely available is a research goal beyond the current results.
The [future-work discussion](public_release_report.md#future-work) describes
the proposed evaluations.


## Portable evidence and verification

The [score snapshot](public_release/score_snapshot.json) records all 264 lanes,
including exclusions, the selected checkpoint, core scores, proof hashes,
grading scheme identities, and the source-report hashes. It links to bundled
proofs and structured grading records using paths relative to the snapshot.
Saved experimental selections identify the rewrites in the separate per-proof
tool tables; their actual inputs are bound in the experimental snapshot. They
do not contribute to the core matrices. These copies preserve the submitted
mathematics and recorded grades; they do not
depend on the original machine's absolute paths. Grading-record exports retain
the original record's hash and repository-relative provenance.

From the repository root, recompute the matrices and verify all bundled artifact
hashes with Python 3.9 or later:

```bash
python -B docs/public_release/verify_scores.py
```

This offline check validates artifact hashes, score-to-proof bindings,
grading-policy identities and reported arithmetic. It does not assess the proofs'
mathematical correctness, make model calls, or rerun generation or external
grading. The recorded grade inputs identify reference and guideline hashes
where the native grader provides them; the complete evaluation-input
archives remain separate from the statement-only solver inputs.

Problem origins and methodological references are listed in [Sources and papers](sources.md).
The [public-copy sanitization notes](reproduction/sanitization.md) describe location
redactions and provenance checksum updates; proof mathematics and score values are unchanged.

### Reproduction and release status

TrinitySM **0.1.0-rc.1** defaults to frozen engine **B 1.12.0** and includes preserved earlier engines and evidence from
research experiments. Frozen versions and deterministic certificate checks make
individual operations inspectable;
model generation and hosted grading can still vary between runs. The score
matrices cover saved core-pipeline runs across recorded implementations, rather
than one uniform rerun of the entire suite.

Keep original run IDs, versions, sampling settings and proof hashes when making
comparisons. Run external grading only after the relevant problem worker finishes,
in a separate environment using the stated rubric and official evaluation inputs.
Rechecking the saved report does not reproduce generation or regrade the proofs.

Model checkpoints, dataset material and copied grading text retain their
respective licenses and attribution. The IMOBench grading material's attribution
is recorded [here](public_release/grading/README.md).

### Sources, licensing and public-copy changes

Problem origins, dataset hashes and the papers used for the benchmark, rubric,
extended reasoning, Cognitive Well methodology and model background are listed in
[Sources and papers](sources.md).
The original project code uses the [CC BY-NC 4.0 license](../LICENSE): sharing
and adaptation are permitted for noncommercial purposes with attribution,
subject to the [license terms](https://creativecommons.org/licenses/by-nc/4.0/).
Copied datasets, grading text and model configuration files retain their own
terms in [NOTICE](../NOTICE).

The release copy removes internal work notes, raw logs, personal paths and
internal network addresses. Affected provenance checksums were recomputed;
[the sanitization record](reproduction/sanitization.md) distinguishes this
public copy from the historical research artifacts. Submitted proof text and
reported score values are preserved. This applies to the release tree; old Git
commits have not been scrubbed.
