# Single-GPU reproduction check from a normal terminal

Run generation directly from a Linux shell. It does not need a Codex session,
hosted inference, or an agent monitoring the job. Grading is a separate command
that invokes the authenticated Codex CLI. The existing published benchmark
results, using Qwen-only final selection, are the baseline; this small run checks
reproduction.

The commands below assume the [local environment and models](local_reproduction.md)
are installed: a 96 GB GPU, the pinned BF16 checkpoints, Python 3.11.15,
approximately 128 GB host RAM and local SSD backing storage for model switching.
Run from the repository root. If other experiments are running, let them finish
before using the same model servers and GPU.

## 1. Update and start the model servers

```bash
git pull --ff-only
.venv-solver/bin/python -B harnesses/proof_workshop/run.py --release 1.12.0 --verify
.venv-solver/bin/python -B scripts/local_servers.py status
.venv-solver/bin/python -B scripts/local_servers.py start --single-gpu 0 --timeout 1800
```

The start command waits for readiness; both server processes run in the
background. Matching managed single-GPU servers are reused. If the manager
reports an existing two-GPU configuration, stop those managed servers after
their experiments finish, then repeat the single-GPU start command:

```bash
.venv-solver/bin/python -B scripts/local_servers.py stop
.venv-solver/bin/python -B scripts/local_servers.py start --single-gpu 0 --timeout 1800
```

## 2. Inspect the six-problem plan, then launch

This example samples **2 IMO + 2 Basic + 2 Advanced** problems with problem
sampling seed **42**. It selects IMO P1/P6, Basic 001/024, and Advanced 008/009.
All six have complete four-lane, twice-graded baseline records.
No generation-seed option is supplied: the original fixed generation settings
are retained (`raw_seed_offset=0`, `v263-v290:problem-only`).

```bash
WORKSHOP_RUN_ID="check1gpu_$(date +%Y%m%d_%H%M%S)"
mkdir -p .workshop/runs
printf '%s\n' "$WORKSHOP_RUN_ID" > .workshop/runs/last_single_gpu_check.txt
git rev-parse HEAD > ".workshop/runs/$WORKSHOP_RUN_ID.commit"

.venv-solver/bin/python -B scripts/run_single_gpu.py \
  --benchmark all --imo-count 2 --basic-count 2 --advanced-count 2 \
  --sample-seed 42 --gpu 0 --run-id "$WORKSHOP_RUN_ID" --dry-run \
  > ".workshop/runs/$WORKSHOP_RUN_ID.plan.json"

cat ".workshop/runs/$WORKSHOP_RUN_ID.plan.json"
```

The plan must show `problem_count: 6`, `candidates_per_problem: 4` and
`release: "1.12.0"`. Dry-run does not contact the servers or create generation
directories. Start the actual run with the same arguments:

```bash
nohup .venv-solver/bin/python -u -B scripts/run_single_gpu.py \
  --benchmark all --imo-count 2 --basic-count 2 --advanced-count 2 \
  --sample-seed 42 --gpu 0 --run-id "$WORKSHOP_RUN_ID" \
  > ".workshop/runs/$WORKSHOP_RUN_ID.log" 2>&1 < /dev/null &

echo $! > ".workshop/runs/$WORKSHOP_RUN_ID.pid"
echo "Run: $WORKSHOP_RUN_ID"
echo "Log: .workshop/runs/$WORKSHOP_RUN_ID.log"
```

SSH can be disconnected after launch. No Codex monitoring or automatic Git
update is involved. Each problem retains four candidate lanes and the existing
draft → refinement 1/2/3 → replacement audit → cross-lane selection workflow.
The scheduler admits work across all selected problems; the recorded limits
remain Gemma 8, Qwen 12 and comparison 12. An eligible earlier proof can remain
the lane final under the existing fallback/audit policy.

## Other problem selections

Use a fresh `--run-id` for each run. Combine the following options with the
same runner, `--gpu`, and the background-launch pattern above.

| Selection | Options |
|---|---|
| All six IMO problems | `--benchmark imo2026` |
| Two from each set | `--benchmark all --imo-count 2 --basic-count 2 --advanced-count 2 --sample-seed 42` |
| Six IMO plus three from each ProofBench set | `--benchmark all --imo-count 6 --basic-count 3 --advanced-count 3 --sample-seed 42` |
| Five Basic problems only | `--benchmark imo-proofbench/basic --basic-count 5 --sample-seed 42` |
| Hand-picked problems across sets | `--benchmark all --problem-id imo2026_p4 --problem-id PB-Basic-004 --problem-id PB-Advanced-018` |
| All 66 problems | `--benchmark all` |

