# Local reproduction and separate grading

The release supports two operations. **Report reproduction** checks saved
artifact hashes, proof-to-grade bindings and score arithmetic, then prints the
published score tables without any network access. **Fresh generation** runs
Gemma and Qwen on one or two local GPUs and saves new proofs. Neither operation needs
Codex, a hosted inference account or an external grading call.

An optional third operation, [grading a completed sampled suite](#grade-a-completed-sampled-suite),
uses a separate authenticated Codex CLI and hosted evaluator. It is never
started by the generation scripts.

## Recompute the published result

From the repository root, with Python 3.9 or later:

```bash
python3 -B scripts/reproduce.py
```

This verifies 264 lane records, 263 selected scores, the original 240 Basic raw
grades, 718 current ProofBench ablation selections, two-pass IMO evidence and
the input/rewrite bindings for seven retained experimental tool examples.
It recomputes the core matrices, Basic, Advanced and IMO ablations,
and per-proof tool tables using only the standard library. The grades
are the saved historical model judgments. This command checks evidence integrity
and consistency; it does not verify mathematical correctness, generate new proofs
or rerun external grading.

## Install local generation dependencies and models

The recorded configuration uses Linux and Python **3.11.15**. The original
layout has two 96 GB GPUs, with BF16 Gemma and Qwen resident on separate GPUs.
The final ProofBench run also used [one 96 GB GPU with model switching](#one-96-gb-gpu-with-model-switching),
approximately 128 GB system RAM, and file-backed weight offload on local storage.
These are observed configurations, not measured minimums. Install GPU drivers first.
Use a **final Python 3.11 release**, preferably 3.11.15. Check `python3.11 -VV`
before setup: some distribution packages provide the old `3.11.0rc1` prerelease.
The installer rejects prerelease interpreters, including those in existing
virtual environments. See [Python environment recovery](#replace-a-prerelease-python-environment).

```bash
python3.11 scripts/setup_environment.py --install --download-models
```

The installer uses [requirements-solver.txt](../requirements-solver.txt) and
[requirements-serving.txt](../requirements-serving.txt), and downloads the
three [pinned model revisions](models.md). The assistant model is included.
No weights or installed environments are distributed with this repository.
If a model requires provider access approval or Hugging Face authentication,
complete that before downloading; the installer does not log in for you.

The installer checks both virtual environments and attempts to repair missing
or unusable `pip` with Python's bundled `ensurepip` after an interrupted setup.
A Debian/Ubuntu system interpreter needs the matching `python3.11-venv`
package, but installing that package alone does not establish that the Python
interpreter is a final release. The uv-managed interpreter below includes venv
support.

The requirements pin distribution versions. The recorded vLLM build and CUDA
stack are documented in [ENVIRONMENT.md](../ENVIRONMENT.md); ordinary package
installation is not a guarantee of identical binary builds or GPU behavior.
Installing dependencies and downloading models needs network access. Subsequent
model serving uses offline loading.

## Replace a prerelease Python environment

If `.venv-serving/bin/python -VV` reports `3.11.0rc1`, replace both virtual
environments with a final Python 3.11 interpreter. A reported startup failure
loaded the Qwen weights successfully and then segfaulted immediately after
`Dynamo bytecode transform`. Aligning Python with the recorded 3.11.15 version
is the first recovery step; it is not proof that every compiler crash has the
same cause.

From the repository root, first update and stop the managed servers. Continue
only when `stop` succeeds:

```bash
git pull --ff-only
python3.11 scripts/local_servers.py stop
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and the
[specific Python version](https://docs.astral.sh/uv/guides/install-python/).
This uses a user-owned Python installation, without replacing system Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$HOME/.local/bin" sh
"$HOME/.local/bin/uv" python install 3.11.15
WORKSHOP_PYTHON="$("$HOME/.local/bin/uv" python find --managed-python 3.11.15)"
"$WORKSHOP_PYTHON" -VV
```

After that command reports Python 3.11.15, back up the existing environments
and recreate them. Run these commands in the same shell. Existing `.models`
files stay in place; `--install` does not download model weights. Pip can
reuse its cached package downloads:

```bash
mkdir -p .workshop
WORKSHOP_ENV_BACKUP="$(mktemp -d .workshop/python-env-backup.XXXXXX)"
mv .venv-solver .venv-serving "$WORKSHOP_ENV_BACKUP/"
"$WORKSHOP_PYTHON" scripts/setup_environment.py --install
.venv-solver/bin/python -VV
.venv-serving/bin/python -VV
```

If a command fails, resolve its error before continuing. Keep the backup until
the new servers work. Once setup completes, start the servers with the new
interpreter:

```bash
.venv-solver/bin/python scripts/local_servers.py start --timeout 1800
```

## Start the two local servers

The two model processes can use separate GPUs or share one GPU through sleep/wake.
Choose one of the following layouts; both use the frozen **B 1.12.0** harness.

### Two GPUs

Use one terminal for setup, background servers and harness execution:

```bash
python3 scripts/local_servers.py start --gemma-gpu 0 --qwen-gpu 1
```

The background manager requires Linux with `/proc` and pidfd support (kernel
5.3 or later). It checks this before launching processes.

This launches Gemma on **GPU 0 / port 8030** and Qwen on **GPU 1 / port 8027**
through the existing `serve_models.py` launcher. It preserves the recorded
BF16, MTP, context and compatibility settings. Both servers run in the
background. The command checks each `/v1/models` endpoint for the expected
model and returns successfully only when both are ready.

The default startup timeout is 900 seconds. Select different GPUs, a longer
timeout or the model-cache path used during setup with:

```bash
python3 scripts/local_servers.py start \
  --gemma-gpu 0 --qwen-gpu 1 --timeout 1800 --model-dir .models
```

### One 96 GB GPU with model switching

This is the serving and scheduling mode used by the final ProofBench continuation.
The [recorded continuation](results/proofbench_single_gpu_20260926/README.md)
retained 16 previously processed portfolios and admitted the remaining 44
portfolios on GPU 0 after GPU 1 went offline.

```bash
python3 scripts/local_servers.py start --single-gpu 0 --timeout 1800
python3 scripts/run_single_gpu.py \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --run-id local_basic001_one_gpu
```

The manager loads Gemma, sleeps it, loads Qwen, sleeps it, and wakes Gemma.
Only one model occupies its full GPU allocation at a time. Sleep level 1 moves
weight bytes into file-backed CPU tensors; wake restores those same bytes.
The recorded compatibility adapter uses reclaimable mapped files instead of
pinned CPU backup allocations. Both model processes keep their CUDA contexts.
Gemma reserves **28 GiB for KV cache** to leave working space for long extended reasoning
prefill and Qwen's sleeping context. Model precision and model revisions stay
the same.

Use a local SSD for the swap directory. Allow roughly **120 GB of free backing
storage, plus headroom**, separate from the model-download cache. The recorded
host had approximately **125.47 GiB RAM**. These are practical starting points
from the run, not measured minimums. Temporary weight files are unlinked after
mapping and released on wake or process exit; their occupied space remains
visible to filesystem free-space accounting while mapped. Select the GPU and
storage path explicitly if needed:

```bash
python3 scripts/local_servers.py start --single-gpu 0 \
  --swap-dir /path/to/local-ssd/workshop-swap --timeout 1800 --model-dir .models
```

`run_single_gpu.py` admits one worker per selected problem. The broker drains
ready work for the awake model across those problems and switches after active
calls finish and a 20-second quiet period. The final recorded admission limits
are **Gemma: 8 proof calls**, **Qwen: 12 proof calls**, and **12 comparison
calls**. A complete logical extended reasoning call keeps its lease across continuations.
Admission happens before the existing inference deadline starts, including the
selector's logical deadline. No extra proof retries or grading calls are added.

Use this runner while the servers are in switching mode; the ordinary
`reproduce.py generate` runner does not schedule sleeping models. To inspect
the plan without launching processes, contacting GPUs or creating files:

```bash
python3 scripts/run_single_gpu.py --benchmark imo-proofbench/basic \
  --run-id local_basic_all_one_gpu --dry-run
```

Remove `--dry-run` to execute. Omit `--problem-id` for the entire benchmark,
repeat it to select multiple problems, or use `--benchmark all` for all three
benchmark sets. `--generation-seed N` records an explicit seed; omitting it
preserves the original fixed settings.

For per-set sampling, use `--benchmark all --imo-count 2 --basic-count 2
--advanced-count 2 --sample-seed 42`. Omitted counts select zero once any count
is supplied. Problem sampling and generation seeds are separate; each supports
an explicit seed or its `--random-...-seed` option. See the
[standalone execution and separate grading guide](single_gpu_check.md) for
background launches, flexible selections, logs and baseline comparisons.

Each problem receives a unique run ID `RUN_ID_PROBLEM_ID` under its benchmark's
`results/` directory. The scheduler plan, adapter hashes, outcomes, per-problem
logs and model-switch journal are in `.workshop/single_gpu/RUN_ID/`:

```bash
cat .workshop/single_gpu/local_basic001_one_gpu/status.json
cat .workshop/single_gpu/local_basic001_one_gpu/scheduler_status.json
tail -f .workshop/single_gpu/local_basic001_one_gpu/broker.log
```

Ctrl-C in the runner stops admission and forwards interruption to its problem
workers, which retain their completed artifacts. The runner owns its broker;
the model servers remain managed by `local_servers.py`. If a server becomes
unhealthy, new admissions pause while the broker retries its health probe.
The runner permits up to 180 seconds for automatic recovery, so first-use
kernel compilation does not abort the run after a single delayed probe.
Existing calls retain their original inference deadlines. An unrecovered
server or a failed model switch stops the run with an error; inspect the logs
before restarting. The runner does not automatically restart servers
or replay completed responses from the private recovery job. Use fresh run IDs
for new attempts; saved runs retain the existing collection/recovery workflow.

### Status, logs and shutdown for either layout

The manager records local process state and appends server logs under
`.workshop/servers/`. Repeating `start` reuses matching managed servers.
It does not adopt or stop unrelated servers occupying the same ports. On
startup failure, timeout or Ctrl-C, it stops the servers newly started by that
invocation and preserves previously running managed servers.

Check status, inspect logs, and stop the managed servers when finished:

```bash
python3 scripts/local_servers.py status
tail -f .workshop/servers/gemma.log .workshop/servers/qwen.log
```

Ctrl-C exits the log viewer; it does not stop the background servers. Stop them
explicitly with:

```bash
python3 scripts/local_servers.py stop
```

`start --dry-run` prints the planned commands without starting servers or
creating state files. Servers load local checkpoints and do not download
missing files. If setup used `--model-dir`, pass the same path to `start`.

Finish or interrupt generation before stopping servers or changing layouts.
`status` shows which single-GPU model is awake and which has its weights offloaded.
Existing managed servers must match the requested GPU layout and swap directory.

For foreground operation **on two separate GPUs**, the original commands remain available. Run each
in a separate terminal and leave both running while using a third terminal for
generation:

```bash
python3 scripts/serve_models.py --model gemma
```

```bash
python3 scripts/serve_models.py --model qwen
```

With foreground operation, wait for both servers to finish loading before
starting generation; these individual launchers do not wait for one another.
Add `--dry-run` to either command to inspect its settings. Ctrl-C stops that
foreground server.

## Ablation: four raw proofs without extended reasoning

The official raw-generation entry point is [scripts/generate_raw.py](../scripts/generate_raw.py).
It uses the evaluated raw runner and byte-identical Workshop Draft prompts.
Each problem gets four candidates: two at temperature 1.0 and two at 0.7,
with top-p 0.95, top-k 64, thinking enabled and a 65,536-token output limit.
Both raw ablation configurations enable native thinking. Here “without extended
reasoning” means a single pass; “with extended reasoning” adds forced continuation
after the initial answer. It is not a thinking-on versus thinking-off comparison.
Each candidate makes **one request** that respects EOS. There are no forced
continuations, token-cap recovery, retries, lazy checks, reviews or grading calls.
Truncated, empty and failed outputs remain flagged; reasoning is not substituted
for a missing proof.

After environment setup, start **only Gemma** for this experiment:

```bash
python3 scripts/serve_models.py --model gemma
```

In another terminal, prepare one problem without model calls:

```bash
python3 -B scripts/generate_raw.py \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --output-dir runs/basic001_raw_no_bf
```

Then generate its four raw proofs from those prepared requests:

```bash
python3 -B scripts/generate_raw.py \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --output-dir runs/basic001_raw_no_bf --resume --execute-models
```

Omit `--problem-id` to process the whole selected benchmark. Use
`--benchmark imo-proofbench/advanced` or `--benchmark imo2026` for the other
sets. For a fresh output directory, `--execute-models` can be used directly.
Each proof is saved as
`OUTPUT/problems/PROBLEM_ID/candidates/CANDIDATE_ID/draft_proof.md`.
`summary.json` records all outcomes, hashes and request counts. Resume validates
existing requests and outcomes without resubmitting failed or truncated calls.
Use a new output directory for an intentional new attempt.

### Two-GPU ablation queue

Use one Gemma server per GPU, in separate terminals. Both need the pinned
Gemma checkpoint and MTP assistant; Qwen is not used by raw generation.

```bash
python3 scripts/serve_models.py --model gemma --gpu 0 --port 8030
python3 scripts/serve_models.py --model gemma --gpu 1 --port 8031
```

These commands each occupy their terminal; run the queue in a third terminal.
Prepare all **30 Advanced problems, six IMO 2026 problems, and Basic-009 and
Basic-026** without model calls:

```bash
python3 -B scripts/run_raw_ablation.py \
  --output-dir runs/advanced_imo_basic_matched_no_bf
```

Start or resume the prepared queue:

```bash
python3 -B scripts/run_raw_ablation.py \
  --output-dir runs/advanced_imo_basic_matched_no_bf --execute-models
```

The queue assigns 19 problems to each server, with four concurrent candidate
requests within a problem: **38 problems / 152 requests** in total. Each server
processes its problems sequentially. Advanced and IMO use seed offset zero.
Basic-009 and Basic-026 use offsets **1592974400** and **2000006**, read from
their manifests for runs with extended reasoning, so all four candidate seeds match those runs.
Problem numbering is derived from the complete benchmark before filtering.
`plan.json` records the split and seed provenance; `worker_0.json`,
`worker_1.json` and each problem's `summary.json` record progress and outcomes.
The queue restarts from saved request outcomes without repeating completed work.

Fresh raw proofs are ungraded. The published ablation includes separately
collected B.5 grades for the Advanced cohort without extended reasoning and the two Basic reruns;
IMO 2026 uses strict v2. Future raw runs are not guaranteed to reproduce the
historical proof text or grades.

## Generate proofs

After both servers are ready:

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --run-id local_basic001_001
```

The same script supports IMO 2026. For P1:

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo2026 --problem-id imo2026_p1 \
  --run-id local_imo2026_p1_001
```

Problem IDs run from `imo2026_p1` through `imo2026_p6`. To generate proofs for
all six problems, omit the problem selector:

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo2026 --run-id local_imo2026_all_001
```

Use a new run ID for every new attempt. The script invokes the existing
experiment launcher with an explicit solver interpreter and loopback endpoints.
Generation with `--dry-run` also creates a run directory; use a separate new
run ID for the subsequent model execution.
Proofs, checkpoints and provenance appear under
`benchmarks/<benchmark>/results/<run-id>/generation/run/`. Runtime logs stay
local and are excluded from Git.

For all 66 problems, omit `--problem-id` and use `--benchmark all`. Each dataset
gets its own run directory. This is a substantial inference run. Add `--dry-run`
for a model-free preflight after installing the solver environment.

The official script runs **Draft**, followed by up to three refinement passes,
and exports each lane's last completed proof, when available. If execution stops
early, completed proofs from earlier stages remain eligible for submission.
Each pass uses the preceding proof. During a normal run, no manual continuation
or later resolver stage is needed.
The public project version is **TrinitySM 0.1.0-rc.1**. The composite pins
default frozen implementation **B 1.12.0** and records both identities, the public controller
and final-pass driver hashes. Final proofs are under `generation/run/proofs/`;
`generation/run/final_results.json` records completion and failure per lane,
separately from whether a completed proof is available for submission.

Earlier A/B engines remain available for historical replay; `--list-releases`
lists the registered versions, and `--release VERSION` selects one explicitly.

The historical table uses scored final outputs with preceding-pass fallbacks
and includes targeted older experiments. A fresh uniform run does not recreate
that experimental history.

Generated proofs are **ungraded**. The script does not assign old scores to new
text. Repeating model generation is not guaranteed to return identical text,
even with the same seeds and settings. [Workshop Tools](../experiments/workshop_tools/README.md)
remains a separate experimental opt-in.

### IMO 2026 plus a random ProofBench sample

[scripts/run_sampled_suite.py](../scripts/run_sampled_suite.py) runs all **six
IMO 2026 problems**, **three Basic problems** sampled without replacement from
the 30-problem Basic pool, and **three Advanced problems** sampled without
replacement from the 30-problem Advanced pool. It uses the existing full
pipeline, with four candidate lanes per problem: **12 problems / 48 planned
proof candidates**. The three benchmarks run sequentially against the same
Gemma and Qwen servers. There are no external grading calls.

With both local servers already ready, launch the suite in the background:

```bash
mkdir -p .workshop/runs
WORKSHOP_RUN_ID="suite_$(date +%Y%m%d_%H%M%S)"
nohup .venv-solver/bin/python -u scripts/run_sampled_suite.py \
  --run-id "$WORKSHOP_RUN_ID" \
  --random-sample-seed --random-generation-seed \
  > ".workshop/runs/$WORKSHOP_RUN_ID.log" 2>&1 < /dev/null &
echo $! > ".workshop/runs/$WORKSHOP_RUN_ID.pid"
echo "Run ID: $WORKSHOP_RUN_ID"
tail -n 50 -F ".workshop/runs/$WORKSHOP_RUN_ID.log"
```

Ctrl-C exits this log viewer; the suite continues in the background. The suite
copies the active benchmark's `generation/console.log` into this single outer
log, so raw-generation, refinement and final-export progress are visible there.
It uses the already-running servers; it does not restart or reconfigure them.

Seed controls are independent:

| Purpose | Fixed setting | Random setting |
| --- | --- | --- |
| Select Basic and Advanced problems | `--sample-seed N` (default: `0`) | `--random-sample-seed` |
| Model generation | Omit generation flags for the original fixed settings, or use `--generation-seed N` | `--random-generation-seed` |

Random options draw unsigned 32-bit values once per suite and record them in
`.workshop/runs/<run-id>/plan.json`, along with the exact selected IDs, input
hashes and launch commands. The generation seed sets the raw seed offset and
the refinement namespace `workshop-generation:N`. Omitting generation flags
keeps offset `0` and the original `v263-v290:problem-only` namespace; explicitly
passing `--generation-seed 0` selects the custom namespace instead. Some
auxiliary calls retain their existing proof-hash/stage-derived seeds. Sampling
settings, prompts and refinement logic are otherwise unchanged.

To repeat the selection and generation seed settings, use the two recorded
numbers and a **new run ID**:

```bash
.venv-solver/bin/python -u scripts/run_sampled_suite.py \
  --run-id suite_repeat_001 --sample-seed 123 --generation-seed 456
```

The numbers above are examples; substitute the saved values. Identical seed
settings do not guarantee byte-identical model outputs. The single-benchmark
`scripts/reproduce.py generate` command also accepts `--generation-seed N` or
`--random-generation-seed`; omitting both preserves its existing behavior.

`--dry-run` prints the selection and commands without creating files or making
model calls, and does not require the solver environment. Random flags draw new
values on each invocation, including dry runs; use the printed seed values to
execute an exact previewed selection. Existing suite or benchmark run paths are
never overwritten. On a benchmark failure, the suite records it and stops before
starting another benchmark. This wrapper does not resume an interrupted run.

Completion is recorded in `.workshop/runs/<run-id>/status.json`. Each benchmark
retains its own artifacts under `benchmarks/<benchmark>/results/<run-id>/`:
`generation/run/proofs/` contains submitted proofs and
`generation/run/final_results.json` records the per-lane result. Generation
completion does not establish mathematical correctness.

Each problem attempts the refinement passes before the next problem starts.
In B 1.12.0, a changed R3 proof first needs four approvals from the Gemma/Qwen
replacement audit; otherwise R2 is selected. See [the exact policy](harness_b_selection.md).
The submitted proof for each candidate is its last eligible completed checkpoint:
**Refinement 3 → Refinement 2 → Refinement 1 → lazy-checked → raw**.
An ordinary stage failure retains the earlier proof and allows the queue and
suite to continue. `final_results.json` records `completed_with_fallbacks` when
the run contains such submissions, with the actual `selected_stage`, failure
reason, and separate fully refined/fallback counts. This is successful
submission generation, not a claim that every candidate reached C3.
User interruption, a missing completed proof, or an export failure still
prevents a successful run. Original prompts, seeds and frozen engine code are
unchanged by the submission policy.

`generation/run/problem_sequence.json` records each problem's start/end time
and `elapsed_seconds`, including its candidate refinement attempts and fallback
collection. This is wall time for the four-candidate portfolio, not the sum of
overlapping model requests. `resumed` identifies timings from a resumed
invocation; those are not presented as fresh end-to-end durations.

### Select one proof per problem (experimental)

The [independent proof selector](proof_selector.md) reads the four unchanged
final candidates after a sampled suite completes. It uses native thinking-prefix
extended reasoning with role-specific continuations and writes to
`.workshop/selections/`, separately from generation and grading. The guide covers
one-problem preflight, background execution, the full 12-problem bank, input
limits and saved artifacts. This experimental selection does not establish
mathematical correctness or replace the existing benchmark metrics.

### Grade a completed sampled suite

To compare generic and role-specific continuation wording in Refinement 1–3,
use the [independent paired experiment](refinement_bf_ablation.md). It starts
from saved lazy-checked proofs, preserves the original chat extended reasoning mechanism and
writes separate results; its grading input format differs from the suite below.

[scripts/grade_sampled_suite.py](../scripts/grade_sampled_suite.py) grades the
**48 submitted final proofs** from a completed 6+3+3 run. It reads the saved suite
plan and each controller's `final_results.json`, including earlier-stage
fallbacks. It refuses unfinished suites, missing lanes, altered proof bytes,
or mismatched statement/reference hashes before starting grading. It does not
regenerate proofs or change the generation directory.

The suite wrapper calls [score_proofbench.py](../scripts/score_proofbench.py),
which verifies and loads the bundled
[IMOBench grading skill's scorer](../benchmarks/imo-proofbench/advanced/results/pipeline_raw_r1c3/grading/scorer/SKILL.md),
and [score_imo_v2.py](../scripts/score_imo_v2.py), which adapts the archived
[strict Olympiad grading skill](../benchmarks/imo2026/results/p2_t07_r02_v356_consolidated_20260917T071542Z/grading/strict_config/SKILL.md)
to the current v2 policy. Use these public scripts for new runs; the strict
skill's original instructions describe v1. Both skill archives and their scorer
dependencies are tracked in Git, so separate skill installation is unnecessary
for these commands. Each evaluator call disables skill discovery and tools;
the skills describe the grading workflow outside the isolated scoring call.

Use Python 3.9+ on a POSIX machine with the completed run, an authenticated
`codex` executable on `PATH`, and access to **gpt-5.6-sol / xhigh**. The solver
venv is sufficient; no additional Python packages or GPU servers are needed
for grading. The hosted grader is separate from Gemma and Qwen.

The rubrics match the published experiment. New sampled-suite runs grade every
benchmark in **two separate passes** by default:

- **IMO 2026:** Strict Olympiad v2, **two passes** by default. Report the mean
  of both grades for each proof, retaining both original passes.
- **Basic and Advanced:** IMOBench B.5, **two passes**, with the published prompt,
  official per-problem reference and guidelines, and scores in **0, 1, 6, 7**.
  The frozen B.5 runner may reuse a grade for identical proofs of the same
  problem within a pass; that reuse is recorded. Pass 2 uses a separate output
  directory and does not reuse pass 1's grades. For Basic and Advanced separately,
  report the mean of both grades for each proof. Both passes and their
  explanations are retained; historical published grades stay unchanged.

Average first averages the proof means within each problem, then weights every
problem equally. Oracle@4 takes the largest proof mean within each problem;
it is not the mean of the two pass-specific oracle scores. The wrapper uses
this mean-per-proof convention for new reports, matching the current README.
Older reports that selected a complete lower-Average pass remain historical records.

There are **96 planned grade records: all 48 submitted proofs graded twice**.
Invalid responses may trigger the scorers' bounded retries; they accept
the first valid response, not the highest score. `--imo-passes 1` selects a
single-pass diagnostic, which does not reproduce the two-pass reporting rule.
Failed or missing grades never become zero scores, and an incomplete benchmark
does not receive an aggregate score.

First read the [external-reference setup](public_release/grading/README.md#external-imo-reference-setup).
The IMO references are fetched from the recorded upstream revision and kept
local; `pdftotext` is required for their preparation. On Ubuntu, install it with
`sudo apt-get install poppler-utils` if needed. `--download-references` explicitly
downloads these references and the official ProofBench CSV, verifies their
recorded hashes, and caches them under `.workshop/external-references/`.
It does not download model weights. `--dataset PATH` can select an existing
byte-identical ProofBench CSV instead.

After generation finishes, preflight the run from the repository root:

```bash
WORKSHOP_RUN_ID="suite_e2e_20260919_142752"
WORKSHOP_GRADING_ID="grading_$(date -u +%Y%m%dT%H%M%SZ)"
.venv-solver/bin/python -B scripts/grade_sampled_suite.py \
  --run-id "$WORKSHOP_RUN_ID" --grading-id "$WORKSHOP_GRADING_ID" \
  --download-references --dry-run
```

The dry run validates inputs without contacting the grader or creating result
directories. The explicit download flag may populate the reference cache.
After it succeeds, launch the grading separately in the background:

```bash
mkdir -p .workshop/runs
nohup .venv-solver/bin/python -u -B scripts/grade_sampled_suite.py \
  --run-id "$WORKSHOP_RUN_ID" --grading-id "$WORKSHOP_GRADING_ID" \
  --workers 4 \
  > ".workshop/runs/${WORKSHOP_RUN_ID}_${WORKSHOP_GRADING_ID}.log" 2>&1 < /dev/null &
echo $! > ".workshop/runs/${WORKSHOP_RUN_ID}_${WORKSHOP_GRADING_ID}.pid"
```

Each actual invocation needs a fresh grading ID; the suite grading wrapper does
not resume or overwrite an earlier grading run. Logs print each pass's detailed
log location. It refreshes each successfully graded experiment's artifact index.
Results are saved under the **same generation run ID**:

| Path | Contents |
|---|---|
| `benchmarks/reports/<run-id>_grading/<grading-id>/REPORT.md` | Combined score table, per-problem generation time, C3 and fallback counts |
| Same directory: `summary.json`, `manifest.json` | All pass scores, completion/failure state, seeds, source hashes and evaluator identities |
| `benchmarks/<benchmark>/results/<run-id>/proofs/<grading-id>/` | Exact submitted proof snapshots |
| Same experiment: `grades/<grading-id>/` | Per-proof structured grades, B.5 explanations and benchmark summary |
| Same experiment: `reports/<grading-id>.md`, `manifest.json` | Benchmark report and proof/grade artifact bindings |
| Same experiment: `grading/work/<grading-id>/` | Private frozen inputs, task manifests, raw evaluator output and pass logs; Git-ignored |

Generation time is taken from `problem_sequence.json`, covers the four-lane
portfolio including refinement attempts, and excludes grading. Unavailable
timings remain unavailable; resumed segments are labeled. Average and Oracle@4
are reported separately. Oracle@4 is a hindsight best-of-four measure, not an
automatically selected competition submission. These are automated judgments,
not mathematical verification.

For an individual ProofBench batch, the portable adapter is
`scripts/score_proofbench.py --task-manifest TASKS --dataset CSV --output-dir NEW_DIR`.
IMO batches continue to use `scripts/score_imo_v2.py --generic-task-manifest TASKS
--output-dir NEW_DIR`. The suite wrapper builds these hash-bound task manifests
automatically; neither scorer receives pipeline reviews or past grades.

### Archive all intermediate results for paired studies

Keep the original suite and experiment directories on the server. To commit a
completed suite's full intermediate evidence, use
[scripts/archive_sampled_suite.py](../scripts/archive_sampled_suite.py). This
standard-library tool makes no model calls and does not change the original
run, stage files in Git, or commit anything. It refuses running, failed or
inconsistent suites, and verifies all **48 final proof bindings** before
exporting. Existing pre-Qwen inputs are bound separately for paired studies;
early fallback submissions without such inputs are retained and explicitly
marked unpaired rather than supplied with an invented baseline.

From the repository root, substitute the actual run ID:

```bash
WORKSHOP_RUN_ID="suite_20260919_095541"
.venv-solver/bin/python -B scripts/archive_sampled_suite.py \
  --run-id "$WORKSHOP_RUN_ID" --dry-run
.venv-solver/bin/python -B scripts/archive_sampled_suite.py \
  --run-id "$WORKSHOP_RUN_ID"
```

The dry run checks completion, input hashes, seed agreement and estimated size;
publication-content checks occur during the actual export. The archive is
`benchmarks/reports/<run-id>_full_trace/`, with:

- `suite/plan.json` and `status.json`: problem selections and sampling/generation seeds;
- `artifacts/<benchmark>/`: all available intermediate generation artifacts,
  including raw/lazy/expansion proofs, per-refinement reviews, fusion, audits,
  repair briefs, resolver outputs, prompts, model responses, metadata and final proofs;
- environment captures: model revisions/configurations, BF16 and KV-cache
  settings, MTP configuration, dependency versions, source snapshots and timing;
- `archive_manifest.json`: original and archived file hashes, an exclusion
  inventory, `paired_inputs` linking available exact pre-Qwen inputs to final
  proofs, and `unpaired_finals` explaining absent pre-Qwen inputs. Actual
  submitted checkpoint names and per-problem timing are preserved.

Operational logs, process state, virtual environments, weight binaries and
external grading work are excluded from the Git copy. They remain untouched on
the server. Model configuration and weight-identity records are retained.
Statements and proof files keep their exact bytes. Prompt/model-response text
is preserved. Recognized machine-path metadata is normalized for publication,
with both source and archive hashes recorded. A disallowed value in model text
causes export to fail instead of silently changing the evidence. Files over
90 MiB require a separate storage decision; they are never silently dropped.

Verify the portable archive, then stage **only that archive directory**:

```bash
WORKSHOP_ARCHIVE="benchmarks/reports/${WORKSHOP_RUN_ID}_full_trace"
.venv-solver/bin/python -B scripts/archive_sampled_suite.py --verify "$WORKSHOP_ARCHIVE"
git add -- "$WORKSHOP_ARCHIVE"
.venv-solver/bin/python -B scripts/audit_release.py
git diff --cached --stat
git diff --cached --check
```

Continue only if verification/audit succeeds and the staged diff contains only
the intended archive:

```bash
git commit -m "Archive ${WORKSHOP_RUN_ID} full intermediate evidence for paired ablations"
git push origin HEAD:release/public-rc1
```

The archive itself is portable, but normalized provenance records are **not
native resume manifests**: embedded hashes refer to original source artifacts.
Keep the originals. A paired ablation must stage fresh manifests from the
byte-identical pre-Qwen inputs and recorded settings; the exporter does not
implement or run the Gemma-only comparison. The same retained intermediates can
support later precision experiments, without claiming that those experiments
have already run.

The current follow-up scope prioritizes end-to-end mixed-model runs and
generation-seed sensitivity on a fixed selection of problems. The complete
Gemma-only comparison and NVFP4 studies are deferred; keeping paired inputs
preserves those options without committing to running them now. The
[mixed-model rationale](mixed_model_rationale.md) records the historical design
motivation and the limits of the available evidence.

### Interrupted runs

On a worker error, SIGINT or SIGTERM, the controller stops active generation
processes and exports each lane's **last eligible completed proof** in this order (a changed R3 proof requires all four audit approvals in 1.12.0):
Refinement 3 → Refinement 2 → Refinement 1 → lazy-checked → raw. It checks
completion records, candidate identity and proof hashes; an unfinished proof
file alone is not eligible. Selection uses completion order, never a grade.
No additional model calls are started after a run interruption. If one final
refinement fails, other running lanes can finish and that lane uses its last
completed proof.

Ordinary refinement failure is different from interruption: after selecting
the failed lane's earlier completed proof, the per-problem queue continues
with the remaining problems. The C3 attempt is not repeated during final export.

The process still returns a nonzero status on failure. `final_results.json`
records the run's execution status and, for each lane, `proof_available`,
`selected_stage`, exported file hash, producer, completion record, and
interruption stage/reason. If a stop left no exact stage or cause on disk, the
receipt identifies an inferred stage or an unknown cause. A lane with no
completed proof has `proof_available: false`; no placeholder proof is created.
Here “completed” means generation completed, not mathematical correctness.

A hard kill (SIGKILL), power loss, or machine crash cannot execute cleanup.
After its workers have stopped, collect the saved proofs without model calls:

```bash
python3 -B harnesses/proof_workshop/run.py --collect-only \
  --output-dir benchmarks/imo-proofbench/basic/results/local_basic001_001/generation/run
```

Use the actual `generation/run` directory for the interrupted experiment.
This command writes `proofs/` and `final_results.json`, leaves intermediate
artifacts intact, and does not resume inference or run grading. It refuses to
collect from an active run. Repeated collection preserves exported proof
contents. Its exit status remains nonzero for an incomplete run even when
proofs were successfully exported. If the outer benchmark launcher was also
killed, its experiment-level completion/index files may remain unfinished;
this recovery command updates the generation results only.

### Recorded format recovery

New 1.12.0 harness runs automatically correct two explicit label mismatches:
a fusion assessment that says a reviewer missed a defect but labels it as
no defect, and a lazy repair that declares `PRESERVE` while supplying distinct
conclusions and a justified change. Only the labels change; proof text and raw
responses are preserved, and strict validation still applies. The correction
code is captured and hash-bound to each new run, with receipts under
`generation/run/label_recoveries/` and in parsed stage results. Existing runs
retain their original behavior, including on resume.
Truncated, empty or ambiguous answers remain failures.

New runs also recover a missing `Decisive checks` heading in a proof comparison
when the existing qualifications contain substantive prose citing at least two
distinct proof locations. The harness copies that evidence verbatim, preserves
the explicit winner and original response, and records hashes and the applied
rule. This works for normal responses and the existing answer-only timeout
continuation, without another model call. The comparison recovery code is
captured with the run; older runs keep their saved rules.

## Quick-start reference

The following setup and experiment reference was moved from the release README.
Commands run from the repository root; the detailed chapters above cover
configuration, diagnostics and recovery.

### Reproduce with scripts

No Codex or hosted inference account is needed. To check saved artifact hashes,
proof-to-grade bindings and score arithmetic, and regenerate the published score
matrices, run:

```bash
python3 -B scripts/reproduce.py
```

This checks the integrity and consistency of the saved evidence; it does not
verify the proofs' mathematical correctness or rerun external grading.

To generate fresh proofs on your own GPUs, use a final Python 3.11 release
(recorded: **3.11.15**) to install dependencies and download the pinned Gemma,
Gemma MTP assistant and Qwen checkpoints. Check `python3.11 -VV` first; see
[Python environment recovery](local_reproduction.md#replace-a-prerelease-python-environment)
if it reports a prerelease such as `3.11.0rc1`:

```bash
python3.11 scripts/setup_environment.py --install --download-models
```

Follow the [local reproduction guide](local_reproduction.md) to start both
local servers and run a problem. Model weights are downloaded directly from
[their providers](models.md) and are not part of this repository. New local
proofs are ungraded; offline report reproduction uses the saved historical grades.

### Setup

#### Inspect the release and verify the report

No GPUs, model weights or hosted grading credentials are needed for the report
verifier. It uses Python 3.9 or later and the standard library.

```bash
git clone https://github.com/trinitylabs-ai/trinitysm.git
cd trinitysm
python3 -B docs/public_release/verify_scores.py
python3 -B harnesses/proof_workshop/run.py --version
python3 -B harnesses/proof_workshop/run.py --list-releases
python3 -B harnesses/proof_workshop/run.py --release 1.12.0 --verify
```

The report verifier checks all 264 lane records, the 263 included selections,
proof/grade bindings, grading-policy identities and bundled artifact hashes. It
also verifies the original 240 Basic raw grades, 718 current ProofBench ablation
selections and the two-pass IMO evidence, then recomputes all published matrices
without accessing the original run directories.

#### Run the complete harness

Run the following commands from the repository root on the Linux GPU server.
Install NVIDIA drivers and a **final Python 3.11 release** first; the recorded
version is **3.11.15**. Check `python3.11 -VV` and avoid prereleases such as
`3.11.0rc1`; the installer also checks Python inside existing environments.
See [Python environment recovery](local_reproduction.md#replace-a-prerelease-python-environment)
if needed. If a model provider requires
authentication or access approval, complete that step before downloading.
The setup script installs the solver and vLLM environments and downloads the
pinned Gemma, Qwen and Gemma MTP assistant checkpoints:

```bash
python3.11 scripts/setup_environment.py --install --download-models
```

Choose a GPU layout. **Both use the same B 1.12.0 harness**, four candidate
lanes, R2/R3 audit and final proof selector:

| Layout | How the models run | Recorded hardware |
|---|---|---|
| **Two GPUs** | Gemma and Qwen stay on separate GPUs; their requests can overlap | 2 × 96 GB GPUs |
| **One GPU** | Gemma and Qwen alternate on the same GPU; sleeping weights use file-backed CPU memory | 1 × 96 GB GPU, approximately 128 GB system RAM and local SSD storage |

**Option 1 — two GPUs:** start the background servers, then generate:

```bash
python3 scripts/local_servers.py start --gemma-gpu 0 --qwen-gpu 1
python3 scripts/reproduce.py generate \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --run-id local_basic001_two_gpu
```

**Option 2 — one 96 GB GPU, using the switching mode from the finalized run:**

```bash
python3 scripts/local_servers.py start --single-gpu 0 --timeout 1800
python3 scripts/run_single_gpu.py \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --run-id local_basic001_one_gpu
```

The single-GPU runner gathers ready work for the awake model, waits for active
requests to finish, then sleeps that model and wakes the other. Queue time is
excluded from inference deadlines. It preserves BF16 weights, MTP, prompts,
seeds, sampling, extended reasoning and selection policies. Gemma uses the recorded
28 GiB KV allocation. This mode was used to continue the final ProofBench run
after the second GPU went offline; its [saved run record](results/proofbench_single_gpu_20260926/README.md)
records **26 model switches**. It does not require both models to fit in VRAM
at once. See the [one-GPU guide](local_reproduction.md#one-96-gb-gpu-with-model-switching)
for storage, progress, stopping and full-benchmark commands.

Both layouts use Gemma on port **8030** and Qwen on port **8027**. Startup logs
are under `.workshop/servers/`. Finish or interrupt generation, then run
`python3 scripts/local_servers.py stop` before changing layouts.

The following additional examples use the two-GPU runner; for one GPU, replace
`scripts/reproduce.py generate` with `scripts/run_single_gpu.py`. The harness uses four
candidate lanes, runs up to three refinement passes and exports each lane's
last eligible completed proof, when available (1.12.0 requires all four audit approvals for a changed R3 proof; otherwise R2 is submitted):

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --run-id local_basic001_001
```

For IMO 2026 P1, use the same script with the IMO benchmark and problem ID:

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo2026 --problem-id imo2026_p1 \
  --run-id local_imo2026_p1_001
```

To run all six IMO 2026 problems, omit `--problem-id`:

```bash
python3 scripts/reproduce.py generate \
  --benchmark imo2026 --run-id local_imo2026_all_001
```

To run all six IMO problems plus **three randomly selected Basic and three
Advanced problems**, use [the sampled-suite script](local_reproduction.md#imo-2026-plus-a-random-proofbench-sample).
The guide includes a background command and one combined progress log.
`--random-sample-seed` and `--random-generation-seed` independently randomize
and record the two seeds. Without generation seed flags, the original fixed
seed settings remain in effect.

B 1.12.0 already includes R2/R3 selection and cross-lane voting; the voter chooses one proof without access to external grading. The separately developed
[independent experimental proof selector](proof_selector.md) can also
choose one unchanged candidate per problem using Gemma/Qwen reviews, audits and
role-specific native thinking-prefix extended reasoning. It writes separate results
and does not change the generation harness or published evaluation metrics.
Its selection quality still needs benchmark evaluation.

An [isolated refinement experiment](refinement_bf_ablation.md) compares the
original chat extended reasoning continuation with role-specific wording from the same four
saved lazy-checked proofs. It preserves the original extended reasoning mechanism and frozen
harness, and exports paired results for separate two-pass grading.

An [independent final-proof completion experiment](post_c3_completion.md) applies
one omission check and, when needed, one local expansion to all saved B final
proofs, including earlier-stage fallbacks.
It uses the original chat extended reasoning with new role-specific instructions, preserves
the original proofs and grades, and exports only changed proofs for grading.

A separate [raw-proof block-repair experiment](block_local_completion.md)
starts before lazy-check and refinement. Gemma returns edits for identified
blocks and their immediate neighbors, Qwen audits the patched proof, and Gemma
can resolve the audit once. It preserves untouched source bytes and compares
repair temperatures 0.7 and 0.4 with an original whole-proof expansion control
at 0.4, using the same raw drafts and seeds. All eligible lanes run concurrently
in batches of four; raw and repaired proofs receive separate two-pass grading.

The [completed six-problem B comparison](../benchmarks/imo2026/results/refinement_bf_B6_selection_first_20260920_1426/README.md)
reports **4.396/7** for role-specific cues versus **4.042/7** for archived original
cues, with **8/24 versus 5/24** proofs receiving full credit in both passes.
The archive includes every proof, both grades and the full score matrix. This
historical-control result is separate from the main release metrics; selector
results and the later P3 recovery are excluded.

You can also [archive its full intermediate results](local_reproduction.md#archive-all-intermediate-results-for-paired-studies)
for paired ablations. The exporter preserves pre-Qwen inputs, final proofs,
reviews, audits, model responses and serving settings with file hashes.

Use a fresh run ID each time. With `reproduce.py generate`, add `--dry-run` for
a model-free preflight, or use `--benchmark all` without `--problem-id` to run
all 66 problems. Its generation preflight also creates a run directory, so use
a different run ID for actual generation. Final proofs are saved in
`benchmarks/<benchmark>/results/<run-id>/generation/run/proofs/`;
`final_results.json` records each lane's completion, selected stage, proof hash
and producer. If execution stops, each lane's last eligible completed proof becomes its
final submission: Refinement 3 → 2 → 1 → lazy-checked → raw. Partial outputs are
excluded. The run retains its failure status and records the interruption
stage and cause separately from proof availability. See the
[interrupted-run recovery instructions](local_reproduction.md#interrupted-runs).

Inspect the background servers or follow their logs:

```bash
python3 scripts/local_servers.py status
tail -f .workshop/servers/gemma.log .workshop/servers/qwen.log
```

Ctrl-C exits the log viewer. To stop the managed servers after the run:

```bash
python3 scripts/local_servers.py stop
```

The manager controls only servers it started; unrelated servers occupying the
same ports are not adopted or stopped. See the
[server instructions](local_reproduction.md#start-the-two-local-servers)
for GPU selection, custom model-cache paths and foreground operation.

The original hardware was **2 × RTX PRO 6000 Blackwell 96 GB**, with BF16 weights
and four-token MTP decoding. The final run continued with the recorded
**one-GPU sleep/wake adapter** after GPU 1 went offline. These are observed
configurations, not measured minimum requirements.
The [local guide](local_reproduction.md) describes installation, serving and
reproduction limits. The [composite entry point](../harnesses/proof_workshop/README.md)
also accepts custom statement-only input directories.

#### Run raw generation without extended reasoning

To run without extended reasoning after starting the local Gemma server:

```bash
python3 -B scripts/generate_raw.py \
  --benchmark imo-proofbench/basic --problem-id PB-Basic-001 \
  --output-dir runs/basic001_raw_no_bf --execute-models
```

This generates four raw drafts. Omit `--problem-id` for all 30 Basic problems,
or change the benchmark to Advanced or IMO 2026. See the
[raw ablation instructions](local_reproduction.md#ablation-four-raw-proofs-without-extended-reasoning)
for preparation without model calls, saved outputs, resume and the two-GPU queue.
