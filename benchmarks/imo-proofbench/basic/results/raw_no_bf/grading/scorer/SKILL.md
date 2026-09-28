---
name: imobench-scoring
description: Grade IMOBench Basic or Advanced proofs with the published ProofAutoGrader rubric and official per-problem grading guidelines. Use for IMOBench scoring, paper-aligned rescoring, and score matrices; keep this evaluation distinct from generic strict Olympiad scoring.
---

# IMOBench scoring

Use bundled `scripts/score.py`. It applies Appendix B.5 of *Towards Robust
Mathematical Reasoning* (arXiv:2511.01846v1), including the official problem's
**Grading guidelines** field. Specific guidelines take precedence over the general
rubric, especially for partial credit. Permitted scores: **0, 1, 6, 7**.

Default grader: **gpt-5.6-sol / xhigh**, one isolated Codex call per distinct proof.
This uses the paper's grading instructions with a different grader; it does not
reproduce its human evaluations or Gemini 2.5 Pro implementation.

## Select and grade

Resolve requested terminal proofs, including the last saved proof of a failed
lane when all available results are requested. Prefer the latest completed attempt
unless the user requests history. Do not implicitly grade unfinished intermediate
proofs as final results. Keep generation, existing scores, and new scores separate.

The default dataset is `/srv/datasets/imobench/proofbench_v2.csv`, pinned by the
hash in `references/source.json`. The runner verifies official input and source
checkpoint hashes before grading.

For an existing Basic score inventory, read its source bindings while excluding
its grades from all model inputs:

```bash
python -B SKILL_DIR/scripts/score.py \
  --source-report /absolute/path/to/current/summary.json \
  --output-dir /absolute/path/to/new/imobench_scores --workers 8
```

For completed v0290 portfolios:

```bash
python -B SKILL_DIR/scripts/score.py \
  --source-run /absolute/path/to/run \
  --output-dir /absolute/path/to/new/imobench_scores
```

Repeat `--source-run` to combine runs; later completed problems override earlier
bindings. `--problem-id PB-Basic-029` limits scope. Explicit proof selection uses
`--task-manifest`; see [input-format.md](references/input-format.md).

Use `--dry-run` to stage and validate without model calls, then `--resume` with
the same inputs. Resume reuses successful grades. `--cache-dir PREVIOUS_SCORE_DIR`
reuses matching grades from this policy only. Identity includes problem, reference,
**guidelines**, proof, prompt, dataset, model and effort. Different-policy scores
are never reused. Failed calls get at most two attempts; `--retry-failed` explicitly
retries remaining failures on a later resume without repeating successful grades.

Every grader receives exactly the published prompt populated with one problem,
its reference, its official guidelines and one proof. Prior scores, reviews,
rankings and provenance stay outside the prompt. Grading inputs and references
must never enter a solver's inputs.

The launcher disables host skill discovery, project instructions, plugins, web,
shell and other agent tools for each grader process. It verifies the event log
contains one completed grading turn and no tool calls before accepting a grade.
It also disables each discovered local skill explicitly and replaces the coding
agent's base instructions with the bundled evaluator-only instructions.
Do not remove these overrides: read-only sandboxing alone permits unrelated
skills and files to influence a grading call. Isolation configuration participates
in cache identity. Verify a small real batch's logs before a large launch on a
new CLI installation; fail closed if the installed CLI lacks these controls.

## Monitor and report

Run long batches in a separate tmux session; inspect `status.json` and `report.md`.
Continue other tasks after a grading failure. Failed calls are unscored, never
converted to mathematical zero. Report every score/category, coverage, failures,
per-problem best and grader settings. Label maxima across candidates as **best of
N**, and distinguish them from single-submission benchmark results. Link detailed
grading reports and preserve earlier policies' scores for comparison.

Read [provenance.md](references/provenance.md) when discussing rubric provenance
or comparability. The prompt source and license are recorded there.