When any count is supplied, omitted counts mean zero. Counts and explicit
problem IDs cannot be combined. With counts, an omitted sampling seed defaults
to 1729. `--random-sample-seed` draws and records a sampling seed instead.

Generation seeds are independent of problem sampling. Omit generation-seed
flags for the published fixed settings, use `--generation-seed N` for an
explicit seed, or `--random-generation-seed` to draw one seed shared by the
selected problems. **`--generation-seed 0` is not the original default**: it
also selects the `workshop-generation:0` namespace. Random-mode dry-run and
execution make separate draws; copy the reported seed into the corresponding
explicit seed option if the inspected plan must be repeated exactly.

### Another six problems after the current run

`scripts/run_next_single_gpu.py` excludes every problem in the specified
previous single-GPU plan, samples from the remaining sorted catalogs, and
delegates generation to the existing `run_single_gpu.py`. Defaults are two
problems from each set, sampling seed 43, and the original fixed generation
settings. Counts, sampling seed, GPU and an explicit generation seed can be
changed through the wrapper's options; it does not change the harness.

For the first run shown above, the next selection is IMO P2/P3, Basic 025/027,
and Advanced 005/017. The exclusion applies to the specified `--after-run`.
The selected IDs, excluded IDs, source-plan hash and sampling seed are saved in
`.workshop/runs/<new-run-id>.followup.json`.

Use `--dry-run` to inspect the selection without writing files, waiting or
contacting model servers. Without `--wait`, the wrapper refuses to start while
the previous run or GPU scheduler is active. With `--wait`, it can be launched
now in the background and starts after every previous problem exits and the
old scheduler releases its lock:

```bash
WORKSHOP_PREVIOUS_RUN_ID="$(cat .workshop/runs/last_single_gpu_check.txt)"
WORKSHOP_NEXT_RUN_ID="check1gpu_next_$(date +%Y%m%d_%H%M%S)"
mkdir -p .workshop/runs
printf '%s\n' "$WORKSHOP_NEXT_RUN_ID" > .workshop/runs/last_next_single_gpu_check.txt

nohup .venv-solver/bin/python -u -B scripts/run_next_single_gpu.py \
  --after-run "$WORKSHOP_PREVIOUS_RUN_ID" \
  --run-id "$WORKSHOP_NEXT_RUN_ID" --sample-seed 43 --gpu 0 --wait \
  > ".workshop/runs/$WORKSHOP_NEXT_RUN_ID.log" 2>&1 < /dev/null &

echo $! > ".workshop/runs/$WORKSHOP_NEXT_RUN_ID.pid"
echo "Next run: $WORKSHOP_NEXT_RUN_ID"
echo "Log: .workshop/runs/$WORKSHOP_NEXT_RUN_ID.log"
```

Keep the existing model servers running. The wrapper does not start or restart
them. SSH may disconnect after this launch; the waiting process and subsequent
generation run without a Codex monitor or an automatic Git update. A previous
`completed_with_failures` is allowed once all problems have exited: an original
P1 format failure does not prevent a disjoint new run. A failed/interrupted
runner or an inconsistent terminal status stops the wrapper for inspection.
No previous failure record is modified or treated as a successful result.

The next run uses the same log/status/output layout and separate grading
command described below. For its run ID, read
`.workshop/runs/last_next_single_gpu_check.txt`; the first run's pointer is kept.

## 3. Check progress and completion

After reconnecting, restore the saved run ID:

```bash
WORKSHOP_RUN_ID="$(cat .workshop/runs/last_single_gpu_check.txt)"
tail -n 50 -F ".workshop/runs/$WORKSHOP_RUN_ID.log"
```

Ctrl-C exits this log viewer without stopping the background run. The detailed
state and per-problem logs are separate:

```bash
cat ".workshop/single_gpu/$WORKSHOP_RUN_ID/status.json"
cat ".workshop/single_gpu/$WORKSHOP_RUN_ID/scheduler_status.json"
tail -n 50 ".workshop/single_gpu/$WORKSHOP_RUN_ID/logs/imo2026_p1.log"
```

`status.json` must report `completed`, with every job's `returncode` equal to
zero. Final proofs and selections for each problem are stored under
`benchmarks/<benchmark>/results/<run-id>_<problem-id>/generation/run/`.
Keep the intermediate outputs, plan, status, environment snapshots and logs.
If the run fails or has missing lanes/selection, preserve the failure; it has
not passed the reproduction check. The runner does not retry whole proofs to
improve a score.

## 4. Grade separately through Codex CLI

