# v0.3.324 Generic Verified Certificate Adapter

## Matched exact computations: working revision `0.3.324+geometry.1`

The deterministic handoff `proof_harness.run_matched_tool(...)` now accepts
`exact_geometry` and `rational_identity`. It takes an explicitly selected operation
and typed Markdown arguments, executes in a CPU/memory-bounded worker, and writes
replayable local evidence. Coordinate constructions, circle powers and second
intersections, linear-root derivation, parameter-independent coefficient roots,
and inversion of a line to a circle are supported. See [the contract and usage](MATCHED_TOOLS.md).

This is the computation layer for a caller that already selected and formalized
the request. The existing automatic detector/matcher/formalizer path is not
extended by this change. Its future integration must retain source-semantic
auditing before consuming the new evidence. The standalone handoff makes no model
calls and never promotes a computation to a complete theorem proof.

The runtime has no problem identifiers, reference inputs, saved successful
formulas, or benchmark-fixture imports. Unit tests use synthetic mathematics;
case-specific validation stays outside this package. The immutable September 9
export is unchanged. Earlier gold-free input controls below remain in effect.

## Gold-free input cleanup: working revision `0.3.324+goldfree.1`

The September 9 frozen release is unchanged. The working revision no longer
reads arbitrary `--associated` files, including files named `fusion_packet.md`.
Use `after_fusion --fusion-result ...` as below, or pass `--fusion-result` together
with the matching primary problem/proof to `proof_harness`. The packet is derived
from the verified effective Fusion producer, not accepted as free-form file input.
Its mathematical text and all model prompts remain unchanged.

New manifests record the context policy, source hashes and working revision.
Mechanical resume revalidates that provenance and the saved packet. Legacy runs
without attachments remain resumable; legacy runs with unbound attachments are
rejected rather than silently trusted. No reference/grade files or model calls are
needed for these checks. The primary submitted proof remains caller-supplied;
this is not a detector for a gold solution mislabeled as that proof.

## Start immediately after Fusion

`after_fusion` consumes the **actual effective Fusion result** produced by the
existing mandatory decision/repair-brief gate. It resolves the exact problem and
proof from that artifact, replays the existing gate's producer bindings without
model calls, and invokes the complete `proof_harness` process below. This is not
a certificate-only replay and does not start from a later Resolver proof.

```bash
python -B -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.after_fusion \
  --fusion-result /absolute/path/case/fusion_repair_brief_audit_rewrite/effective_fusion_result.json \
  --output-dir /absolute/path/new_post_fusion_run --master-seed 12345 \
  --batch-size 8 --workers 8 --execute-models
```

Omit `--execute-models` to validate the real handoff and prepare the full run
without inference. In-process callers can use
`after_fusion.run_after_fusion_result(effective_result, output=..., seed=...,
execute_models=True)` immediately after the existing Fusion gate returns. The
persisted `_v290_effective_result_path` must match the in-memory result. There
are no global monkeypatches or changes to the old portfolio runner.

For an explicitly requested matcher-menu experiment, pass repeatable
`--exclude-operation OPERATION` flags and optionally
`--detection-from /absolute/path/previous_run/tool_rewrite`. This validates and
reuses only the detector output bound to identical problem, proof and associated
documents, then makes one new matcher-stage call with the requested menu. The
old matcher decision is not supplied or rewritten; the previous run stays intact.
Keep the same master seed and other settings when isolating a menu change.

`resume_algebra_workflow --source-run /absolute/path/run/tool_rewrite
--output-dir /absolute/path/new_recovery --sample sample_01` resumes a saved,
accepted candidate stopped at the diagnosed threaded Laurent child-exit error.
It checks the original input/admission bindings, reuses the completed non-proving
division/radical prefix, and restarts only Laurent and downstream stages. Sample
flags are repeatable; the first checked certificate enters appendix synthesis.
Original artifacts and model decisions are not edited. Laurent calls from worker
threads now use a fresh spawned interpreter to avoid inherited executor state.

`resume_selected_division --source-run /absolute/path/run/tool_rewrite
--output-dir /absolute/path/new_recovery --execute-models` resumes the already
selected division certificate after a source-anchor failure before any rewrite
call. It replays the certificate and checks the same parser/semantic admission,
inputs and unique whitespace-equivalent detector span. It preserves the saved
sample seed and model configuration, then runs the existing appendix synthesis
and final Qwen revision/audit. No model decisions, original artifacts or proof
text are edited, and no formalization or solver searches are repeated.

The packaged harness now defaults to Qwen as the main proof writer in all three
available rewrite/audit cycles: writer temperature 0.2, Qwen audit temperature
0.1, unchanged Markdown prompts, mandatory budget forcing and attach-only
appendix. Detection, formalization and semantic-admission roles are unchanged.
Use `proof_harness --proof-rewriter gemma` for an explicit old-profile comparison.
Saved pre-switch configurations keep Gemma unless explicitly overridden. For a
new synthesis from the selected division checkpoint, pass
`resume_selected_division --proof-rewriter qwen`; the override is recorded without
editing old artifacts or supplying earlier drafts/grades. The existing separate
post-PASS Qwen revision/audit remains enabled.

The exact model-written effective Fusion packet, including `resolver_brief`,
becomes one advisory Markdown context document. Original reviewer transcripts,
brief-audit certification labels, prior grading and the old successful proof
are not supplied to the new models. The brief is not rewritten by the host and
cannot supply extra mathematical assumptions. Completed but rejected briefs
retain that disposition and may proceed under the existing gate policy; a
missing, unfinished or corrupt gate is never silently bypassed.

The complete path is:

```text
effective Fusion packet + its original problem/proof
  -> model gap detection and operation matching
  -> formalization / parser / isolated semantic-audit feedback loop
  -> division -> guarded radical -> eligible Laurent -> reduced guarded radical
  -> checked certificate + required source lift
  -> main lemma statement + immutable proof appendix
  -> Qwen main-proof rewrite -> full Qwen audit (up to three cycles)
  -> final Qwen revision -> full Qwen audit -> rewritten proof + provenance
```

An audited `ACCEPT_AS_WRITTEN` Fusion decision is preserved without an invented
tool request. If the detector declines, selects an unsupported operation, or no
formalization produces checked evidence, the adapter reports
`needs_regular_resolver` rather than fabricating a rewrite. An optional
host-owned `fallback(handoff)` callback can continue the ordinary Resolver with
the unchanged Fusion packet. Mechanical/integrity failures never silently invoke
that fallback. A successful tool-assisted path publishes `rewritten_proof.md`,
including Appendix A, at the post-Fusion run root. Detailed progress is in the
`tool_rewrite/` child run. Existing reviews, Fusion, brief audits and earlier
proof artifacts remain untouched.

