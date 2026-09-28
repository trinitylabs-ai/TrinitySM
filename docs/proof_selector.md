# Independent proof selector (experimental)

The selector chooses **one unchanged proof from four saved final candidates**.
It runs after generation, in a separate module and output directory. It does not
change the released generation harness, resume its workers, rewrite proofs, or
read reference solutions and external grades. Selection quality has not yet been
measured on the live Gemma/Qwen servers or the benchmark suite.

Entry points:

- `scripts/select_proofs.py`
- `python -m harnesses.proof_selector`

The module uses the existing local Gemma 4 31B and Qwen3.6 27B servers. It adds no
Python dependencies. Start the servers using the
[local reproduction guide](local_reproduction.md#start-the-two-local-servers).
The selector uses the pinned vLLM tokenizer and completion APIs directly; it does
not use the generation pipeline's chat transport or process-wide wrappers.

## Review and selection

1. **Assess all four candidates independently.** For each complete original
   proof, Gemma locates the first invalid implication, Qwen attacks the argument,
   and Gemma checks whether every critical obligation can be closed. These calls
   reuse the frozen review system prompts, user-prompt builders and parsers.
2. **Fuse the three review records.** Gemma reads the problem, that one proof and
   the three final structured reviews. It distinguishes acceptance as written,
   acceptance with routine completion, a required repair and an inconclusive
   assessment.
3. **Audit the assessment.** Qwen checks an acceptance against the complete
   proof, or tries to refute a negative assessment. A supported criticism is
   still a criticism: it does not certify a hypothetical repaired proof.
4. **Revisit disagreement.** A rejected acceptance, challenged criticism or
   unresolved audit triggers another review–fusion–audit round, up to three
   rounds in total by default. Each round receives the original proof and only
   the latest structured dispute. It does not receive accumulated reasoning
   transcripts. Stable assessments stop early; remaining disputes are recorded
   as uncertain.
5. **Choose an existing candidate.** If any acceptances survive their audit,
   compare those candidates. Otherwise compare all four and mark the choice
   `best_effort_unverified`. Gemma and Qwen independently compare compact final
   assessment packets, with the A/B order reversed for Qwen. Disagreement gets
   one Gemma arbitration. Unresolved ties retain the earlier candidate in a
   recorded, seed-derived order. With multiple candidates, these comparisons
   form a tournament.

Reviewers and audits see the full proof; the final comparisons see assessment
packets rather than multiple full proofs. This keeps their inputs smaller, but
the comparison can inherit mistakes or omissions in those assessments. The
procedure is an experimental model judgment, **not mathematical verification or
an external grade**. `audited_acceptance` also remains a model judgment.

The proof is never repaired during selection. Even when routine completion is
accepted, the exported file remains byte-for-byte identical to the input proof.
Candidate IDs, checkpoint names, external scores and generation seed metadata
are not added to model prompts. Candidate order and per-call seeds are derived
from the selection seed and recorded. This does not guarantee identical GPU
outputs across serving configurations.

A four-candidate assessment uses 20 logical model calls for its first round.
Comparisons and arbitration add at most nine. With three rounds for every
candidate, the maximum is 69 logical calls before retries. Each logical call can
contain several native completion requests. With one extended reasoning extension actually
performed, a logical call uses three generation requests: initial thinking,
continued thinking and one final answer. If all four candidates enter comparison
and no assessment needs another round, that is 26–29 logical calls, or 78–87
generation requests when every call performs its extension, excluding retries
and tokenizer requests. Hitting the thinking cap before an extension reduces the
request count. Wall time and token usage are recorded; changing extended reasoning does not by
itself establish a speed improvement.

## Native extended reasoning

Version **0.3.0** restores native thinking-prefix extended reasoning for the independent selector.
The version 0.2.0 chat-rewrite experiment is identified by research commit
`c66ba49` and its saved output directories; those historical objects are not
guaranteed to be included in a snapshot publication. Use a fresh selection ID for a new
run; existing artifacts are never overwritten. The generation harness and
candidate assessment/comparison procedure are unchanged.

This implements the open-thinking-prefix mechanism described in
[s1 §3.1](https://arxiv.org/html/2501.19393v1#S3.SS1) and its
[reference implementation](https://github.com/simplescaling/s1/blob/main/eval/lm-evaluation-harness/lm_eval/models/vllm_causallms.py).
The role-specific continuation prose is our adaptation, not a result established
by that paper for this selector or these models.

For every review, fusion, audit and comparison call:

```text
render system + user once, with the model's native thinking channel open
  → generate reasoning, stopping at its thinking-end token
  → remove that terminal token from the retained token sequence
  → append the role's continuation inside the same open thinking channel
  → generate more reasoning
  → close thinking once, then generate the structured final response
```

The continuation carries the **exact retained token IDs**. It adds neither a new
user turn nor an earlier final answer. There is no first final answer before the
extended reasoning extension. Separate completion requests can reuse a thinking prefix without
requiring a single persistent generation request.

Gemma uses `<|channel>thought\n … <channel|>`; Qwen uses
`<think>\n … </think>`. The actual server tokenizer must reproduce these
boundaries. Unsupported templates, missing output token IDs, context overflow
and malformed or truncated answers fail explicitly. There is no silent fallback
to the released pipeline's chat-based continuation.

The default forces one continuation when reasoning ends naturally before the
budget is exhausted. The **65,536-token thinking cap is shared across the first
reasoning and its extensions**, not granted separately to each. When the cap is
reached, the client closes thinking and requests the answer; it records that the
cap was hit and how many extensions actually ran. Injected cue/closure tokens
are accounted for separately. A format failure can restart the logical call
once, with compact parser feedback; both attempts remain on disk.

The final structured answer has a separate **8,192-token cap**. The active
options are `--thinking-budget` and `--answer-max-tokens`; the chat experiment's
`--gemma-max-tokens` and `--qwen-max-tokens` are rejected rather than silently
reinterpreted. `--bf-extensions` still defaults to 1, with 0 available for a
no-extension ablation and explicitly requested counts up to 4 supported.

Each role has its own cue in
[`protocols.py`](../harnesses/proof_selector/protocols.py). For example:

> Wait. I should verify that my proposed witness satisfies every hypothesis
> and actually defeats the target claim. I should try to refute my own attack
> using the submitted proof. If no decisive attack survives, I should say so.
> I must distinguish a false objection from a real flaw and finish in the
> original required format.

The other cues respectively recheck the earliest break, critical obligations,
Fusion's mathematical grounds, acceptance, criticism, comparison and arbitration.
They ask for reconsideration in both directions rather than presupposing that a
proof or objection is correct.

## Run after the sampled suite completes

The default input loader requires a **completed 6+3+3 suite with all 48 exported
lane proofs**, including valid earlier-stage fallbacks. It validates the complete
bank before applying `--problem-id`. It checks statement and proof hashes,
producer agreement, completion metadata and source stability. Generation and
selection use different run directories.

After pulling the branch, preflight one problem without writing artifacts or
calling the servers:

```bash
git pull --ff-only
.venv-solver/bin/python -B scripts/select_proofs.py \
  --run-id suite_e2e_20260919_142752 \
  --problem-id imo2026_p1 \
  --selection-seed 0 \
  --dry-run
```

Then run that problem in the background with a fresh selection ID:

```bash
WORKSHOP_SELECTION_ID="selector_$(date +%Y%m%d_%H%M%S)"
mkdir -p .workshop/runs

nohup .venv-solver/bin/python -u -B scripts/select_proofs.py \
  --run-id suite_e2e_20260919_142752 \
  --problem-id imo2026_p1 \
  --selection-id "$WORKSHOP_SELECTION_ID" \
  --selection-seed 0 \
  > ".workshop/runs/$WORKSHOP_SELECTION_ID.log" 2>&1 < /dev/null &

echo $! > ".workshop/runs/$WORKSHOP_SELECTION_ID.pid"
echo "Log: .workshop/runs/$WORKSHOP_SELECTION_ID.log"
```

Omit `--problem-id` to select one proof for **each of the 12 problems**. The
problem order follows the saved suite plan; problems and candidate assessments
run sequentially. Use `--random-selection-seed` instead of `--selection-seed N`
to draw and record one new selection seed. This does not alter the original
generation or sampling seeds.

An existing destination is never reused. Use a new selection ID for a new trial.
SIGINT/SIGTERM stop the selector and record interruption; the model servers stay
running. There is no resume mode in this first version. Partial artifacts remain
available for inspection but do not constitute a completed selection.

Important options:

| Option | Default | Meaning |
| --- | ---: | --- |
| `--max-rounds` | 3 | Maximum review–fusion–audit rounds per candidate |
| `--bf-extensions` | 1 | Maximum forced thinking continuations per call; 0 disables extensions |
| `--thinking-budget` | 65536 | Total generated thinking tokens per attempt |
| `--answer-max-tokens` | 8192 | Separate final-response token limit |
| `--max-input-tokens` | 24576 | Initial templated input cap; excess fails rather than truncates |
| `--max-continuation-input-tokens` | 98304 | Cap for prefixes containing retained reasoning |
| `--attempts` | 2 | Maximum attempts per logical call |
| `--timeout` | 2400 | HTTP timeout in seconds per request |
| `--gemma-endpoint` | `http://127.0.0.1:8030/v1` | Local Gemma server |
| `--qwen-endpoint` | `http://127.0.0.1:8027/v1` | Local Qwen server |

The client also checks the server's actual context limit. It never silently cuts
a proof or review to meet a limit. If an input is too long, inspect the preserved
request before deliberately changing the configured cap.

## Use the already published IMO proofs

The repository already contains 24 baseline final proofs: four candidates for
each of the six IMO 2026 problems. Of these, 22 are R1-C3 proofs and two are
R1-C1 fallbacks. Their mapping is in
[`score_snapshot.json`](public_release/score_snapshot.json), and their exact bytes
are preserved under `docs/public_release/evidence/proofs/`.

Use them immediately as an alternative to waiting for a new generation suite:

```bash
.venv-solver/bin/python -B scripts/select_proofs.py \
  --published-imo --problem-id imo2026_p1 --dry-run

.venv-solver/bin/python -u -B scripts/select_proofs.py \
  --published-imo --problem-id imo2026_p1 \
  --selection-id published_imo_p1_001 --selection-seed 0
```

Omit `--problem-id` to process all six problems. For background execution, use
the `nohup` pattern above with `--published-imo` in place of `--run-id ...`.
Outputs use generation-run label `published_imo2026_baseline`.

The loader reads the snapshot only to bind problem IDs, candidate IDs, final
checkpoint names, proof paths and hashes. It does not open grading records or
provide snapshot scores, tool-rewritten proofs or reference solutions to the
selector. This input bank evaluates selection on the historical published
proofs; it is separate from the new random-seed generation run.

## Outputs and evaluation

```text
.workshop/selections/<generation-run-id>/<selection-id>/
  plan.json                       # source hashes, code/protocol identity, seeds, settings
  status.json                     # suite progress, completion or failure
  REPORT.md                       # selected candidates and selection wall times
  problems/<problem-id>/
    inputs/                       # problem and four unchanged input proof snapshots
    candidates/                   # reviews, fusions, audits and all attempts
    comparisons/                  # paired comparisons and any arbitration
    selection.json                # decisions, uncertainty, token usage and duration
    selected_proof.md              # exact bytes of the chosen input proof
```

Each model call preserves requests, raw responses, token IDs, tokenizer checks,
reasoning segments, final structured responses, actual extended reasoning extensions and token
usage. Initial protocol reuse is read-only and checked against pinned source
hashes; it does not import legacy stage runners or install their wrappers.

The existing `grade_sampled_suite.py` still grades all 48 generation outputs. It
does not run this selector or replace the published Average/Oracle@4 metrics.
To evaluate selection later, freeze the selector choices first, then associate
each selected candidate ID and proof hash with its separately produced grade.
Selection time is additional to the already recorded generation time.

## Standalone input bank

`--input-manifest path/to/manifest.json` supports a separate bank of exactly four
proofs per problem, without requiring the sampled-suite runner. Paths are relative
to the manifest directory and must stay within it; hashes cover the exact file
bytes. A problem file can be plain text or JSON containing `claim`, `problem` or
`statement`. Additional JSON fields, such as references or scores, are not put in
the model prompt.

```json
{
  "schema": "proof-selector-input-v1",
  "run_id": "my-proof-bank",
  "problems": [{
    "problem_id": "problem-1",
    "problem_path": "problem.txt",
    "problem_file_sha256": "<SHA256 of problem.txt bytes>",
    "candidates": [
      {"candidate_id": "a", "proof_path": "a.md", "proof_file_sha256": "<SHA256>"},
      {"candidate_id": "b", "proof_path": "b.md", "proof_file_sha256": "<SHA256>"},
      {"candidate_id": "c", "proof_path": "c.md", "proof_file_sha256": "<SHA256>"},
      {"candidate_id": "d", "proof_path": "d.md", "proof_file_sha256": "<SHA256>"}
    ]
  }]
}
```

```bash
.venv-solver/bin/python -B -m harnesses.proof_selector \
  --input-manifest path/to/manifest.json --dry-run
```
