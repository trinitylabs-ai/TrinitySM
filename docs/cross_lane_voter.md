# Cross-lane voter: Harness B 1.12.0

The default harness now chooses one proof per problem after choosing each lane's
eligible final proof. R3 requires all four bound explicit raw R2/R3 auditor approvals; body consistency
checks are diagnostic only. Otherwise
R2 is retained. Missing refinements retain the last completed checkpoint.

For four lane finals the voter runs six unordered pairs, each in both independent
presentation orders with Qwen only: **12 logical comparisons, twelve
concurrent calls**. All calls are queued together for one problem. They see
only the statement and the two numbered proofs; no grades, reference solutions,
other reviews or other comparison responses. The revised symmetric mathematical-audit
prompt and the ordinary extended reasoning cue are used. Every comparison chooses
exactly A or B. The two orders of a
pair use separate conversations and the same seed key.

Each valid Qwen comparison contributes one vote. The winner has the most votes
(maximum 6 per candidate); a tie uses the seed-derived candidate order recorded
before inference. The `combined` summary is a compatibility alias for the Qwen tally.
The seed is the run's raw seed offset (default 0); the recorded namespace is also
bound, and a custom namespace is appended to each comparison's seed key. The
candidate-order hash is the tested rule: SHA256 of the JSON encoding of
`[seed, problem_id, exact_proof_hash, candidate_id, "blind_order"]`.

Comparison temperature is 0.2. Extended reasoning retains the initial reasoning
and answer, with the existing role cue and model-specific caps. A 600-second logical comparison
deadline selects a valid initial answer, or permits one answer-only continuation
from saved reasoning (thinking disabled, 8192 tokens, 120 seconds). No fresh
timeout retry is allowed; failed completion leaves the vote invalid.
No model calls are added to repair comparison formatting. A deterministic parser
accepts harmless Markdown variation and rejects absent or ambiguous choices.
The public 1.12.0 controller also accepts a single explicit `Winner: Proof A`
or `Winner: Proof B` when collecting saved comparisons, using the existing
`explicit-winner-proof-prefix-v1` recovery rule. It removes only the literal
`Proof ` prefix in memory, revalidates the complete response, and records the
original/normalized hashes and exact edit in `mechanical_recovery`. Raw response
files and frozen engine files remain unchanged. Duplicate winners, nonbinary
choices, additional winner prose and missing required fields remain invalid.
This collection step adds no model calls and still requires all planned votes.
The serving profiles already permit twelve concurrent sequences for each model;
raw generation and refinement still run four lanes at a time.

With two or three available lane finals, run the full round robin over that set
(2 or 6 calls respectively). One available proof wins without calls. Identical
proofs in different lanes remain separate candidates. No proof text is rewritten.
A transport failure, invalid response or interrupted comparison leaves selection
incomplete; all completed lane proofs remain available. Partial votes do not
produce a winner. The controller records the incomplete selection and can proceed
to other problems; its final status reports the failure.

## Artifacts and resume

- `proofs/<problem>/<lane>.md`: all eligible lane finals, as before.
- `cross_lane_voter/<problem>/<portfolio hash>/`: bound inputs, manifest, audit
  plan, per-call reasoning, answers and continuations, status, `SELECTIONS.json`, and `REPORT.md`.
- `selected_proof.md` inside that directory: exact winning proof bytes, available
  only after a complete valid vote set.
- `final_results.json`: `problem_selections` records each winner, stage, proof
  path/hash, full vote table, batch/concurrency settings and observed concurrency.

New runs capture the policy and its source hashes in `harness_release.json`,
`selector_policy.json` and `selector_runtime/`. Both GPU layouts schedule only
Qwen for this final selector; generation and the R2/R3 audit keep their model roles.
Existing runs retain their recorded selector when resumed or collected.

The report includes Qwen order-disagreement counts and rates. These compare the candidate identities chosen in
both orders, not the literal A/B labels. Zero completed order pairs is reported
as unavailable, not a zero disagreement rate.

Resume checks exact proof bytes, source stage, statement, runtime, release,
prompt, plan and saved response bindings. Completed or interrupted calls are
never automatically repeated. Offline `--collect-only` reparses saved Markdown
and recomputes the tally without inference; changing a cached winner cannot
change the result. A changed eligible portfolio gets a new artifact directory,
so previous winner proofs and vote records remain preserved.

Parser updates do not retroactively change an already finished run's recorded
exit code or scheduler status. A previously failed run must be re-collected
explicitly; retain its original execution record. The frozen worker's per-call
result can remain invalid while the controller's newly parsed vote is valid;
the raw response and the mechanical recovery receipt explain that distinction.

B 1.11.0 and earlier releases retain their original behavior. Historical score
tables remain attached to their original runs. The P2/P4/P5 trials are encouraging
small-sample selection evidence; selecting one proof does not increase the fixed
four-proof portfolio's oracle@4 or average score.