The certified-checkpoint replication through this packaged synthesis core,
`v0324r32_p2_harness_replication_20260909`, independently scored **7/7 strict**
on the newly generated proof. Its proof SHA-256 is
`8dc31e86ae079de4d970bb24d87e8f6155f97da8c5bf2aede7dbdc8086d215b1`.
This result does not imply that a fresh post-Fusion formalization run has already
reproduced 7/7. `test_after_fusion.py` covers the actual handoff format, unchanged
gate decisions, source/hash rejection, host fallback and terminal publication.

## Packaged problem-to-proof harness

`proof_harness` is the user-facing entry point. Input: a problem statement, one
proof, and optional associated Markdown documents. Output: `rewritten_proof.md`
and `result.json` with the audit verdict, source/certificate hashes, selected
request and full stage artifacts. The proof contains the lemma statement in its
main body and the **complete checked lemma proof as Appendix A**.

The fresh path composes the existing modules:

1. Qwen detects the gap and chooses an operation. `NO_TOOL` and unsupported
   operations are recorded without changing or resampling the model's decision.
2. Up to eight independently seeded Gemma formalization tracks, three cycles
   each, compile source-grounded typed guards. Parser failure skips the semantic
   audit. An isolated Gemma audit must accept the same parsed draft before tools.
   Only the latest parser/audit/tool feedback enters a repair; no human math hints.
   In expression fields only, a singleton `(name)` is normalized to `(symbol name)`
   when `name` is declared and is not a reserved expression operator. Tool targets,
   generators, guards and domain facts use the same AST normalizer; raw model
   text and source quotations stay untouched. Applied rewrites are recorded as
   `parenthesized_declared_symbols`. Unknown names, operator calls, extra operands
   and source-copy errors are not repaired. Parsing still requires the unchanged
   source checks and semantic acceptance before tools; no model retry is needed
   merely for this spelling. Old normalization records are unchanged when this
   new alias is absent.
3. One deterministic algebra cascade: guarded substitution/normalization/division
   → guarded radical membership → eligible Laurent reduction → reduced guarded
   radical membership. Radical execution directly exports a checked identity;
   there is no redundant positive screen before certificate export. Laurent
   candidates also need a checked lift to the original target. Inconclusive
   computation goes back to the next formalization cycle, not to a fabricated
   disproof or acceptance.
   Certificate export runs **before** lift and consistency checks. If it is not
   verified (including a timeout), those follow-up checks are recorded as skipped
   and the route returns immediately. Only a verified certificate launches them:
   the Laurent lift is mandatory, while consistency remains a parallel diagnostic.
   Trial manifests record `certificate_first_followups_on_verified_v1` so this
   scheduling change is distinguishable from older, all-parallel runs.
   Division substitution retains an already justified nonzero denominator when
   cancellation removes it from a transformed guard's numerator. Its nonzero
   status is checked against the pre-substitution guards; no new source
   assumption is introduced, and all later denominator checks remain mandatory.
   Division results record `retain_checked_substitution_denominator_v1`.
4. The first verified candidate immediately enters synthesis. Other tracks stop
   at their next stage boundary; already-running requests are allowed to finish.
   Radical-source consistency is a parallel diagnostic and does not delay synthesis, but a known
   contradiction prevents final publication.
5. Gemma writes the main proof with an immutable lemma marker, including both
   the hypotheses-to-lemma connection and the lemma-to-conclusion connection.
   It does **not** receive the large appendix body. Deterministic code inserts
   the lemma and appends its exact checked proof once. Qwen audits the complete
   assembled proof, including the appendix and the original tool-call purpose.
   There are at most three initial rewrite/audit cycles.
   Rewrite system instructions are case-independent: model-authored semantic
   bindings and target labels are not interpolated into the proof contract.
   The accepted formalization remains untrusted user context, with generic
   obligations to derive its source equations, guards and connection to the goal.
6. After an accepted initial rewrite, Qwen makes **one final revision** of its
   main draft, followed by one full-proof Qwen audit. The original source,
   recorded tool purpose, accepted formalization and fixed lemma remain context;
   the initial draft is included as untrusted working text. The exact appendix
   suffix is removed and the lemma replaced by its marker using a lossless,
   hash-checked round trip. No appendix body, prior whole-proof audit, strict
   grade, gold solution or successful example is added to the writer's prompt.
   The final writer uses the configured Qwen model at temperature 0.2; its auditor
   retains temperature 0.1. Both stages use mandatory budget forcing and the
   existing token/prompt caps. There are no additional algebra or formalization
   calls. Only a final whole-proof PASS publishes `rewritten_proof.md`; rejection
   preserves the drafts but does not silently fall back to the initial proof.
   A same-model audit is not independent-model validation, a strict score, or a
   formal theorem proof.

The shared `appendix_synthesis` module enables the final revision by default for
both fresh division/radical routes and certified-checkpoint replay. Its initial
core artifacts remain unchanged in `02_synthesis/`; the final pair is stored in
`02_synthesis/05_final_qwen_revision/`. Inspect `final_revision.json` for its
policy and input/output hashes and `appendix_pipeline_result.json` for the
complete successful handoff. The parent result and public rewritten proof refer
to the final Qwen output, not the initial core's `terminal_proof.md`.
An explicit `final_qwen_revision=False` Python argument preserves the old profile
for controlled comparisons; normal entry points do not disable the new step.

Fresh run (omit `--execute-models` for an offline plan and input snapshots):

```bash
python -B -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.proof_harness \
  --problem-file /absolute/path/problem.md --problem-id my_problem \
  --proof-file /absolute/path/proof.md \
  --output-dir /absolute/path/new_run --master-seed 12345 \
  --batch-size 8 --workers 8 --execute-models
```

A problem JSON may instead contain `problem_id` and `statement` (or `claim` or
`problem`). Other fields, including reference solutions, are excluded from the
input snapshot. `--associated /path/repair_brief.md` is repeatable; supplied
documents are untrusted context, not additional certified hypotheses. They may
not replace detector/matcher records. No reference solution or grading feedback
belongs in generation inputs.

