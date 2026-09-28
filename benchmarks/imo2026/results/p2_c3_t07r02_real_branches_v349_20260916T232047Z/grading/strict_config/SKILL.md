---
name: strict-gold-informed-olympiad-scorer
description: Run strict, gold-informed Codex grading of submitted Olympiad proofs on the 0--7 scale. Use when asked for a strict scorer, harsh scorer, skeptical-jury grading, proof-as-submitted scoring, strict gold-informed rescoring, or a conservative audit of terminal Cognitive Well/math-harness proofs, including requests for all scores, best score per problem, or the sum of per-problem best scores.
---

# Strict Gold-Informed Olympiad Scorer

Use the bundled launcher. Do not improvise a grading prompt or silently fall back
to the more charitable calibrated policy.

## Run the audit

1. Resolve every requested terminal proof and its problem-specific gold reference.
2. Verify source artifacts are complete and hash-consistent when the source schema
   provides hashes. For unfinished or unsupported portfolios, bind final proof files
   explicitly instead of importing intermediate reviews.
3. Choose a new empty output directory.
4. Run one of:

```bash
python SKILL_DIR/scripts/score.py \
  --source-run /absolute/path/to/completed_run \
  --output-dir /absolute/path/to/new_score_run \
  --workers 4
```

```bash
python SKILL_DIR/scripts/score.py \
  --proof-task imo2026_p3:anchored_a=/absolute/path/to/proof.md \
  --proof-task imo2026_p3:location_aware=/absolute/path/to/other_proof.md \
  --output-dir /absolute/path/to/new_score_run \
  --workers 2
```

Replace `SKILL_DIR` with this skill directory. The launcher forces the strict
policy and defaults to `xhigh` reasoning. Pass `--reasoning-effort max` only when
the user explicitly requests a different effort.

Give each grader call only one problem, its gold reference, and one submitted
proof. Never supply pipeline reviews, reconciliation packets, candidate rankings,
neighboring scores, or the expected grade.

## Apply the strict standard

Read [references/rubric.md](references/rubric.md) when interpreting a score,
explaining a cap, checking provenance, or comparing strict and calibrated results.
Judge correctness as submitted. Do not repair a proof mentally from the gold.

## Monitor and report

For a long batch, run it in tmux and inspect `status.json`. After completion,
report:

- every score and verdict;
- the first load-bearing mathematical defect for each proof below 7;
- the score vector and best score for every problem;
- the sum of the per-problem best scores when multiple problems were graded;
- the model, reasoning effort, strict-policy hash, and any failed calls.

Keep artifact identifiers internally for traceability. Omit them from the display
table when the user asks for scores only. Do not treat pipeline provenance labels
such as `UNCERTIFIED_TRACE` as mathematical defects.