Only this phase requires an authenticated `codex` CLI with access to
`gpt-5.6-sol`. Install `pdftotext` if references must be prepared, and follow
the [external reference setup](public_release/grading/README.md#external-imo-reference-setup).
The explicit `--download-references` option below obtains the hash-pinned
grading inputs; omit it when those inputs already exist locally.

The adapter reads the actual scheduler plan, so it supports the other problem
selections above as well. It validates completion, statements, proof hashes,
seed settings and saved selector winners before sending any grading request.
IMO uses Strict Olympiad v2; Basic/Advanced use IMOBench B.5. Every new final
proof is graded twice. For six problems this is **24 proofs / 48 judgments**.
Existing baseline proofs are not re-graded. References and previous grades
are never passed to generation; previous grades are also excluded from the
new evaluator's tasks.

```bash
WORKSHOP_RUN_ID="$(cat .workshop/runs/last_single_gpu_check.txt)"
WORKSHOP_GRADING_ID="grading_$(date +%Y%m%d_%H%M%S)"
printf '%s\n' "$WORKSHOP_GRADING_ID" > ".workshop/runs/$WORKSHOP_RUN_ID.grading_id"

.venv-solver/bin/python -B scripts/grade_single_gpu_run.py \
  --run-id "$WORKSHOP_RUN_ID" --grading-id "$WORKSHOP_GRADING_ID" \
  --workers 4 --download-references --dry-run
```

After preflight succeeds, start grading in the background:

```bash
nohup .venv-solver/bin/python -u -B scripts/grade_single_gpu_run.py \
  --run-id "$WORKSHOP_RUN_ID" --grading-id "$WORKSHOP_GRADING_ID" --workers 4 \
  > ".workshop/runs/$WORKSHOP_RUN_ID.$WORKSHOP_GRADING_ID.log" 2>&1 < /dev/null &

echo $! > ".workshop/runs/$WORKSHOP_RUN_ID.$WORKSHOP_GRADING_ID.pid"
```

The Python adapter invokes the existing isolated `codex exec` graders. No
interactive Codex agent needs to stay open. Separate pass directories retain
both raw evaluator responses and grades; successful grades are not shared
between passes. Failed evaluator requests follow the existing bounded retry
policy. Missing or invalid grades do not become zero scores.

### Grade a selection recovered from an explicit `Winner: Proof A/B`

An offline `--collect-only` can recover an unambiguous saved comparison while
leaving the original runner exit code 1 and `completed_with_failures` intact.
The grading adapter rejects that run by default. After recollection, add
`--allow-recovered-selection` to **both** the preflight and grading commands
above to grade the recovered portfolio.

This option requires every problem to have exited and every lane to have a
saved final proof. For a failed job it verifies that inference finished, the
original failure was an incomplete selection, the four lane finals are
unchanged, and all 24 saved comparisons are bound to the original prompts,
proofs and response files. The only admitted repair is the existing mechanical
interpretation of `Winner: Proof A/B` as `Winner: A/B`. It recomputes the tally
and checks it against the saved recovered selection, without model calls or
generation-file edits. Other failures or incomplete selections still stop
grading before any reference download or evaluator request.

The grading manifest, summary and report retain the original failure and list
the recovered cases. Scores from these saved proofs can be compared, but the
original run is not relabeled as a clean end-to-end pass. Keep its original
status and completion files; do not edit their exit codes to bypass preflight.

## 5. Read the comparison

```bash
WORKSHOP_RUN_ID="$(cat .workshop/runs/last_single_gpu_check.txt)"
WORKSHOP_GRADING_ID="$(cat ".workshop/runs/$WORKSHOP_RUN_ID.grading_id")"
cat "benchmarks/reports/${WORKSHOP_RUN_ID}_reproduction/$WORKSHOP_GRADING_ID/REPORT.md"
```

`summary.json` alongside the report records the original and new two-pass
scores, per-lane changes, selected stages, proof-text identity, selected-lane
changes and generation wall time. The report compares Average, Oracle@4 and
Selector@1 for each problem. The mean is taken per proof before computing an
oracle or lane average. A missing baseline lane remains absent and its smaller
denominator is shown; the recommended six-problem selection has no such gaps.

The [baseline manifest](reproduction/single_gpu_baselines.json) pins the
[Qwen-only scorecard](results/qwen_selection_20260928/SCORECARD.json) for all 66
problems. It reuses the archived proofs and two grades per proof and changes
only the final selected lane using saved Qwen votes and the original seeded tie
order. Thus new Qwen-only runs are compared with the same final selection
policy. The report records both policies; a resumed older run keeps its saved
Gemma+Qwen selection and is explicitly marked as a different-policy comparison.
Existing comparison reports retain their original baseline and are not rewritten.

This is a check against the saved published results. Same score, same proof
and successful execution are separate observations. Generation elapsed time
includes waiting for model switches and other problems; it is not GPU compute
time. The report leaves the original scorecards and published result tables
unchanged.