Certified-checkpoint replay uses the same synthesis module and requires no new
detector, matcher, formalizer, semantic-encoding audit, or Singular search:

For fresh multi-proof experiments, the existing `experiment` controller accepts
`"entrypoint": "proof_harness"` in its external configuration. It validates the
packaged input and publication hashes, runs each proof through fresh detection,
and independently scores accepted terminal proofs with Markdown grader output.
Unaccepted routes remain unscored; legacy semantic-recovery code is not applied
to the new artifact format. This entrypoint has no overall synthesis deadline;
the existing bounded model-call counts, token limits and per-tool CPU caps remain.

```bash
python -B -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.proof_harness \
  --resume-certified-trial /absolute/path/certificate_trial \
  --appendix-from /absolute/path/saved_appendix_run \
  --output-dir /absolute/path/new_replication --master-seed 12345 --execute-models
```

`--appendix-from` is optional: without it, the saved witness is re-expanded and
rendered using exact sparse coefficient tables, with no slow polynomial
factorization. With it, the existing appendix and all its source bindings are
checked and reused unchanged. The accepted formalization, original problem/proof,
semantic audit, exact certificate and source lift must remain available. Always
use a new output directory; old runs are never overwritten. This is explicit
checkpoint replay, not arbitrary process-crash resumption or fresh formalization.

Defaults preserve the successful synthesis profile: Gemma 31B, temperature 0.2,
maximal reasoning; Qwen3.6 27B, temperature 0.1 for audits and 0.2 for the final
revision; mandatory budget forcing, 16k
thinking budget, 32k/48k output/parser-recovery caps, 180k-character prompt cap,
and **no model HTTP or overall deadline during synthesis**. Detector/matcher and
Gemma formalization/audit use temperature 0.1 and the existing 600-second HTTP
limit. Division has 60 seconds, other CPU checks 600 seconds and 4 GiB per worker.
The maximum fresh logical stage count is 58 with eight three-cycle tracks; parser
recovery/mandatory continuation may make multiple HTTP calls within one stage.
There are no model-generated JSON outputs; JSON files are deterministic ledgers.

Monitor the root `status.json`, `selection.json`, per-sample `status.json`, and
the selected synthesis's `model_budget.json`. Run the CLI in the existing job
manager/tmux for logout persistence. Strict scoring remains a separate,
isolated post-run operation and is never fed back as generation guidance.

Modules: `proof_harness` (inputs/orchestration), `algebra_workflow` (admitted
algebra and certificate handoff), `appendix_synthesis` (successful attach-only
rewrite), and the existing parsers, domain compiler, algebra kernels and whole-
proof auditor. No problem-specific adapter or saved success is loaded in fresh
mode. Test with `test_proof_harness.py`, `test_appendix.py`,
`test_division_fresh_audited.py`, `test_division_audit_repair.py`,
`test_radical_packaging.py`, `test_generic_rewrite.py` and `test_final_revision.py`.

Empirical reference: the saved-certificate attach-only P2 experiment
`v0324r31_p2_deterministic_appendix_20260909` received an independent strict 7/7.
That is evidence for this synthesis path on one proof, not a guarantee of 7/7
or of successful fresh formalization on other inputs. The new top-level fresh
composition is covered by synthetic model-call tests with real exact arithmetic;
fresh GPU success must be reported separately from certified-checkpoint replay.

## Local evidence from a repair brief and resulting proof

`local_evidence_experiment` takes an original theorem, original proof, Fusion
repair brief, and resulting proof. Gemma selects and formalizes one useful local
check, using Markdown only. It can choose an existing exact expansion/finite
enumeration operation or the generic `check_linear_real_implication` operation.
No reference solution, strict grade, manually selected mathematical claim, or
operator-supplied witness enters the model context.

The linear tool accepts bounded typed piecewise-linear real formulas, including
minimum, maximum, absolute value, and ranked values. It checks premise consistency
before testing the implication with Z3. A counterexample is independently replayed
using exact rational arithmetic. An UNSAT result establishes only the encoded
local implication and does not include an independently checked proof certificate.
Neither outcome certifies the full theorem or the correctness of the encoding.

Up to three cycles use parser feedback, then a separate Gemma semantic audit,
then CPU execution. Parser failures skip the audit and tool; semantic rejections
skip the tool. A usable local result triggers one Qwen proof/brief rewrite and
one Gemma whole-proof comparison audit. Models may explicitly report unresolved
mathematics. Strict scoring is not part of this pilot. It has at most eight
logical model stages, mandatory budget forcing, and an 80k-character prompt cap.
The existing servers are Gemma on port 8030 and Qwen3.6 on port 8027.

```bash
python -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.local_evidence_experiment \
  --problem-file /absolute/path/to/problem.json \
  --original-proof /absolute/path/to/original.md \
  --repair-brief /absolute/path/to/repair_brief.md \
  --resulting-proof /absolute/path/to/resulting.md \
  --output /absolute/path/to/new_run --master-seed 12345
```

Focused tests: `test_linear_evidence.py`; these include independent witness
replay, nonlinearity rejection, premise consistency, and parser/audit/tool gates.

Linear-input normalization accepts `tool-args` as an unambiguous fence alias for
the already-selected linear operation and rewrites finite decimal expression
literals to exact rationals, without floating-point rounding. It never edits
source prose, comparisons, domains, or mathematical claims. Canonical arguments
and every normalization are saved; the auditor sees both original and canonical
input. All original model output remains unchanged.

`--resume-run /path/to/terminal_run --saved-cycle N` (instead of the four source
paths) rechecks one saved parser rejection after a mechanical normalization fix.
It validates input hashes and budget-forced model provenance and refuses cases
that already reached an auditor or tool. No new formalization call is made;
the recovery uses at most three stages: audit, rewrite, and final proof audit.
The client response timeout is 900 seconds per HTTP request and can be set with
`--request-timeout-sec`; this does not change token budgets or model prompts.
Already-running requests retain the timeout with which they were submitted.

`--rewrite-from-run /path/to/run --rewriter gemma` (or `qwen`) starts only the
brief/proof rewrite and subsequent proof audit, including for a concurrent model
comparison. It rebinds the source hashes, budget-forced formalization and semantic
audit, admission, request, and saved exact rational witness. The witness is replayed
without a new solver search. The rewrite prompt is identical to the original
evidence-driven prompt. No new formalization or semantic-audit call is made.
This recovery currently supports checked linear-real counterexamples only;
unsupported evidence fails closed. It never treats a model audit as a strict score.

