# Harness B 1.11.0: audited finals and cross-lane voting

**This records B 1.11.0; the current default is [B 1.12.0](harness_b_selection.md).** It adds a [cross-lane voter](cross_lane_voter.md) after the R2/R3 auditor. B 1.10.0 introduced twelve concurrent calls per model; that concurrency and all generation, refinement and R2/R3 settings are retained. Previous B 1.10.0/1.9.0/1.8.0 and A 1.7.0 remain available with their original hashes.

```bash
python -B harnesses/proof_workshop/run.py --verify
python -B harnesses/proof_workshop/run.py --release 1.11.0 \
  --problem-dir benchmarks/imo2026/problems --problem-id imo2026_p2 \
  --output-dir /absolute/path/to/new_run --dry-run
```

Use `--execute-models` for a new inference run. Integration checks use scripted
responses with networking disabled; creating this release does not launch a benchmark.

## Workflow

Raw generation → original lazy-check → conditional original whole-proof expansion
→ B Refinement 1 → 2 → 3 → replacement audit → cross-lane voter → final proof export.

| Stage | Setting |
|---|---|
| Raw generation | Original four lanes, prompts, temperatures and seeds |
| Lazy-check | Original prompt, temperature 0.1, four lanes concurrently |
| Expansion | Original whole-proof prompt; temperature 0.4 for primary and extended reasoning |
| Conditional expansion | Only lanes with reported issues, once per lane under existing recovery policy |
| Refinement 1–3 | Existing B role-specific reasoning-plus-answer extended reasoning and batch four |
| Final replacement audit | Gemma and Qwen, each in both independent presentation orders, temperature 0.2 |
| Audit concurrency | Up to twenty-four logical calls: twelve Gemma + twelve Qwen; up to sixteen calls per problem |
| Audit acceptance | All four mechanically valid calls must approve the R3 replacement |

This uses the **original** lazy-check and expansion, including their original extended reasoning
text. The experimental block expansion and its audit/resolve loop are not used.
Original model revisions, token caps and recovery behavior remain. Each server
now allows twelve concurrent sequences; other serving settings are unchanged.
Separate audit pools allow twelve calls per model, twenty-four total. One problem
with four changed lanes supplies only eight calls per model; larger multi-lane
audit jobs can fill all twelve slots. No extra audit calls are added to fill slots.
Four-lane generation and refinement scheduling are unchanged. The increased limit is not
a guarantee of proportional speedup. Status records the configured limits and
observed peak concurrency, both total and per model.
The post-resolver audit uses the tested Markdown prompt and continuation cue.
Each reversed-order call has the same seed and receives no other audit's response.
Existing chat extended reasoning retains that call's reasoning and answer.

## Selection, failure and resume

The new audit runs at the tested **Refinement 2 → 3** boundary. R1 and R2 continue
normally. If the R2/R3 proof text is identical after stripping outer whitespace,
no audit calls are made and the completed R3 artifact remains eligible.

For changed proofs, all four calls must approve R3. Rejection, unresolved checks,
invalid coverage, transport failure or a missing audit retains the completed R2
proof. A failed R3 generation also retains the normal last completed checkpoint.
The audit creates no repair-model calls and does not rerun the resolver.

Mechanical validation checks changed-block coverage, preservation, scope,
qualifications and consistency of acceptance with the reported checks. Code binds
actual proof bytes, request inputs and saved responses. Model-copied hashes remain
optional diagnostics. This is validation of the audit record, not a formal proof
checker. Auditors receive only the statement, two proofs and computed changes;
they receive no grades, reference solutions or prior audit verdicts.

Both R2 and attempted R3 proofs remain in their original native directories.
`post_resolver_audit/<problem>/<lane>/` stores input snapshots, prompts, call records,
parsed votes and selection. Problem-level `status.json` and `bf_events_*.jsonl`
record progress, time and extended reasoning. `final_results.json` records the selected stage,
audit decision and an explicit reason when the audit retains R2.

Resume reuses completed audit calls after verifying their bindings. Interrupted
calls are preserved and cause R2 fallback; they are not automatically repeated.
`--collect-only` revalidates saved responses without inference and cannot bypass
the audit by reading an unaudited R3 terminal file.

## Evidence and limits

The 19 unequal-score ProofBench cases contained four 0/1→6/7 improvements and one
6→1 regression. Every final audit strategy retained all four improvements and
blocked that regression. In the combined rule, smaller gains and losses canceled:
the mean across those 19 cases remained 2.842/7. There were mistakes within the
0/1 and 6/7 bands. These are existing single-pass IMOBench B.5 grades from a
retrospective diagnostic, not a fresh end-to-end benchmark of 1.11.0.

The original expansion-at-0.4 experiment and auditor experiments were separate.
An increase in average score or oracle@4 for the combined release is not yet
established. Historical benchmark tables and score identities remain unchanged.
