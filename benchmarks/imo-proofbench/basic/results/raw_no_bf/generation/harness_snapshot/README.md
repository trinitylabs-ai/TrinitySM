# Gemma 4: four raw proofs with MTP=4, without budget forcing

This standalone harness generates four raw drafts per problem using
`google/gemma-4-31B-it` in BF16. It checks the actual local vLLM listening process
for `method=mtp`, `num_speculative_tokens=4`, and the `gemma4` reasoning parser
before submitting each problem.

Each candidate makes **one chat-completions request** containing the original
system prompt and problem prompt. Thinking remains enabled. The request respects
EOS, sets `min_tokens=0`, and stops when the model finishes or reaches its output
cap. There are no follow-up messages, budget-forcing continuations, cap recovery,
automatic retries, or seed changes after a failure.

The output is the raw generation stage. Lazy checks, proof repairs, external
grading, and Codex calls are not part of this harness. The previous harness and
its results are separate.

## Frozen generation defaults

| Candidate | Temperature | Base seed |
|---|---:|---:|
| `t10_r01` | 1.0 | 2360094352 |
| `t10_r02` | 1.0 | 2367214500 |
| `t07_r01` | 0.7 | 3233582896 |
| `t07_r02` | 0.7 | 220229344 |

- Four concurrent requests within a problem; problems run sequentially.
- `top_p=0.95`, `top_k=64`, output cap **65,536 tokens**.
- Default endpoint: `http://127.0.0.1:8030/v1`.
- Default request timeout: 14,400 seconds.
- The original problem-neutral prompts are copied byte-for-byte into `prompts/`.
- The original per-problem seed derivation is preserved. Problems are numbered
  by sorted ID across the input directory **before** applying a selection filter.
- `--raw-seed-offset` defaults to zero. To match a previous attempt with an
  offset, supply that attempt's recorded offset explicitly.

The client uses only the Python standard library. It does not import the earlier
generation runtime. The server must already be running locally; its model and
MTP settings are verified, rather than inferred from an endpoint name.

## Run

From `/opt/proof-workshop`, stage all 30 Basic problems without contacting the
server:

```bash
python -u -B harnesses/gemma4_raw_mtp4_no_budget_forcing/run.py \
  --output-dir runs/basic_raw_mtp4_no_bf_run01
```

Generate from that staged configuration:

```bash
python -u -B harnesses/gemma4_raw_mtp4_no_budget_forcing/run.py \
  --output-dir runs/basic_raw_mtp4_no_bf_run01 \
  --resume --execute-models
```

For a fresh output directory, `--execute-models` can be used directly. Select
individual problems with repeatable `--problem-id PB-Basic-001` arguments. Supply
`--problem-dir PATH` for a different directory of statement-only JSON files.
Each file must contain exactly `problem_id` and `problem` (or `claim`). Reference
answers, grading guidelines, and other auxiliary fields are rejected.

Optional controls: `--endpoint`, `--max-tokens`, `--timeout-sec`, and
`--raw-seed-offset`. Changing any input, prompt, code, or generation setting
requires a new output directory. A dry run can be resumed with execution enabled.

## Results and progress

The runner prints progress after each completed request and every 60 seconds
while waiting. Inspect `status.json` or `summary.json`, for example:

```bash
watch -n 10 'python -m json.tool runs/basic_raw_mtp4_no_bf_run01/status.json'
```

Each `problems/PROBLEM_ID/candidates/CANDIDATE_ID/` contains:

- `request.json`: the exact generation payload.
- `request_started.json`: the durable marker that prevents accidental retries.
- `raw_response.json`: the server response, including usage and finish reason.
- `reasoning.txt`: returned reasoning, saved separately from the final content.
- `draft_proof.md`: returned final content, when nonempty.
- `result.json`: state, hashes, timing, server identity, and request counts.

States are `completed`, `truncated`, `reasoning_only`, `empty_response`, `failed`,
or `interrupted`. `completed` means generation ended with nonempty final content;
it does not certify mathematical correctness. At the cap, returned proof text is
preserved and marked `truncated`. Reasoning is never substituted for a missing
final answer.

Failures in one lane do not stop the other lanes or subsequent problems. Resume
validates and reuses recorded outcomes, including failures and truncations. An
interrupted request with a saved response is recovered locally; one without a
saved response remains flagged instead of being submitted again. Explicitly use
a new output directory for another generation attempt.

Exit codes: `0` for a dry run or all generations completed normally; `2` when
generation finished with flagged outcomes; `1` for configuration or integrity
errors. Live server checks are recorded in `server_verifications/`.

## Split an existing queue across two GPUs

`split_run.py` prepares two disjoint halves using the unchanged generation runner.
The source runner must first finish its active batch and release its run lock.
Both local Gemma servers must already be running with BF16 and MTP=4.

```bash
python -B harnesses/gemma4_raw_mtp4_no_budget_forcing/split_run.py \
  --source-run runs/basic_raw_mtp4_no_bf_run01 \
  --output-dir runs/basic_raw_mtp4_no_bf_dual \
  --gpu1-endpoint http://127.0.0.1:8031/v1

tmux new-session -d -s raw-no-bf-gpu0 \
  'bash /opt/proof-workshop/runs/basic_raw_mtp4_no_bf_dual/gpu0/launch.sh'
tmux new-session -d -s raw-no-bf-gpu1 \
  'bash /opt/proof-workshop/runs/basic_raw_mtp4_no_bf_dual/gpu1/launch.sh'

python -u -B harnesses/gemma4_raw_mtp4_no_budget_forcing/split_run.py \
  --output-dir runs/basic_raw_mtp4_no_bf_dual --monitor
```

Preparation makes no model calls. It preserves global problem numbering and
verifies every generation payload against the source before importing completed
outcomes. Saved source candidate files remain intact. The original run receives
a `continuation.json` pointer to the split run; use the generated shard launchers
to continue. Do not restart the original queue alongside the shards.

GPU0 retains the source endpoint and receives the first half; GPU1 receives the
second half. Each shard has its own `worker.log`, `status.json`, and `summary.json`.
The monitor updates aggregate `status.json` and `summary.json` every 15 seconds
and exits when both shards finish. It can run in a separate tmux session.

## Validation

```bash
python -B -m pytest -q -p no:cacheprovider \
  harnesses/gemma4_raw_mtp4_no_budget_forcing/test_run.py \
  harnesses/gemma4_raw_mtp4_no_budget_forcing/test_split_run.py
```

Tests cover the frozen prompt and seed policy, exactly four requests per problem,
single-turn payloads, truncation, reasoning-only output, failed requests, resume,
crash recovery, input and artifact integrity, and verification of the actual
MTP=4 listening process.
Split tests also cover disjoint coverage, unchanged request payloads and cached
proofs, prevention of duplicate generation, source locking, and aggregate status.