`local_evidence_reconsider --source-run /path/to/timed_out_run --output /path/to/new_run
--request-timeout-sec 900` resumes only an unfinished mandatory reconsideration
when the complete primary response was already saved. It checks the original
evidence, raw response, reasoning, prompts, and generation-parameter hashes. It
retains the original seed, token budget, model, temperature, and continuation cue;
only the HTTP timeout changes. There is one continuation request, with no primary
regeneration, formalization, semantic re-audit, or solver search. A completed proof
still receives the usual proof audit; an unresolved response remains unresolved.

## Model-authored division-only experiment

### Located deterministic parser feedback

`division_fresh_audited` retains parser-first gating: invalid drafts skip the
semantic auditor and algebra tool. `parser_feedback.py` now supplies read-only
line/field diagnostics, offending text, expected syntax, and exact typed-leaf
spelling suggestions for declared variables in zero-argument operator position.
It checks independent fields so multiple errors can be reported in one retry.
No mathematical operand/grouping, source quotation, guard, or decision is guessed
or edited. Source-copy diagnostics never select a replacement source passage.
The original strict parser remains the sole parser PASS gate; a model-authored
replacement must pass it and the semantic audit before execution.

Diagnostics are at most 12 records and 6000 feedback characters. They only use
the current model draft, original source text and generic grammar. No extra model
call is added. Retry prompts retain only the latest draft/feedback and ask the
model to preserve unaffected mathematics. Run manifests record
`parser_feedback_version=located_parser_feedback_v1`.

### Source-grounded domain-ledger experiment

`division_batch --domain-ledger --batch-size 8 --cycles 3 --auditor gemma`
enables an additional Markdown Domain Ledger inside each existing formalization.
It does not add model calls. The same three-cycle parser/audit/tool feedback loop
and mandatory budget forcing apply. Old runs remain on their original contract
unless the flag is supplied; continuations preserve the saved flag.

Each fact contains a type, safe polynomial AST (or RETAINED/NONE), a source
identifier, an excerpt matched to the original theorem/proof, and a model-written
justification. The compiler only derives nonzero from POSITIVE, NEGATIVE, or
NONZERO. Weak inequalities and other restrictions are retained for semantic audit,
not silently enforced by the polynomial backend. Every authored nonzero guard and
division denominator must be covered by compiled factors. Source matching is NOT
semantic entailment or proof that the domain inventory is complete.

Both gates bind to the same model draft and deterministic compilation. Artifacts
retain the original guard program, source hashes, fact-to-rule mapping, compiled
guard hash, and audit. Gemma audits the original inputs and current draft plus a
compact compilation summary; it sees neither prior audit verdicts nor tool results.
Only the author receives parser/audit/tool feedback for the next cycle. There are
no reference solutions, hand-selected counterexamples, or problem-specific guards
in the reusable prompt/compiler. This remains a division-only backend, not a new
Singular or counterexample-search portfolio.

Temperature comparison: `division_batch --formalizer-temperatures
0.1 0.1 0.2 0.2 0.3 0.3 0.4 0.4` assigns one temperature per track. It remains
fixed through that track's repair cycles; the auditor stays at 0.1. The single-run
flag is `--formalizer-temperature`. Source-bound continuations preserve it.
Optional `--after-batch /path/to/baseline` waits before starting the comparison and
blocks on a prerequisite mechanical failure. It never supplies earlier math to
the new model calls. All controls are generic and saved in run artifacts.

Version 1.1 applies the existing declared-leaf AST spelling normalization to the
ledger too, reports multiple source-copy mismatches in one bounded feedback item,
and clarifies literal source copying and non-repetition in the generic prompt.
It does not repair mathematical expressions, weaken source matching, or add facts.

Focused regression suite: 101 tests across `test_domain_ledger.py`,
`test_rational_division.py`, `test_division_audit_repair.py`, and
`test_division_fresh_audited.py`. Includes weak-inequality non-strengthening,
source/AST validation, guard coverage, retained branches, deterministic compilation,
toy exact proof/replay, and same-draft semantic gating without extra model calls.

`division_experiment` reuses only a saved acquisition's original theorem, proof,
and detector/matcher request. A single new Gemma logical stage chooses `CALL_TOOL`
or `NO_TOOL` in Markdown and supplies fresh guarded polynomial arguments. It gets
no earlier formalization, certificate, gold proof, grading feedback, or operator
mathematical representation. The stage uses temperature 0.1, maximal reasoning,
mandatory budget forcing, a 16k thinking budget and 32k/48k parser recovery.
The decision parser accepts optional blank lines and LF/CRLF line endings without
changing the decision, typed expressions, or guards. Decision tokens and section
order remain exact; conflicting decisions, extra sections, and malformed typed
blocks are rejected. The original model response is retained unchanged.

On `CALL_TOOL`, `rational_division` executes once with a 60-second/4-GiB bound:
guard-checked linear substitutions, rational normalization, polynomial division,
then independent witness re-expansion. It performs no Groebner construction,
Laurent transformation, or Singular call. Nonzero remainder/time limit means
`INCONCLUSIVE`, not disproof. Even `VERIFIED_SUPPORT` is conditional algebra only:
formalization semantics are not audited. This experiment deliberately stops before
semantic auditing, proof synthesis, and strict scoring.

```bash
python -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.division_experiment \
  --source-acquisition /absolute/path/to/saved/01_acquisition \
  --output-dir /absolute/path/to/new_run --master-seed 12345 --execute-models
```

## Audit-feedback division continuation

The bounded `division_audit_repair` continuation resumes the latest canonical
forced draft from a stopped division experiment. It rechecks source bindings,
sends the unchanged draft plus original inputs to one independent Qwen semantic
audit, then gives Gemma one repair stage with that audit and deterministic parser
feedback. Both models use temperature 0.1, Markdown-only output, mandatory budget
forcing and the existing 32k/48k parser recovery. Audit verdicts are preserved;
neither a rejection nor an acceptance is imposed by the host. A repaired
`CALL_TOOL` draft must pass parsing and a new independent Qwen audit of that exact
Markdown before invoking the same 60-second division backend once. The final
audit sees only original inputs and the repaired draft, not the previous audit,
parser feedback, or any exact result. Its verdict is hash-bound to the draft and
compiled request. Rejection, malformed audit, `NO_TOOL`, or parser failure invokes
no tool. There is at most one repair stage and one final audit stage, not a loop
until acceptance. Full recovery uses at most three logical model stages. Qwen's
acceptance is model judgment, not a formal proof of semantic correctness. Proof
synthesis and strict scoring are outside this experiment.

