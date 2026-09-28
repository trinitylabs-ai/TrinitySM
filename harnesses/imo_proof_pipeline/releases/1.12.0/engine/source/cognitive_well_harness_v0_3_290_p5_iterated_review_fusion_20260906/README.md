# Cognitive Well v0.3.290

Current execution policy: `r1_two_cycles_terminal_v1`. Proof generation ends
at **R1-C2**. Resolver 2, Resolver 3, and their prerequisite post-R1 audit ledger
are no longer executed. Historical runs and their scoring artifacts are unchanged.

For fresh problem-only datasets, see the [standalone v263 → v290 launcher](../docs/v263_v290_standalone_launcher.md).
It uses v263 only through raw generation, lazy checking and conditional proof
refinement, then hands those four actual proofs to v290. `--problem-id ID` on
this module explicitly binds a non-default saved `lazy_checked` portfolio;
omitting it preserves the historical IMO portfolio selector.

Iterated review/fusion experiment over four saved proofs from v0.3.257 (P5 by
default). Use `--problem-number N --input-checkpoint lazy_checked` for another
problem in that source portfolio. The problem identity and expected hashes come
from its saved input manifest, without changing any mathematical prompt or policy.
Each process binds exactly one problem before starting its lane worker threads;
different problems must use separate processes. The default input is the
Resolver-1 checkpoint; `--input-checkpoint lazy_checked` instead starts fresh
Cycle-1 reviews from the four saved `checked_proof.md` lazy-check outputs.
No raw generation or lazy checking is repeated. Each later cycle reviews the
preceding cycle's terminal proof; the mandatory fusion gate is unchanged.

`--no-optional-exact-evidence` disables the extra tool nomination, compilation,
semantic audit, and computation branch. It does not disable the mandatory fusion
decision/repair-brief gate. The default remains enabled for backward compatibility.
For a stopped run at a completed cycle boundary, `--resume-after-cycle N` validates
and reuses every completed lane and preserves failed-lane decisions. It rejects
overwriting later-stage work and records changed evidence settings separately in
`resume_after_cycle_N.json`; the original manifest remains unchanged.
`--resume-fresh-reviews` additionally permits resuming an interrupted fresh-review
stage (including Cycle 1 with no `--resume-after-cycle`). It rejects stages that
already reached Fusion, reuses the inherited hash/identity-bound review caches,
and archives obsolete mechanical failure records rather than deleting them.

```text
R1-C1: three reviews -> Fusion -> mandatory decision/brief gate -> Resolver
R1-C2: three reviews -> Fusion -> mandatory decision/brief gate -> Resolver
END: publish R1-C2 proof paths/hashes; independent strict scoring remains separate
```

The decision boundary restores the useful parts of v0.3.266, v0.3.268, and
v0.3.269. Every `REPAIR_NEEDED` Fusion brief receives a fresh Qwen Markdown
audit. A rejected brief receives a Gemma Markdown rewrite, exact one-line
`resolver_brief` replacement, and a fresh Qwen audit. At most two rewrites are
allowed. After both rewrites, a mathematically rejected brief now still reaches
proof synthesis by default, in every R1 cycle. Its certification remains
`REJECTED` with no certified round; completion of audit processing is not
certification. The unchanged Resolver independently evaluates the advisory
Fusion record. Parser, transport and provenance failures still stop the lane.
The separate strict scorer grades the submitted proof regardless of the brief's
certification status.

To finish saved Cycle-1 brief-gate rejections without rerunning reviews, use
`resume_rejected_synthesis --run-root OLD_RUN --output-dir NEW_RUN
--skill-launcher PATH_TO_STRICT_SKILL_SCRIPT --execute-models`. Repeat
`--run-root` for multiple portfolios. It selects only unsynthesized Cycle-1
rejections, validates/reuses their final brief and full audit chain, and calls the
existing Resolver with unchanged prompts, seeds, temperatures, and mandatory
budget forcing. Four synthesis workers and independent per-proof strict scoring
run automatically. Old artifacts remain untouched. A model's `RESOLUTION_FAILED`
is recorded as such, not silently graded as a newly synthesized proof. Without
`--execute-models`, it only prepares and validates inputs in a new directory.

An `ACCEPT_AS_WRITTEN` or `ACCEPT_WITH_ROUTINE_COMPLETION` decision cannot
bypass the boundary merely because it has no `resolver_brief`. Qwen audits the
complete proof and accepting Fusion record. A rejected acceptance returns to a
fresh Gemma Fusion adjudication. If that adjudication emits `REPAIR_NEEDED`, its
brief enters the same audit/rewrite/re-audit boundary. Repeated rejected
acceptances fail closed before the Resolver.

All four candidate lanes remain independent. The problem, proof, Fusion,
brief, audits, rewrites, effective Fusion, Resolver input, and terminal proof
are hash-bound. No reference solution, v0.3.139 proof, strict score, Codex
feedback, or human audit is included in a model prompt.
R1 cycles use up to four concurrent lane workers. Each worker writes only its
lane; portfolio checkpoint
lists retain frozen candidate order regardless of completion order.

