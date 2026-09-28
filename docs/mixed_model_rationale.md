# Why combine Gemma and Qwen?

**Small controlled tests showed different strengths in diagnosis and repair,
so we designed the harness to combine Gemma and Qwen.** Gemma generates and
revises proofs, while Qwen contributes complementary reviews and audits. The
experiments below explain why we chose this division of roles.

Historical scores below are grading outcomes, not formal verification of the
proofs.

## Feedback comparison with a fixed Gemma resolver

The comparison held the **source proofs, BF16 Gemma resolver and refinement
seeds** fixed while changing the feedback provider.

| Feedback provider | P4 final proof score | P5 final proof score |
|---|---:|---:|
| Gemma | 3/7 | 3/7 |
| Qwen | 7/7 | 3/7 |

For P4, the reported diagnosis differed: Gemma focused on a minor angle issue
and missed the crucial gap, while Qwen identified a missing invariant. The
subsequent Gemma revision using Qwen's feedback received the higher score.
P5 showed no improvement. Together, these observations motivated using Qwen
feedback as an additional input to Gemma's revision process; they do not show
a consistent advantage across problems.

The reported controls apply to this local feedback comparison. They do not
establish equal reviewer prompts, call counts or token budgets, or a comparison
between two otherwise identical complete harnesses.

## Complementary reviewer behavior

A separate reviewer experiment used **36 proofs and two temperatures per
model**. The counts below measure identification of the exact earliest defect:

| Problem | Qwen | Gemma |
|---|---:|---:|
| P4 | 5/12 reviews | 2/12 reviews |
| P6 | 6/12 reviews | 10/12 reviews |

The ordering reverses between P4 and P6, motivating the use of complementary
reviewer perspectives. These are review outcomes, not final-proof scores;
repeated reviews must not be counted as independent proof samples.

For the 31 invalid proofs in that study, the reported coverage was:

| Feedback source | Invalid proofs covered |
|---|---:|
| Qwen, temperature 0.2 | 19/31 |
| Gemma, temperature 0.4 | 20/31 |
| Union of the two reviewers' correct findings | 24/31 |

**The union is an oracle upper bound:** it assumes that the correct finding can
be selected whenever either reviewer supplies it. It is not measured accuracy
of the harness's fusion or audit stage, an end-to-end proof success rate, or a
compute-matched improvement over either reviewer alone.

## What this supports and the current experiment scope

These experiments informed the harness architecture: combine the models'
different diagnostic strengths and use their feedback to guide Gemma's proof
revision. The observed complementarity is the reason for the mixed-model
design. The small development comparisons do not quantify Qwen's contribution
to the current full harness or establish an overall advantage over an
otherwise identical Gemma-only system.

**A larger-scale controlled ablation study is needed to quantify the
mixed-model contribution and determine whether these benefits generalize.**
A suitable follow-up would compare mixed-model and Gemma-only conditions on
the same problem set and paired starting proofs, across multiple recorded
generation seeds, with matched prompts, call counts, token budgets and grading.
It should report variability, per-problem outcomes and execution time alongside
aggregate scores. This is future work, not a result established by the small
development comparisons above.

The current priority is **end-to-end mixed-model execution and generation-seed
sensitivity**, with per-lane submitted checkpoints, separate automated grading,
and per-problem wall times. Seed comparisons should keep the selected problem
set fixed and change recorded generation seeds. Intermediate artifacts and
serving settings remain preserved for later analysis.

Each suite launched with a randomly drawn generation seed is one seed setting.
Repeating the same problems across different recorded seeds tests operational
reliability as well as outcome variability. Track end-to-end completion, C3
completion and fallback rates, errors, and wall time; assess mathematical
quality through the separate grading workflow. Successful execution across
seeds supports the harness's operational reliability without establishing the
correctness of every proof or isolating the benefit of mixing models.

A full Gemma-only comparison and NVFP4 experiments are **deferred** from the
current study. The existing experiments motivate the design; isolating the
effect of Qwen across the full pipeline remains an open question.