```bash
python -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.division_audit_repair \
  --previous-run /absolute/path/to/stopped_division_run \
  --output-dir /absolute/path/to/new_run --master-seed 12346 --execute-models
```

To resume an already-created canonical repair, add `--resume-repaired` and point
`--previous-run` at its audit-repair run. This validates source and model-response
bindings and performs only the final Qwen gate (one logical model stage); it does
not regenerate the formalization or repeat its earlier audit. A previous result
is not supplied to Qwen. Historical files are never overwritten; use a new output
directory. `semantic_certified` in this experiment denotes **model-audit acceptance
only**, explicitly labeled `semantic_certification_kind: model_audit_only`.

## Fresh tool-assisted proof rewrite

For a fresh formalization with a separate model-auditor call, use
`division_fresh_audited --auditor gemma` (or `qwen`). This starts from the original
theorem, proof and recorded detector/matcher request, without reusing a prior
formalization, audit, diagnostic, certificate or score. Gemma-only mode sends
**every** model call to Gemma; the auditor has a fresh conversation containing
only the original inputs and current Markdown, never the author's reasoning or
another audit. Using the same model is context isolation, not a guarantee of
independent mathematical judgment.

Each trial has up to `--cycles 3`: one initial formalization and up to two
feedback-driven rewrites. Every draft is parsed first. Parser failure skips the
semantic audit and tool, records `02_audit/skipped.json`, and sends only the latest
draft and deterministic parser feedback to the next rewrite. No audit verdict is
invented, and no earlier draft's audit is carried forward. A failure in the final
cycle ends the track without another model call. Parser-valid CALL_TOOL drafts
receive an independent audit. Each rewrite sees only feedback belonging to its
latest draft, alongside the original inputs.
Passing both gates invokes the tool without a duplicate audit. Exact support ends
the loop; an inconclusive result is added to the next rewrite's feedback at every
cycle, alongside that draft's parser and audit feedback. The semantic auditor sees
only the original inputs and current draft, never earlier exact outcomes. There
are at most six logical stages per trial (three formalizations, up to three audits);
three parser failures need only three author stages and zero audits. Temperature
defaults to 0.1, with the formalizer schedule configurable as above. Mandatory
budget forcing and token caps are unchanged. Manifests/status record
`audit_on_parser_failure: false` and status counts `audit_calls_skipped`.
A separate `parser.json` records formalization validity; transport response
capture alone does not mean parsing passed. Only parser PASS and auditor ACCEPT
on the same draft allow one division-tool invocation per cycle (at most three).
No proof synthesis/scoring. A nonzero remainder or timeout is not called disproof.

```bash
python -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.division_fresh_audited \
  --source-acquisition /absolute/path/to/saved/01_acquisition \
  --output-dir /absolute/path/to/new_run --master-seed 12347 \
  --auditor gemma --execute-models
```

## Full proof-rewrite interface

`division_batch` runs up to eight independent `division_fresh_audited` workers
concurrently, using distinct deterministic seeds and separate artifact directories.
Use the same CLI arguments, plus `--batch-size 8`. No draft, audit, or exact result
is shared between trial prompts. With `--auditor gemma`, all model stages use
Gemma only. Temperature and per-trial budgets stay unchanged; eight trials have a
maximum of 48 logical stages and 24 bounded tool invocations. The detached
controller records each trial's stage, parser/audit gates, sizes and tool result.
It continues the other trials when one rejects or fails.

`division_tool_feedback_resume` supports adopting the tool-feedback rule for an
already-running batch without killing in-flight model calls. It validates the
saved draft, audit, original source and exact-tool request, then resumes only unused
cycles following INCONCLUSIVE. `--previous-batch` watches completed workers and
starts these continuations as slots become available; `--previous-run` resumes one
track. Original artifacts are preserved, seeds and total cycle limits are retained,
and the continuation's `status.json` provides the combined current batch view.

The `rewrite` module is the reusable proof-plus-associated-information interface:
input a theorem file and an original proof file; output a terminal rewritten proof,
the verified evidence, audits, and hash-bound provenance. It runs fresh detection,
matching, eight guarded formalizations, deterministic AST deduplication, Laurent
and Singular checks, exact replay, an exact-blind semantic audit, and the generic
immutable-certificate synthesis loop. No certificate is transferred between input
proofs. The first fully promoted route enters synthesis immediately.

The currently supported acquisition provider is polynomial ideal membership with
unit-circle/guarded-linear Laurent reduction. Unsupported model-selected operations
or certificates fail closed without rewriting the model's decision.

```bash
python -m cognitive_well_harness_v0_3_343_real_root_classification_20260916.rewrite \
  --problem-file /absolute/path/to/theorem.json \
  --proof-file /absolute/path/to/original_proof.md \
  --output-dir /absolute/path/to/new_run --master-seed 12345
```

`experiment` is a separate, problem-independent detached controller. Its input
configuration specifies proof paths and score thresholds. It runs one fresh pilot,
uses the unmodified isolated strict-scoring launcher, and runs the remaining
distinct proofs only after the pilot passes. It can resume completed case/score
artifacts by hash. It does not pass grades or gold references into synthesis.
Unmet score gates or mechanical failures are recorded for generic refinement, not
hidden or retried indefinitely. Historical attempts are never overwritten.

An exact-proved request rejected by the semantic auditor has one bounded recovery:
Qwen reassesses the actual unchanged typed input and earlier feedback, without any
tool outcome or gold reference. It must explicitly justify its assessment. If the
reassessment accepts, this case's existing certificate is replayed before synthesis.
If it rejects, Gemma may make one complete model-authored formalization repair,
followed by new Laurent/Singular/lift checks and an exact-blind Qwen audit. No human
removes guards, and no repeated re-audits are sampled until acceptance. Recovery
uses at most nine extra logical stages and never exceeds the original 24-stage
case ceiling. The stopped controller can resume this recovery without restarting
detection, matching, or the eight-sample portfolio.

If an accepted reassessment stops in deterministic certificate rendering before
any synthesis call, the controller can resume in a separate child directory.
This rebinds the saved acceptance, original source, and same-case certificate;
it makes no new reassessment, formalization, or Singular call and retains the
remaining original call budget. It cannot resample a semantic rejection or
restart a failed model synthesis. The original failure artifacts are preserved.