All new repair-boundary model outputs are Markdown. JSON files are deterministic
manifests and provenance only. Gemma retains fresh 32k, 48k, and 64k boundary
recovery rungs and the inherited 32k floor. Qwen uses a fixed **49,152-token cap
per HTTP request**, including the mandatory same-trace budget-forcing call.
A canonical Qwen output ending at the cap fails the logical call immediately:
no cap retry, escalation, or fallback to the pre-forcing response. Bounded
non-cap parser/transport repairs remain at 49,152. Temperatures and mathematical
prompts are unchanged. Request timeouts remain 600 seconds, except Qwen
Reviewer 2 retains its 2,400-second floor. New manifests and producer bindings
record `qwen-49152-no-cap-retry-v1`; old completed bindings remain replayable.

Strict scoring is deliberately outside the model pipeline. `score_targets.json`
records immutable proof paths and hashes after baseline and every R1 cycle;
later scores must not control model selection or stopping. New manifests list
only `R1-C1`, `R1-C2`, and `R1-C3`, with `terminal_checkpoint: R1-C3`.
Successful lanes finish with exactly their C3 proof. Earlier lane failures retain
their completed checkpoint proofs without being labeled C3 successes.

To score each lane immediately upon checkpoint completion, attach the separate
`score_when_ready` watcher. It validates the saved terminal proof, snapshots it,
and invokes the existing strict-scoring skill once per proof/checkpoint. No
reviews, repair briefs, or neighboring scores enter the grader prompt. It never
writes into the model run and does not wait for a portfolio-wide cycle barrier:

```bash
python -m cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906.score_when_ready \
  --run-root runs/EXISTING_MODEL_RUN \
  --output-dir runs/NEW_SEPARATE_SCORE_RUN \
  --skill-launcher /home/user/.codex/skills/strict-gold-informed-olympiad-scorer/scripts/score.py
```

Use `score_when_ready --resume` after a mechanical model-run interruption to
validate and retain completed grades without regrading them. The old scoring
completion summary is preserved separately until the resumed watcher finishes.
Read-only R2/R3 validation remains available only for historical manifests that
explicitly include those checkpoints; it never executes either Resolver.

`queue_problems` waits for a prerequisite model run and its per-proof scoring,
then launches the existing harness one problem at a time. It freezes the queued
lazy-check input hashes, disables optional tools, and attaches the same strict
scoring watcher to each run. The queue can be reattached with the same arguments;
a file lock prevents two queue supervisors, and workers are reattached by module
and exact output directory. Model/scorer children have independent sessions, so
a supervisor pause does not terminate them. Completed checkpoints are never
rerun; an interrupted first fresh-review stage can reuse its cached outputs.
Mechanical initialization/orchestrator
failures pause the queue for a repair/resume instead of changing model decisions.

Mechanical recovery preserves earlier outputs and journals. Use
`--resume-after-cycle 3` to validate the saved R1 checkpoints and finalize the
portfolio without further model calls. `--resume-downstream` has been removed.
Resuming a run that already contains historical post-R1/R2/R3 work is rejected
without modifying it; use a fresh output root for the upgraded experiment.
The `resolve_workers` runtime field/CLI option remains for frozen-configuration
compatibility; R1 lane concurrency is controlled by `workers_per_endpoint`.

For a recorded Reviewer2 timeout, `recover_review_lane --run-root RUN --candidate
ID --execute-models` can finish just that lane's remaining R1 cycles while the
parent continues other lanes. It uses the same cycle function, seeds, prompts,
and mandatory gates, and reuses successful cached reviews. It refuses model-gate
rejections and writes no other lane or root status. Once both workers settle,
resume the portfolio with `--resume-after-cycle 3` to reconcile the recovered
lane and finalize its C3 proof without further model calls. Do not release the
next problem before this reconciliation
and its strict scoring are complete.

Dry run:

```bash
python -m cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 \
  --output-dir runs/v0290_p5_iterated_review_fusion_dry_run_20260906 \
  --dry-run
```

Live execution requires explicit authorization:

```bash
python -m cognitive_well_harness_v0_3_290_p5_iterated_review_fusion_20260906 \
  --output-dir runs/v0290_p5_iterated_review_fusion_20260906 \
  --input-checkpoint lazy_checked \
  --execute-models
```

## Composite release 1.3.0 override

The Qwen cap policy is now `qwen-cap-65536-prefix-or-primary-v1`: initial calls
use 49,152, a repeated capped output permits one 65,536-token clean-prefix retry,
and nonrepetitive capped output permits only a validated completed primary
fallback. Timeout and length recovery share the one physical retry allowance.
See the bundled `release_notes/QWEN_CAP_RECOVERY_1.3.0.md`.

## Composite release 1.4.0 override

In 1.4.0, both models used `unified-limits-65536-600-one-retry-v1` for token and time
limits. That release allowed 65,536 tokens and 600 seconds for recovery. A second limit
stop fails closed. A nonrepetitive primary gets one fresh input-only attempt;
a nonrepetitive budget-forcing request may use a completed valid primary.
See `release_notes/UNIFIED_LIMIT_RECOVERY_1.4.0.md` in the bundled engine.

In IMO Proof Pipeline 1.6.0, recovery requests allow 65,536 tokens and 300 seconds. Primary requests retain the 600-second wall deadline. One retry is allowed; a second limit fails closed.

IMO Proof Pipeline 1.7.0 uses 450 seconds for recovery requests. Initial calls retain 600 seconds, recovery retains 65,536 tokens and one retry, and generation ends at R1-C2.
