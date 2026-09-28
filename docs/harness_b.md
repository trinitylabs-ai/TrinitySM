# Harness B: role-specific extended reasoning during refinement

**This page records original B (1.8.0). The current default is [B 1.12.0](harness_b_selection.md), which adds original expansion at 0.4 and the post-resolver auditor. A (1.7.0) and original B remain available.** Both run Draft followed by three
refinement passes and submit each lane's last completed proof.

```bash
# Original B, explicitly selected
python -B harnesses/proof_workshop/run.py --release 1.8.0 --verify
python -B harnesses/proof_workshop/run.py --release 1.8.0 \
  --problem-dir benchmarks/imo2026/problems --problem-id imo2026_p2 \
  --output-dir /absolute/path/to/new_run --dry-run

# A, the previous version
python -B harnesses/proof_workshop/run.py --release 1.7.0 --verify
```

Replace `--dry-run` with `--execute-models` to generate proofs. Benchmark and
sampled-suite launchers now default to B 1.12.0 and accept `--release 1.7.0` for A.
Existing runs retain their recorded release when resumed or collected; an
explicit different release is rejected before launching work.

## Exact change

B uses the exact `refinement-bf-role-cues-v1` strings from the completed
[archived B experiment](../benchmarks/imo2026/results/refinement_bf_B6_selection_first_20260920_1426/README.md).
The frozen policy lives in
[1.8.0's engine](../harnesses/imo_proof_pipeline/releases/1.8.0/engine/source/experiments/local_math_verifier/refinement_bf_policy.py).

| Refinement role | Continuation focus |
|---|---|
| Reviewer 1 | Earliest unsupported implication and routine versus substantive omissions |
| Reviewer 2 | Validate an attack or counterexample, then try to refute it |
| Reviewer 3 | Charitable interpretation versus an unproved nontrivial repair |
| Fusion / reconsideration | Resolve reviewer disagreements against the proof |
| Acceptance audit | Independently check the decisive implications |
| Repair-brief audit | Viability, quantifiers and circular reasoning |
| Repair-brief rewrite | Revise the unresolved repair obligation |
| Resolver | Return a complete revised proof resolving valid criticism |

The original chat extended reasoning retains the initial reasoning and answer, appends the
role instruction, and requests a complete replacement in the original format.
The same routing applies in refinement passes 1, 2 and 3. Extractor and gap
selector auxiliary calls retain their original continuation instruction.
Stage names and exact system-prompt hashes identify each role; unknown or
ambiguous routes fail closed. Each refinement process saves `policy.json` and
`continuations.jsonl` under its `refinement_bf/` directory.

Draft generation, its existing lazy check and conditional expansion, primary
system prompts, models, token budgets, sampling, seed rules, recovery and
checkpoint fallback retain A's settings. The independent proof selector and
post-C3 experiment are not included. An experiment replacing Draft's lazy
check/expansion is a separate variant and must have its own identity.

## Evidence and limits

The archived six-problem comparison reports B **4.396/7** versus A **4.042/7**
on average, and **8/24** versus **5/24** proofs receiving 7 in both grading
passes. It reuses historical A controls and saved lazy-checked inputs, so these
are descriptive results, not a fresh end-to-end benchmark or a causal claim.
Existing public benchmark tables keep their original evidence and identities.

The promotion checks both release inventories, exact cue equality, unchanged
A assets and Draft settings, no-network three-pass execution, and saved-run
recovery. These checks make no model calls and do not assess fresh proof quality.