The fresh path uses at most 24 logical model stages, two parser-recovery caps
(32k/48k), a 16k thinking budget, and a 180k-character prompt ceiling. It retains
only the latest rejected response in parser feedback and supplies the immutable
certificate only once per repair prompt. Laurent preprocessing and Singular each
retain their 600-second limits. Models emit Markdown; host ledgers are JSON.

Symbol safety reserves both identifiers and printed mathematical spellings for
all generated names. Legacy QQ(i) strings declaring a variable named `I` are
ambiguous and are rejected explicitly, never silently read as the imaginary unit.
Rational source-guard expressions preserve the variable `I` normally.

Problem-specific historical adapters have moved to
`experiments/legacy_problem_specific_adapters`. No current generic entry point
imports them; static and clean-process tests enforce that boundary.

This package replaces a problem-specific certificate-to-proof bridge with a
problem-independent protocol for polynomial ideal-membership evidence.

## Authority split

The certificate-author model receives the theorem, the complete proof attempt,
the frozen typed polynomial request, its typed nonzero guards, and an independently
replayed affirmative exact result.  The model chooses:

- which frozen source relations to expose;
- any explanatory intermediate polynomial identities;
- the semantic meaning of the formal target and guards; and
- the theorem conclusion to which the certificate is applied.

Deterministic code makes none of those mathematical selections.  It only parses a
bounded safe expression language, rejects symbols or relation labels outside the
frozen request, verifies explicit model-written polynomial combinations by exact
`QQ` expansion, checks cancellation factors against the frozen nonzero guards,
and exposes polynomial-division quotients for unit-circle identities. The
production path never searches the full source ideal again. It
requires the final equality to be exactly the frozen target equal to zero,
independently reparses the typed formal request, binds all source artifacts and
exact replay records by hash, and renders the verified mathematics as readable
Markdown.

The rendered block then enters the existing generic whole-proof synthesis loop:
Gemma writes a complete proof, deterministic lint inserts the immutable verified
block exactly once, and Qwen independently audits the surrounding semantic
derivation.  The first Qwen `PASS` is selected; otherwise the run fails closed.

That same audit now compares the original untrusted proof with the current
replacement on every cycle. Qwen identifies still-needed reasoning lost during
rewriting and supplies justified restoration passages in its existing Markdown
issues. Gemma checks and incorporates the suggestions before another whole-proof
audit; the original proof and suggested repairs are never credited as reasoning
already present in the submitted replacement. Valid alternative routes and
necessary removal of source errors remain allowed. No extra stage or larger token
budget is introduced, and the exact certificate remains immutable.

Fresh and saved-route loaders now carry hash-bound detector and matcher Markdown
into both synthesis and auditing. In the audit prompt the order is theorem,
original proof, frozen tool-purpose records, audit instructions, then the full
rewritten proof last. These records supply the model-authored trigger, desired
exact fact, and downstream obligation without human mathematical additions. Qwen
must give a short four-link `Gap Closure` explanation with actual submitted
passages, not just a PASS checkbox. No extra model call or larger token cap is
introduced. Other associated documents are not automatically exposed.

## Validated first-rewrite profile

`first_rewrite.prepare(adapter)` and `first_rewrite.run(...)` expose the bounded
first-rewrite behavior as reusable Python entry points; no temporary experiment
runner or benchmark path is required. The adapter supplies the original proof,
theorem, recorded detector/matcher, verified evidence provider, and same-case
model-authored semantic contract. `prepare` returns the single-cycle adapter and
prompt/proof/certificate hashes without model inference. `run` performs one Gemma
rewrite followed by one Qwen audit, using temperatures 0.2/0.1 by default and the
existing 32k/48k budget-forced Markdown caller. Pass the already-consumed
`prior_model_stages` to enforce the original 24-stage ceiling.

The detector's unique whitespace-equivalent trigger is marked as an `EXPLICIT_UPDATE` block in
Gemma's prompt-only view of the source. Gemma must update that application block
first, then derive both connections around it: original hypotheses/expressions to
the lemma, and its conclusion back to the original claim. The certificate is
immutable and appears once. Qwen gets the unmodified original proof, tool-purpose
records, and the new proof last, with a four-link `Gap Closure` explanation.
These shared prompt and validation changes also apply to the existing fresh
end-to-end and multi-cycle entry points; their cycle budgets are not silently
changed to one.

Only Qwen PASS promotes a terminal proof. A rejection remains `failed_closed`,
retains the submitted proof/audit for inspection or independent scoring, and is
not silently retried. Strict scoring remains separate and does not supply feedback
to generation. The profile never removes a mathematical guard or imports a
benchmark-specific adapter, previous rewritten proof, gold solution, or score.

```python
from cognitive_well_harness_v0_3_343_real_root_classification_20260916.first_rewrite import run

result = run(adapter=adapter, output_dir=output_dir, master_seed=seed,
             prior_model_stages=already_used_stages)
```

## Model protocol

Every model-facing response is Markdown.  The certificate author uses two strict
Markdown headings and a fenced `certificate-args` block containing a line-oriented
S-expression DSL.  It is not JSON and cannot contain executable code.  Proof
rewrites and proof audits likewise use their existing strict Markdown protocols.
Internal provenance ledgers are JSON because they are emitted by deterministic
code, never by a model.

## Reasoning and budget forcing

The certificate-author role must use `max`, `xhigh`, or `ultra` reasoning.  Before
the default model call, the harness explicitly installs the inherited mandatory
budget-forcing transport.  Each 32k/48k/64k attempt therefore consists of an
initial reasoning response followed by one semantic continuation that emits a
complete replacement Markdown artifact.  Parser failures advance to a fresh cap
with deterministic accumulated feedback.

New v324 launches additionally set the server's native thinking-token budget to
16,384, leaving room within every 32k/48k/64k completion cap for a final Markdown
answer. This preserves deep reasoning and the mandatory semantic continuation.
The shared caller's default remains unchanged for other harnesses. This setting
does not retroactively change an already-running process.

The adapter accepts only the canonical forced response.  It independently checks
the forcing schema, policy, model, stage, text hash, cue hash, token cap, recovery
attempt, unstructured/Markdown mode, and 600-second request timeout.  The same
binding is replayed for every proof rewrite and Qwen audit artifact.

## Scope

The current implementation is generic across safe polynomial ideal-membership
requests.  It deliberately does not claim to adapt every exact operation.  A
caller must provide an operation-specific `replay_exact` function returning a
standardized, independently verified affirmative record.  A stored `PROVED` word
alone is not accepted.

The `resume_saved` entry point loads a saved first-promoted direct-Laurent
selection, checks its frozen formalization and accepted semantic audit, re-expands
the saved multiplier identity, and checks the saved lift bindings. It does not
rerun detection, matching, formalization, Laurent search, or Singular. Subsequent
materializations check the artifact hashes against that successful replay, rather
than repeating the initial expansion. The author receives the complete saved
witness rendered as Markdown, without truncated polynomial expressions.

`resume_proved_exact` handles an earlier checkpoint: a failed exact route with a
saved proved target, a completed source lift, and no semantic audit attempt. It
copies and binds that case's artifacts into a new output directory, replays the
unchanged certificate, then runs the existing Qwen audit and synthesis gates.
It never resamples an existing semantic verdict. The safe polynomial decoder uses
an explicit AST stack, so long valid multiplier sums do not exceed Python's
recursion limit; its syntax whitelist and exact coefficient rules are unchanged.

`fresh_formalizations` regenerates only parser-failed arms with new seeds and the
same temperature schedule. Its first prompts contain no rejected drafts or old
feedback. Successful arms are untouched. This entry point stops after generation
and parsing by default. Its opt-in `--resume-checks-from` mode resumes every
compiled arm from a completed fresh portfolio through the existing direct-Laurent
exact/audit/synthesis path. It reparses and binds the saved theorem, proof, tool
decision, raw/canonical formalizations, guards, and producer records. Failed arms
are not regenerated. Original and fresh-generation model stages both count toward
the unchanged 24-stage case limit. The original artifacts remain untouched; the
new acquisition directory receives copies needed by the synthesis provider.

`compact_audit` is an opt-in diagnostic for a saved rewritten proof. It retains
the original proof, tool purpose, and exact lemma statement, but omits only the
verified saved witness's internal derivation from Qwen's audit view. All
surrounding proof text is unchanged. The saved certificate, verification record,
and source-artifact hashes are checked before omission; unknown renderer formats
fail closed. The full submitted proof and original run remain unchanged.
One audit with the saved model configuration, seed, and mandatory continuation
is allowed; neither semantic rejection nor parser failure triggers another audit.
No earlier audit response, grading feedback, or operator mathematical hint is
supplied. This diagnostic does not replace the default full-certificate audit or
promote a proof. Invoke with `--source` pointing to the synthesis directory and
`--output` pointing to a new directory outside it; `--prepare-only` makes no calls.
The optional `--with-changes` flag adds a deterministic line-change ledger, with
the frozen certificate represented by its insertion marker. Every addition,
deletion, or replacement block has an ordered ID, exact before/after text, and
local context. Qwen must review every ID in Markdown as JUSTIFIED, INVALID, or
UNRESOLVED with a reason. The parser checks coverage and verdict consistency,
not mathematical correctness; legitimate changes of route remain allowed.
This uses the same single audit and does not resample omitted or rejected reviews.

`saved_witness.py` provides a lossless fallback for a compact author that fails.
It renders the actual saved substitutions, guarded pivot, compatibility identities,
multiplier identity, and target lift. Horner rewriting and shared-expression names
shorten the stored polynomials; every rewritten polynomial is re-expanded and
compared exactly. This is presentation, not a new ideal-membership search.
Pivot-factor nonzero witnesses include both transformed source guards and Laurent
units established by checked source-circle inverse identities. Unit names or
stored assertion flags alone cannot justify a nonzero factor.

`radical_resume_synthesis --trial ... --output ... --no-time-limit --factor-first`
resumes a saved verified radical identity and its source lift without acquiring
new formalizations or running Singular. The optional factor-first presentation
compares exact factorization with Horner form before shared-expression naming;
all introduced expressions are re-expanded and checked. The fixed presentation
and prompt-size budgets remain in force: no certificate expressions are omitted.
`--no-time-limit` passes an explicit `None` to both the rendering worker wait and
every model HTTP request, including budget-forced continuations. Completion
provenance checks require that same explicit setting. There is no overall
wall-clock deadline; memory, token, and three rewrite/audit-cycle limits remain.
These options are opt-in and preserve the earlier default behavior.

`--skip-rendering --no-time-limit` instead rebinds the saved accepted request,
verification, and source lift, then starts synthesis immediately. It performs no
factorization, multiplier rendering, new certificate expansion, or Singular
search. The frozen implication is printed only as a lemma statement. Both models
receive the accepted formalization and explicit notice that the certificate
derivation is absent: Gemma must write the lemma's actual proof and Qwen must audit
it, in addition to both semantic connections. A machine-verified claim alone does
not establish a complete written proof. The large saved witness remains hash-bound
in the provenance artifacts but is not sent in the prompt. This option cannot be
combined with `--factor-first` and does not change the existing retry/token limits.

`--with-appendix --no-time-limit` supplies the full saved Laurent/radical proof as
Appendix A, with the lemma statement in the main text. It rechecks the exact
multiplier identity using sparse QQ(i) polynomial arithmetic and prints every
multiplier in coefficient/exponent tables. The printed rows are parsed back and
compared exactly; extracting the common monomial requires no polynomial
factorization. No term is dropped, and the source substitutions, guards, and
target lift remain explicit. The appendix is hash-bound, shown once per model
prompt, and appended unchanged to each submitted proof before Qwen audits it.
Gemma may cite the supplied appendix but must derive the semantic input and output
connections. The statement-only policy is not used in this mode. Memory, prompt,
token and retry budgets remain unchanged; no new Singular search is performed.

The opt-in `--appendix-attach-only` view keeps that appendix out of Gemma's input
on every rewrite cycle while still inserting the exact same checked body after
the generated main proof. Qwen sees the full assembled document. The model is
explicitly told what it has not seen and may cite Appendix A only for the frozen
lemma. Hash and duplicate-insertion checks are unchanged. `--appendix-from RUN`
reuses an existing bound appendix without rendering or replaying the algebra;
`--wait-for-run RUN` queues inference until a preceding run is terminal, without
stopping or modifying it. Use these options with `--with-appendix`.

### Current-draft repair

The first fresh proof rewrite after tool verification omits `fusion_packet.md`
from the writer prompt. The problem, source proof, detector/matcher purpose,
accepted formalization and immutable lemma statement remain; the appendix is
still attach-only. Fusion provenance is archived unchanged, and the auditor and
subsequent repair context retain their existing inputs. Each call records its
supplied/omitted associated documents in `context_policy.json`. This is a generic
pipeline-role policy, not a mathematical or problem-specific prompt edit.

On subsequent synthesis cycles, the shared core can mark a uniquely quoted
passage in the **current replacement draft**, in addition to the detector's
original-source block. This is prompt annotation, not mathematical editing.
Only exact quotation matches are used, with optional removal of an edge
ellipsis; missing, ambiguous, overlapping, and interior-ellipsis quotations are
not guessed. Immutable lemma and appendix bodies are removed before matching.
The existing Qwen issue list appears once beside the first marked passage.
Generic instructions ask the writer to derive the disputed connection, preserve
correct material, and remove all prompt markers. Output lint enforces removal.

To test a single saved repair transition without repeating formalization,
rendering, or algebra, use the existing radical resume command with:

```text
--with-appendix --appendix-attach-only --no-time-limit
--repair-from /absolute/path/to/saved/rewrite --repair-cycle 2 --max-cycles 1
```

The ordinary `--trial`, new `--output`, and `--master-seed` arguments still apply.
The saved draft must have its own rejecting model audit. Task, certificate,
assembled proof, original audit prompt, and canonical budget-forced response
bindings are checked before inference. A passing audit or unrelated scorer
feedback cannot be recast as repair input. Associated source documents and the
appendix are reused unchanged. One cycle permits one writer and one auditor
stage, with the existing bounded parser recovery and mandatory budget forcing.
No successful reference proof or human mathematical hint is inserted.

`author_guided_replay` adds the existing certificate-author stage to a completed
generic rewrite's saved case, without reacquiring its formalization. The author
gets the original proof and the complete verified witness rendered as Markdown.
The latest budget-forced author's semantic notes condition the existing synthesis
contract; its proposed compact algebra is checked but never substitutes for the
frozen witness in this comparison. Notes remain untrusted even when their syntax
passes. The replay admits one author stage (32k/48k parser recovery), at most three
proof/audit cycles, and optional isolated strict scoring, within the original
24-stage case budget. Prior rewritten proofs and grading feedback are not model
inputs. All previous results remain intact.

`resume_saved_witness` runs that fallback only after the compact-author run has
failed closed. It reuses the latest completed budget-forced response's semantic
notes as **untrusted context**, never its rejected mathematical program. The proof
author and Qwen must substantiate those notes against the original theorem. This
path makes zero additional certificate-author calls.

`score_when_ready` waits for the outer synthesis result, verifies its terminal
proof hash, and invokes the existing strict-scoring skill launcher. It does not
grade an unfinished or failed proof, and supplies no pipeline critiques or target
score to the independent grader.

```bash
/home/user/miniconda3/envs/math/bin/python -m \
  cognitive_well_harness_v0_3_343_real_root_classification_20260916.resume_saved \
  --selection-run /absolute/path/to/saved_selection_run \
  --output-dir /absolute/path/to/new_packaging_run \
  --master-seed 12345
```

Run the focused regression suite in the math environment:

`backend_comparison` is a CPU-only diagnostic on saved tool requests. Admission
requires parser and semantic acceptance tied to the same Markdown draft and typed
request. `--routes laurent_guarded_radical --preview-source /path/to/prior_run`
reuses hash-bound Laurent previews where available, computes only missing
previews, and sends every transformed nonzero guard to the radical backend.
The default limits are two CPU workers, 600 seconds per step, and 4 GiB per
bounded CAS/preprocessing job. No model calls or problem-specific hints are added.
Radical successes are screens only: an independently checked certificate and,
for a Laurent route, the source-to-Laurent lift remain required before promotion.
Consistency is a parallel diagnostic, not a blocking gate. Pending or timed-out
checks do not delay packaging; a completed contradictory result is flagged.

### Native-trigonometric composite pilot

`trig_experiment` starts from an existing sample's original `input/` documents,
not its polynomial formalization. Gemma authors a native `trig-args` Markdown
input with explicit primitive angles, scalar symbols, ordered definitions,
equations, a target, and source-bound domain facts. No mathematical content is
inferred from symbol names. Parser failures skip the separate Gemma semantic
audit; only acceptance of the same immutable input permits the CPU tool.

`trig_formalization` records syntax-level denominators before cancellation,
expands standard sine/cosine identities, compiles only justified nonzero domain
facts, and retains the native input and its expansion map. Domain source matching
and algebraic compilation are deterministic; mathematical faithfulness remains
the auditor's responsibility. Source matching preserves a literal match first;
otherwise it permits one matching pair of enclosing straight or curly quotation
marks, then requires a nonempty verbatim match (ignoring whitespace only).
It does not repair interior text or LaTeX, search a different source, or supply a
missing guard. Original model Markdown is retained unchanged.
The algebra backend does not enforce inequalities
or retained branch/range facts. Supported angles are bounded integer linear
combinations of primitive angles plus integer multiples of pi/2.

The composite pilot uses factor normalization, guarded substitution with three
fixed selection policies, and two deterministic divisor orders. Checks of target
powers 1 and 2 and square-free factor normalization are elementary field rules,
not a full radical-ideal search. Every positive result replays its factor,
substitution, division, and trig-input bindings. Search uses at most 36 checks,
three substitution steps per policy, 20 seconds per step, and 300 seconds overall.
It makes no Singular, Laurent, or intermediate model calls. Inconclusive results
feed the next formalization cycle (at most three). This pilot does not yet invoke
the heavyweight fallback cascade or automatically package its native trig proof
into a whole-proof rewrite.

```bash
/home/user/miniconda3/envs/math/bin/python -B -m \
  cognitive_well_harness_v0_3_343_real_root_classification_20260916.trig_experiment \
  --source /absolute/path/to/existing/sample \
  --output /absolute/path/to/new/run --master-seed 12345 --cycles 3
```

For parser-only recovery, point `--source` at the prior native-trig run and add
`--saved-cycles 2 3` (the selected cycle numbers). Use a new output directory.
This rechecks source hashes and the original model-response provenance, reparses
the unchanged saved Markdown, and resumes at the same semantic audit. It makes
no fresh formalization calls, invokes the composite tool only on audit ACCEPT,
and stops at the first verified target or exhaustion of the selected drafts.

```bash
/home/user/miniconda3/envs/math/bin/python -m unittest -v \
  cognitive_well_harness_v0_3_343_real_root_classification_20260916.test_harness
```
